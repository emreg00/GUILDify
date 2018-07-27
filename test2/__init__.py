from pyramid.config import Configurator
from pyramid.session import UnencryptedCookieSessionFactoryConfig

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    session_factory = UnencryptedCookieSessionFactoryConfig('ent85an')
    config = Configurator(settings=settings, session_factory=session_factory)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'test2:static')
    config.add_route('home', '/')
    config.add_view('test2.views.home_view', renderer='templates/home.pt', route_name='home')
    config.add_route('data', 'data/{session_id}/{file_name}')
    config.add_view('test2.views.file_view', route_name='data')
    config.add_route('data_network', 'data/{species}')
    config.add_view('test2.views.file_view', route_name='data_network')
    config.add_route('query', 'query')
    config.add_view(view='test2.views.query_result_view', renderer='templates/query.pt', route_name='query')
    config.add_route('status', 'status')
    config.add_view(view='test2.views.run_scoring_method_view', renderer='templates/status.pt', route_name='status')
    config.add_route('retrieve', 'retrieve')
    config.add_view(view='test2.views.retrieve_results_view', route_name='retrieve')
    config.add_route('result', 'result/{session_id}/{n_start}/{n_end}/{p_top}')
    config.add_view('test2.views.scoring_results_view', renderer='templates/result.pt', route_name='result')
    config.add_route('result_overlap', 'result_overlap/{session_id1}/{session_id2}/{n_start}/{n_end}/{p_top}')
    config.add_view('test2.views.scoring_results_overlap_view', renderer='templates/result_overlap.pt', route_name='result_overlap')
    config.add_route('result_ajax', 'result_ajax/{session_id}/{n_start}/{n_end}') 
    config.add_view('test2.views.results_ajax', renderer='json', route_name='result_ajax') 
    config.add_route('result_overlap_ajax', 'result_overlap_ajax/{session_id1}/{session_id2}/{n_start}/{n_end}/{p_top}') 
    config.add_view('test2.views.results_overlap_ajax', renderer='json', route_name='result_overlap_ajax') 
    config.add_route('doc', 'doc')
    config.add_view('test2.views.doc_view', renderer='templates/doc.pt', route_name='doc')
    return config.make_wsgi_app()

