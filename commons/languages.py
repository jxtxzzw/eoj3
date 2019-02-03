import itertools


class Language:
  def __init__(self, name, code, versions, extensions):
    self.name = name
    self.versions = versions
    self.code = code
    self.extensions = extensions

  def language_choice_tuples(self):
    choices = []
    for version in self.versions:
      if not version:
        choices.append((self.code, self.name))
      else:
        choices.append((self.code + "." + version, "{} ({}.{})".format(self.name, self.code, version)))
    return choices


LANGUAGES = [
  Language("C", "c", ["gcc"], ["c"]),
  Language("C++", "cpp", ["g++", "g++11", "g++14", "g++17"], ["cc", "cpp", "cxx", "c++", "C"]),
  Language("Java", "java", ["8"], ["java"]),
  Language("Kotlin", "kotlin", [""], ["kt"]),
  Language("Pascal", "pascal", ["fpc"], ["pas"]),
  Language("Python", "python", ["2", "3"], ["py"]),
  Language("Scala", "scala", [""], ["scala"]),
]


LANG_CHOICES = list(itertools.chain(map(lambda l: l.language_choice_tuples(), LANGUAGES)))
DEFAULT_LANG_CODE = "cpp"
