import nltk
from nltk.corpus import stopwords

stop_words = [word.upper() for word in list(stopwords.words("english"))]
print(stop_words)