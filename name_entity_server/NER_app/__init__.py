import nltk
import ssl
import platform

DO_NLTK_DOWNLOAD = True
required_nltk_corpuses = ['names', 'stopwords', 'verbnet']


def nltk_download():
    if not DO_NLTK_DOWNLOAD:
        return

    if platform.system() == 'Darwin':
        # I have to disable ssl in case you use Mac computers.
        # Issue: https://github.com/python/cpython/issues/73666
        try:
            _create_unverified_https_context = ssl._create_unverified_context
        except AttributeError:
            pass
        else:
            ssl._create_default_https_context = _create_unverified_https_context

    for corpus in required_nltk_corpuses:
        nltk.download(corpus)


nltk_download()