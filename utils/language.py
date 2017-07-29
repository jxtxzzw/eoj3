LANG_CHOICE = (
    ('c', 'C'),
    ('cpp', 'C++'),
    ('py2', 'Python 2'),
    ('python', 'Python 3'),
    ('java', 'Java 8'),
    ('pas', 'Pascal'),
)


LANG_CHOICE_NORMAL = dict(
    py2='python'
)


def normal_lang_id(lang):
    if LANG_CHOICE_NORMAL.get(lang):
        return LANG_CHOICE_NORMAL[lang]
    return lang