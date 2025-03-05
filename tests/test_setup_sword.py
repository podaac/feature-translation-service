"""
==============
test_setup_sword.py
==============

Test download, process and load SWORD DB into FTS RDS
"""

import os
from os import listdir
from os.path import dirname, join, realpath, isfile
import unittest
from unittest.mock import patch
from sqlalchemy import create_engine
from sqlalchemy.orm import Session


os.environ['DB_HOST'] = 'host'
os.environ['DB_NAME'] = 'db'
os.environ['DB_USER'] = 'user'
os.environ['DB_PASS'] = 'password'
os.environ['SWORD_S3_BUCKET'] = 'bucket'
os.environ['SWORD_S3_PATH'] = 'internal/SWORD/Reaches_Nodes_Test'

import fts.db.sword.setup_sword as setup_sword


class TestSWORDdb(unittest.TestCase):
    """
    Test sword db contents
    """

    @classmethod
    def setUpClass(cls):
        cls.test_dir = dirname(realpath(__file__))
        cls.test_data_dir = join(cls.test_dir, 'data')
        cls.test_files = [f for f in listdir(cls.test_data_dir)
                          if isfile(join(cls.test_data_dir, f))]
        cls.engine = create_engine('sqlite:///:memory:')
        cls.session = Session(cls.engine)

        # test pull sword from s3
        cls.sword_shp_data = "/".join([cls.test_data_dir, os.environ['SWORD_S3_PATH'], "shp"])

        # database takes time to load, best to only load it once prior to all tests
        setup_sword.load_nodes(cls.engine, cls.sword_shp_data)
        setup_sword.load_reaches(cls.engine, cls.sword_shp_data)
        cls.one_reach, cls.one_node = setup_sword.table_check(cls.engine)
        setup_sword.table_row_count(cls.engine)

    def test_tables_exist(self):
        """
        Test that data is found within reach and node table
        # """
        assert self.one_reach is not None
        assert self.one_node is not None

    def test_num_fields(self):
        """
        Test that data is found within each table have the correct number of fields
        """
        self.assertEqual(29, len(self.one_reach))
        self.assertEqual(25, len(self.one_node))

    def test_geom_type(self):
        """
        Test that data in each table is the correct geom
        """
        print(self.one_reach)
        print(self.one_node)
        self.assertEqual("LINESTRING", self.one_reach[25].split(" ")[0])
        self.assertEqual("POINT", self.one_node[21].split(" ")[0])

    def tearDown(self):
        self.session.close()
