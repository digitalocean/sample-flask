from pathlib import Path
from flask import Blueprint
from flask import render_template, url_for, request
from forms import LanguageForm, TranslationForm
from kb import KnowledgeBase, Translation
from rdflib import URIRef

bp = Blueprint('translations', __name__, url_prefix='/translations')

kb = KnowledgeBase()
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translations.ttl")
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translators.ttl")

# form = LanguageForm()
source_language_facet = kb.source_language_facet()
target_language_facet = kb.target_language_facet()
magazine_facet = kb.magazine_facet()
genre_facet = kb.genre_facet()
pubdate_facet = kb.pubdate_facet()


@bp.route("/", methods=['GET', 'POST'])
def index():
    translations: list[Translation] = kb.translations()
    form = TranslationForm()

    if request.method == 'POST':

        sl = form.sl.data
        if sl != 'any':
            translations = list(filter(lambda x: sl in map(lambda x: str(x), x.source_languages), translations))

        tl = form.tl.data
        if tl != 'any':
            translations = list(filter(lambda x: tl in map(lambda x: str(x), x.languages), translations))

        magazine = form.magazine.data
        if magazine != 'any':
            translations = list(filter(lambda x: str(x.magazine) == magazine, translations))

        genre = form.genre.data
        if genre != 'any':
            translations = list(filter(lambda x: str(x.genre) == genre, translations))

        before_date = form.before_date.data
        if before_date != 'any':
            translations = list(filter(lambda x:  int(x.pubDate) < int(before_date), translations))

        after_date = form.after_date.data
        if after_date != 'any':
            translations = list(filter(lambda x: int(x.pubDate) > int(after_date), translations))



    form.sl.choices = [(l['lang'], l['label']) for l in source_language_facet]
    form.sl.choices.append(('any', 'any'))

    form.tl.choices = [(l['lang'], l['label']) for l in target_language_facet]
    form.tl.choices.append(('any', 'any'))

    form.magazine.choices = [(m['magazine'], m['label']) for m in magazine_facet]
    form.magazine.choices.append(('any', 'any'))

    form.genre.choices = [(item['genre'], item['label']) for item in genre_facet]
    form.genre.choices.append(('any', 'any'))

    form.after_date.choices = [(item['pubDate'], item['label']) for item in pubdate_facet]
    form.after_date.choices.append(('any', 'any'))

    form.before_date.choices = [(item['pubDate'], item['label']) for item in pubdate_facet]
    form.before_date.choices.append(('any', 'any'))



    start = request.args.get('start', type=int, default=0)
    length = request.args.get('length', type=int, default=10)
    count = len(translations)
    page_count = (count // length)
    current = int((start - 1) / length) + 1

    # data = [x.to_dict() for x in translations[start:start+length]]
    data = [x.to_dict() for x in translations]
    # data = translations
    return render_template("translations/index.html",
                           form=form,
                           translations=data,
                           )

# @bp.route("/", methods=['GET', 'POST'])
# def index():
#     return render_template("translations/index.html",
#                            source_language_facet=source_language_facet,
#                            target_language_facet=target_language_facet,
#                            )


@bp.route("/foo", methods=['GET', 'POST'])
def index_foo():
    language = None
    if request.method == 'POST':
        language = request.form['language']
    form = LanguageForm()
    return render_template('translations/index.html',
                           form=form,
                           language=language,
                           translations=translations,
                           source_language_facet=source_language_facet,
                           target_language_facet=target_language_facet,
                           )

@bp.route("/data", methods=['GET'])
def data():
    translations = kb.translations()
    total = len(translations)
    start = request.args.get('start', type=int, default=0)
    length = request.args.get('length', type=int, default=5)
    slice = translations[start:start+length]
    data_slice = [tr.to_dict() for tr in slice]
    return {"data": data_slice,
            "total": total }
