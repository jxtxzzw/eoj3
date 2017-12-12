from datetime import datetime
from os import path, listdir
import re

from django.conf import settings


LANG_CONFIG = {
    "cpp": {
        "name": "c++11",
        "compilerFile": "/usr/bin/g++",
        "compilerArgs": "-O2 -std=c++11 -o {exe_path} {code_path} -DONLINE_JUDGE -lm -fmax-errors=3",
        "codeFile": "foo.cc",
        "exeFile": "foo",
        "executeFile": "{exe_path}",
    },
    "java": {
        "name": "java",
        "compilerFile": "/usr/bin/javac",
        "compilerArgs": "-d {workspace} -encoding utf8 {code_path}",
        "codeFile": "Main.java",
        "exeFile": "Main",
        "executeFile": "/usr/bin/java",
        "executeArgs": "-cp {workspace} Main",
    },
    "python": {
        "name": "python3",
        "compilerFile": "/usr/bin/python3",
        "compilerArgs": "-m py_compile {code_path}",
        "codeFile": "foo.py",
        "exeFile": "foo",
        "executeFile": "/usr/bin/python3",
        "executeArgs": "{code_path}",
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
    return re.match(r"^[\.a-zA-Z0-9_-]{4,64}$", alias)


def valid_fingerprint_check(fingerprint):
    return re.match(r"^[a-z0-9]{16,128}$", fingerprint)


def get_repo_directory(pid):
    return path.join(settings.REPO_DIR, str(pid))
