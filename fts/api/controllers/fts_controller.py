# pylint: disable=invalid-name, broad-except, redefined-builtin, unnecessary-comprehension
# pylint: disable=redefined-outer-name, unused-argument, no-else-return, too-many-branches
# pylint: disable=too-many-arguments
# pylint: disable=too-many-statements, too-many-locals

"""
==============
fts_controller.py
==============
"""

import logging
import os
import sys
import time

import boto3
import geojson
import pymysql

try:
    DB_PASSWORD_SSM_NAME = os.environ['DB_PASSWORD_SSM_NAME']
    ssm = boto3.client('ssm')

    ssm_fts_user_pass = ssm.get_parameter(Name=DB_PASSWORD_SSM_NAME, WithDecryption=True)
    DB_PASSWORD = ssm_fts_user_pass['Parameter']['Value']
except Exception:
    DB_PASSWORD = os.environ['DB_PASSWORD']

DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PORT = 3306

logger = logging.getLogger()
logger.setLevel(logging.INFO)

try:
    conn = pymysql.connect(
        host=DB_HOST, user=DB_USERNAME, passwd=DB_PASSWORD, db=DB_NAME, connect_timeout=10
    )

except pymysql.MySQLError as e:
    logger.error("ERROR: Unexpected error: Could not connect to MySql instance.")
    logger.error(e)
    sys.exit()

logger.info("SUCCESS: Connection to mysql instance succeeded")

MAX_PRECISION = 15
OBJECT_URL = 'https://podaac-feature-translation-service.s3-us-west-2.amazonaws.com/{}.zip'
SOURCE_URL = 'ftp://rockyftp.cr.usgs.gov/vdelivery/Datasets/Staged/Hydrography/WBD/HU2/Shape/WBD_{}_HU2_Shape.zip'


###################


def create_feature(polygon, type):
    """
    Create a Geojson feature with 'type' property, which in this case
    indicates the type of polygon (bbox, convex hull, etc)

    Parameters
    ----------
    polygon : geojson.Polygon
        The polygon geometry
    type : str
        The value of the 'type' property.

    Returns
    -------
    geojson.Feature
        The feature which contains the given geometry and properties
    """
    return geojson.Feature(geometry=polygon, properties=dict(type=type))


def str_to_float_pair_list(list_str):
    """
    Convert a comma delimited string to a float list of pairs.

    Parameters
    ----------
    list_str: str
        Input string which is comma delimited and has an even number
        of items

    Returns
    -------
    list
        List of float tuples
    """
    list_str = list_str.split(',')
    float_points = list(map(float, list_str))
    return [point for point in zip(float_points[::2], float_points[1::2])]


def convert_flat_list_bbox_to_geojson_polygon(bbox_str):
    """
    Convert a flat list of points to a GeoJSON polygon. The points given
    represent a bbox of the following form: west, south, east, north

    This will find the corner coordinates and create a GeoJSON Polygon.

    Parameters
    ----------
    bbox_str: str
        Flat (1-D) list (comma-delimited string) of points which
        represent the bbox.
    Returns
    -------
    dict
        The geojson polygon which was created from the given string
    """
    pairs = str_to_float_pair_list(bbox_str)
    bottom_left = pairs[0]
    top_left = (pairs[0][0], pairs[1][1])
    top_right = pairs[1]
    bottom_right = (pairs[1][0], pairs[0][1])
    points = [bottom_left, top_left, top_right, bottom_right]
    points.append(points[0])
    return geojson.Polygon([points], precision=MAX_PRECISION)


def convert_flat_list_to_geojson_polygon(exterior_points, interior_points=None):
    """
    Convert a flat list of points to a GeoJSON polygon.

    For example, the following list: [a, b, c, d, e, f] actually
    represents three pairs: [(a, b), (c, d), (e, f)] and can be
    represented as a GeoJSON Polygon
    {"coordinates": [[[a, b],[c, d],[e, f]],[],"type": "Polygon"}

    Parameters
    ----------
    exterior_points: str
        Flat (1-D) list (comma-delimited string) of points which
        represent the exterior points in the polygon.
    interior_points: str, optional
        Flat (1-D) list (comma-delimited string) of points which
        represent the interior points in the polygon. This creates a hole in the exterior polygon.

    Returns
    -------
    dict
        The geojson polygon which was created from the given string
    """
    points = []
    exterior_points = str_to_float_pair_list(exterior_points)
    exterior_points.append(exterior_points[0])
    points.append(exterior_points)

    if interior_points:
        interior_points = str_to_float_pair_list(interior_points)
        interior_points.append(interior_points[0])
        points.append(interior_points)

    return geojson.Polygon(points, precision=MAX_PRECISION)


def return_json(cur, identifier, name, exact, polygon_format, elapsed_time, hits, page_number,
                page_size):
    """
    Get the results of the DB query, and construct the resulting dict
    given the polygon format and identifier.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    identifier : str
        'HUC' or 'region'
    name       : str
        The name of the region
    exact      : bool
        True if an exact HUC should be queried
    polygon_format : str
        The format which the polygon should be represented as. Should
        be geojson, flat, or None (also '') (which will use flat)
    elapsed_time       : int
        Number of ms to query DB
    hits               : int
        Total number of results that match query result
    page_number        : int
        The requested page number when getting partial results
    page_size        : int
        The maximum number of results to return per call

    Returns
    -------
    dict
        The constructed response
    """
    results = cur.fetchall()

    data = {}

    if polygon_format and (
            polygon_format.lower() != 'geojson' and polygon_format.lower() != 'flat'):
        msg = f'400: Invalid polygon_format. Should be \'flat\' or \'geojson\', but ' \
              f'\'{polygon_format}\' was given.'
        raise Exception(msg)

    results_count = len(results)

    if results_count == 0:
        msg = f'404: Results with the specified {identifier} {name} were not found.'
        raise Exception(msg)

    partial_results = False
    status = "200 OK"
    if hits > results_count:
        partial_results = True
        status = "206 PARTIAL CONTENT"

    data['status'] = status
    data['time'] = str(elapsed_time) + " ms."
    data['hits'] = hits
    if partial_results:
        data['results_count'] = results_count

    data['search on'] = dict(
        parameter=identifier,
        exact=exact,
        polygon_format=polygon_format,
        page_number=page_number,
        page_size=page_size
    )

    result_list = []
    for elem in results:
        result_dict = {}
        huc = elem[0]
        name = elem[1]
        convex_hull = elem[2]
        visvalingam = elem[3]
        bbox = elem[4]

        result_dict['Region Name'] = name
        result_dict['HUC'] = huc
        result_dict['USGS Polygon'] = {
            'Object URL': OBJECT_URL.format(huc),
            'Source': SOURCE_URL.format(huc[:2])
        }

        if not polygon_format or polygon_format.lower() == 'flat':
            result_dict['Bounding Box'] = bbox
            result_dict['Convex Hull Polygon'] = convex_hull
            result_dict['Visvalingam Polygon'] = visvalingam

        elif polygon_format.lower() == 'geojson':
            convex_hull = convert_flat_list_to_geojson_polygon(convex_hull)
            visvalingam = convert_flat_list_to_geojson_polygon(visvalingam)
            bbox = convert_flat_list_bbox_to_geojson_polygon(bbox)

            feature_collection = geojson.FeatureCollection([
                create_feature(bbox, 'bbox'),
                create_feature(convex_hull, 'Convex Hull'),
                create_feature(visvalingam, 'Visvalingam')
            ])
            result_dict['geojson'] = feature_collection

        result_list.append(result_dict)

    data['results'] = result_list

    return data


def get_huc_hits_count(cur, huc):
    """
    Get the row/hit count for the given HUC query.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    huc        : str
        The huc search field

    Returns
    -------
    int
        Row count
    """
    cur.execute("select COUNT(*) from huc_table where `HUC` LIKE %s", huc + "%")

    hits = cur.fetchall()

    return hits[0][0]


def get_region_hits_count(cur, region):
    """
    Get the row/hit count for the given region query.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    region        : str
        The region search field

    Returns
    -------
    int
        Row count
    """
    cur.execute("select COUNT(*) from huc_table where `Region` LIKE %s", region + "%")

    hits = cur.fetchall()

    return hits[0][0]


def get_reach_hits_count(cur, reach, river_name):
    """
    Get the row/hit count for the given reach query.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    reach        : str
        The reach search field
    river_name        : str
        The river_name search field

    Returns
    -------
    int
        Row count
    """
    if river_name:
        args = (reach + "%", river_name + "%")
        cur.execute("SELECT COUNT(*) FROM reaches WHERE reach_id LIKE %s AND river_name LIKE %s", args)
    else:
        cur.execute("SELECT COUNT(*) FROM reaches WHERE reach_id LIKE %s", reach + "%")

    hits = cur.fetchall()

    return hits[0][0]


def get_river_name_hits_count(cur, name, include_reaches, include_nodes):
    """
    Get the row/hit count for the given river query.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    name        : str
        The river name search field
    include_reaches      : bool
        Include reaches in results if True, otherwise exclude reaches in result
    include_nodes      : bool
        Include nodes in results if True, otherwise exclude reaches in result

    Returns
    -------
    int
        Row count
    """
    if include_nodes and include_reaches:
        args = (name + "%", name + "%")
        cur.execute("SELECT COUNT(*) FROM reaches, nodes WHERE reaches.reach_id = nodes.reach_id AND reaches.river_name LIKE %s AND nodes.river_name LIKE %s", args)
    elif include_nodes:
        cur.execute("SELECT COUNT(*) FROM nodes WHERE river_name LIKE %s", name)
    elif include_reaches:
        cur.execute("SELECT COUNT(*) FROM reaches WHERE river_name LIKE %s", name)
    else:
        msg = '400: Both reaches and nodes are false.  At least one must be set to true.'
        raise Exception(msg)

    hits = cur.fetchall()

    return hits[0][0]


def get_node_hits_count(cur, node, river_name):
    """
    Get the row/hit count for the given node query.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    node        : str
        The node search field
    river_name        : str
        The river_name search field

    Returns
    -------
    int
        Row count
    """
    if river_name:
        args = (node + "%", river_name + "%")
        cur.execute("SELECT COUNT(*) FROM nodes WHERE node_id LIKE %s AND river_name LIKE %s", args)
    else:
        cur.execute("SELECT COUNT(*) FROM nodes WHERE node_id LIKE %s", node + "%")

    hits = cur.fetchall()

    return hits[0][0]


def lambda_handler(event, context):
    """
    This function queries the HUC database for relevant results
    """
    with conn.cursor() as cur:

        # Start a timer to measure query time.
        start = time.time()

        # Default inputs
        polygon_format = ''
        page_number = 1
        page_size = 100
        exact = False
        hits = 1

        if 'polygon_format' in event['body']:
            polygon_format = event['body']['polygon_format'].lower()

        if 'page_number' in event['body'] and event['body']['page_number'] != '':
            try:
                page_number = int(event['body']['page_number'])
                if page_number < 1:
                    raise ValueError
            except ValueError as ex:
                raise Exception("400: page_number must be a number, 1 or greater.") from ex

        if 'page_size' in event['body'] and event['body']['page_size'] != '':
            try:
                page_size = int(event['body']['page_size'])
                if page_size < 1:
                    raise ValueError
            except ValueError as ex:
                raise Exception("400: page_size must be a number, 1 or greater.") from ex

        if 'exact' in event['body'] and event['body']['exact'].lower() == "true":
            exact = True

        offset = page_size * (page_number - 1)

        # Entered if the user queries by HUC
        if "HUC" in event['body']:

            huc = event['body']['HUC']

            # User queries an exact HUC
            if exact:
                cur.execute("select * from huc_table where `HUC` = %s", huc)
            # User queries partial HUC
            else:
                hits = get_huc_hits_count(cur, huc)

                args = (huc + "%", offset, page_size)

                cur.execute("select * from huc_table"
                            " where `HUC` LIKE %s ORDER BY CHAR_LENGTH(HUC), HUC LIMIT %s,%s",
                            args)

            elapsed_time = round((time.time() - start) * 1000, 3)
            return return_json(cur, "HUC", huc, exact, polygon_format, elapsed_time, hits,
                               page_number, page_size)

        # Similar process for region
        elif "region" in event['body']:

            # Handle spaces in request
            region = " ".join(event['body']['region'].split("%20"))

            # User queries exact region
            if exact:
                cur.execute("select * from huc_table where `Region` = %s", region)
            # User queries partial region match
            else:
                hits = get_region_hits_count(cur, region)

                args = (region + "%", offset, page_size)
                cur.execute("select * from huc_table"
                            " where `Region` LIKE %s ORDER BY CHAR_LENGTH(HUC), HUC LIMIT %s,%s",
                            args)

            elapsed_time = round((time.time() - start) * 1000, 3)
            return return_json(cur, "region", region, exact, polygon_format, elapsed_time, hits,
                               page_number, page_size)

        # Similar process for reach
        elif "reach" in event['body']:

            # Handle spaces in request
            reach = " ".join(event['body']['reach'].split("%20"))
            river_name = " ".join(event['body']['river_name'].split("%20"))

            return process_reach(reach, river_name, exact, cur, start, page_number, page_size)
        # Similar process for node
        elif "node" in event['body']:

            # Handle spaces in request
            node = " ".join(event['body']['node'].split("%20"))
            river_name = " ".join(event['body']['river_name'].split("%20"))

            return process_node(node, river_name, exact, cur, start, page_number, page_size)
        # process for rivers name
        elif "name" in event['body']:

            # Handle spaces in request
            river_name = " ".join(event['body']['name'].split("%20"))
            #   path = context['path']

            include_reaches = True
            include_nodes = True

            if 'nodes' in event['body'] and event['body']['nodes'].lower() == "false":
                include_nodes = False

            if 'reaches' in event['body'] and event['body']['reaches'].lower() == "false":
                include_reaches = False

            return process_river(river_name, exact, cur, start, include_reaches, include_nodes, page_number,
                                 page_size)
        else:
            # Return 400 error assuming path is incorrect.
            msg = "400: The specified URL is invalid (does not exist)."
            raise Exception(msg)


def process_river(river_name, exact, cur, start, include_reaches, include_nodes, page_number, page_size):
    """
    Submits a river_name query to the DB, and passes that result to the return_json_passthrough to get
    the output reaches and nodes results.

    Parameters
    ----------
    river_name : str
        The input river name
    exact      : bool
        True if an exact river_name should be queried
    cur        : pymysql.cursor
        pymysql connection cursor
    start      : int
        start time to measure query duration
    include_reaches  : bool
        Include reaches in results if True, otherwise exclude reaches in result
    include_nodes    : bool
        Include nodes in results if True, otherwise exclude reaches in result
    page_number      : int
        The requested page number when getting partial results
    page_size        : int
        The maximum number of results to return per call

    Returns
    -------
    dict
        The constructed response
    """

    offset = page_size * (page_number - 1)

    # User queries exact river_name
    if exact:
        hits = get_river_name_hits_count(cur, river_name, include_reaches, include_nodes)

        if include_nodes and include_reaches:
            args = (river_name, river_name, offset, page_size)

            cur.execute("SELECT reaches.*, nodes.* FROM reaches, nodes WHERE reaches.reach_id = nodes.reach_id AND reaches.river_name = %s AND nodes.river_name = %s"
                        " ORDER BY node_id LIMIT %s,%s", args)
        elif include_nodes:
            # Include only nodes
            args = (river_name, offset, page_size)

            cur.execute("SELECT * FROM nodes WHERE river_name = %s ORDER BY node_id LIMIT %s,%s", args)
        elif include_reaches:
            # Include only reaches
            args = (river_name, offset, page_size)

            cur.execute("SELECT * FROM reaches WHERE river_name = %s ORDER BY reach_id LIMIT %s,%s", args)
        else:
            msg = '400: Both reaches and nodes are false.  At least one must be set to true.'
            raise Exception(msg)

    # User queries partial river_name match
    else:
        hits = get_river_name_hits_count(cur, river_name, include_reaches, include_nodes)

        if include_nodes and include_reaches:
            args = (river_name + "%", river_name + "%", offset, page_size)

            cur.execute("SELECT reaches.*, nodes.* FROM reaches, nodes WHERE reaches.reach_id = nodes.reach_id AND reaches.river_name LIKE %s AND nodes.river_name LIKE %s"
                        " ORDER BY node_id LIMIT %s,%s", args)
        elif include_nodes:
            # Include only nodes
            args = (river_name + "%", offset, page_size)

            cur.execute("SELECT * FROM nodes WHERE river_name LIKE %s ORDER BY node_id LIMIT %s,%s", args)
        elif include_reaches:
            # Include only reaches
            args = (river_name + "%", offset, page_size)

            cur.execute("SELECT * FROM reaches WHERE river_name LIKE %s ORDER BY reach_id LIMIT %s,%s", args)
        else:
            msg = '400: Both reaches and nodes are false.  At least one must be set to true.'
            raise Exception(msg)

    elapsed_time = round((time.time() - start) * 1000, 3)

    return return_json_pass_through(cur, "name", river_name, river_name, exact, elapsed_time, hits,
                                    page_number, page_size)


def process_reach(reach, river_name, exact, cur, start, page_number, page_size):
    """
    Submits a reach query to the DB, and passes that result to the return_json_passthrough to get
    the output reach results.

    Parameters
    ----------
    reach       : str
        The input reach id
    river_name       : str
        The input river_name
    exact      : bool
        True if an exact reach should be queried
    cur        : pymysql.cursor
        pymysql connection cursor
    start       : int
        start time to measure query duration
    page_number        : int
        The requested page number when getting partial results
    page_size        : int
        The maximum number of results to return per call

    Returns
    -------
    dict
        The constructed response
    """

    hits = 1
    offset = page_size * (page_number - 1)

    # User queries exact reach
    if exact:
        if river_name:
            args = (reach, river_name + "%")

            cur.execute("SELECT * FROM reaches WHERE reach_id = %s AND river_name LIKE %s", args)
        else:
            cur.execute("SELECT * FROM reaches WHERE reach_id = %s", reach)
    # User queries partial region match
    else:
        hits = get_reach_hits_count(cur, reach, river_name)

        if river_name:
            args = (reach + "%", river_name + "%", offset, page_size)

            cur.execute("SELECT * FROM reaches WHERE reach_id LIKE %s AND river_name LIKE %s ORDER BY reach_id LIMIT %s,%s", args)
        else:
            args = (reach + "%", offset, page_size)

            cur.execute("SELECT * FROM reaches WHERE reach_id LIKE %s ORDER BY reach_id LIMIT %s,%s", args)

    elapsed_time = round((time.time() - start) * 1000, 3)
    return return_json_pass_through(cur, "reach", reach, river_name, exact, elapsed_time, hits,
                                    page_number, page_size)


def process_node(node, river_name, exact, cur, start, page_number, page_size):
    """
    Submits a node query to the DB, and passes that result to the return_json_passthrough to get
    the output node results.

    Parameters
    ----------
    node       : str
        The input node id
    river_name       : str
        The input river_name id
    exact      : bool
        True if an exact node should be queried
    cur        : pymysql.cursor
        pymysql connection cursor
    start       : int
        start time to measure query duration
    page_number        : int
        The requested page number when getting partial results
    page_size        : int
        The maximum number of results to return per call

    Returns
    -------
    dict
        The constructed response
    """

    hits = 1
    offset = page_size * (page_number - 1)

    # User queries exact node
    if exact:
        if river_name:
            args = (node, river_name + "%")

            cur.execute("SELECT * FROM nodes WHERE node_id = %s AND river_name LIKE %s", args)
        else:
            cur.execute("SELECT * FROM nodes WHERE node_id = %s", node)

    # User queries partial region match
    else:
        hits = get_node_hits_count(cur, node, river_name)

        if river_name:
            args = (node + "%", river_name + "%", offset, page_size)

            cur.execute("SELECT * FROM nodes WHERE node_id LIKE %s AND river_name LIKE %s ORDER BY node_id LIMIT %s,%s", args)
        else:
            args = (node + "%", offset, page_size)

            cur.execute("SELECT * FROM nodes WHERE node_id LIKE %s ORDER BY node_id LIMIT %s,%s", args)

    elapsed_time = round((time.time() - start) * 1000, 3)
    return return_json_pass_through(cur, "node", node, river_name, exact, elapsed_time, hits,
                                    page_number, page_size)


def return_json_pass_through(cur, identifier, name, river_name, exact, elapsed_time, hits, page_number, page_size):
    """
    Get the results of the DB query, and construct the resulting dict given the identifier, name.

    Parameters
    ----------
    cur        : pymysql.cursor
        pymysql connection cursor
    identifier : str
        'reach' or 'node'
    name       : str
        The input reach or node id
    river_name       : str
        The input reach or node id
    exact      : bool
        True if an exact reach or node should be queried
    elapsed_time       : int
        Number of ms to query DB
    hits               : int
        Total number of results that match query result
    page_number        : int
        The requested page number when getting partial results
    page_size        : int
        The maximum number of results to return per call

    Returns
    -------
    dict
        The constructed response
    """
    results = cur.fetchall()

    data = {}

    results_count = len(results)

    if results_count == 0:
        msg = f'404: Results with the specified {identifier} {name} were not found.'
        raise Exception(msg)

    partial_results = False
    status = "200 OK"
    if hits > results_count:
        partial_results = True
        status = "206 PARTIAL CONTENT"

    data['status'] = status
    data['time'] = str(elapsed_time) + " ms."
    data['hits'] = hits
    if partial_results:
        data['results_count'] = results_count

    data['search on'] = dict(
        parameter=identifier,
        river_name=river_name,
        exact=exact,
        page_number=page_number,
        page_size=page_size
    )
    data['results'] = []

    columns = cur.description
    result = [{columns[index][0]: column for index, column in enumerate(value)} for value in
              results]

    # Reformat results
    for res in result:
        if 'geojson' in res:
            res['geojson'] = geojson.loads(res['geojson'])
    data['results'] = result

    return data
