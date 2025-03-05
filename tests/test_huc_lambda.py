import os
from unittest.mock import patch

import pytest

name = "San Joaquin"
huc = '1804'
bbox = "-121.93679916804501,36.36688239563472,-118.65438684397327,38.757297326299295"
convex_hull = "-120.63835246068544,36.36688239563472,-120.63808719818587,36.3669077091763," \
              "-118.73841884071788,37.07942819140368,-118.67420150956752,37.106490572611676"
visvalingam = "-120.54009506083798,38.751263262767,-120.64081991068161,38.70357532638269," \
              "-120.71727710431293,38.70154573055248,-120.74424469072943,38.67445884830289," \
              "-120.82514061977054,38.69750556180878,-120.85090918535553,38.634815070239426"


def get_feature_given_type_property(feature_collection, type_property):
    """
    Get a feature from a feature collection which matches the provided
    'type' property.

    Parameters
    ----------
    feature_collection : geojson.Property
    type_property : str

    Returns
    -------
    geojson.Feature
        The Feature in the FeatureCollection which has the matching
        'type' property, or None if none match.
    """
    for feature in feature_collection['features']:
        if feature['properties']['type'] == type_property:
            return feature
    return None


@pytest.fixture(scope='function', autouse=True)
def db_environs():
    """Make sure no real values are in the database env vars"""
    os.environ['DB_HOST'] = "foo"
    os.environ['DB_NAME'] = "foo"
    os.environ['DB_USERNAME'] = "foo"
    os.environ['DB_PASSWORD'] = "foo"


@patch('pymysql.connect')
def test_return_geojson_huc(db_environs):
    """
    Call the return_json function from fts_controller.py and ensure
    the expected result is given. Use HUC as search type, and
    geojson as polygon_format.
    """
    # Create fake values which the mocked fetchall method returns
    results = [[huc, name, convex_hull, visvalingam, bbox]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    polygon_format = 'geojson'
    search_type = 'HUC'
    exact = True

    response_json = huc_controller.return_json(MockConn(), search_type, "name", exact,
                                               polygon_format, 0, 1, 1, 100)

    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert len(json_results) == 1
    assert json_results[0]['HUC'] == huc
    assert len(json_results[0]['geojson']['features']) == 3

    feature_collection = json_results[0]['geojson']

    bbox_geojson = get_feature_given_type_property(
        feature_collection, 'bbox')['geometry']['coordinates'][0]
    convex_hull_geojson = get_feature_given_type_property(
        feature_collection, 'Convex Hull')['geometry']['coordinates'][0]
    visvalingam_geojson = get_feature_given_type_property(
        feature_collection, 'Visvalingam')['geometry']['coordinates'][0]

    # Geojson pairs should match flat input lists.
    assert ','.join([str(point) for pair in convex_hull_geojson[:-1]
                     for point in pair]) == convex_hull
    assert ','.join([str(point) for pair in visvalingam_geojson[:-1]
                     for point in pair]) == visvalingam

    # Geojson pairs should be the corners of the geojson polygon (square)
    in_bbox = list(map(float, bbox.split(',')))
    assert bbox_geojson[0][0] == bbox_geojson[1][0] == in_bbox[0]
    assert bbox_geojson[0][1] == bbox_geojson[3][1] == in_bbox[1]
    assert bbox_geojson[2][0] == bbox_geojson[3][0] == in_bbox[2]
    assert bbox_geojson[1][1] == bbox_geojson[2][1] == in_bbox[3]

    # First element should match last element
    assert bbox_geojson[0] == bbox_geojson[-1]
    assert convex_hull_geojson[0] == convex_hull_geojson[-1]
    assert visvalingam_geojson[0] == visvalingam_geojson[-1]


@patch('pymysql.connect')
def test_return_json_empty(db_environs):
    """
    If results (from mysql query) are empty, IndexError should be thrown
    """
    results = [[]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    polygon_format = 'geojson'
    search_type = 'HUC'
    exact = True

    with pytest.raises(IndexError):
        huc_controller.return_json(MockConn(), search_type, "name", exact, polygon_format, 0, 1,
                                   1, 100)


@patch('pymysql.connect')
def test_return_geojson_region(db_environs):
    """
    Call the return_json function from fts_controller.py and ensure
    the expected result is given. Use region as search type, and
    geojson as polygon_format.
    """
    results = [[huc, name, convex_hull, visvalingam, bbox]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    polygon_format = 'geojson'
    search_type = 'region'
    exact = True

    response_json = huc_controller.return_json(MockConn(), search_type, 'name', exact,
                                               polygon_format, 0, 1, 1, 100)
    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert len(json_results) == 1
    assert json_results[0]['Region Name'] == name

    # geojson in response should be the same in region vs HUC search
    response_json_huc = huc_controller.return_json(MockConn(), 'HUC', 'name', exact,
                                                   polygon_format, 0, 1, 1, 100)

    assert json_results[0]['geojson'] == response_json_huc['results'][0]['geojson']


@patch('pymysql.connect')
def test_flat_polygon_huc(db_environs):
    """
    Test that the expected results are returned when the specified
    polygon_format is 'flat' and the search type is 'HUC'
    """
    results = [[huc, name, convex_hull, visvalingam, bbox]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    polygon_format = 'flat'
    search_type = 'HUC'
    exact = True

    response_json = huc_controller.return_json(MockConn(), search_type, "name", exact,
                                               polygon_format, 0, 1, 1, 100)

    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert len(json_results) == 1
    assert 'Bounding Box' in json_results[0]
    assert 'Convex Hull Polygon' in json_results[0]
    assert 'Visvalingam Polygon' in json_results[0]

    assert json_results[0]['Bounding Box'] == bbox
    assert json_results[0]['Convex Hull Polygon'] == convex_hull
    assert json_results[0]['Visvalingam Polygon'] == visvalingam


@patch('pymysql.connect')
def test_flat_polygon_region(db_environs):
    """
    Test that the expected results are returned when the specified
    polygon_format is 'flat' and the search type is 'region'
    """
    results = [[huc, name, convex_hull, visvalingam, bbox]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    polygon_format = 'flat'
    search_type = 'region'
    exact = True

    response_json = huc_controller.return_json(MockConn(), search_type, 'name', exact,
                                               polygon_format, 0, 1, 1, 100)
    assert response_json['search on']['parameter'] == search_type
    assert response_json['search on']['exact'] == exact

    json_results = response_json['results']
    assert len(json_results) == 1
    assert json_results[0]['Region Name'] == name

    # response should be the same in region vs HUC search
    response_json_huc = huc_controller.return_json(MockConn(), 'HUC', 'name', exact,
                                                   polygon_format, 0, 1, 1, 100)

    assert json_results[0] == response_json_huc['results'][0]


@patch('pymysql.connect')
def test_invalid_polygon_format(db_environs):
    """
    Test that an invalid polygon_format results in an error message
    being returned.
    Parameters
    """
    results = [[huc, name, convex_hull, visvalingam, bbox]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    polygon_format = 'foo'
    search_type = 'region'
    exact = True

    try:
        huc_controller.return_json(MockConn(), search_type, 'name', exact, polygon_format, 0, 1,
                                   1, 100)
    except Exception as e:
        msg = str(e)
        assert '400' in msg
        assert f'but \'{polygon_format}\' was given' in msg


@patch('pymysql.connect')
def test_missing_polygon_format(db_environs):
    """
    Test that the 'flat' polygon_format is used when the polygon is
    not provided.
    """
    results = [[huc, name, convex_hull, visvalingam, bbox]]

    class MockConn:
        @staticmethod
        def fetchall(): return results

    import fts.api.controllers.fts_controller as huc_controller

    flat_polygon_format = 'flat'
    none_polygon_format = None
    empty_polygon_format = ''
    search_type = 'region'
    exact = True

    response_json_flat = huc_controller.return_json(MockConn(), search_type, 'name', exact,
                                                    flat_polygon_format, 0, 1, 1, 100)

    response_json_none = huc_controller.return_json(MockConn(), search_type, 'name', exact,
                                                    none_polygon_format, 0, 1, 1, 100)

    response_json_empty = huc_controller.return_json(MockConn(), search_type, 'name', exact,
                                                     empty_polygon_format, 0, 1, 1, 100)

    assert response_json_flat['search on'].pop('polygon_format') == flat_polygon_format
    assert response_json_none['search on'].pop('polygon_format') == none_polygon_format
    assert response_json_empty['search on'].pop('polygon_format') == empty_polygon_format

    assert response_json_flat == response_json_none == response_json_empty
