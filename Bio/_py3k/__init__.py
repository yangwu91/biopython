# Copyright 2010-2018 by Peter Cock.  All rights reserved.
#
# This file is part of the Biopython distribution and governed by your
# choice of the "Biopython License Agreement" or the "BSD 3-Clause License".
# Please see the LICENSE file that should have been included as part of this
# package.
"""Python 3 compatibility tools (PRIVATE).

We used to have lines like this under Python 2 in order to use
iterator based zip, map and filter (in Python 3 these functions
are all iterator based)::

    from future_builtins import zip

There is no similar option for range yet, other than::

    range = xrange
    input = raw_input

or:

    from __builtin__ import xrange as range
    from __builtin__ import raw_input as input

Under Python 3 these imports need to be removed. Also, deliberate
importing of built in functions like open changes from Python 2::

    from __builtin__ import open

To do this under Python 3:

    from builtins import open

Instead, we can do this under either Python 2 or 3:

    from Bio._py3k import open
    from Bio._py3k import zip

Once we drop support for Python 2, the whole of Bio._py3k will
go away.
"""

# From the point of view of pep8 and flake8, there are lots of issues with
# this file. This line tells flake8 to ignore it for quality assurance:
# flake8: noqa

import sys


if sys.version_info[0] >= 3:
    # Code for Python 3
    from builtins import open, zip, map, filter, range, input

    import codecs

    # Lots of our Python 2 code uses isinstance(x, basestring)
    # which after 2to3 becomes isinstance(x, str)
    basestring = str
    unicode = str

    _bytes_to_string = lambda b: b.decode()  # bytes to unicode string
    _string_to_bytes = lambda s: s.encode()  # unicode string to bytes

    def _bytes_bytearray_to_str(s):
        """If s is bytes or bytearray, convert to a unicode string (PRIVATE)."""
        if isinstance(s, (bytes, bytearray)):
            return s.decode()
        return s

    def _as_unicode(s):
        """Turn byte string or unicode string into a unicode string (PRIVATE)."""
        if isinstance(s, str):
            return s
        # Assume it is a bytes string
        # Note ISO-8859-1 aka Latin-1 preserves first 256 chars
        return codecs.latin_1_decode(s)[0]

    def _as_bytes(s):
        """Turn byte string or unicode string into a bytes string (PRIVATE).

        The Python 2 version returns a (byte) string.
        """
        if isinstance(s, bytes):
            return s
        # Assume it is a unicode string
        # Note ISO-8859-1 aka Latin-1 preserves first 256 chars
        return codecs.latin_1_encode(s)[0]

    _as_string = _as_unicode

    def _is_int_or_long(i):
        """Check if the value is an integer (PRIVATE).

        Note there are no longs on Python 3.
        """
        return isinstance(i, int)

    import io
    import locale

    # Python 3.4 onwards, the standard library wrappers should work:
    def _binary_to_string_handle(handle):
        """Treat a binary (bytes) handle like a text (unicode) handle (PRIVATE)."""
        try:
            # If this is a network handle from urllib,
            # the HTTP headers may tell us the encoding.
            encoding = handle.headers.get_content_charset()
        except AttributeError:
            encoding = None
        if encoding is None:
            # The W3C recommendation is:
            # When no explicit charset parameter is provided by the sender,
            # media subtypes of the "text" type are defined to have a default
            # charset value of "ISO-8859-1" when received via HTTP.
            # "ISO-8859-1" is also known as 'latin-1'
            # See the following for more detail:
            # https://www.w3.org/Protocols/rfc2616/rfc2616-sec3.html#sec3.7.1
            encoding = 'latin-1'
        wrapped = io.TextIOWrapper(io.BufferedReader(handle), encoding=encoding)
        try:
            # If wrapping an online handle, this is nice to have:
            wrapped.url = handle.url
        except AttributeError:
            pass
        return wrapped

    # This is to avoid the deprecation warning from open(filename, "rU")
    _universal_read_mode = "r"  # text mode does universal new lines

    # On Python 3, this will be a unicode StringIO
    from io import StringIO

    # On Python 3 urllib, urllib2, and urlparse were merged:
    from urllib.request import urlopen, Request, urlretrieve, urlparse, urlcleanup
    from urllib.parse import urlencode, quote
    from urllib.error import HTTPError

else:
    # Python 2 code
    from __builtin__ import open, basestring, unicode

    # Import Python3 like iterator functions:
    from future_builtins import zip, map, filter
    from __builtin__ import xrange as range
    from __builtin__ import raw_input as input

    _bytes_to_string = lambda b: b  # bytes to string, i.e. do nothing
    _string_to_bytes = lambda s: str(s)  # str (or unicode) to bytes string

    def _bytes_bytearray_to_str(s):
        """If s is bytes or bytearray, convert to a string (PRIVATE)."""
        if isinstance(s, (bytes, bytearray)):
            return str(s)
        return s

    def _as_unicode(s):
        """Turn a (byte) string or a unicode string into a (byte) string (PRIVATE)."""
        # Will be changed by 2to3 to "isinstance(s, str)" but doesn't matter:
        if isinstance(s, unicode):
            return s
        return s.decode()

    def _as_bytes(s):
        """Turn a (byte) string or a unicode string into a (byte) string (PRIVATE)."""
        return str(s)

    _as_string = _as_bytes

    def _is_int_or_long(i):
        """Check if the value is an integer or long (PRIVATE)."""
        return isinstance(i, (int, long))

    def _binary_to_string_handle(handle):
        """Treat a binary handle like a text handle (PRIVATE)."""
        return handle

    # This private variable is set to "r" on Python 3 for text
    # mode which include universal readlines mode
    _universal_read_mode = "rU"

    # On Python 2 this will be a (bytes) string based handle.
    # Note this doesn't work as it is unicode based:
    # from io import StringIO
    try:
        from cStringIO import StringIO
    except ImportError:
        from StringIO import StringIO

    # Under urllib.request on Python 3:
    from urllib2 import urlopen, Request
    from urllib import urlretrieve, urlcleanup
    from urlparse import urlparse

    # Under urllib.parse on Python 3:
    from urllib import urlencode, quote

    # Under urllib.error on Python 3:
    from urllib2 import HTTPError


if sys.platform == "win32":
    # Can't use commands.getoutput on Python 2, Unix only/broken:
    # http://bugs.python.org/issue15073
    # Can't use subprocess.getoutput on Python 3, Unix only/broken:
    # http://bugs.python.org/issue10197
    def getoutput(cmd):
        import subprocess
        child = subprocess.Popen(cmd,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 shell=False)
        stdout, stderr = child.communicate()
        # Remove trailing \n to match the Unix function,
        return stdout.rstrip("\n")
elif sys.version_info[0] >= 3:
    # Use subprocess.getoutput on Python 3,
    from subprocess import getoutput
else:
    # Use commands.getoutput on Python 2,
    from commands import getoutput
