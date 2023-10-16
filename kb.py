import re
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF
from rdflib.plugins.sparql import prepareQuery
from pathlib import Path

LRM = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
SCHEMA = Namespace("https://schema.org/")
NOMEN = Namespace("http://spacesoftranslation.org/ns/nomena/")
PERSON = Namespace("http://spacesoftranslation.org/ns/people/")
JOURNAL = Namespace("http://spacesoftranslation.org/ns/journals/")
ISSUE = Namespace("http://spacesoftranslation.org/ns/issues/")
WORK = Namespace("http://spacesoftranslation.org/ns/works/")
EXPRESSION = Namespace("http://spacesoftranslation.org/ns/expressions/")
TRANSLATION = Namespace("http://spacesoftranslation.org/ns/translations/")


class Person():
    def __init__(self, graph, uriref):
        self.graph = graph
        self.id = uriref
        self._names = None

    def to_dict(self):
        return {"person": self.names[0]}

    def __repr__(self):
        return f"<Person: {self.label}>"

    @property
    def label(self):
        return next(self.graph.objects(self.id, RDFS.label)).toPython()

    @property
    def names(self):
        if self._names is None:
            appellations = self.graph.objects(self.id, LRM.R13_has_appellation)
            self._names = []
            for a in appellations:
                names = self.graph.objects(a, LRM.R33_has_string)
                self._names = [n.toPython() for n in names]
        return self._names



class Magazine():
    def __init__(self, graph, uriref) -> None:
        self.graph: Graph = graph
        self.id = uriref


    def __repr__(self) -> str:
        return f"<Magazine: {self.label}>"


    @property
    def label(self) -> str:
        return next(self.graph.objects(self.id, RDFS.label)).toPython()

    @property
    def issues(self) -> list:
        issues = self.graph.objects(self.id, LRM.R67_has_part)
        return [Issue(self.graph, issue) for issue in issues]


    def to_dict(self) -> dict:
        return { "key": self.id.split('/')[-1],
                 "id": self.id,
                 "label" : self.label,
                 "issues": [i.to_dict() for i in self.issues] }

class Issue():
    def __init__(self, graph, uriref) -> None:
        self.graph = graph
        self.id = uriref

    def __repr__(self) -> str:
        return f"<Issue: {self.label}>"

    @property
    def label(self) -> str:
        return next(self.graph.objects(self.id, RDFS.label))


    @property
    def magazine(self):
        # return Magazine(self.graph, next(self.graph.subjects(self.id, LRM.R67_has_part)))
        return Magazine(self.graph, next(self.graph.objects(self.id, LRM.R67i_is_part_of)))

    def to_dict(self) -> dict:
        return {"issue": self.id,
                "label": self.label }


class Translator(Person):
    def __init__(self, graph, uriref, **kwargs):
        super().__init__(graph, uriref)
        self._translations = None


    @property
    def label(self):
        return next(self.graph.objects(self.id, RDFS.label)).toPython()

    @property
    def birthDate(self):
        try:
            return next(self.graph.objects(self.id, SCHEMA.birthDate)).toPython()
        except StopIteration:
            return None

    @property
    def deathDate(self):
        try:
            return next(self.graph.objects(self.id, SCHEMA.deathDate)).toPython()
        except StopIteration:
            return None

    @property
    def gender(self):
        try:
            return next(self.graph.objects(self.id, SCHEMA.gender)).toPython()
        except StopIteration:
            return None

    @property
    def nationality(self):
        try:
            return next(self.graph.objects(self.id, SCHEMA.nationality)).toPython()
        except StopIteration:
            return None

    @property
    def translations(self) -> list | None:
        if self._translations is None:
            query = prepareQuery("""
            select ?work ?label
            where {
            ?person crm:P14i_performed ?creation .
            ?creation lrm:R17_created ?expression .
            ?expression lrm:R3_realises ?work .
            ?work rdfs:label ?label .
            }
            """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})
            data = {}
            result = self.graph.query(query, initBindings={'person': self.id})
            if result:
                self._translations = [{"work": str(row.work), "label": str(row.label)} for row in result]

        return self._translations


    def to_dict(self)->dict:
        id = str(self.id)
        key = id.split('/')[-1]
        return {
            "key": key,
            "id": str(self.id),
            "label": self.label,
            "birthDate":  self.birthDate,
            "deathDate": self.deathDate,
            "gender": self.gender,
            "nationality": self.nationality,
            "translations": self.translations
        }



class Translation():
    def __init__(self, graph: Graph, expr: URIRef) -> None:
        self.graph: graph = graph
        self.expr = expr

    def __repr__(self) -> str:
        return f"<Translation: {self.title}>"


    @property
    def work(self):
        return next(self.graph.objects(self.expr, LRM.R3_realises))

    @property
    def title(self):
        work = next(self.graph.objects(self.expr, LRM.R3_realises))
        return next(self.graph.objects(work, RDFS.label))

    @property
    def languages(self):
        return list(self.graph.objects(self.expr, CRM.P72_has_language))

    @property
    def source_languages(self):
        original_expr = next(self.graph.objects(self.expr, LRM.R76i_is_derivative_of))
        # original_language = next(self.graph.objects(original_expr, CRM.P72_has_language))
        # return original_language
        return list(self.graph.objects(original_expr, CRM.P72_has_language))

    @property
    def authors(self):
        query = prepareQuery("""
        SELECT ?person
        WHERE
        {
        ?expr lrm:R76i_is_derivative_of ?original .
        ?original lrm:R17i_was_created_by ?creation .
        ?person crm:P14i_performed ?creation .
        }
        """, initNs = {"lrm": LRM, "crm": CRM})
        result = self.graph.query(query, initBindings={'expr': self.expr})
        return [Person(self.graph, row.person) for row in result]

    @property
    def translators(self):
        q = prepareQuery("""
        SELECT ?person
        WHERE
        {
        ?creation lrm:R17_created ?expr .
        ?person crm:P14i_performed ?creation .
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(q, initBindings={'expr': self.expr})
        return [Translator(self.graph, row.person) for row in result]

    @property
    def pubDate(self):
        graph = self.graph
        issue = next(graph.objects(self.work, LRM.R67i_is_part_of))
        pub_expr = next(graph.objects(issue, LRM.R3i_is_realised_by))
        manifestation = next(graph.objects(pub_expr, LRM.R4i_is_embodied_in))
        manifestation_creation = next(graph.objects(manifestation, LRM.R24i_was_created_by))
        time_span = next(graph.objects(manifestation_creation, CRM.P4_has_time_span))
        date_label = next(graph.objects(time_span, RDFS.label))
        return date_label.toPython()

    @property
    def magazine(self):
        graph = self.graph
        issue = next(graph.objects(self.work, LRM.R67i_is_part_of))
        magazine = next(graph.objects(issue, LRM.R67i_is_part_of))
        # return next(graph.objects(magazine, RDFS.label)).toPython()
        return magazine

    @property
    def issue(self):
        graph = self.graph
        issue = next(graph.objects(self.work, LRM.R67i_is_part_of))
        # return next(graph.objects(issue, RDFS.label)).toPython()
        return issue

    @property
    def genre(self):
        graph = self.graph
        genre = next(graph.objects(self.work, LRM.P2_has_type))
        # return genre.toPython()
        return genre


    def to_dict(self):
        magazine = next(self.graph.objects(self.magazine, RDFS.label))
        issue = next(self.graph.objects(self.issue, RDFS.label))
        s_langs = ";".join([str(next(self.graph.objects(l, RDFS.label)))
                            for l in self.source_languages])
        t_langs = ";".join([str(next(self.graph.objects(l, RDFS.label)))
                            for l in self.languages])

        return {
            "magazine": magazine,
            "issue": issue,
            "pubDate": self.pubDate,
            "author": self.authors[0].names[0],
            "title": self.title,
            "translator": self.translators[0].names[0],
            "genre": self.genre,
            "sl": s_langs,
            "tl": t_langs,
        }




class TranslationOld():
    def __init__(self, graph: Graph, **kwargs):
        self.graph = graph
        self.work = kwargs['trans_work']
        self.expr = kwargs['trans_expr']
        self.original_expr = kwargs['original_expr']
        self._sl = kwargs['sl']
        self._tl = kwargs['tl']
        self._authors = None
        self._translators = None

    @property
    def sl(self):
        return next(self.graph.objects(self._sl, RDFS.label)).toPython()

    @property
    def tl(self):
        return next(self.graph.objects(self._tl, RDFS.label)).toPython()


    @property
    def titles(self):
        labels = self.graph.objects(self.work, RDFS.label)
        return [x.toPython() for x in labels]

    @property
    def languages(self):
        langs = self.graph.objects(self.expr, CRM.P72_has_language)
        labels = []
        for lang in langs:
            labels.append(next(self.graph.objects(lang, RDFS.label)).toPython())
        return labels

    @property
    def authors(self):
        if self._authors is None:
            query = prepareQuery("""
            SELECT ?person
            WHERE
            {
            ?expr lrm:R76i_is_derivative_of ?original .
            ?original lrm:R17i_was_created_by ?creation .
            ?person crm:P14i_performed ?creation .
            }
            """, initNs = {"lrm": LRM, "crm": CRM})
            result = self.graph.query(query, initBindings={'expr': self.expr})
            self._authors = [Person(self.graph, row.person) for row in result]
        return self._authors


    @property
    def translators(self):
        if self._translators is None:
            query = prepareQuery("""
            SELECT distinct ?person
            WHERE
            {
            ?expr lrm:R17i_was_created_by ?creation .
            ?person crm:P14i_performed ?creation .
            }
            """, initNs = {"lrm": LRM, "crm": CRM})
            result = self.graph.query(query, initBindings={'expr': self.expr})
            self._translators = [Person(self.graph, row.person) for row in result]
        return self._translators


    @property
    def pubDate(self):
        graph = self.graph
        issue = next(graph.objects(self.work, LRM.R67i_is_part_of))
        pub_expr = next(graph.objects(issue, LRM.R3i_is_realised_by))
        manifestation = next(graph.objects(pub_expr, LRM.R4i_is_embodied_in))
        manifestation_creation = next(graph.objects(manifestation, LRM.R24i_was_created_by))
        time_span = next(graph.objects(manifestation_creation, CRM.P4_has_time_span))
        date_label = next(graph.objects(time_span, RDFS.label))
        return date_label.toPython()

    @property
    def magazine(self):
        graph = self.graph
        issue = next(graph.objects(self.work, LRM.R67i_is_part_of))
        magazine = next(graph.objects(issue, LRM.R67i_is_part_of))
        return next(graph.objects(magazine, RDFS.label)).toPython()

    @property
    def issue(self):
        graph = self.graph
        issue = next(graph.objects(self.work, LRM.R67i_is_part_of))
        return next(graph.objects(issue, RDFS.label)).toPython()

    @property
    def genre(self):
        graph = self.graph
        genre = next(graph.objects(self.work, LRM.P2_has_type))
        return genre.toPython()


    def to_dict(self):
        return {
            "magazine": self.magazine,
            "issue": self.issue,
            "pubDate": self.pubDate,
            "author": self.authors[0].names[0],
            "title": self.titles[0],
            "translator": self.translators[0].names[0],
            "genre": self.genre,
            "source_language": self.sl,
            "target_language": self.tl
        }



class KnowledgeBase():
    def __init__(self) -> None:
        self.graph = Graph()

    def import_data(self, data:str) -> None:
        try:
            self.graph.parse(data, format="turtle")
        except FileNotFoundError:
            print("couldn't find file")


    def translations(self):
        q = prepareQuery("""
        PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        SELECT ?trans_expr
        WHERE {
        ?trans_expr lrm:R76i_is_derivative_of ?original_expr.
        ?original_expr crm:P72_has_language ?sl .
        ?trans_expr crm:P72_has_language ?tl .
        FILTER (?sl != ?tl) .
        }""",
        initNs = {
            "lrm": "http://iflastandards.info/ns/lrm/lrmer/",
            "crm": "http://www.cidoc-crm.org/cidoc-crm/",
            "rdfs": RDFS,
        })

        results = self.graph.query(q)
        return [Translation(self.graph, row.trans_expr) for row in results]


    def translators(self) -> list:
        q = prepareQuery("""
        PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select distinct ?person where {
        ?expr lrm:R76i_is_derivative_of ?original .
        ?expr lrm:R17i_was_created_by ?creation .
        ?person crm:P14i_performed ?creation .
        ?person rdfs:label ?label .
        }""",
        initNs = {
            "lrm": "http://iflastandards.info/ns/lrm/lrmer/",
            "crm": "http://www.cidoc-crm.org/cidoc-crm/",
            "rdfs": RDFS,
            })

        results = self.graph.query(q)
        return [Translator(self.graph, row.person) for row in results]


    def translator(self, uri: str) -> Translator:
        """Returns data about a translator."""
        uriref = URIRef(uri)
        return Translator(self.graph, uriref)

    
    def magazines(self) -> list:
        q = prepareQuery("""
        SELECT distinct ?magazine
        WHERE
        {
        ?magazine a lrm:F18_Serial_Work .
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(q)
        return [Magazine(self.graph, m.magazine) for m in result]


    def magazine(self, uri) -> Magazine:
        uriref = URIRef(uri)
        return Magazine(self.graph, uriref)
        


    def facets(self):
        """Return facets for UI.

        Useful facets include:
        1. Source & Target Languages
        2. Magazines
        3. Date range
        """
        pass

    def source_language_facet(self):
        query = prepareQuery("""
        SELECT distinct ?sl ?label (count(?sl) as ?n)
        WHERE
        {
        ?translation lrm:R76i_is_derivative_of ?original.
        ?original crm:P72_has_language ?sl .
        ?translation crm:P72_has_language ?tl .
        FILTER (?sl != ?tl) .
        ?sl rdfs:label ?label .
        }
        group by ?label ?sl""",
        initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"lang": row.sl,
                 "label": row.label.toPython(),
                 "count": row.n.toPython()} for row in result]

    def target_language_facet(self):
        query = prepareQuery("""
        SELECT distinct ?tl ?label (count(?tl) as ?n)
        WHERE
        {
        ?translation lrm:R76i_is_derivative_of ?original.
        ?original crm:P72_has_language ?sl .
        ?translation crm:P72_has_language ?tl .
        FILTER (?sl != ?tl) .
        ?tl rdfs:label ?label .
        }
        group by ?label ?tl""",
        initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"lang": row.tl,
                 "label": row.label.toPython(),
                 "count": row.n.toPython()} for row in result]


    def magazine_facet(self):
        query = prepareQuery("""
        SELECT distinct ?magazine ?label
        WHERE
        {
        ?magazine a lrm:F18_Serial_Work .
        ?magazine rdfs:label ?label
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"magazine": row.magazine,
                 "label": row.label.toPython()} for row in result]


    def genre_facet(self):
        query = prepareQuery("""
        SELECT distinct ?genre
        WHERE
        {
        ?work a lrm:F1_Work .
        ?work lrm:P2_has_type ?genre .
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"genre": row.genre.toPython(),
                 "label": row.genre.toPython()} for row in result]


    def pubdate_facet(self):
        query = prepareQuery("""
        select distinct ?label
        where{
        ?mc crm:P4_has_time_span ?span .
        ?span lrm:P82_at_some_time_within ?duration .
	?span rdfs:label ?label} order by ?label""", initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"pubDate": row.label.toPython(),
                 "label": row.label.toPython()} for row in result]






class KnowledgeBaseOld():
    def __init__(self) -> None:
        self.graph = Graph()
        self._translations = None
        self._translators = None
        self._translation_query = prepareQuery("""
        PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT *
        WHERE
        {
        ?trans_expr lrm:R76i_is_derivative_of ?original_expr.
        ?original_expr crm:P72_has_language ?sl .
        ?trans_expr crm:P72_has_language ?tl .
        FILTER (?sl != ?tl) .
        ?trans_expr lrm:R3_realises ?trans_work .
        }""",
        initNs = {
            "lrm": "http://iflastandards.info/ns/lrm/lrmer/",
            "crm": "http://www.cidoc-crm.org/cidoc-crm/",
            "rdfs": RDFS,
            })

        self._translator_query = prepareQuery("""
        PREFIX lrm: <http://iflastandards.info/ns/lrm/lrmer/>
        PREFIX crm: <http://www.cidoc-crm.org/cidoc-crm/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        select distinct ?person where {
        ?expr lrm:R76i_is_derivative_of ?original .
        ?expr lrm:R17i_was_created_by ?creation .
        ?person crm:P14i_performed ?creation .
        ?person rdfs:label ?label .
        }""",
        initNs = {
            "lrm": "http://iflastandards.info/ns/lrm/lrmer/",
            "crm": "http://www.cidoc-crm.org/cidoc-crm/",
            "rdfs": RDFS,
            })


    def import_data(self, data:str) -> None:
        try:
            self.graph.parse(data, format="turtle")
        except FileNotFoundError:
            print("couldn't find file")


    def facets(self):
        """Return facets for UI.

        Useful facets include:
        1. Source & Target Languages
        2. Magazines
        3. Date range
        """
        pass

    def source_language_facet(self):
        query = prepareQuery("""
        SELECT distinct ?sl ?label (count(?sl) as ?n)
        WHERE
        {
        ?translation lrm:R76i_is_derivative_of ?original.
        ?original crm:P72_has_language ?sl .
        ?translation crm:P72_has_language ?tl .
        FILTER (?sl != ?tl) .
        ?sl rdfs:label ?label .
        }
        group by ?label ?sl""",
        initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"lang": row.sl.toPython(),
                 "label": row.label.toPython(),
                 "count": row.n.toPython()} for row in result]

    def target_language_facet(self):
        query = prepareQuery("""
        SELECT distinct ?tl ?label (count(?tl) as ?n)
        WHERE
        {
        ?translation lrm:R76i_is_derivative_of ?original.
        ?original crm:P72_has_language ?sl .
        ?translation crm:P72_has_language ?tl .
        FILTER (?sl != ?tl) .
        ?tl rdfs:label ?label .
        }
        group by ?label ?tl""",
        initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"lang": row.tl.toPython(),
                 "label": row.label.toPython(),
                 "count": row.n.toPython()} for row in result]


    def magazine_facet(self):
        query = prepareQuery("""
        SELECT distinct ?magazine ?label
        WHERE
        {
        ?magazine a lrm:F18_Serial_Work .
        ?magazine rdfs:label ?label
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"magazine": row.magazine.toPython(),
                 "label": row.label.toPython()} for row in result]


    def genre_facet(self):
        query = prepareQuery("""
        SELECT distinct ?genre
        WHERE
        {
        ?work a lrm:F1_Work .
        ?work lrm:P2_has_type ?genre .
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"genre": row.genre.toPython(),
                 "label": row.genre.toPython()} for row in result]


    def pubdate_facet(self):
        query = prepareQuery("""
        select distinct ?label
        where{
        ?mc crm:P4_has_time_span ?span .
        ?span lrm:P82_at_some_time_within ?duration .
	?span rdfs:label ?label} order by ?label""", initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})

        result = self.graph.query(query)
        return [{"pubDate": row.label.toPython(),
                 "label": row.label.toPython()} for row in result]


    def translations(self) -> list:
        if self._translations is None:
            self._translations = []
            results = self.graph.query(self._translation_query)
            for row in results:
                self._translations.append(Translation(self.graph,
                                                      trans_work=row.trans_work,
                                                      trans_expr=row.trans_expr,
                                                      original_expr=row.original_expr,
                                                      sl=row.sl,
                                                      tl=row.tl,
                                                      ))
        return self._translations

    def translators(self) -> list:
        if self._translators is None:
            self._translators = []
            results = self.graph.query(self._translator_query)
            for row in results:
                self._translators.append(Translator(self.graph, row.person))
        return self._translators

    def translator_old(self, uri: URIRef) -> dict:
        """Returns data about a translator."""
        query = prepareQuery("""
        select ?work ?label
        where {
        ?person crm:P14i_performed ?creation .
        ?creation lrm:R17_created ?expression .
        ?expression lrm:R3_realises ?work .
        ?work rdfs:label ?label .
        }
        """, initNs = {"lrm": LRM, "crm": CRM, "rdfs": RDFS})
        data = {}
        result = self.graph.query(query, initBindings={'person': uri})
        if result:
            data = [{"work": str(row.work), "label": str(row.label)} for row in result]
        return data

    def translator(self, uri: str) -> dict:
        """Returns data about a translator."""
        uriref = URIRef(uri)
        return Translator(self.graph, uriref)
