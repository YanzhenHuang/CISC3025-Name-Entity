import nltk
import ssl

# # Disable ssl in case you use Mac computers.
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#
# nltk.download('names')
# nltk.download('stopwords')