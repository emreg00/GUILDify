
from test2.models import BIANAQuery
from test2.models import GUILDifier
from test2.models import GUILDScoreParser
import uuid

from pyramid.view import view_config
from pyramid.renderers import get_renderer

from pyramid.httpexceptions import HTTPFound

from pyramid.events import NewRequest, ApplicationCreated
from pyramid.events import subscriber

from webob import Response


def home_view(request):
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    return { "species_list": BIANAQuery.SPECIES_NAMES,
	     "species_to_value": BIANAQuery.SPECIES_NAME_TO_VALUE } 

def doc_view(request):
    return { }

def file_view(request):
    #print request.matchdict
    if "species" in request.matchdict:
	species = request.matchdict["species"]
	network_file_prefix = GUILDifier.NETWORK_FILE[:GUILDifier.NETWORK_FILE.rfind(".")]
	file_path = GUILDifier.DATA_DIR + species + "/" + GUILDifier.FILTERED_NETWORK_FILE # network_file_prefix + "_no_tap.sif"
    else:
	session_id = request.matchdict["session_id"]
	file_name = request.matchdict["file_name"]
	#print session_id, file_name
	# file_path = request.session["file_name"] #"../../../data/sessions/%s/%s" % (session_id, file_name)))
	file_path = GUILDifier.SESSION_DIR + session_id + "/" + file_name
    response = Response("".join([ line for line in open(file_path) ]))
    response.content_type = 'text/plain'
    return response

def query_result_view(request):
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    if request.method == 'POST':
        if request.POST.get('keywords') or request.POST.get('user_entity_ids'):
	    keywords = request.POST['keywords']
	    species = request.POST['species']
	    user_entity_ids = None 
	    genes = None 
	    ue_ids = []
	    try:
		query = BIANAQuery(settings)

	    except ValueError, e:
		if e.message == "biana":
		    request.session.flash('Internal server error, please reload the page and and try again! Contact to the webmaster if the problem persists.')
		    return HTTPFound(location=request.route_url('home'))
		    #query = BIANAQuery(settings)
		    #query.reconnect()
		    try:
		    	query = BIANAQuery(settings)
		    except ValueError, e:
		    	if e.message == "biana":
		    	    request.session.flash('Internal server error, please reload the page and and try again! Contact to the webmaster if the problem persists.')
		    	    return HTTPFound(location=request.route_url('home'))
	    if request.POST.get('user_entity_ids'):
		user_entity_ids = map(lambda x: str(x.strip("'\"")), request.POST['user_entity_ids'].strip("[]").split(", "))
		genes = request.POST['genes'].split()
		print "added genes:", genes
	    try:
		values, ue_ids, ue_ids_in_network = query.get_associated_user_entities(keywords, species, user_entity_ids, genes)
		if values is None:
	    	    request.session.flash('No match for the query!')
	    	    return HTTPFound(location=request.route_url('home'))
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
	    	    request.session.flash('No match for genes in the query! You can go back and try with other gene symbols.')
	    	    return HTTPFound(location=request.route_url('home'))
	    except Exception, inst: # inst.message == "biana"
		print "Execption inst:", inst
		#if inst[0] in (2006, 2013):
		#query.reconnect()
		#request.session.flash('Invalid session or no match for the query, please start over!')
		request.session.flash('Invalid session, please start over!')
		return HTTPFound(location=request.route_url('home'))
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
	else:
            request.session.flash('Please enter a keyword!')
	    return HTTPFound(location=request.route_url('home'))
    else:
	request.session.flash('Invalid session, please start over!')
	return HTTPFound(location=request.route_url('home'))
    return {}

def run_scoring_method_view(request):
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    if request.method == 'POST':
	#print request.POST
	user_entity_ids = []
        for user_entity_id in request.POST:
	    try: 
		int(user_entity_id)
	    except: 
		continue
	    user_entity_ids.append(user_entity_id)
	print user_entity_ids
	session_id = str(uuid.uuid4())
	print "Session:", session_id
	species = request.POST["species"]
	scoring_parameters = {} 
	if "netscore" in request.POST:
	    scoring_parameters["ns"] = [int(request.POST["repetitionSelector"]), int(request.POST["iterationSelector"])]
	if "netzcore" in request.POST:
	    scoring_parameters["nz"] = [int(request.POST["repetitionZelector"])]
	if "netshort" in request.POST:
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
    elif "id" in request.session:
	session_id = request.session["id"]
	species = request.session["species"]
	message = request.session["message"]
	result = GUILDifier(session_id, species, settings)
	return dict(session_id = session_id, 
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[species],
		    seed_file_url = result.seed_file_url,
		    network_file_url = result.network_file_url,
		    message=message,
		    submitted=False)
    request.session.flash('Invalid session, please start over!')
    return HTTPFound(location=request.route_url('home'))

def scoring_results_view(request):
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    session_id = request.matchdict["session_id"]
    result = GUILDifier(session_id, species = None, settings = settings)
    ready_flag = result.create_output_file()
    if ready_flag is None: # Error 
	request.session["id"] = session_id
	request.session["species"] = result.species
	request.session["message"] = "error/contact webmaster"
	return HTTPFound(location=request.route_url('status'))
    elif ready_flag: # Finished
	if "id" in request.session:
	    del request.session["id"]
	    del request.session["species"]
	    del request.session["message"]
	n_start = int(request.matchdict["n_start"])
	n_end = int(request.matchdict["n_end"])
	p_top = request.matchdict["p_top"]
	parser = GUILDScoreParser(result.output_file)
	values = parser.get_user_entity_info_and_scores(n_start, n_end, result.species)
	return dict(session_id = session_id,
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[result.species], 
		    n_start = n_start, 
		    n_end = n_end,
		    n_node = result.n_node,
		    values = values,
		    output_file_url = result.output_file_url,
		    seed_file_url = result.seed_file_url,
		    network_file_url = result.network_file_url,
		    network_json = result.get_network_json(p_top),
		    subnetwork_file_url = result.subnetwork_file_url+"."+p_top,
		    drug_file_url = result.drug_file_url+"."+p_top,
		    not_last_page = n_end<result.n_node,
		    top1 = p_top == "1",
		    top5 = p_top == "5",
		    top10 = p_top == "10",
		    human = result.species == "9606")
    request.session["id"] = session_id
    request.session["species"] = result.species
    request.session["message"] = "queued/running"
    return HTTPFound(location=request.route_url('status'))

#!
def scoring_results_overlap_view(request):
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    session_id = request.matchdict["session_id1"]
    session_id2 = request.matchdict["session_id2"]
    result = GUILDifier(session_id, species = None, settings = settings)
    result2 = GUILDifier(session_id2, species = None, settings = settings)
    ready_flag = result.create_output_file()
    ready_flag2 = result2.create_output_file()
    if ready_flag is None or ready_flag2 is None: # Error 
	request.session["id"] = session_id
	request.session["species"] = result.species
	request.session["message"] = "error/contact webmaster"
	return HTTPFound(location=request.route_url('status'))
    elif ready_flag and ready_flag2: # Finished
	if "id" in request.session:
	    del request.session["id"]
	    del request.session["species"]
	    del request.session["message"]
	n_start = int(request.matchdict["n_start"])
	n_end = int(request.matchdict["n_end"])
	p_top = request.matchdict["p_top"]
	parser = GUILDScoreParser(result.output_file)
	parser2 = GUILDScoreParser(result2.output_file)
	values, values_stat = parser.overlap_with(parser2, result.n_node, result.species, int(p_top))
	return dict(session_id1 = session_id,
		    session_id2 = session_id2,
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[result.species], 
		    n_start = n_start, 
		    n_end = min(n_end, len(values)),
		    n_node = len(values),
		    values = values[(n_start-1):n_end],
		    values_stat = values_stat,
		    output_file_url = result.output_file_url,
		    seed_file_url = result.seed_file_url,
		    network_file_url = result.network_file_url,
		    network_json = result.get_network_json(p_top),
		    subnetwork_file_url = result.subnetwork_file_url+"."+p_top,
		    drug_file_url = result.drug_file_url+"."+p_top,
		    not_last_page = n_end<result.n_node,
		    p_top = p_top,
		    top1 = p_top == "1",
		    top5 = p_top == "5",
		    top10 = p_top == "10",
		    human = result.species == "9606")
    request.session["id"] = session_id
    request.session["species"] = result.species
    request.session["message"] = "queued/running"
    return HTTPFound(location=request.route_url('status'))

#@view_config(route_name='result_ajax', permission='perm', xhr=True, renderer='json')
def results_ajax(request): 
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    session_id = request.matchdict["session_id"]
    n_start = int(request.matchdict["n_start"])
    n_end = int(request.matchdict["n_end"])
    result = GUILDifier(session_id, species = None, settings = settings)
    result.create_output_file()
    parser = GUILDScoreParser(result.output_file)
    values = parser.get_user_entity_info_and_scores(n_start, n_end, result.species)
    return dict(n_start = n_start, 
		n_end = n_end,
		n_node = result.n_node,
		values = [ ";".join(map(lambda x: str(x), value)) for value in values ])

#!
def results_overlap_ajax(request): 
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    session_id = request.matchdict["session_id1"]
    session_id2 = request.matchdict["session_id2"]
    n_start = int(request.matchdict["n_start"])
    n_end = int(request.matchdict["n_end"])
    p_top = request.matchdict["p_top"]
    result = GUILDifier(session_id, species = None, settings = settings)
    result.create_output_file()
    parser = GUILDScoreParser(result.output_file)
    result2 = GUILDifier(session_id2, species = None, settings = settings)
    result2.create_output_file()
    parser2 = GUILDScoreParser(result2.output_file)
    values, values_stat = parser.overlap_with(parser2, result.n_node, result.species, int(p_top)) 
    return dict(n_start = n_start, 
		n_end = n_end,
		n_node = result.n_node,
		p_top = p_top,
		values = [ ";".join(map(lambda x: str(x), value)) for value in values[(n_start-1):n_end] ])

def retrieve_results_view(request):
    settings = request.registry.settings
    GUILDifier.set_parameters(settings)
    if request.method == 'POST':
    #!
	if request.POST.get('session_id1') and request.POST.get('session_id2'):
	    session_id = request.POST["session_id1"]
	    session_id2 = request.POST["session_id2"]
	    try:
		result = GUILDifier(session_id, species = None, settings = settings)
		result2 = GUILDifier(session_id2, species = None, settings = settings)
	    except: # job(s) not finished / session does not exist
		request.session.flash('Provided job id is not valid!')
		return HTTPFound(location=request.route_url('home'))
	    ready_flag = result.create_output_file()
	    ready_flag2 = result2.create_output_file()
	    if (ready_flag is None or ready_flag == False) or (ready_flag2 is None or ready_flag2 == False): # Error / still running
		request.session.flash('Provided job id is not valid!')
		return HTTPFound(location=request.route_url('home'))
	    else:
		return HTTPFound(location=request.route_url('result_overlap', session_id1 = session_id, session_id2 = session_id2, n_start = "1", n_end = "20", p_top = "1"))
	if request.POST.get('session_id'):
	    session_id = request.POST["session_id"]
	    try:
		result = GUILDifier(session_id, species = None, settings = settings)
	    except: # species.txt does not exits - job not finished
		request.session.flash('Provided job id is not valid!')
		return HTTPFound(location=request.route_url('home'))
	    ready_flag = result.create_output_file()
	    if ready_flag is None or ready_flag == False: # Error / still running
		request.session.flash('Provided job id is not valid!')
		return HTTPFound(location=request.route_url('home'))
	    else:
		return HTTPFound(location=request.route_url('result', session_id = session_id, n_start = "1", n_end = "20", p_top = "1"))
    request.session.flash('No job id is provided!')
    return HTTPFound(location=request.route_url('home'))


def old_run_scoring_method_view(request):
    if request.method == 'POST':
	user_entity_ids = []
        for user_entity_id in request.POST:
	    if user_entity_id != "species":
		user_entity_ids.append(user_entity_id)
	print user_entity_ids
	request.session["id"] = str(uuid.uuid4())
	species = request.POST["species"]
	request.session["species"] = species
	result = GUILDifier(request.session["id"], species, request.registry.settings)
	result.prepare(user_entity_ids)
	result.score()
	result.create_output_file()
	request.session["file_name"] = result.output_file
	request.session["file_url"] = result.output_file_url
	request.session["n_result"] = result.n_node
	n_start = int(request.matchdict["n_start"])
	n_end = int(request.matchdict["n_end"])
	parser = GUILDScoreParser(request.session["file_name"])
	values = parser.get_user_entity_info_and_scores(n_start, n_end, species)
	return dict(n_start = n_start, 
		    n_end = n_end,
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[species], 
		    n_node = result.n_node,
		    values = values,
		    output_file_url = request.session["file_url"],
		    not_last_page = n_end<(result.n_node-20))
    elif request.method == 'GET':
	n_start = int(request.matchdict["n_start"])
	n_end = int(request.matchdict["n_end"])
	if "species" not in request.session:
	    request.session.flash('Invalid session, please start over!')
	    return HTTPFound(location=request.route_url('home'))
	species = request.session["species"]
	parser = GUILDScoreParser(request.session["file_name"])
	values = parser.get_user_entity_info_and_scores(n_start, n_end, species)
	n_node = request.session["n_result"]
	return dict(n_start = n_start, 
		    n_end = n_end,
		    species = BIANAQuery.TAX_ID_TO_SPECIES_NAME[species], 
		    n_node = n_node,
		    values = values,
		    output_file_url = request.session["file_url"],
		    not_last_page = n_end<n_node)
    else:
	request.session.flash('Invalid session, please start over!')
	return HTTPFound(location=request.route_url('home'))
    return {}


# subscribers
@subscriber(NewRequest)
def new_request_subscriber(event):
    #request = event.request
    print "New request"
    #settings = request.registry.settings
    #request.db = sqlite3.connect(settings['db']) # need to be added in __init__
    #request.add_finished_callback(close_db_connection)

def close_db_connection(request):
    #request.db.close()
    pass
    
@subscriber(ApplicationCreated)
def application_created_subscriber(event):
    print "Greet the world!"
    #settings = event.request.registry.settings
    #GUILDifier.set_parameters(settings)

