import json

if __name__ == "__main__":
    articles = []
    with open('openalex_articles.json', 'r') as f:
        articles = json.load(f)
    print(articles[0])