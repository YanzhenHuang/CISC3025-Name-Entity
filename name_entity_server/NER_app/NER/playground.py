import nltk
from nltk.corpus import stopwords
from MEM import MEMM

model = MEMM()

model.train()
model.test()

model.show_samples((0, 40))
