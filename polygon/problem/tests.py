from django.test import SimpleTestCase

from polygon.problem.exception import RepositoryException
from polygon.problem.source import SourceManager
from utils import random_string


class RepositoryTestCase(SimpleTestCase):

    def setUp(self):
        self.sm = SourceManager(2000)

    def test_source_manager(self):
        name = random_string()
        new_name = random_string()
        self.sm.create_source_file(name, 'checker', 13768, 'cpp', '#include ...')
        self.assertEqual('#include ...', self.sm.view_source_file(name))
        print(self.sm.list_source_files())
        with self.assertRaisesMessage(RepositoryException, "File '%s' already exists." % name):
            self.sm.create_source_file(name, 'interactor', 13768, 'cpp', '#include ...')
        self.sm.edit_source_file(name, name=new_name)
        print(self.sm.list_source_files(), name)
        with self.assertRaises(RepositoryException):
            self.sm.edit_source_file(name, lang='python')
        self.sm.edit_source_file(new_name, lang='python')
        print(self.sm.list_source_files())
        self.sm.edit_source_file(new_name, tag='solution_correct')
        print(self.sm.list_source_files())
        self.sm.edit_source_file(new_name, code='#include ,,,,,,,,')
        self.assertEqual('#include ,,,,,,,,', self.sm.view_source_file(new_name))
        print(self.sm.list_source_files())
        self.sm.delete_source_file(new_name)
        with self.assertRaises(RepositoryException):
            self.sm.view_source_file(new_name)


