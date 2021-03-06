
from askomics.libaskomics.rdfdb.SparqlQueryBuilder import SparqlQueryBuilder
from askomics.libaskomics.rdfdb.QueryLauncher import QueryLauncher
from askomics.libaskomics.SourceFileConvertor import SourceFileConvertor

class InterfaceTPS(object):
    def __init__(self,settings,request):
        self.settings = settings
        self.request = request
        pass

    def empty(self):
        #empty database
        sqb = SparqlQueryBuilder(self.settings, self.request.session)
        ql = QueryLauncher(self.settings, self.request.session)
        namedGraphs = self.list_named_graphs()
        for graph in namedGraphs:
            ql.execute_query(sqb.get_delete_query_string(graph).query)

    def list_named_graphs(self):
        sqb = SparqlQueryBuilder(self.settings, self.request.session)
        ql = QueryLauncher(self.settings, self.request.session)

        res = ql.execute_query(sqb.get_list_named_graphs().query)

        namedGraphs = []

        for indexResult in range(len(res['results']['bindings'])):
            namedGraphs.append(res['results']['bindings'][indexResult]['g']['value'])

        return namedGraphs
    def drop_graph(self, graph):
        sqb = SparqlQueryBuilder(self.settings, self.request.session)
        ql = QueryLauncher(self.settings, self.request.session)
        ql.execute_query(sqb.get_drop_named_graph(graph).query)

    def load_file(self,f,col_types):
        disabled_columns = []
        sfc = SourceFileConvertor(self.settings, self.request.session)
        src_file = sfc.get_source_file(f)
        src_file.set_forced_column_types(col_types)
        src_file.set_disabled_columns(disabled_columns)
        data = src_file.persist('','noload')

    def load_test1(self):
        col_types = ['entity_start','text','category','numeric','text']
        self.load_file("personne.tsv",col_types)

    def load_test2(self):
        #empty database
        self.empty()

        col_types = ['entity_start', 'text', 'category', 'numeric', 'text']
        self.load_file("personne.tsv", col_types)
        col_types = ['entity_start', 'text']
        self.load_file("instrument.tsv", col_types)
        col_types = ['entity', 'entitySym']
        self.load_file("connait.tsv", col_types)
        col_types = ['entity', 'entity']
        self.load_file("enseigne.tsv", col_types)
        col_types = ['entity', 'entity']
        self.load_file("joue.tsv", col_types)

    def load_test3(self):
        # Transcripts
        col_types = ['entity', 'taxon', 'ref', 'start', 'end', 'strand', 'category']
        self.load_file('transcript.tsv', col_types)
        # QTL
        col_types = ['entity', 'taxon', 'ref', 'start', 'end']
        self.load_file('qtl.tsv', col_types)
