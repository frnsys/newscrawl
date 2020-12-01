import json
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

include_entities = False

rows = defaultdict(dict)
sent_counts = {}
with open('data/sentences.jsonl', 'r') as f:
    for line in tqdm(f):
        d = json.loads(line)

        # Avoid identical articles
        sents = '\n'.join([s.strip() for s in d['sents']])
        if sents in sent_counts:
            sent_counts[sents] += 1
            continue
        rows[d['id']]['sentences'] = sents
        sent_counts[sents] = 1

print('Redundant:', sum(1 if s > 1 else 0 for s in sent_counts.values()))

if include_entities:
    columns = ['title', 'sentences', 'entities', 'url']
    with open('data/entities.jsonl', 'r') as f:
         for line in tqdm(f):
             d = json.loads(line)
             if d['id'] not in rows: continue

             # Filter entities to reduce file size and clutter
             entities = [e for e in d['entities'] if e['label'] in ['PERSON', 'ORG']]
             for e in entities:
                 e['text'] = e['text'].strip()
             entities = ['{text} [{label}]'.format(**e) for e in entities]
             entities = set(entities)
             rows[d['id']]['entities'] = ';'.join(entities)
else:
    columns = ['title', 'sentences', 'url']

with open('data/articles.jsonl', 'r') as f:
    for line in tqdm(f):
        a = json.loads(line)
        if not a['success']: continue
        if a['id'] not in rows: continue
        rows[a['id']]['url'] = a['url']
        rows[a['id']]['title'] = a['title']

rows = list(rows.values())
df = pd.DataFrame(rows)
df = df[columns]
df.to_csv('data/articles.csv', index=False)
