import spacy

nlp = spacy.load('en_core_web_sm')


def find_matching_sentences(keywords, articles):
    for a in articles:
        if not a['success']: continue
        sents = []
        doc = nlp(a['text'])
        for sent in doc.sents:
            text = sent.text.lower()
            if any(kw in text for kw in keywords):
                sents.append(sent.text)
        yield a['id'], sents


def extract_entities(articles):
    for a in articles:
        entities = []
        doc = nlp(a['text'])
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_
            })
        yield a['id'], entities
