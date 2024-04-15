#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# --------------------------------------------------
# Description:
# --------------------------------------------------
# Author: Konfido <konfido.du@outlook.com>
# Created Date : April 4th 2020, 17:45:05
# Last Modified: April 4th 2020, 17:45:05
# --------------------------------------------------
import re
import os
import pickle
import geonamescache

# NLP Packages
import nltk.sem.chat80
from nltk.corpus import stopwords, verbnet
from nltk.classify.maxent import MaxentClassifier
from sklearn.metrics import (accuracy_score, fbeta_score, precision_score,
                             recall_score)
from nltk.corpus import names
from nltk.stem import PorterStemmer

p_stemmer = PorterStemmer()

""" Libraries for feature selection """
gc = geonamescache.GeonamesCache()
week_names = [
    'MONDAY',
    'TUESDAY',
    'WEDNESDAY',
    'THURSDAY',
    'FRIDAY',
    'SATURDAY',
    'SUNDAY',
    'MON',
    'TUE',
    'WED',
    'THU',
    'FRI',
    'SAT',
    'SUN'
]
month_names = [
    'JANUARY',
    'FEBRUARY',
    'MARCH',
    'APRIL',
    'MAY',
    'JUNE',
    'JULY',
    'AUGUST',
    'SEPTEMBER',
    'OCTOBER',
    'NOVEMBER',
    'DECEMBER',
    'JAN',
    'FEB',
    'MAR',
    'APR',
    'MAY',
    'JUN',
    'JUL',
    'AUG',
    'SEP',
    'OCT',
    'NOV',
    'DEC'
]

country_names = [country['name'].upper() for country in gc.get_countries().values()] if gc else []
country_names.extend(['REPUBLIC', 'KINGDOM', 'UNITED', 'STATES'])

city_names = [city['name'].upper() for city in gc.get_cities().values()] if gc else None
stop_words = list(stopwords.words("english"))
verbs = [p_stemmer.stem(word)for word in verbnet.lemmas()]
stored_names = names.words('male.txt') + names.words('female.txt')

""" Match Patterns """
pattern_features = {

    # + Start with Capital-lowercase, and the rest letters are lowercase.
    'p_cap_low': re.compile(r'^[A-Z](\'[A-Z]?|[a-z][A-Z])?[a-z]+'),

    # + Single capital letter followed by a period. e.g. D., L., ... Initials of human name.
    'p_cap_period': re.compile(r'^[A-Z]\.$'),

    # - Noun suffixes. e.g. option, movement, tidiness, friendship, childhood, usage, allowance.
    'p_noun_like': re.compile(r'(([aio]?tion|ment|ness|ship|hood|\w+age|[ae]nce)[sd]?$)/i'),

}

"""
- Person status prefix.      e.g. Mr., Ms., Mrs., ...
'p_name_prefix': re.compile(r'M[a-z]{1,3}\.'),

- All capital letters.
'p_all_cap': re.compile(r'^[A-Z]+$'),
# - Possessive case. e.g. 's, ....
'p_possessive_like': re.compile(r'\'s$'),

# - Location name abbreviation. U.S., U.K., D.C.,  ...
'p_country_abbrev_like': re.compile(r'([A-Z]\.){2,3}'),

# - Numeric expressions.
'p_num_slash': re.compile(r'(\d+-)+\d+|\+\d+|\d+|\d+\.\d+'),

No vowels is good, but it is not too common in actual use.
"""


class MEMM:
    def __init__(self):
        self.train_path = "data/train"
        self.dev_path = "data/dev"
        self.beta = 0.5  # Used for f-score evaluation
        self.max_iter = 5
        self.classifier = None

    def features(self, words, previous_label, position):
        """
        Note: The previous label of current word is the only visible label.

        :param words: a list of the words in the entire corpus
        :param previous_label: the label for position-1 (or O if it's the start
                of a new sentence)
        :param position: the word you are adding features for
        """

        def is_something_else():
            non_name_bool = (
                # Week names: Monday, Tuesday, ...
                current_word.upper() in week_names or
                # Month Names: January, February, ...
                current_word.upper() in month_names or

                # Is location name: Country + City. "China" matches "People's Republic of China"
                any(current_word.upper() in country_name for country_name in country_names) or

                current_word.upper() in city_names or

                # Stop words: prep, adj, ...
                current_word in stop_words
            )
            return non_name_bool

        features = {}
        """ Baseline Features """
        current_word = words[position]
        features['has_(%s)' % current_word] = 1  # has_current_word
        features['prev_label'] = previous_label  # previous label

        # First letter capitalized.
        if current_word[0].isupper():
            features['p_all_capital'] = 1

        # ===== TODO: Add your features here ======= #

        # ---------- Pattern Features ---------- #
        for feature_name, feature_pattern in pattern_features.items():
            if re.match(feature_pattern, current_word):
                features[feature_name] = 1

        # ---------- Library Features ---------- #
        # Is in name list. Usefulness proved.
        if current_word in stored_names:
            features['is_in_name_list'] = 1

        # - Tend not to be names
        if is_something_else():
            features['is_sth_else'] = 1

        # --------- Contextual Features --------- #
        human_status = ['Mr.', 'Ms.', 'Mrs.', 'Dr.', 'Prof.']

        # Is the start of a sentence
        if (position > 0 and words[position - 1] == '.') or position == 0:
            features['is_start_of_sentence'] = 1

        # + Is target of restricted attribute clause. Usefulness proved.
        if (
            (position < len(words) - 2 and words[position+1] == "," and (words[position+2] == "who" or words[position+2] == "whose")) or
            (position < len(words) - 3 and words[position+2] == "," and (words[position+3] == "who" or words[position+3] == "whose"))
        ):
            features['is_target_of_clause'] = 1

        # + Is after Mr., Ms., Mrs., Dr., Prof.
        if position > 0 and words[position - 1] in human_status:
            features['is_after_status'] = 1

        # + Is before a verb: This feature plays a negative role! Don't add it.
        #if position < len(words) - 1 and p_stemmer.stem(words[position + 1]) in verbs:
        #    features['is_after_verb'] = 1

        """
                if previous_label == 'PERSON':
            features['is_previous_person'] = 1

        if previous_label == 'O':
            features['is_previous_other'] = 1

        # ------------- Position Related -------------
        Is around the first place in a sentence.
        if (position > 0 and words[position-1] == ".") or (position > 1 and words[position-2] == "."):
            features['is_around_first'] = 1

        Is the last word
        if position == len(words) - 1:
            features['is_last_word'] = 1



        # Is after name prefix
        if position < len(words) - 1 and re.match(r'M[a-z]{1,3}\.', words[position-1]):
            features['is_after_name_prefix'] = 1

        + Is in possessive case
        if position < len(words) -1 and words[position+1] == "'s":
            features['is_possessive'] = 1

        if words[position+1] == "verb":
            features['is_after_verb'] = 1

        if words[position - 1] in stop_words:
            features['is_after_stop_word'] = 1

        if not position >= len(words) - 1 and words[position + 1] in stop_words:
            features['is_before_stop_word'] = 1
        """

        # =============== TODO: Done ================#
        return features

    def load_data(self, filename):
        words = []
        labels = []
        for line in open(filename, "r", encoding="utf-8"):
            doublet = line.strip().split("\t")
            if len(doublet) < 2:  # remove emtpy lines
                continue
            words.append(doublet[0])
            labels.append(doublet[1])
        return words, labels

    def train(self):
        print('Training classifier...')
        # Load word-labels
        words, labels = self.load_data(self.train_path)
        previous_labels = ["O"] + labels

        # Extract Features for all words
        features = [self.features(words, previous_labels[i], i)
                    for i in range(len(words))]

        # Pack word-features to train-samples
        train_samples = [(f, l) for (f, l) in zip(features, labels)]
        classifier = MaxentClassifier.train(
            train_samples, max_iter=self.max_iter)

        # Get weights for all features
        self.classifier = classifier
        print(classifier)

    def test(self):
        print('Testing classifier...')
        # Load word-labels
        words, labels = self.load_data(self.dev_path)
        previous_labels = ["O"] + labels

        # Extract Features for all words
        features = [self.features(words, previous_labels[i], i)
                    for i in range(len(words))]
        results = [self.classifier.classify(n) for n in features]

        f_score = fbeta_score(labels, results, average='macro', beta=self.beta)
        precision = precision_score(labels, results, average='macro')
        recall = recall_score(labels, results, average='macro')
        accuracy = accuracy_score(labels, results)

        print("%-15s %.4f\n%-15s %.4f\n%-15s %.4f\n%-15s %.4f\n" %
              ("f_score=", f_score, "accuracy=", accuracy, "recall=", recall,
               "precision=", precision))

        return True

    def show_samples(self, bound):
        """Show some sample probability distributions.
        """
        words, labels = self.load_data(self.train_path)
        previous_labels = ["O"] + labels
        features = [self.features(words, previous_labels[i], i)
                    for i in range(len(words))]
        (m, n) = bound
        pdists = self.classifier.prob_classify_many(features[m:n])

        print('  Words          P(PERSON)  P(O)\n' + '-' * 40)
        for (word, label, pdist) in list(zip(words, labels, pdists))[m:n]:
            if label == 'PERSON':
                fmt = '  %-15s *%6.4f   %6.4f'
            else:
                fmt = '  %-15s  %6.4f  *%6.4f'
            print(fmt % (word, pdist.prob('PERSON'), pdist.prob('O')))

    def dump_model(self):
        model_pkl_path = os.path.abspath('../../name_entity_server/static/model.pkl').replace('\\', '/')
        with open(model_pkl_path, 'wb') as f:
            pickle.dump(self.classifier, f)

    def load_model(self):
        model_pkl_path = os.path.abspath('../../name_entity_server/static/model.pkl').replace('\\', '/')
        with open(model_pkl_path, 'rb') as f:
            self.classifier = pickle.load(f)

    # Predict the single entity.
    def predict_entities(self, sentence):
        punctuation = [',', '?', '!']

        def split_words_with_punctuation(_words):
            updated_words = []
            for _word in _words:
                if (len(_word) > 3 and _word[-1] == ".") or _word[-1] in punctuation:
                    _punc = _word[-1]
                    _word = _word.rstrip(_word[-1])
                    updated_words.append(_word)
                    updated_words.append(_punc)
                else:
                    updated_words.append(_word)

            return updated_words

        # Pre-process
        _words = sentence.split()
        token_list = split_words_with_punctuation(_words)

        # Initialize the previous label to be 'O'
        previous_label = 'O'

        # Classify each label
        predicted_labels = []
        for position, word in enumerate(token_list):
            features = self.features(token_list, previous_label, position)
            predicted_label = self.classifier.classify(features)  # Decide the label
            predicted_labels.append(predicted_label)
            previous_label = predicted_label

        return predicted_labels, token_list
