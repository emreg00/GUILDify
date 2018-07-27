
import MySQLdb

DATA_DIR = "/home/emre/arastirma/guildify/data/"
DB_NAME = "test_GUILDIFY_2013" # test_BIANA_JUNE_2011
UNIX_SOCKET = None #"/home/emre/tmp/mysql.sock"

def main():
    fetch_data()

    if UNIX_SOCKET is not None:
	db = MySQLdb.connect(UNIX_SOCKET) #host= dbhost, user=dbuser, passwd=dbpassword) #)
    else:
	db = MySQLdb.connect() 
    cursor = db.cursor()
    query = "use %s" % DB_NAME 
    cursor.execute(query)

    create_tables(cursor)
    insert_data(cursor)
    create_indices(cursor)

    cursor.close()
    db.close()

    create_drug_target_mapping()
    return

def fetch_data():
    import os
    for folder in ["omim", "go", "drugbank"]:
	if not os.path.exists(DATA_DIR + folder):
	    os.mkdir(DATA_DIR + folder)
    # OMIM
    os.system("wget ftp://anonymous:e%2Eguney%40neu%2Eedu@grcf.jhmi.edu/OMIM/morbidmap")
    os.system("mv morbidmap %s/omim/" % DATA_DIR)
    # DrugBank
    os.system("wget http://www.drugbank.ca/system/downloads/current/drugbank.xml.zip")
    os.system("unzip drugbank.xml.zip")
    os.system("mv drugbank.xml %s/drugbank/" % DATA_DIR)
    # GO
    os.system("wget http://www.geneontology.org/ontology/obo_format_1_2/gene_ontology.1_2.obo")
    os.system("mv gene_ontology.1_2.obo %s/go/" % DATA_DIR)
    species_prefices = [ "goa_human", "mgi", "rgd", "sgd", "wb"] 
    species_prefices += [ "fb", "zfin", "ecocyc", "goa_chicken", "goa_cow", "tair", "pombase" ]
    for species_prefix in species_prefices:
	print species_prefix
	os.system("wget http://cvsweb.geneontology.org/cgi-bin/cvsweb.cgi/go/gene-associations/gene_association." + species_prefix + ".gz?rev=HEAD")
	os.system("mv gene_association.%s.gz?rev=HEAD %s/go/" % (species_prefix, DATA_DIR))
    return

def create_drug_target_mapping():
    from parse_drugbank import output_drug_info # get_drug_info, get_drugs_for_targets
    drugbank_file = DATA_DIR + "drugbank/drugbank.xml" # test.xml
    #output_file = DATA_DIR + "drugs.txt"
    #get_drugs_for_targets(drugbank_file, output_file)
    output_file = DATA_DIR + "drug_info.txt"
    #get_drug_info(drugbank_file, output_file)
    output_drug_info(drugbank_file, output_file)
    return

def create_tables(cursor):
    query = "\
    CREATE TABLE IF NOT EXISTS guildify_descriptions (\
	desc_id INT NOT NULL AUTO_INCREMENT,\
	description text,\
	source ENUM('swissprot', 'trembl', 'go', 'omim', 'other'),\
	PRIMARY KEY (desc_id)\
    )\
    ENGINE=MyISAM;\
    "
    cursor.execute(query)

    query = """
    CREATE TABLE IF NOT EXISTS guildify_genes (
	id INT NOT NULL AUTO_INCREMENT,
	desc_id INT NOT NULL,
	gene_symbol VARCHAR(255) NOT NULL,
	tax_id INTEGER(3) UNSIGNED,
	PRIMARY KEY (id)
    )
    ENGINE=MyISAM;
    """
    cursor.execute(query)
    #try:
    #	cursor.execute(query)
    #	result = cursor.fetchall()
    #except Exception, inst:
    #	print str(inst)
    #	#raise ValueError(inst)
    return

def insert_data(cursor):
    # swissprot / trembl - unique - description / function / keywords / disease
    insert_uniprot_data(cursor)
    # omim
    insert_omim_data(cursor)
    # go
    insert_go_data(cursor)
    return

def insert_uniprot_data(cursor):
    for source in ['swissprot', 'trembl']:
	cursor.execute("SELECT externalDatabaseID, databaseName FROM externalDatabase")
	db_found = False
	for row in cursor.fetchall():
	    if row[1] == source: # 'swissprot': 7 'trembl': 1
		db_id = int(row[0])
		db_found = True
		break
	if db_found is False:
	    raise ValueError("Unknown source: %s" % source)
	for table_type in ['Description', 'Function', 'Keyword', 'Disease']:
	    query = "SELECT D.value, G.value, T.value FROM externalEntity E, externalEntity%s D, externalEntityGeneSymbol G, externalEntityTaxID T where E.externalEntityID=D.externalEntityID AND E.externalEntityID=G.externalEntityID AND E.externalEntityID=T.externalEntityID AND E.externalDatabaseID=%s AND G.type='unique'" % (table_type, db_id)
	    fill_guildify_tables_from_query_results(cursor, query, source)
    return

def insert_omim_data(cursor):
    f = open("%s/omim/morbidmap" % DATA_DIR) 
    desc_to_genes = {}
    for line in f:
	words = line.strip().split("|")
	if words[0][0] == "?":
	    continue
	desc = words[0]
	for word in words[1].split(", "):
	    desc_to_genes.setdefault(desc, set()).add(word.strip())
    f.close()
    tax_id = "9606"
    result = []
    for desc, genes in desc_to_genes.iteritems():
	result.append( (desc, [(gene, tax_id) for gene in genes] ) )
    fill_guildify_tables_from_results(cursor, result, 'omim')
    return

def insert_go_data(cursor):
    from GO import GO
    species_prefices = [ "goa_human", "mgi", "rgd", "sgd", "wb"] 
    species_prefices += [ "fb", "zfin", "ecocyc", "goa_chicken", "goa_cow", "tair", "pombase" ]
    for species_prefix in species_prefices:
	print species_prefix
	go = GO("%s/go/gene_ontology.1_2.obo" % DATA_DIR, 
		False, 
		"%s/go/gene_association.%s.gz?rev=HEAD" % (DATA_DIR, species_prefix), 
		exclude_evidences=[])
	print len(go.g.nodes()), len(go.go_id_to_genes)
	result = []
	for go_id, data in go.g.nodes(data=True):
	    if go_id not in go.go_id_to_genes:
		continue
	    desc = data['n']
	    result.append( (desc, [(gene, tax_id) for gene, tax_id in go.go_id_to_genes[go_id]] ) )
	fill_guildify_tables_from_results(cursor, result, 'go')
    return

def regularize_string(val):
    if isinstance(val, unicode):
	# Transform to ascii
	value = val.encode('ascii','replace')
    else:
	value = str(val)
	value = "\"%s\"" % value.replace('\\','\\\\').replace('"','\\"')
    return value

def fill_guildify_tables_from_query_results(cursor, query, source):
    cursor.execute(query)
    result = cursor.fetchall()
    for row in result:
	#print row
	value = regularize_string(row[0])
	query = """INSERT INTO guildify_descriptions (description, source) VALUES (%s, '%s')""" % (value, source) 
	cursor.execute(query)
	query = "Select LAST_INSERT_ID()"
	cursor.execute(query)
	desc_id = int(cursor.fetchone()[0])
	value = regularize_string(row[1]).replace("'", "\\'")
	query = """INSERT INTO guildify_genes (desc_id, gene_symbol, tax_id) VALUES ('%s', %s, '%s')""" % (desc_id, value, row[2]) 
	cursor.execute(query)
    return

def fill_guildify_tables_from_results(cursor, result, source):
    for desc, genes in result:
	#print row
	value = regularize_string(desc)
	query = """INSERT INTO guildify_descriptions (description, source) VALUES (%s, '%s')""" % (value, source) 
	cursor.execute(query)
	query = "Select LAST_INSERT_ID()"
	cursor.execute(query)
	desc_id = int(cursor.fetchone()[0])
	for gene, tax_id in genes:
	    value = regularize_string(gene).replace("'", "\\'") # if commented %s -> '%s' below
	    query = """INSERT INTO guildify_genes (desc_id, gene_symbol, tax_id) VALUES ('%s', %s, '%s')""" % (desc_id, value, tax_id) 
	    cursor.execute(query)
    return


def create_indices(cursor):
    query = "ALTER TABLE guildify_descriptions ADD FULLTEXT (description);"
    cursor.execute(query)
    return

if __name__ == "__main__":
    main()

