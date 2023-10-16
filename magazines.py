from flask import Blueprint
from flask import render_template
from kb import KnowledgeBase, Translation
from rdflib.plugins.sparql import prepareQuery
from rdflib import Graph, URIRef, Namespace, Literal
from rdflib.namespace._RDFS import RDFS
from rdflib.namespace._RDF import RDF


LRM = Namespace("http://iflastandards.info/ns/lrm/lrmer/")
CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")


bp = Blueprint('magazines', __name__, url_prefix='/magazines')

kb = KnowledgeBase()
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translations.ttl")
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translators.ttl")

lookup = {}
for magazine in kb.magazines():
    data = magazine.to_dict()
    lookup[data['key']] = data


@bp.route('/', methods=('GET', 'POST'))
def index():
    magazines = [m.to_dict() for m in kb.magazines()]
    return render_template('magazines/index.html',
                               magazines=magazines)


@bp.route("<magid>")
def issues_of(magid):
    uriref = lookup[magid]['id']
    data = kb.magazine(uriref)
    return data.to_dict()
