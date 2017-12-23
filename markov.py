import numpy as np
import pandas as pd
import nltk
import yaml
import re

import pymongo
from pymongo import MongoClient


class Transition(object):
    """"""
    def __init__(self, key, value):
        super(Transition, self).__init__()
        self.key = key
        self.count = 1
        self.transitions = {value: 1}

    def update(self, value):
        self.count += 1
        if value not in self.transitions:
            self.transitions[value] = 1
        else:
            self.transitions[value] += 1

    @property
    def predict_next(self):
        a = self.transitions.keys()
        p = np.array(self.transitions.values()) / float(self.count)
        return np.random.choice(a=a, size=1, p=p)[0]


class MarkovModel(object):
    def __init__(self, words, order=3, use_pos=False):
        self.cache = {}
        self.words = words
        self.n_words = len(self.words)
        self.order = order
        self.use_pos = use_pos
        self._initialise_cache()

    def _ngrams(self):
        if len(self.words) < self.order:
            return

        for i in xrange(self.n_words - (self.order - 1)):
            words = self.words[i:i + self.order]
            yield tuple(words)

    def _initialise_cache(self):
        for words in self._ngrams():
            key, value = tuple(words[:-1]), words[-1]
            if key not in self.cache:
                self.cache[key] = Transition(key, value)
            else:
                self.cache[key].update(value)

    def _seed_key(self):
        i = np.random.randint(0, self.n_words - self.order)
        words = self.words[i:i + (self.order - 1)]
        return tuple(words)

    def _generate(self, size):
        key = self._seed_key()
        words = list(key)
        for _ in xrange(size - 1):
            v = self.cache[key].predict_next
            words.append(v)
            key = tuple(list(key)[1:] + [v])
        return words

    def _text_post_processing(self, words):
        return ' '.join(words)

    def generate_text(self, size):
        words = self._generate(size)
        return self._text_post_processing(words)


if __name__ == '__main__':
    def get_data(cursor):
        attributes = ['slug', 'synopsis']
        results = []
        for i, x in enumerate(cursor):
            print i, x['slug'], x['averageRating']
            results.append([x[k] for k in attributes])

        df = pd.DataFrame(results, columns=attributes)
        return df

    def test_anime_synopsis(n_synopsis, order):
        client = MongoClient()
        db = client.kitsu
        cursor = db.anime.find()
        df = get_data(cursor)
        words = ' '.join([s for s in df.synopsis.values[-n_synopsis:]]).split()
        hmm = MarkovModel(words, order=order)
        return hmm

    hmm = test_anime_synopsis(n_synopsis=10000, order=4)
    print hmm.generate_text(50)
