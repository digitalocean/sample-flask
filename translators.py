from pathlib import Path
from flask import Blueprint
from flask import render_template, url_for, request
from forms import LanguageForm, TranslationForm
from kb import KnowledgeBase, Translation, Person, Translator, PERSON
from rdflib import URIRef


bp = Blueprint('translators', __name__, url_prefix='/translators')

kb = KnowledgeBase()
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translations.ttl")
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translators.ttl")

translators: list[Translator] = kb.translators()

lookup = {}
for x in translators:
    data = x.to_dict()
    key = data['key']
    lookup[key] = data


@bp.route('/', methods=('GET', 'POST'))
def index():
    data = [x.to_dict() for x in translators]
    return render_template('translators/index.html',
                           translators=data)

@bp.route("/<personid>")
def translations_by(personid):
    uriref = URIRef(lookup[personid]['id'])
    # return hit.to_dict()
    # return hit
    data = kb.translator(uriref)
    return data.to_dict()
