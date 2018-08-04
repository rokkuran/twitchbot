from bot import Bot

import socket
import re
import yaml

from time import sleep
from collections import Counter

from nltk import word_tokenize
from nltk.corpus import stopwords
from string import punctuation



class CountBot(Bot):
    """"""
    def __init__(self, output_path=None, **kwargs):
        super(CountBot, self).__init__(**kwargs)
        self.output_path = output_path
        self.counts = Counter()
        self.recent = []


    def _update_counts(self, msg):
        tokens = word_tokenize(msg)
        exclusions = stopwords.words('english') + list(punctuation)
        tokens = [x for x in tokens if x not in exclusions]
        self.counts.update(tokens)

        # TODO: make n_recent an argument
        if len(self.recent) >= 200:
            self.recent = self.recent[200:] + tokens
        else:
            self.recent.extend(tokens)

        if self._msg_count % 20 == 0:
            n_top = 10
            recent_counts = Counter(self.recent).most_common(n_top)

            print('\nToken Counts @ msg_count=%s; n_keys=%s; n_counts=%s' \
                % (self._msg_count, len(self.counts), sum(self.counts.values())))

            for x, y in zip(self.counts.most_common(n_top), recent_counts):
                print('%s | %s' % (x, y))


    def action(self, username, msg):
        self._msg_count += 1
        self._update_counts(msg)


if __name__ == '__main__':
    bot = CountBot(channel="#merlinidota")
    bot.run()
