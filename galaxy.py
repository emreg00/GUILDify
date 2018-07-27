import ConfigParser 
from test2.models import BIANAQuery
from test2.models import GUILDifier
from test2.models import GUILDScoreParser
import uuid


def main():
    g = get_guildify()
    print g.get_species()
    #get_available_species()
    species = "9606"
    #keywords = '"inflammatory bowel disease"'
    keywords = '"alzheimer disease"'
    d = g.phenotype_to_genes(keywords, species)
    print d
    query_ids = d["user_entity_ids_in_network"] #['14807906'] 
    parameters = { "netscore": None, "repetitionSelector": 3, "iterationSelector": 2 }
    d = g.genes_to_scores(query_ids, species, parameters)
    print d
    return


def get_guildify():
    g = GUILDify("config.ini")
    return g 


def get_available_species():
    g = get_guildify()
    return g.get_species()


class GUILDify:

    def __init__(self, config_file):
	config = ConfigParser.SafeConfigParser()
	config.read(config_file)
	self.settings = dict(config._defaults)
	#self.settings = self.create_settings_dict(db_host, db_user, db_pass, db_name, unification_protocol, guild_excecutable, data_dir, cluster_script, queue_name)
	GUILDifier.set_parameters(self.settings)
	return

    
    def get_settings(self):
	return self.settings


    def get_species(self):
	#GUILDifier.set_parameters(self.settings)
	return { "species_list": BIANAQuery.SPECIES_NAMES,
		 "species_to_value": BIANAQuery.SPECIES_NAME_TO_VALUE } 

    def phenotype_to_genes(self, keywords, species):
	#g = get_guildify()
	user_entity_ids = None 
	genes = None 
	ue_ids = []
	try:
	    query = BIANAQuery(self.get_settings())
	except ValueError, e:
	    if e.message == "biana":
		print 'Internal server error, please reload the page and and try again! Contact to the webmaster if the problem persists.'
	try:
	    values, ue_ids, ue_ids_in_network = query.get_associated_user_entities(keywords, species, user_entity_ids, genes)
	    if values is None:
		print 'No match for the query!'
	    #values = [('410664',), ('108201',), ('409022',)] 
	    values_in_network = []
	    values_not_in_network = []
	    for val in values:
		if val[0].endswith("disabled/>"):
		    values_not_in_network.append(val)
		else:
		    values_in_network.append(val)
	except ValueError, e:
	    # None of the added genes are found
	    if e.message == "biana": 
		print 'No match for genes in the query! You can go back and try with other gene symbols.'
		return 
	except Exception, inst: # inst.message == "biana"
	    print "Execption inst:", inst
	    print 'Invalid session, please start over!'
	    return
	return dict(keywords = keywords, 
		    tax_id = species, 
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[species], 
		    n_node = len(values),
		    n_node_in_network = len(values_in_network),
		    n_node_not_in_network = len(values_not_in_network),
		    user_entity_ids = ue_ids,
		    user_entity_ids_in_network = ue_ids_in_network,
		    values_in_network = values_in_network,
		    values_not_in_network = values_not_in_network)


    def genes_to_scores(self, query_ids, species, parameters):
	"""
	parameters containing scoring parameters
	"""
	#g = get_guildify()
	settings = self.get_settings()
	GUILDifier.set_parameters(settings)
	user_entity_ids = []
	for user_entity_id in query_ids:
	    try: 
		int(user_entity_id)
	    except: 
		continue
	    user_entity_ids.append(user_entity_id)
	print user_entity_ids
	session_id = str(uuid.uuid4())
	print "Session:", session_id
	scoring_parameters = {} 
	if "netscore" in parameters:
	    scoring_parameters["ns"] = [int(parameters["repetitionSelector"]), int(parameters["iterationSelector"])]
	if "netzcore" in parameters:
	    scoring_parameters["nz"] = [int(parameters["repetitionZelector"])]
	if "netshort" in parameters:
	    scoring_parameters["nd"] = None
	result = GUILDifier(session_id, species, settings)
	result.prepare(user_entity_ids)
	result.score(scoring_parameters)
	return dict(session_id = session_id, 
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[species],
		    seed_file_url = result.seed_file_url,
		    network_file_url = result.network_file_url,
		    message="submitted",
		    submitted=True)



if __name__ == "__main__":
    main()

