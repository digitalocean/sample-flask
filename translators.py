from pathlib import Path
from flask import Blueprint
from flask import render_template, url_for, request
from forms import LanguageForm, TranslationForm
from kb import KnowledgeBase, Translation, Person, Translator


bp = Blueprint('translators', __name__, url_prefix='/translators')

kb = KnowledgeBase()
kb.import_data(Path("DE_Translations.ttl"))
kb.import_data(Path("DE_Translators.ttl"))

@bp.route('/', methods=('GET', 'POST'))
def index():
    translators: list[Translator] = kb.translators()
    data = [x.to_dict() for x in translators]
    return render_template('translators/index.html',
                           translators=data)
