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



class MEMM:
    def __init__(self):
        self.train_path = "../data/train"
        self.dev_path = "../data/dev"
        self.beta = 0
        self.max_iter = 0
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
        features['has_(%s)' % current_word] = 1         # has_current_word
        features['prev_label'] = previous_label         # previous label

        # First letter capitalized.
        if current_word[0].isupper():
            features['Titlecase'] = 1

        # ===== TODO: Add your features here ======= #

        """ Libraries """
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
        country_names = [country['name'].upper() for country in gc.get_countries().values()]
        city_names = [city['name'].upper() for city in gc.get_cities().values()]
        stop_words = list(stopwords.words("english"))

        # ---------- Language Matches ---------- #
        # No Letters
        if re.match(r'[\w|\d]+', current_word):
            features['no_letters'] = 1

        # All letters capitalized
        if re.match(r'[A-Z]+$', current_word):
            features['all_capital'] = 1

        # Prefix - A single capital letter followed by a period.
        if re.match(r'[A-Z]\.', current_word):
            features['prefix'] = 1

        # Ends with -ian, -ese
        if re.match(r'ian$|ese$', current_word):
            features['is_nationality'] = 1

        # Score Comparison
        if re.match(r'\d+-\d+', current_word):
            features['is_score_compare'] = 1

        # Precise date
        if re.match(r'\d{4}-\d{2}-\d{2}', current_word):
            features['is_ymd'] = 1

        # Country Name abbreviation: e.g. U.S., U.K., U.S.S.R.,
        if re.match(r'([A-Z]\.){2,4}', current_word):
            features['is_country_abbreviation'] = 1

        # ---------- Library elements ---------- #
        # Is week day
        if current_word.upper() in week_names:
            features['is_weekday'] = 1

        # Is month name
        if current_word.upper() in month_names:
            features['is_month'] = 1

        # Is country name
        if current_word.upper() in country_names:
            features['country'] = 1

        # Is city name
        if current_word.upper() in city_names:
            features['city'] = 1

        # Is stop words
        if current_word in stop_words:
            features['is_stop_word'] = 1

        #=============== TODO: Done ================#
        return features

    def load_data(self, filename):
        words = []
        labels = []
        for line in open(filename, "r", encoding="utf-8"):
            doublet = line.strip().split("\t")
            if len(doublet) < 2:     # remove emtpy lines
                continue
            words.append(doublet[0])
            labels.append(doublet[1])
        return words, labels

    def train(self):
        print('Training classifier...')
        words, labels = self.load_data(self.train_path)
        previous_labels = ["O"] + labels
        features = [self.features(words, previous_labels[i], i)
                    for i in range(len(words))]
        train_samples = [(f, l) for (f, l) in zip(features, labels)]
        classifier = MaxentClassifier.train(
            train_samples, max_iter=self.max_iter)
        self.classifier = classifier

    def test(self):
        print('Testing classifier...')
        words, labels = self.load_data(self.dev_path)
        previous_labels = ["O"] + labels
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
        with open('../model.pkl', 'wb') as f:
            pickle.dump(self.classifier, f)

    def load_model(self):
        with open('../model.pkl', 'rb') as f:
            self.classifier = pickle.load(f)
