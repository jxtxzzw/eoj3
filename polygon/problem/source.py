import json
from os import path, removedirs, makedirs, rename

from copy import deepcopy

import time

from polygon.problem.exception import RepositoryException
from polygon.problem.utils import get_repo_directory, normal_regex_check, LANG_CONFIG

TAG_LIST = [
    ('checker', 'checker'),
    ('interactor', 'interactor'),
    ('generator', 'generator'),
    ('validator', 'validator'),
    ('solution_main', 'solution - main correct'),
    ('solution_correct', 'solution - correct'),
    ('solution_tle_or_ok', 'solution - time limit exceeded or correct'),
    ('solution_wa', 'solution - wrong answer'),
    ('solution_incorrect', 'solution - incorrect'),
    ('solution_fail', 'solution - runtime error'),
]


class SourceManager:
    def __init__(self, problem_id):
        self.pid = problem_id
        self.source_dir = path.join(get_repo_directory(self.pid), 'source')
        self.source_desc_file = path.join(self.source_dir, 'source.desc')
        makedirs(self.source_dir, exist_ok=True)

    @property
    def source_desc(self):
        try:
            with open(self.source_desc_file, 'r') as desc_handler:
                return json.loads(desc_handler.read())
        except FileNotFoundError:
            return {}
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
        self.verify_name(name)
        self.verify_tag(tag)
        code_dir = path.join(self.source_dir, name)
        makedirs(code_dir, exist_ok=True)
        code_path = path.join(code_dir, LANG_CONFIG[lang]['codeFile'])
        with open(code_path, 'w') as code_file_handler:
            code_file_handler.write(code)
        self.source_desc[name] = {
            "tag": tag,
            "userId": user_id,
            "modificationTime": time.time(),
            "lang": lang,
            "length": path.getsize(code_path),
        }

    def edit_source_file(self, old_name, **kwargs):
        if old_name not in self.source_desc:
            return RepositoryException("You are trying to edit a non-existing source.")
        name = old_name
        code_dir = path.join(self.source_dir, name)
        if 'name' in kwargs:
            name = kwargs['name']
            self.verify_name(name)
            self.source_desc[name] = self.source_desc.pop(old_name)
            rename(path.join(self.source_dir, old_name), path.join(self.source_dir, name))
        elif 'code' in kwargs:
            code_path = path.join(code_dir, LANG_CONFIG[self.source_desc[name]['lang']]['codeFile'])
            with open(code_path, 'w') as code_file_handler:
                code_file_handler.write(kwargs['code'])
            self.source_desc[name].update(length=path.getsize(code_path))
        elif 'lang' in kwargs:
            self.source_desc[name].update(lang=kwargs['lang'])
            code_path = path.join(code_dir, LANG_CONFIG[self.source_desc[name]['lang']]['codeFile'])
            with open(code_path, 'w') as code_file_handler:
                code_file_handler.write(kwargs['code'])
        elif 'tag' in kwargs:
            tag = kwargs['tag']
            self.verify_tag(tag)
            self.source_desc[name].update(tag=tag)
        self.source_desc[name].update(modificationTime=time.time())

    def view_source_file(self, name):
        code_path = path.join(self.source_dir, name, LANG_CONFIG[self.source_desc[name]['lang']]['codeFile'])
        with open(code_path, 'r') as file:
            return file.read()

    def verify_name(self, name):
        code_dir = path.join(self.source_dir, name)
        if path.exists(code_dir):
            raise RepositoryException("File '%s' already exists." % name)
        if not normal_regex_check(name):
            raise RepositoryException("File name '%s' does not satisfy file regular protocol.")

    def verify_tag(self, tag):
        if tag not in dict(TAG_LIST).keys():
            raise RepositoryException("Unexpected tag '%s'" % tag)
