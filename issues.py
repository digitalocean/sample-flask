from flask import Blueprint
from flask import render_template
from kb import KnowledgeBase, Magazine, Issue
from rdflib.plugins.sparql import prepareQuery
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF


LRM = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


bp = Blueprint('issues', __name__, url_prefix='/issues')

kb = KnowledgeBase()
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translations.ttl")
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translators.ttl")

lookup = {}
for magazine in kb.magazines():
    for issue in magazine.issues:
        data = issue.to_dict()
        lookup[data['key']] = data


@bp.route('/', methods=('GET', 'POST'))
def index():
    issues = [v for k, v in lookup.items()]
    return issues


@bp.route("<issueid>")
def issue(issueid):
    return lookup[issueid]
