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
import pycountry
import geonamescache

# NLP Packages
import nltk.sem.chat80
from nltk.corpus import stopwords
from nltk.classify.maxent import MaxentClassifier
from sklearn.metrics import (accuracy_score, fbeta_score, precision_score,
                             recall_score)
from nltk.corpus import names

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
stored_names = names.words('male.txt') + names.words('female.txt')

""" Match Patterns """
pattern_features = {

    # + Start with Capital-lowercase, and the rest letters are lowercase.
    'p_cap_low': re.compile(r'[A-Z](\'|[A-Z])?[a-z]+'),

    # + Single capital letter followed by a period. e.g. D., L., ... Initials of human name.
    'p_cap_period': re.compile(r'^[A-Z]\.$'),

    # - Person status prefix.      e.g. Mr., Ms., Mrs., ...
    'p_name_prefix': re.compile(r'M[a-z]{1,3}\.'),

    # - All capital letters.
    'p_all_cap': re.compile(r'^[A-Z]+$'),

    # - Noun suffixes. e.g. option, movement, tidiness, friendship, childhood, usage, allowance.
    'p_noun_like': re.compile(r'(([aio]?tion|ment|ness|ship|hood|\w+age|[ae]nce)s?$)/i'),

    # - Possessive case. e.g. 's, ....
    'p_possessive_like': re.compile(r'\'s$'),

    # - Location name abbreviation. U.S., U.K., D.C.,  ...
    'p_country_abbrev_like': re.compile(r'([A-Z]\.){2,3}'),

    # - Numeric expressions.
    'p_num_slash': re.compile(r'(\d+-)+\d+|\+\d+|\d+|\d+\.\d+'),

    # "No vowels" is good, but it is not too common in actual use.

}


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

        features = {}
        """ Baseline Features """
        current_word = words[position]
        features['has_(%s)' % current_word] = 1  # has_current_word
        features['prev_label'] = previous_label  # previous label

        # First letter capitalized.
        if current_word[0].isupper():
            features['p_all_capital'] = 1

        # ===== TODO: Add your features here ======= #

        # ---------- Language Matches ---------- #
        for feature_name, feature_pattern in pattern_features.items():
            if re.match(feature_pattern, current_word):
                features[feature_name] = 1

        # ---------- Library elements ---------- #
        # Is in name list
        if current_word in stored_names:
            features['is_in_name_list'] = 1

        # Is week day
        if current_word.upper() in week_names or current_word.upper() in month_names:
            features['is_time'] = 1

        # Is location name: Country + City
        # "China" matches "People's Republic of China"
        if (
                any(current_word.upper() in country_name for country_name in country_names) or
                current_word.upper() in city_names
        ):
            features['is_location'] = 1

        # Is stop words
        if current_word in stop_words:
            features['is_stop_word'] = 1

        # if previous_label == 'PERSON':
        #     features['is_previous_person'] = 1

        if previous_label == 'O':
            features['is_previous_other'] = 1

        # # ------------- Position Related -------------
        if words[position-1] == "." or words[position-2] == ".":
            features['is_around_first'] = 1

        if position == len(words) - 1:
            features['is_last_word'] = 1

        if position < len(words) - 2 and words[position+1] == "," and words[position+2] == "who":
            features['is_target_of_claus'] = 1

        # if words[position+1] == "verb":
        #     features['is_after_verb'] = 1

        # if words[position - 1] in stop_words:
        #     features['is_after_stop_word'] = 1
        #
        # if not position >= len(words) - 1 and words[position + 1] in stop_words:
        #     features['is_before_stop_word'] = 1



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
        # def tokenize_sentence(_sentence):
        #     tokenizer = nltk.tokenize.RegexpTokenizer(r'[\s]+', gaps=True)
        #
        #     # Unify Punctuation
        #     _sentence = re.sub(r'\"|\.\.+|\(|\)|\s--+\s|(?<=[A-Za-z])/|&[a-z]+;|>', ' ', _sentence)
        #     _sentence = re.sub(r'(?<![A-Z])([.,?!"]\s+)', ' ', _sentence)
        #
        #     # Tokenize using unified punctuation
        #     _token_array = tokenizer.tokenize(_sentence)
        #
        #     # Post-process
        #     token_array = []
        #     for token in _token_array:
        #         token = token.rstrip(',?!"-.')
        #         token = token.lower()
        #         token_array.append(token) if token != "-" or "" else None
        #
        #     return token_array

        # Pre-process
        words = sentence.split()
        # words = tokenize_sentence(sentence)

        # Initialize the previous label to be 'O'
        previous_label = 'O'

        # Classify each label
        predicted_labels = []
        for position, word in enumerate(words):
            features = self.features(words, previous_label, position)
            predicted_label = self.classifier.classify(features)  # Decide the label
            predicted_labels.append(predicted_label)
            previous_label = predicted_label

        return predicted_labels



        # # McArthur Style
        # if re.match(r'(^[A-Z][a-z][A-Z])[A-Za-z]+', current_word):
        #     features['p_mcarthur_style'] = 1
        #
        # # O'Brien Style
        # if re.match(r'^O\'[A-Z][A-Za-z]+', current_word):
        #     features['p_o_prime_style'] = 1
        #
        # # No Letters
        # if re.match(r'[\W|\d]+', current_word):
        #     features['p_no_letters'] = 1

        # # End letters capitalized
        # if re.match(r'[A-Z]+$', current_word):
        #     features['p_ends_capital'] = 1

        # # All characters are letters
        # if re.match(r'[A-Za-z]+', current_word):
        #     features['p_all_letters'] = 1

        # # All characters are lowercase
        # if re.match(r'[a-z]+$', current_word):
        #     features['p_all_lower'] = 1

        # # Camel case
        # if re.match(r'^[a-z]+(?:[A-Z][a-z]*)*$', current_word):
        #     features['p_camel'] = 1

        # Prefix - First letter cap, then lower. e.g. D., S., Mr., Ms.,...
        # if re.match(r'[A-Z][a-z]{1,3}\.', current_word):
        #     features['p_prefix'] = 1

        # # Special Suffix
        # if re.match(r'ian$|ese$|sh$', current_word):
        #     features['p_nationality_like'] = 1
        # elif re.match(r'ist$|th$', current_word):
        #     features['p_special_suffix'] = 1
        # elif re.match(r'\'s$', current_word):
        #     features['p_possessive_case'] = 1
        # elif re.match(r'([aio]?tion$|ment$|ness$|ship$|\w+age$|[ae]nce$)/i', current_word):
        #     features['p_noun_like'] = 1

        # Score Comparison
        # if re.match(r'\d+-\d+', current_word):
        #     features['p_score_compare'] = 1
        #
        # # Precise date
        # if re.match(r'\d{4}-\d{2}-\d{2}', current_word):
        #     features['p_ymd'] = 1
        #
        # # Country Name abbreviation: e.g. U.S., U.K., U.S.S.R.,
        # if re.match(r'([A-Z]\.){2,5}', current_word):
        #     features['p_country_abbreviation'] = 1