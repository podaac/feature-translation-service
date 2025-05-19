# pylint: disable-msg=R0914, W0707, duplicate-code, W0640

"""
==============
setup_sword.py
==============

Test calls to setup_sword.py
"""

import logging
import io
import os
from os import walk
from pathlib import Path
import json
import boto3
import pandas as pd
from sqlalchemy.exc import OperationalError, NoSuchTableError
from sqlalchemy import \
    create_engine, MetaData, Table, Text, Integer, \
    Float, select
from sqlalchemy.sql import text as text_query
from sqlalchemy.dialects.mysql import VARCHAR
from tqdm import tqdm
import fiona
import shapely.wkt
import shapely.geometry
import geopandas

DB_HOST = os.environ['DB_HOST']
DB_NAME = os.environ['DB_NAME']
DB_USER = os.environ['DB_USER']
DB_PASS = os.environ['DB_PASS']
SWORD_S3_BUCKET = os.environ['SWORD_S3_BUCKET']
SWORD_S3_PATH = os.environ['SWORD_S3_PATH']

NETCDF_FS = [
    "sa_apriori_rivers",
    "oc_apriori_rivers",
    "na_apriori_rivers",
    "eu_apriori_rivers",
    "as_apriori_rivers",
    "af_apriori_rivers"
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def pull_sword(s3_bucket, s3_sword_path):
    """
    Pull s3 data function for pulling SWORD reach / node data
    """
    s3_resource = boto3.resource('s3')
    bucket = s3_resource.Bucket(s3_bucket)
    objects = bucket.objects.filter(Prefix=s3_sword_path)
    for obj in objects:
        if not os.path.exists(os.path.dirname(obj.key)):
            os.makedirs(os.path.dirname(obj.key))
        bucket.download_file(obj.key, obj.key)
    logger.info("Sword S3 data pulled successfully")


def insert_into_db(data_frame, tbl_name, engine, datatype):
    """
    Database load function
    """
    class TqdmToLogger(io.StringIO):
        """
        Helper class to output stream for TQDM
        which will output to logger module instead of
        the stdout
        """
        logr = None
        level = None
        buf = ''

        def __init__(self, logr, level=None):
            super().__init__()
            self.logger = logr
            self.level = level or logging.INFO

        def write(self, buf):
            self.buf = buf.strip('\r\n\t ')

        def flush(self):
            self.logger.log(self.level, self.buf)

    def chunker(seq, size):
        """
        Progress bar helper to determine position sizes
        """
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))

    def insert_with_progress(
            sword_dframe,
            sword_tbl,
            sword_engine,
            d_type=None
    ):
        """
        Pandas to_sql with progress bar in order to load to RDS
        """
        tqdm_out = TqdmToLogger(logger, level=logging.INFO)
        chunksize = int(len(sword_dframe) / 10)
        with tqdm(total=len(sword_dframe), file=tqdm_out) as pbar:
            for _, cdf in enumerate(chunker(sword_dframe, chunksize)):
                # replace = "replace" if i == 0 else "append"
                cdf.to_sql(
                    sword_tbl,
                    sword_engine,
                    if_exists="append",
                    index=False,
                    dtype=d_type
                )
                pbar.update(chunksize)

    insert_with_progress(data_frame, tbl_name, engine, datatype)


def drop_reach_table(sqla_engine):
    """
    Drop reach table

    Parameters:
    SQLAlchemy Engine
    """
    logger.info("Dropping reach table")
    conn = sqla_engine.connect()
    try:
        drop_tbl_reach = text_query(
            "DROP TABLE reaches"
        )
        drop_reach_results = conn.execute(drop_tbl_reach)
        logger.debug(drop_reach_results)
        logger.info("Reach table dropped")
    except (OperationalError, NoSuchTableError):
        logger.info("No reach table to drop")


def drop_node_table(engine):
    """
    Drop node table
    """
    logger.info("Dropping node table")
    conn = engine.connect()
    try:
        drop_tbl_node = text_query(
            "DROP TABLE nodes"
        )
        drop_node_results = conn.execute(drop_tbl_node)
        logger.debug(drop_node_results)
        logger.info("Node table dropped")
    except (OperationalError, NoSuchTableError):
        logger.info("No node table to drop")


def determine_netcdf_name_from_prefix(shp):
    """
    Helper for returning shapefile and reconstructed netcdf filenames
    """
    path_obj = Path(shp)
    db_ver = path_obj.stem[-3:]
    shp_filename = str(path_obj.stem) + ".shp"
    continent_prefix = shp_filename[:2]
    netcdf_filename = str(
        [("_".join([file, db_ver])) + ".nc" for file in NETCDF_FS
            if file[:2] == continent_prefix][0]
    )
    return netcdf_filename, shp_filename


def load_reaches(engine, sword_shp_path):
    """
    Drop and load reaches into FTS DB
    """
    logger.info("Loading reaches")

    def clean_reach_shapefile(shapefile):
        """
        Used to remove bad data, single-point reach features, from a shapefile
        """
        shp_path = Path(shapefile)
        name = str(shp_path.stem)
        new_name = name + "_CLEANED.shp"
        root_dir = str(shp_path.parent)
        clean_shpfile_name = "/".join([root_dir, new_name])
        with fiona.open(shapefile) as source, fiona.open(clean_shpfile_name,
                                                         'w',
                                                         driver=source.driver,
                                                         crs=source.crs,
                                                         schema=source.schema
                                                         ) as dest:
            for feat in source:
                coords = len(feat['geometry']['coordinates'])
                if coords >= 2:
                    dest.write(feat)
        return clean_shpfile_name

    try:
        _, dirs, _ = next(walk(sword_shp_path))
    except StopIteration:
        raise StopIteration("Directory not found")
    sword_dir_paths = ["/".join([sword_shp_path, d]) for d in dirs]
    logger.debug(sword_dir_paths)

    # drop table before loading
    drop_reach_table(engine)

    for dpath in sword_dir_paths:
        try:
            _, dirs, filenames = next(walk(dpath))
        except StopIteration:
            raise StopIteration("Directory not found")

        reach_shapefiles = [
            "/".join([dpath, name]) for name in filenames
            if name.endswith(".shp") and "reaches" in name
        ]

        for reach_shpfile in reach_shapefiles:
            # Two or more coordinate tuples,
            # each consisting of floating point values
            # for longitude, latitude, and altitude.
            try:
                gdf = geopandas.read_file(reach_shpfile)
            except ValueError:
                clean_shpfile = clean_reach_shapefile(reach_shpfile)
                gdf = geopandas.read_file(clean_shpfile)

            # two fields *_up *_dn to be dropped
            # inconsistent data type causing load errors
            # field examples:
            # 37     73111000395  73111000103  73111000013
            # 39                                      None
            # 40                               73111000041
            gdf = gdf.drop(columns=['rch_id_up', 'rch_id_dn'])
            dframe = pd.DataFrame(gdf)

            # prepare fields to be added
            dframe['geojson'] = dframe['geometry'].apply(
                lambda x: json.dumps(
                    shapely.geometry.mapping(shapely.wkt.loads(str(x)))
                )
            ).astype('str')

            netcdf_filename, shp_filename = \
                determine_netcdf_name_from_prefix(reach_shpfile)

            dframe['shp_origin'] = dframe['geometry'].apply(
                lambda x: str(shp_filename)
            ).astype('str')
            dframe['netcdf_origin'] = dframe['geometry'].apply(
                    lambda x: str(netcdf_filename)
            ).astype('str')

            reach_headers = [
                'x',
                'y',
                'reach_id',
                'reach_len',
                'n_nodes',
                'wse',
                'wse_var',
                'width',
                'width_var',
                'facc',
                'n_chan_max',
                'n_chan_mod',
                'obstr_type',
                'grod_id',
                'hfalls_id',
                'slope',
                'dist_out',
                'lakeflag',
                'max_width',
                'n_rch_up',
                'n_rch_dn',
                'swot_orbit',
                'swot_obs',
                'type',
                'river_name',
                'geometry',
                'geojson',
                'shp_origin',
                'netcdf_origin',
            ]

            reach_dtypes = [
                'float',
                'float',
                'str',
                'float',
                'int',
                'float',
                'float',
                'float',
                'float',
                'float',
                'int',
                'int',
                'int',
                'int',
                'int',
                'float',
                'float',
                'int',
                'int',
                'int',
                'int',
                'str',
                'int',
                'int',
                'str',
                'str',
                'str',
                'str',
                'str'
            ]

            reach_dtype_dict = dict(zip(reach_headers, reach_dtypes))
            for key, val in reach_dtype_dict.items():
                dframe[key] = dframe[key].astype(val)

            # pandas / sqla load to RDS
            reach_sqla_types = [
                Float,
                Float,
                VARCHAR(12),
                Float,
                Integer,
                Float,
                Float,
                Float,
                Float,
                Float,
                Integer,
                Integer,
                Integer,
                Integer,
                Integer,
                Float,
                Float,
                Integer,
                Integer,
                Integer,
                Integer,
                Text,
                Integer,
                Integer,
                Text,
                Text,
                Text,
                Text,
                Text
            ]

            reach_sqla_types_dict = dict(zip(reach_headers, reach_sqla_types))
            logger.info("Current reach file: %s", reach_shpfile)
            reach_table_name = 'reaches'
            insert_into_db(
                dframe, reach_table_name, engine, reach_sqla_types_dict
            )


def load_nodes(engine, sword_shp_path):
    """
    Drop and load nodes into FTS DB
    """
    logger.info("Loading nodes")

    try:
        _, dirs, _ = next(walk(sword_shp_path))
    except StopIteration:
        raise StopIteration("Directory not found")
    sword_dir_paths = ["/".join([sword_shp_path, d]) for d in dirs]
    logger.debug(sword_dir_paths)

    # drop table before loading
    drop_node_table(engine)

    for dpath in sword_dir_paths:
        try:
            _, dirs, filenames = next(walk(dpath))
        except StopIteration:
            raise StopIteration("Directory not found")
        node_shapefiles = \
            ["/".join([dpath, name]) for name in filenames
             if name.endswith(".shp") and "nodes" in name]
        logger.debug(node_shapefiles)

        for node_shpfile in node_shapefiles:
            logger.debug(node_shpfile)
            gdf = geopandas.read_file(node_shpfile)

            # prepare fields to be added
            gdf['geojson'] = gdf['geometry'].apply(lambda x: json.dumps(
                shapely.geometry.mapping(shapely.wkt.loads(str(x)))
            )).astype('str')

            netcdf_filename, shp_filename = \
                determine_netcdf_name_from_prefix(node_shpfile)

            gdf['shp_origin'] = gdf['geometry'].apply(
                lambda x: str(shp_filename)
            ).astype('str')
            gdf['netcdf_origin'] = gdf['geometry'].apply(
                    lambda x: str(netcdf_filename)
            ).astype('str')

            gdf['geometry'] = gdf['geometry'].astype('str')

            # pandas / sqla load to RDS
            node_table_name = 'nodes'
            node_headers = [
                'x',
                'y',
                'node_id',
                'node_len',
                'reach_id',
                'wse',
                'wse_var',
                'width',
                'wth_var',
                'n_chan_max',
                'n_chan_mod',
                'obstr_type',
                'grod_id',
                'hfalls_id',
                'dist_out',
                'type',
                'facc',
                'lakeflag',
                'max_width',
                'river_name',
                'manual_add',
                'geometry',
                'geojson',
                'shp_origin',
                'netcdf_origin'
            ]

            node_sqla_types = [
                Float,
                Float,
                VARCHAR(15),
                Float,
                VARCHAR(12),
                Float,
                Float,
                Float,
                Float,
                Integer,
                Integer,
                Integer,
                Integer,
                Integer,
                Integer,
                Integer,
                Float,
                Integer,
                Float,
                Text,
                Integer,
                Text,
                Text,
                Text,
                Text
            ]

            node_sqla_types_dict = dict(zip(node_headers, node_sqla_types))
            logger.info("Current node file: %s", node_shpfile)
            insert_into_db(
                gdf, node_table_name, engine, node_sqla_types_dict
            )


def table_check(engine):
    """
    Table data check function
    """
    logger.info("Performing table check")
    conn = engine.connect()
    metadata = MetaData()

    reaches = Table(
        'reaches', metadata, autoload_with=engine
    )
    reach_query = select(reaches).limit(4)

    one_reach = None
    try:
        reach_result = conn.execute(reach_query)
        print("Reach columns: %s", reach_result.keys())
        one_reach = reach_result.fetchone()
        logger.info("ONE REACH: %s", one_reach)
        logger.info("Number of reach columns: %s", len(one_reach))
        reach_resultset = reach_result.fetchall()
        logger.info(reach_resultset)
    except NoSuchTableError:
        logger.info("No table available")

    nodes = Table(
        'nodes', metadata, autoload_with=engine
    )
    node_query = select(nodes).limit(4)

    one_node = None
    try:
        node_result = conn.execute(node_query)
        print("Node columns: %s", node_result.keys())
        one_node = node_result.fetchone()
        logger.info("ONE NODE: %s", one_node)
        logger.info("Number of node columns: %s", len(one_node))
        node_resultset = node_result.fetchall()
        logger.info(node_resultset)
    except NoSuchTableError:
        logger.info("No table available")

    return one_reach, one_node


def table_status(engine):
    """
    Table status check function
    """
    logger.info("Performing table status")
    conn = engine.connect()

    # Report fields
    # SELECT table_name,Engine,Version,Row_format,table_rows,Avg_row_length,
    # Data_length,Max_data_length,Index_length,Data_free,Auto_increment,
    # Create_time,Update_time,Check_time,table_collation,Checksum,
    # Create_options,table_comment FROM information_schema.tables
    # WHERE table_schema = DATABASE();

    tbl_status = text_query(
        "SELECT * "
        "FROM information_schema.tables "
        "WHERE table_schema = DATABASE()"
    )
    status_results = conn.execute(tbl_status)
    for result in status_results:
        logger.info(result)


def table_data_types_reaches(engine):
    """
    Reach table column name & data types check function
    """
    logger.info("Performing data type check on reach table")
    conn = engine.connect()

    tbl_data_type = text_query(
        "SELECT COLUMN_NAME,DATA_TYPE "
        "FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE table_schema = :dbname and table_name = 'reaches'"
    )
    dtype_results = conn.execute(tbl_data_type, {"dbname": DB_NAME})
    for result in dtype_results:
        logger.info(result)


def table_data_types_nodes(engine):
    """
    Node table column name & data types check function
    """
    logger.info("Performing data type check on node table")
    conn = engine.connect()

    tbl_data_type = text_query(
        "SELECT COLUMN_NAME,DATA_TYPE "
        "FROM INFORMATION_SCHEMA.COLUMNS "
        "WHERE table_schema = :dbname and table_name = 'nodes'"
    )
    dtype_results = conn.execute(tbl_data_type, {"dbname": DB_NAME})
    for result in dtype_results:
        logger.info(result)


def table_row_count(engine):
    """
    Table status check function
    """
    logger.info("Performing row count")
    conn = engine.connect()

    tbl_status = text_query(
        "select count(*) from reaches"
    )
    reach_count = None
    try:
        reach_results = conn.execute(tbl_status)
        reach_count = str(reach_results.first())
        logger.info("Reach row count: %s", reach_count)
    except NoSuchTableError:
        logger.info("No table available")

    tbl_status = text_query(
        "select count(*) from nodes"
    )
    node_count = None
    try:
        node_results = conn.execute(tbl_status)
        node_count = str(node_results.first())
        logger.info("Node row count: %s", node_count)
    except NoSuchTableError:
        logger.info("No row available")

    return reach_count, node_count


def table_index(engine):
    """
    Run index generation on new tables
    """
    logger.info("Indexing tables")
    conn = engine.connect()

    tbl_reach_index = text_query(
        "CREATE INDEX reach_id_idx ON reaches(reach_id) USING BTREE"
    )
    tbl_rvrname_reach_index = text_query(
        "CREATE INDEX river_name_idx ON reaches (river_name(300)) USING BTREE"
    )
    try:
        conn.execute(tbl_reach_index)
        conn.execute(tbl_rvrname_reach_index)
    except NoSuchTableError:
        logger.info("No table available")

    tbl_node_index = text_query(
        "CREATE INDEX node_id_idx ON nodes(node_id) USING BTREE"
    )
    tbl_rvrname_node_index = text_query(
        "CREATE INDEX river_name_idx ON nodes (river_name(300)) USING BTREE"
    )
    try:
        conn.execute(tbl_node_index)
        conn.execute(tbl_rvrname_node_index)
    except NoSuchTableError:
        logger.info("No table available")


def main():
    """
    Entry point to load sword db.
    """

    # pull sword data
    pull_sword(SWORD_S3_BUCKET, SWORD_S3_PATH)

    # sql alchemy engine
    engine = create_engine(
        'mysql+pymysql://' + DB_USER + ':' + DB_PASS + '@'
        + DB_HOST + '/' + DB_NAME
    )

    # load RDS tables
    local_sword_path = "/".join([SWORD_S3_PATH, "shp"])
    load_nodes(engine, local_sword_path)
    load_reaches(engine, local_sword_path)
    table_index(engine)

    # check RDS tables
    table_row_count(engine)
    table_status(engine)
    table_check(engine)
    table_data_types_reaches(engine)
    table_data_types_nodes(engine)


if __name__ == '__main__':
    main()
