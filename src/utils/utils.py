import re
from unidecode import unidecode


def replace_special_chars(s):
    #s = s.replace('\\', '\\')
    #s = s.replace('\u00f6', 'o').replace('\u2013', ' ').replace('\u0161', 's').replace('\u00e1', 'a').replace('\u2014', '-')
    #s = s.replace('\u0092', "'").replace('\u00ed', 'i').replace('\u00e8', 'e').replace('\u0092', "'").replace('\u00e9', 'e')
    #s = s.replace('\u00e0', 'a').replace('\u2019', "'").replace('\u2010', '-').replace('\u00b7', '.').replace('\u00fc', 'u')
    #s = s.replace('\u201c', '"').replace('\u201d', '\'').replace('\u2018', "'").replace('\u00f3', 'o').replace('\u0159', 'r')
    #s = s.replace('\u00e4', 'ae').replace('\u00f2', 'o').replace('\u2606', '').replace('\u2026', '...').replace('\u2122', ' tm ')
    #s = s.replace('\u00bd', ' 1/2 ').replace('\uff1a', ':').replace('\u00b0', ' deg ').replace('\u221e', ' infinity ')
    #s = s.replace('\u0107', 'c')
    s = unidecode(s)
    s = s.replace("\"", '\'').replace('\n', ' ')
    return s


def preprocess_term(term):
    #terms = term.split(' ').split('.').split('/').split(',')
    term = replace_special_chars(term)
    terms = re.split('[ .,_:\/]', term)
    for i in range(len(terms)):
        terms[i] = terms[i].replace('[', ' ').replace(']', ' ').replace('"', ' ').replace('&', ' ')
        terms[i] = ''.join(c for c in terms[i] if not c.isdigit())
        terms[i] = terms[i].strip()
    filtered_words = [word.lower() for word in terms if not word.isnumeric()]
    preprocessed_term = ' '.join(filtered_words)
    preprocessed_term = preprocessed_term.strip()
    preprocessed_term = re.sub(r'\s+', ' ', preprocessed_term)
    if 'null' in preprocessed_term or '<' in preprocessed_term:
        return None
    return preprocessed_term

def preprocess_title(title):
    title = replace_special_chars(title)
    return title


def preprocess_term_initial(term):
        filtered_words = [word.lower() for word in term.split(' ') if not word.isnumeric()]
        preprocessed_term = ' '.join(filtered_words)
        return preprocessed_term