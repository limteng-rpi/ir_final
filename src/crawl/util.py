import os


def load_seed_urls(name, dir='seed'):
    """Load a list of seed URLs from file"""
    seed_file = os.path.join(os.path.dirname(__file__), dir, '{}.txt'.format(name))
    urls = open(seed_file, 'r', encoding='utf-8').read().split('\n')
    urls = [l.strip() for l in urls if l.strip()]
    print(urls)
    return urls