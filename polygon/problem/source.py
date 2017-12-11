# d = {
#     "name": ,
#     "tag": ,
#     "modificationTime": 1512307455439,
#     "userId": 11905,
#     "type": "cpp.g++11",
#     "length": ,
# }

import json
from os import path, removedirs, makedirs

from copy import deepcopy

from polygon.problem.exception import RepositoryException
from polygon.problem.utils import get_repo_directory, normal_regex_check


class SourceManager:

    def __init__(self, pid):
        self.pid = pid
        self.source_dir = path.join(get_repo_directory(pid), 'source')
        self.source_desc_file = path.join(self.source_dir, 'source.desc')
        makedirs(self.source_dir, exist_ok=True)

    @property
    def source_desc(self):
        try:
            with open(self.source_desc_file, 'r') as desc_handler:
                return json.loads(desc_handler.read())
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            raise RepositoryException("JSON Decode Error when listing source files. Contact admin.")

    @source_desc.setter
    def source_desc(self, val):
        with open(self.source_desc_file, 'r') as desc_handler:
            desc_handler.write(json.dumps(val))

    def list_source_files(self):
        raw = deepcopy(self.source_desc)
        for key, val in raw.items():
            val['name'] = key
        return raw.values()

    def delete_source_file(self, name):
        try:
            self.source_desc.pop(name)
            removedirs(self.source_dir, name)
        except KeyError:
            raise RepositoryException("Try to delete a file '%s' that does not exist." % name)


    def create_source_file(self, name, tag, user_id, lang, code):
        dir = path.join(self.source_dir, name)
        if path.exists(dir):
            raise RepositoryException("File '%s' already exists." % name)
        if not normal_regex_check(name):
            raise RepositoryException("File name '%s' does not satisfy file regular protocol.")
        makedirs(dir, exist_ok=True)

