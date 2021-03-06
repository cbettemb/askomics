from glob import glob
import logging
import os.path
import re

from askomics.libaskomics.ParamManager import ParamManager
from askomics.libaskomics.source_file.SourceFileGff import SourceFileGff
from askomics.libaskomics.source_file.SourceFileTsv import SourceFileTsv
from askomics.libaskomics.source_file.SourceFileTtl import SourceFileTtl

class SourceFileConvertor(ParamManager):
    """
    A SourceFileConvertor instance provides methods to:
        - display an overview of the tabulated files the user want to convert in AskOmics.
        - convert the tabulated files in turtle files, taking care of:
            * the format of the data already in the database
              (detection of new and missing headers in the user files).
            * the abstraction generation corresponding to the header of the user files.
            * the generation of the part of the domain code that wan be automatically generated.
    """

    def __init__(self, settings, session):

        ParamManager.__init__(self, settings, session)
        self.log = logging.getLogger(__name__)

    def get_source_files(self):
        """
        :return: List of the file to convert paths
        :rtype: List
        """
        src_dir = self.get_source_file_directory()
        paths = glob(src_dir + '/*')

        files = []

        for p in paths:
            file_type = self.guess_file_type(p)
            if file_type == 'gff':
                files.append(SourceFileGff(self.settings, self.session, p, '', []))
            elif file_type == 'csv':
                files.append(SourceFileTsv(self.settings, self.session, p, int(self.settings["askomics.overview_lines_limit"])))
            elif file_type == 'ttl':
                files.append(SourceFileTtl(self.settings, self.session, p))

        return files

    def guess_file_type(self, filepath):
        extension = os.path.splitext(filepath)[1]
        if extension.lower() in ('.gff', '.gff2', '.gff3'):
            return 'gff'
        elif extension.lower() in ('.ttl',):
            return 'ttl'
        else:
            return 'csv'

    def get_rdf_files(self):
        """
        :return: List of the file to convert paths
        :rtype: List
        """
        src_dir = self.get_source_file_directory()
        paths = glob(src_dir + '/*[.ttl,.rdf]')

        files = []
        for p in paths:
            files.append(SourceFileTsv(self.settings, self.session, p, int(self.settings["askomics.overview_lines_limit"])))

        return files

    def get_source_file(self, name):
        """
        Return an object representing a source file

        :param name: The name of the source file to return
        :return: List of the file to convert paths
        :rtype: SourceFile
        """
        # As the name can be different than the on-disk filename (extension are removed), we loop on all SourceFile objects
        files = self.get_source_files()

        for f in files:
            if f.name == name:
                return f

        return None

    def get_source_file_gff(self, name, tax, ent):
        """
        Return an object representing a gff source file

        :param name: Yhe name of the gff file to return
        :return: the sourcefile
        :rtype: SourceFileGff
        """

        files = self.get_source_files_gff(tax, ent)

        for f in files:
            if f.name == name:
                return f

        return None

    def get_source_files_gff(self, tax='', ent=[]):
        """
        :return: List of the file to convert paths
        :rtype: List
        """
        src_dir = self.get_source_file_directory()
        paths = glob(src_dir + '/*.gff3')

        files = []
        for p in paths:
            files.append(SourceFileGff(self.settings, self.session, p, tax, ent))

        return files
