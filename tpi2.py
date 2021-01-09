#encoding: utf8
# https://www.pythoncentral.io/cutting-and-slicing-strings-in-python/
# https://stackoverflow.com/questions/51115660/modifying-list-of-dictionary-using-list-comprehension
# https://www.geeksforgeeks.org/string-capitalize-python/
# https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects

from semantic_network import *
from bayes_net import *
from constraintsearch import *
from collections import Counter

class MyBN(BayesNet):
    def individual_probabilities(self):
        return { var : self.individualProb(var, True) for var, _ in self.dependencies.items() }

    def individualProb(self, var, val):
        variaveis = [k for k in self.dependencies.keys() if k != var]

        return sum([
            self.jointProb([(var, val)] + conj)
            for conj in self._generate_conjunction(variaveis)
        ])

    def _generate_conjunction(self, variaveis):
        if len(variaveis) == 1:
            return [[(variaveis[0], True)], [(variaveis[0], False)]]

        l = []
        for c in self._generate_conjunction(variaveis[1:]):
            l.append([(variaveis[0], True)] + c)
            l.append([(variaveis[0], False)] + c)

        return l

class MySemNet(SemanticNetwork):
    def __init__(self):
        SemanticNetwork.__init__(self)

    def translate_ontology(self):
        # print([d.relation for d in self.declarations if isinstance(d.relation, Subtype)])
        subt_decl = [d.relation for d in self.declarations if isinstance(d.relation, Subtype)]
        # subtypes_rel[type] = [ subtypes ]
        subtypes_rel = { t.entity2 : set() for t in subt_decl}
        [subtypes_rel[t.entity2].add(t.entity1) for t in subt_decl]

        return sorted([ "Qx " + "".join([str(s).capitalize() + "(x) or " for s in sorted(list(subtypes))]).rpartition(" or ")[0] + " => " + str(btype).capitalize() +"(x)" for btype, subtypes in subtypes_rel.items()], key=lambda x : x.rpartition(" => ")[2])

        # def generate_str(subtypes, btype):
        #     sub = ""
        #     sep = ""
        #     subtypes.sort()
        #     for s in subtypes:
        #         sub += sep + s.capitalize()
        #         sep = " or "

        #     return "Qx " + sub + " => " + btype

        # fst_order = []
        # for k in subtypes_rel.keys():
        #     fst_order.append(generate_str(list(subtypes_rel[k]), k))

        # return fst_order


    def query_inherit(self,entity,assoc):
        parents = [d.relation.entity2 for d in self.declarations if not isinstance(d.relation, Association) and d.relation.entity1 == entity]

        ldecl = []

        for p in parents:
            ldecl += self.query_inherit(p, assoc)
        
        ldecl_inv = [d for d in self.declarations if isinstance(d.relation, Association) and d.relation.entity2 == entity and d.relation.inverse == assoc]

        return ldecl + self.query_local(e1=entity, relname=assoc) + ldecl_inv

    def query(self,entity,relname):
        local = self.query_local(e1=entity, relname=relname)

        for l in local:
            if isinstance(l.relation, Member):
                return [d.relation.entity2 for d in local]
            if isinstance(l.relation, Subtype):
                return [d.relation.entity2 for d in local]
            if isinstance(l.relation, Association):
                # most common triple
                mct, _ = Counter([d.relation.assoc_properties() for d in local]).most_common(1)[0]
                assocs = list(filter(lambda x: x.relation.assoc_properties() in [mct], local))
                if mct[0] == 'single':
                    return [Counter([d.relation.entity2 for d in local]).most_common(1)[0][0]]
                else: # 'multiple'
                    return sorted(list(set([d.relation.entity2 for d in [dd for sublist in [self.query_inherit(d.relation.entity1, d.relation.name) for d in assocs] for dd in sublist] if d.relation.assoc_properties() in [mct]])))


class MyCS(ConstraintSearch):

    def search_all(self,domains=None,xpto=None):
        # Pode usar o argumento 'xpto' para passar mais
        # informação, caso precise
        #
        # IMPLEMENTAR AQUI
        pass


