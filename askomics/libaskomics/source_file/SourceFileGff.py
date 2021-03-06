"""
Classes to import data from a gff3 source files
"""
import re
from BCBio.GFF import GFFExaminer
from BCBio import GFF

from askomics.libaskomics.source_file.SourceFile import SourceFile
from askomics.libaskomics.utils import rreplace

class SourceFileGff(SourceFile):
    """
    Class representing a Gff3 Source file
    """

    def __init__(self, settings, session, path, tax, ent):

        SourceFile.__init__(self, settings, session, path)

        self.type = 'gff'

        self.abstraction_dict = {}

        self.domain_knowledge_dict = {}

        self.pos_attr_list = [
            'position_taxon', 'position_ref', 'position_start', 'position_end',
            'position_strand'
        ]

        self.categories_list = ['position_taxon', 'position_ref', 'position_strand']

        self.taxon = tax

        self.entities = ent


    def get_entities(self):
        """
        get all the entities present in a gff file

        :return: The list of all the entities
        :rtype: List
        """
        exam = GFFExaminer()
        handle = open(self.path)
        entities = []
        gff_type = exam.available_limits(handle)['gff_type']
        for ent in gff_type:
            entities.append(ent[0])

        handle.close()

        return entities


    def get_turtle(self):
        """
        Get turtle string for a gff file
        """

        self.log.debug('--> get turtle <--')
        self.log.debug(self.path)
        handle = open(self.path)

        limit = dict(gff_type=self.entities)

        self.log.debug('--> go!')

        regex = re.compile(r'.*:')
        ttl = ''

        #TODO: test which loop is the faster
        for rec in GFF.parse(handle, limit_info=limit, target_lines=10000):
        # for rec in GFF.parse(handle, limit_info=limit):
            ref_entity = ':' + str(rec.id)
            for feat in rec.features:
                type_entity = ':'+feat.type
                if feat.id == '': # if there is no ID field, take the entity type as id
                    id_entity = feat.type
                else:
                    id_entity = regex.sub('', feat.id)
                start_entity = int(feat.location.start)
                end_entity = int(feat.location.end)

                if int(feat.location.strand == 1):
                    strand_entity = ':plus'
                elif int(feat.location.strand == -1):
                    strand_entity = ':minus'
                else:
                    strand_entity = ''

                taxon_entity = ':' + self.taxon

                attribute_dict = {
                    'rdf:type': type_entity,
                    'rdfs:label': '\"'+id_entity+'\"',
                    ':position_taxon': taxon_entity,
                    ':position_ref': ref_entity,
                    ':position_start': start_entity,
                    ':position_end': end_entity,
                    ':position_strand': strand_entity
                }

                # Abstraction
                if type_entity not in self.abstraction_dict.keys():
                    self.abstraction_dict[type_entity] = {'pos_attr': self.pos_attr_list, 'normal_attr' : []}

                # Domain knowledge ---------------------------------------------------------------
                if type_entity not in self.domain_knowledge_dict.keys():
                    self.domain_knowledge_dict[type_entity] = {'category' : {}}

                if self.domain_knowledge_dict[type_entity]['category'] == {}:
                    for category in self.categories_list:
                        self.domain_knowledge_dict[type_entity]['category'][category] = []

                # Strand
                if strand_entity not in self.domain_knowledge_dict[type_entity]['category']['position_strand']:
                    self.domain_knowledge_dict[type_entity]['category']['position_strand'].append(strand_entity)
                # taxon
                if taxon_entity not in self.domain_knowledge_dict[type_entity]['category']['position_taxon']:
                    self.domain_knowledge_dict[type_entity]['category']['position_taxon'].append(taxon_entity)
                # ref
                if ref_entity not in self.domain_knowledge_dict[type_entity]['category']['position_ref']:
                    self.domain_knowledge_dict[type_entity]['category']['position_ref'].append(ref_entity)
                # ---------------------------------------------------------------------------------

                for qualifier_key, qualifier_value in feat.qualifiers.items():
                    for val in qualifier_value:
                        if qualifier_key == 'Parent':
                            attribute_dict[':' + str(qualifier_key)] = str(':' + regex.sub('', val))
                            # Store the parent relation in abstraction
                            if {'Parent' : re.sub(r':.*', '', val)} not in self.abstraction_dict[type_entity]['normal_attr']:
                                self.abstraction_dict[type_entity]['normal_attr'].append({'Parent' : re.sub(r':.*', '', val)})
                        else:
                            attribute_dict[':' + str(qualifier_key)] = str('\"' + val + '\"')
                            # store normal attr in abstraction
                            if qualifier_key not in self.abstraction_dict[type_entity]['normal_attr']:
                                self.abstraction_dict[type_entity]['normal_attr'].append(qualifier_key)

                entity = {":"+id_entity: attribute_dict}

                ttl += self.get_content_ttl(entity)
        yield ttl

        handle.close()


    def get_content_ttl(self, entity):
        """
        Get the ttl string for an entity
        """

        for id_entity, attribute_dict in entity.items():
            first = True
            ttl = str(id_entity)
            indent = len(str(id_entity)) * ' ' + ' '
            for key, attr in attribute_dict.items():
                if attr == ':': # empty attr, dont insert triple
                    continue
                if first:
                    ttl += ' ' + str(key) + ' ' + str(attr) + ' ;\n'
                    first = False
                else:
                    ttl += indent + str(key) + ' ' + str(attr) + ' ;\n'

        ttl += '\n'

        ttl = rreplace(ttl, ';', '.', 1)

        return ttl

    def get_abstraction(self):
        """
        Get Abstraction (turtle) of the GFF
        """

        ttl =  '#################\n'
        ttl += '#  Abstraction  #\n'
        ttl += '#################\n\n'

        for entity, attribute_dict in self.abstraction_dict.items():
            ttl += entity + ' ' + 'rdf:type owl:Class ;\n'
            indent = len(entity) * ' ' + ' '
            ttl += indent + 'rdfs:label \"' + entity.replace(":", "") + "\" ;\n"
            ttl += indent + 'displaySetting:startPoint \"true\"^^xsd:boolean .\n\n'
            for type_attr, attr_list in attribute_dict.items():
                if type_attr == 'pos_attr': # positionable attributes
                    for pos_attr in attr_list:
                        if pos_attr in ('position_start', 'position_end'):
                            ttl += ':' + pos_attr + ' displaySetting:attribute \"true\"^^xsd:boolean ;\n'
                            indent = len(pos_attr) * ' ' + '  '
                            ttl += indent + 'rdf:type owl:DatatypeProperty ;\n'
                            ttl += indent + 'rdfs:label \"' + pos_attr.replace('position_', '') + '\" ;\n'
                            ttl += indent + 'rdfs:domain ' + entity + ' ;\n'
                            ttl += indent + 'rdfs:range xsd:decimal .\n\n'
                        else:
                            # No taxon, don't write triple and continue loop
                            if pos_attr == 'position_taxon' and self.taxon == '':
                                continue
                            ttl += ':' + pos_attr + ' displaySetting:attribute \"true\"^^xsd:boolean ;\n'
                            indent = len(pos_attr) * ' ' + '  '
                            ttl += indent + 'rdf:type owl:ObjectProperty ;\n'
                            ttl += indent + 'rdfs:label \"' + pos_attr.replace('position_', '') + '\" ;\n'
                            ttl += indent + 'rdfs:domain ' + entity + ' ;\n'
                            ttl += indent + 'rdfs:range :' + pos_attr.replace('position_', '') + "Category .\n\n"
                else: # other attributes
                    for attr in attr_list:
                        if type(attr) == type({}): # Parent relation
                            for key, value in attr.items():
                                ttl += ':' + key + ' rdf:type owl:ObjectProperty ;\n'
                                indent = len(key) * ' ' + '  '
                                ttl += indent + 'rdfs:label \"' + key + '\" ;\n'
                                ttl += indent + 'rdfs:domain ' + entity + " ;\n"
                                ttl += indent + 'rdfs:range :' + value + ' .\n\n'
                        else: # normal attributes
                            ttl += ':'+ attr + ' displaySetting:attribute \"true\"^^xsd:boolean ;\n'
                            indent = len(attr) * ' ' + '  '
                            ttl += indent + 'rdf:type owl:DatatypeProperty ;\n'
                            ttl += indent + 'rdfs:label \"' + attr + '\" ;\n'
                            ttl += indent + 'rdfs:domain ' + entity + " ;\n"
                            ttl += indent + 'rdfs:range xsd:string .\n\n'

        return ttl

    def get_domain_knowledge(self):
        """
        Get Domain Knowledge (turtle) of the GFF
        """

        ttl =  '######################\n'
        ttl += '#  Domain knowledge  #\n'
        ttl += '######################\n\n'

        for entity, dk_dict in self.domain_knowledge_dict.items():
            # Positionable entity
            ttl += entity + ' displaySetting:is_positionable \"true\"^^xsd:boolean .\n'
            ttl += ':is_positionable rdfs:label \'is_positionable\' .\n'
            ttl += ':is_positionable rdf:type owl:ObjectProperty .\n\n'

            for category_dict in dk_dict.values():
                for category, cat_list in category_dict.items():
                    # dont write triple for taxon if user don't enter one
                    if category == 'position_taxon' and self.taxon == '':
                        continue
                    for cat in cat_list:
                        ttl += ':' + str(category.replace('position_', '')) + 'Category displaySetting:category ' + str(cat) + ' .\n'
                        ttl += str(cat) + ' rdf:type :' + str(category.replace('position_', '')) + ' ;\n'
                        indent = len(str(cat)) * ' ' + ' '
                        ttl += indent + 'rdfs:label \"' + str(cat.replace(':', '')) + '\" .\n'

            ttl += '\n'

        return ttl