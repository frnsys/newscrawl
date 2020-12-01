import config
import mediacloud.api
from tqdm import tqdm

mc = mediacloud.api.MediaCloud(config.MEDIACLOUD_API_KEY)


def count_stories(query, date_range):
    """Count the number of stories matching a query"""
    res = mc.storyCount(query, solr_filter=mc.publish_date_query(*date_range))
    return res['count']


def search_stories(query, date_range, last_story_id=0, fetch_size=1000):
    """Search MediaCloud for a query"""
    stories = []
    bar = tqdm(desc=query)
    while True:
        new_stories = mc.storyList(query,
                                       solr_filter=mc.publish_date_query(*date_range),
                                       last_processed_stories_id=last_story_id,
                                       rows=fetch_size)
        stories.extend(new_stories)
        last_story_id = stories[-1]['processed_stories_id']
        bar.update(len(new_stories))
        if len(new_stories) < fetch_size:
            break
    return stories, last_story_id


if __name__ == '__main__':
    import json
    from . import nlp
    from .articles import get_articles
    from collections import defaultdict

    common_delimiters = ['|', '::', '- FOX']

    # Load existing story ids, if any
    try:
        with open('data/last_story_ids.json', 'r') as f:
            last_story_ids = json.load(f)
    except FileNotFoundError:
        last_story_ids = {}

    new_stories = []
    for q in config.queries:
        print('Query:', q)
        last_story_id = last_story_ids.get(q, 0)
        stories, last_story_id = search_stories(
                q, (config.START_DATE, config.END_DATE),
                last_story_id=last_story_id)

        for s in stories:
            s['query'] = q
        new_stories += stories

        # Save story data
        print('>', len(stories), 'new stories')
        with open('data/stories.jsonl', 'a') as f:
            lines = [json.dumps(s) for s in stories]
            f.write('\n'.join(lines)+'\n')

        # Keep track of last story seen for this query
        # to avoid duplicates
        last_story_ids[q] = last_story_id
        with open('data/last_story_ids.json', 'w') as f:
            json.dump(last_story_ids, f)

    # Get full article data
    titles = defaultdict(list)
    for s in new_stories:
        # Only working with English-language results here
        if s['language'] != 'en': continue

        # Extract title, and try to clean up a little
        title = s['title']
        for d in common_delimiters:
            title = title.split(d)[0].strip()
        titles[title].append(s)

    print(sum(len(v) for v in titles.values()))
    print(len(titles))

    # Load existing titles
    # We assume that articles with identical titles
    # are duplicates
    try:
        existing_titles = set()
        with open('data/articles.jsonl', 'r') as f:
            for l in f.read().splitlines():
                a = json.loads(l)
                existing_titles.add(a['title'])
    except FileNotFoundError:
        existing_titles = set()
    remaining = [{'title': t, 'stories': vs} for t, vs in titles.items() if t not in existing_titles]

    # Get the article data and save each to disk
    articles = []
    for article in get_articles(remaining):
        with open('data/articles.jsonl', 'a') as f:
            f.write(json.dumps(article)+'\n')
        if article['success']:
            articles.append(article)

    # Find sentences matching specified keywords, for skimming articles
    try:
        with open('data/sentences.jsonl', 'r') as f:
            completed = {json.loads(l)['id'] for l in f}
    except FileNotFoundError:
        completed = set()

    for a_id, sents in nlp.find_matching_sentences(config.KEYWORDS, articles):
        with open('data/sentences.jsonl', 'a') as f:
            d = json.dumps({
                'id': a_id,
                'sents': sents
            })
            f.write(d + '\n')

    try:
        with open('data/entities.jsonl', 'r') as f:
            completed = {json.loads(l)['id'] for l in f}
    except FileNotFoundError:
        completed = set()

    for a_id, entities in nlp.extract_entities(articles):
        with open('data/entities.jsonl', 'a') as f:
            d = json.dumps({
                'id': a_id,
                'entities': entities
            })
            f.write(d + '\n')