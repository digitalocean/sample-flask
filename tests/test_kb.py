from kb import KnowledgeBase, Translation


kb = KnowledgeBase()
kb.import_data("https://spatrem-knowledge-graphs.nyc3.digitaloceanspaces.com/DE_Translations.ttl")

def test_translations():
    translations = kb.translations()
    assert translations[0].title.toPython() == 'Ein Neo-Stalinismus?'
    assert translations[0].work is not None
