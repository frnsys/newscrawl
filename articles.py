from tqdm import tqdm
from hashlib import md5
from newspaper import Article
from newspaper.article import ArticleException
from concurrent.futures import as_completed, ProcessPoolExecutor


def get_article(d):
    """Fetch an article"""
    id = md5(d['title'].encode('utf8')).hexdigest()
    for s in d['stories']:
        try:
            a = Article(s['url'])
            a.download()
            a.parse()
        except ArticleException:
            continue
        return {
            'id': id,
            'title': d['title'],
            'url': s['url'],
            'text': a.text,
            'html': a.html,
            'success': True
        }
    else:
        return {
            'id': id,
            'title': d['title'],
            'success': False
        }


def get_articles(articles):
    """Fetches article data for multiple articles in parallel"""
    executor = ProcessPoolExecutor()
    jobs = [executor.submit(get_article, a) for a in articles]
    for i, job in tqdm(enumerate(as_completed(jobs)), total=len(jobs)):
        article = job.result()
        yield article
