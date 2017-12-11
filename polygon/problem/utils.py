from datetime import datetime
from os import path, listdir
import re

from django.conf import settings


LANG_CONFIG = {
    "cpp": {
        "name": "c++11",
        "compiler_file": "/usr/bin/g++",
        "compiler_args": "-O2 -std=c++11 -o {exe_path} {code_path} -DONLINE_JUDGE -lm -fmax-errors=3",
        "code_file": "foo.cc",
        "exe_file": "foo",
        "execute_file": "{exe_path}",
    },
    "java": {
        "name": "java",
        "compiler_file": "/usr/bin/javac",
        "compiler_args": "-d {workspace} -encoding utf8 {code_path}",
        "code_file": "Main.java",
        "exe_file": "Main",
        "execute_file": "/usr/bin/java",
        "execute_args": "-cp {workspace} Main",
    },
    "python": {
        "name": "python3",
        "compiler_file": "/usr/bin/python3",
        "compiler_args": "-m py_compile {code_path}",
        "code_file": "foo.py",
        "exe_file": "foo",
        "execute_file": "/usr/bin/python3",
        "execute_args": "{code_path}",
    }
}


def sort_out_directory(directory):
    if not path.exists(directory):
        return []
    return sorted(list(map(lambda file: {'filename': path.basename(file),
                                         'modified_time': datetime.fromtimestamp(path.getmtime(file)).
                                                          strftime(settings.DATETIME_FORMAT_TEMPLATE),
                                         'size': path.getsize(file)},
                           listdir_with_prefix(directory))),
                  key=lambda d: d['modified_time'], reverse=True)


def listdir_with_prefix(directory):
    return list(map(lambda file: path.join(directory, file),
                    filter(lambda f2: not f2.startswith('.'),
                           listdir(directory))))


def normal_regex_check(alias):
    return re.match(r"^[\.a-z0-9_-]{4,64}$", alias)


def valid_fingerprint_check(fingerprint):
    return re.match(r"^[a-z0-9]{16,128}$", fingerprint)


def get_repo_directory(pid):
    return path.join(settings.REPO_DIR, str(pid))
