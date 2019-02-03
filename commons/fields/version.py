import struct

from django.db import models


class VersionNumber(object):
  def __init__(self, major, minor=0, patch=0, build=0):
    self.number = (int(major), int(minor), int(patch), int(build))
    if any([i < 0 or i > 255 for i in self.number]):
      raise ValueError("Version number components must between 0 and 255,"
                       " inclusive")

  def __int__(self):
    """
    Maps a version number to a two's complement signed 32-bit integer by
    first calculating an unsigned 32-bit integer in the range [0,2**32-1],
    then subtracts 2**31 to get a number in the range [-2*31, 2**31-1].
    """
    major, minor, patch, build = self.number
    num = major << 24 | minor << 16 | patch << 8 | build
    return num - 2 ** 31

  def __str__(self):
    """
    Pretty printing of version number; doesn't print 0's on the end
    """
    end_index = 0
    for index, part in enumerate(self.number):
      if part != 0:
        end_index = index

    return ".".join([str(i) for i in self.number[:end_index + 1]])

  def __repr__(self):
    return "<%s.%s%s>" % (
      self.__class__.__module__,
      self.__class__.__name__,
      repr(self.number)
    )


class VersionNumberField(models.IntegerField):
  """
  A version number. Stored as a integer. Retrieved as a VersionNumber. Like
  magic. Major, minor, patch, build must not exceed 255
  """
  def db_type(self, connection):
    return 'integer'

  def to_python(self, value):
    """
    Convert a int to a VersionNumber
    """
    if value is None:
      return None
    if isinstance(value, VersionNumber):
      return value
    if isinstance(value, tuple):
      return VersionNumber(*value)

    part_bytes = struct.pack(">I", value + 2 ** 31)
    part_ints = [ord(i) for i in part_bytes]
    return VersionNumber(*part_ints)

  def get_prep_value(self, value):
    """
    Convert a VersionNumber or tuple to an int
    """
    if isinstance(value, VersionNumber):
      return int(value)
    if isinstance(value, tuple):
      return int(VersionNumber(*value))
    if isinstance(value, int):
      return value
