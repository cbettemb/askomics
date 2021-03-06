"""
Classes to import data from a gff3 source files
"""

import os, shutil
import textwrap
from pygments import highlight
from pygments.lexers import TurtleLexer
from pygments.formatters import HtmlFormatter

from askomics.libaskomics.source_file.SourceFile import SourceFile

class SourceFileTtl(SourceFile):
    """
    Class representing a ttl Source file
    """

    def __init__(self, settings, session, path):

        SourceFile.__init__(self, settings, session, path)

        self.type = 'ttl'

    def get_preview_ttl(self):
        """
        Return the first 100 lines of a ttl file,
        text is formated with syntax color
        """

        head = ''

        with open(self.path, 'r') as fp:
            for x in range(1,100):
                head += fp.readline()

        ttl = textwrap.dedent("""
        {content}
        """).format(content=head)

        formatter = HtmlFormatter(cssclass='preview_field', nowrap=True, nobackground=True)
        return highlight(ttl, TurtleLexer(), formatter) # Formated html

    def persist(self, urlbase):
        """
        insert the ttl sourcefile in the TS
        
        """

        pathttl = self.get_ttl_directory()
        shutil.copy(self.path, pathttl)
        fo = open(pathttl + '/' + os.path.basename(self.path))

        self.load_data_from_file(fo, urlbase)
        self.get_metadatas()


