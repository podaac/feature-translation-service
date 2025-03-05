import os
from unittest.mock import patch

import pytest
import geojson

node_set = {
      "x": 175.232,
      "y": -41.2985,
      "node_id": "57101000410023",
      "node_len": 182.971,
      "reach_id": "57101000413",
      "wse": 1.3,
      "wse_var": 0,
      "width": 131,
      "wth_var": 84.6667,
      "n_chan_max": 1,
      "n_chan_mod": 1,
      "grod_id": 0,
      "dist_out": 56916,
      "type": 3,
      "facc": 2076.51,
      "geometry": "POINT (175.2321400773249 -41.29848621498549)",
      "geojson": "{\"type\": \"Point\", \"coordinates\": [175.2321400773249, -41.29848621498549]}",
      "shp_origin": "oc_apriori_rivers_nodes_hb57_v08.shp",
      "netcdf_origin": "oc_apriori_rivers_v08.nc"
}

reach_set = {
      "reach_id": "56100100013",
      "reach_len": 1759.05,
      "n_nodes": 9,
      "wse": 242.7,
      "wse_var": 0.752237,
      "width": 389,
      "width_var": 28637.4,
      "facc": 57885.9,
      "n_chan_max": 3,
      "n_chan_mod": 1,
      "grod_id": 0,
      "slope": 1.38233,
      "dist_out": 1759.05,
      "lakeflag": 1,
      "type": 3,
      "river_name": "Yana River",
      "n_rch_up": "3",
      "n_rch_dn": "0",
      "geometry": "LINESTRING (115.8203307618278 -29.45151128768198, 115.8200183326346 -29.45177924962262, 115.8197735054906 -29.45155147020594, 115.8197766385315 -29.45128076708868, 115.8197797715295 -29.45101006396008, 115.8197829044847 -29.45073936082018, 115.819786037397 -29.45046865766896, 115.8197891702665 -29.45019795450641, 115.8197923030931 -29.44992725133256, 115.8197954358769 -29.44965654814738, 115.8197985686179 -29.44938584495088, 115.819801701316 -29.44911514174307, 115.8198048339712 -29.44884443852393, 115.8198079665837 -29.44857373529346, 115.8197492417525 -29.44830248368359, 115.8196905172085 -29.44803123204569, 115.819569935884 -29.44775943193756, 115.8193874982818 -29.44748708320487, 115.8192050616366 -29.44721473423848, 115.8190226259484 -29.44694238503837, 115.8187783348285 -29.44666948681295, 115.8185959012235 -29.44639713706532, 115.8184134685756 -29.44612478708399, 115.8182310368846 -29.44585243686899, 115.8180486061506 -29.44558008642032, 115.8178661763735 -29.44530773573799, 115.8176218921815 -29.44503483552084, 115.8174394644874 -29.4447624842911, 115.8171951827184 -29.44448958333754, 115.8169509022465 -29.44421668196138, 115.8167066230714 -29.44394378016261, 115.8164623451933 -29.44367087794125, 115.8161562142658 -29.44339742534301, 115.8158500849786 -29.44312397207582, 115.815605811333 -29.44285106836912, 115.8153615389842 -29.44257816423993, 115.8151791215933 -29.44230581010662, 115.814996705159 -29.4420334557398, 115.8148142896815 -29.44176110113946, 115.8146318751606 -29.44148874630559, 115.8144494615964 -29.44121639123821, 115.8142670489887 -29.44094403593733, 115.8140846373377 -29.44067168040295, 115.8139640791218 -29.44039987558558, 115.8138435215258 -29.4401280706662, 115.8137229645496 -29.43985626564483, 115.8136024081934 -29.4395844605215, 115.8135437042675 -29.43931320642346, 115.8134231489836 -29.43904140114754, 115.8132407428442 -29.43876904453964, 115.8131820402755 -29.43849779028982, 115.8131233379935 -29.43822653601208, 115.8131264869763 -29.43795583300447, 115.8131914867321 -29.43768568124874, 115.813380187431 -29.43741663181171)",
      "geojson": "{\"type\": \"LineString\", \"coordinates\": [[115.8203307618278, -29.45151128768198], [115.8200183326346, -29.45177924962262], [115.8197735054906, -29.45155147020594], [115.8197766385315, -29.45128076708868], [115.8197797715295, -29.45101006396008], [115.8197829044847, -29.45073936082018], [115.819786037397, -29.45046865766896], [115.8197891702665, -29.45019795450641], [115.8197923030931, -29.44992725133256], [115.8197954358769, -29.44965654814738], [115.8197985686179, -29.44938584495088], [115.819801701316, -29.44911514174307], [115.8198048339712, -29.44884443852393], [115.8198079665837, -29.44857373529346], [115.8197492417525, -29.44830248368359], [115.8196905172085, -29.44803123204569], [115.819569935884, -29.44775943193756], [115.8193874982818, -29.44748708320487], [115.8192050616366, -29.44721473423848], [115.8190226259484, -29.44694238503837], [115.8187783348285, -29.44666948681295], [115.8185959012235, -29.44639713706532], [115.8184134685756, -29.44612478708399], [115.8182310368846, -29.44585243686899], [115.8180486061506, -29.44558008642032], [115.8178661763735, -29.44530773573799], [115.8176218921815, -29.44503483552084], [115.8174394644874, -29.4447624842911], [115.8171951827184, -29.44448958333754], [115.8169509022465, -29.44421668196138], [115.8167066230714, -29.44394378016261], [115.8164623451933, -29.44367087794125], [115.8161562142658, -29.44339742534301], [115.8158500849786, -29.44312397207582], [115.815605811333, -29.44285106836912], [115.8153615389842, -29.44257816423993], [115.8151791215933, -29.44230581010662], [115.814996705159, -29.4420334557398], [115.8148142896815, -29.44176110113946], [115.8146318751606, -29.44148874630559], [115.8144494615964, -29.44121639123821], [115.8142670489887, -29.44094403593733], [115.8140846373377, -29.44067168040295], [115.8139640791218, -29.44039987558558], [115.8138435215258, -29.4401280706662], [115.8137229645496, -29.43985626564483], [115.8136024081934, -29.4395844605215], [115.8135437042675, -29.43931320642346], [115.8134231489836, -29.43904140114754], [115.8132407428442, -29.43876904453964], [115.8131820402755, -29.43849779028982], [115.8131233379935, -29.43822653601208], [115.8131264869763, -29.43795583300447], [115.8131914867321, -29.43768568124874], [115.813380187431, -29.43741663181171]]}",
      "shp_origin": "oc_apriori_rivers_reaches_hb56_v08.shp",
      "netcdf_origin": "oc_apriori_rivers_v08.nc"
}

@pytest.fixture(scope='function', autouse=True)
def db_environs():
    """Make sure no real values are in the database env vars"""
    os.environ['DB_HOST'] = "foo"
    os.environ['DB_NAME'] = "foo"
    os.environ['DB_USERNAME'] = "foo"
    os.environ['DB_PASSWORD'] = "foo"


@patch('pymysql.connect')
def test_return_node(db_environs):
    """
    Call the return_json_pass_through function from fts_controller.py and ensure
    the expected result is given. Use 'node' as search type and exact = True
    """
    node = node_set['node_id']

    # Create fake values which the mocked fetchall method returns
    results = [[node, node_set['geometry'], node_set['geojson'], node_set['reach_id']]]

    class MockConn:
        description = [['node_id'], ['geometry'], ['geojson'], ['reach_id']]
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as node_controller

    search_type = 'node'
    exact = True

    response_json = node_controller.return_json_pass_through(MockConn(), search_type, node, '', exact, 0, 1, 1, 100)

    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert len(json_results) == 1
    assert 'POINT' in json_results[0]['geometry']
    assert json_results[0]['reach_id'] == node_set['reach_id']
    assert isinstance(json_results[0]['geojson'], dict)
    geo = geojson.GeoJSON.to_instance(json_results[0]['geojson'])
    assert geo.is_valid
    assert geo['type'] == 'Point'
    assert len(geo['coordinates']) == 2


@patch('pymysql.connect')
def test_return_reach(db_environs):
    """
    Call the return_json_pass_through function from fts_controller.py and ensure
    the expected result is given. Use 'reach' as search type
    """
    reach = reach_set['reach_id']

    # Create fake values which the mocked fetchall method returns
    results = [[reach, reach_set['geometry'], reach_set['geojson']]]

    class MockConn:
        description = [['reach_id'], ['geometry'], ['geojson']]
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as node_controller

    search_type = 'reach'
    exact = True

    response_json = node_controller.return_json_pass_through(MockConn(), search_type, reach, '', exact, 0, 1, 1, 100)

    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert 'LINESTRING' in json_results[0]['geometry']
    assert isinstance(json_results[0]['geojson'], dict)
    geo = geojson.GeoJSON.to_instance(json_results[0]['geojson'])
    assert geo.is_valid
    assert geo['type'] == 'LineString'
    assert len(geo['coordinates']) == 55


@patch('pymysql.connect')
def test_return_river_name(db_environs):
    """
    Call the return_json_pass_through function from fts_controller.py and ensure
    the expected result is given. Use 'reach' as search type
    """
    river_name = 'Yana'

    # Create fake values which the mocked fetchall method returns
    results = [[reach_set['river_name'], reach_set['geometry'], reach_set['geojson']]]

    class MockConn:
        description = [['river_name'], ['geometry'], ['geojson']]
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as node_controller

    search_type = 'name'
    exact = False

    response_json = node_controller.return_json_pass_through(MockConn(), search_type, river_name, '', exact, 0, 1, 1, 100)

    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert river_name in json_results[0]['river_name']
    assert 'LINESTRING' in json_results[0]['geometry']
    assert isinstance(json_results[0]['geojson'], dict)
    geo = geojson.GeoJSON.to_instance(json_results[0]['geojson'])
    assert geo.is_valid
    assert geo['type'] == 'LineString'
    assert len(geo['coordinates']) == 55