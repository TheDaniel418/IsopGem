#!/home/daniel/Desktop/IsopGem/venv_py311/bin/python3.11

# $Id: rst2html4.py 7994 2016-12-10 17:41:45Z milde $
# Author: David Goodger <goodger@python.org>
# Copyright: This module has been placed in the public domain.

"""
A minimal front end to the Docutils Publisher, producing (X)HTML.

The output conforms to XHTML 1.0 transitional
and almost to HTML 4.01 transitional (except for closing empty tags).
"""

try:
    import locale

    locale.setlocale(locale.LC_ALL, "")
except:
    pass

from docutils.core import default_description, publish_cmdline

description = (
    "Generates (X)HTML documents from standalone reStructuredText "
    "sources.  " + default_description
)

publish_cmdline(writer_name="html4", description=description)
