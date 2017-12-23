from bot import Bot
from markov import MarkovModel

import numpy as np
import re
import csv
import random
import nltk
import yaml

from time import sleep
from datetime import datetime


class MarkovTwitch(MarkovModel):
    def _punctuation_fix(self, text):
        return re.sub(r'\s([?.!"](?:\s|$))', r'\1', text)

    def _at_fix(self, text):
        return re.sub(r'(?<=\()\s+(?=[^\W_])', text)

    def _space_after_emote_fix(self, text):
        path = '/home/rokkuran/workspace/miscellaneous/twitch/'
        emotes = yaml.load(open(path + 'emotes.yml', 'rb'))['emotes_official']
        a = [s for s in emotes if s in text]
        for emote in a:
            text = text.replace('%s.' % emote, '%s ' % emote)
        return text

    def _text_post_processing(self, gen_words):
        if self.use_pos:
            text = ' '.join(np.array(gen_words)[:, 0].tolist())
        else:
            text = ' '.join(gen_words)
        text = self._punctuation_fix(text)
        text = self._space_after_emote_fix(text)
        return text


class MarkovEchoBot(Bot):
    """"""
    def __init__(self, n_words=10000, markov_max_length=6, history_path=None,
                 output_path=None, verbose=False, **kwargs):
        super(MarkovEchoBot, self).__init__(**kwargs)
        self.n_words = n_words
        self.markov_max_length = markov_max_length
        self.output_path = output_path
        self.verbose = verbose

        self.words = []

    def _write_bot_msg(self, msg):
        args = (self.output_path, self.channel, self._nickname)
        filepath = '%s/%s_%s.csv' % args
        with open(filepath, 'ab') as f:
            try:
                writer = csv.writer(f)
                time_format = '%Y-%m-%d %H:%M:%S'
                t = datetime.strftime(datetime.now(), time_format)
                writer.writerow([t, self._nickname, msg])
            except UnicodeEncodeError as e:
                print '\n\n%s\n\n' % e

    def _update_words(self, msg):
        if len(self.words) < self.n_words:
            self.words.extend(msg.split())
        else:
            for word in msg.split():
                self.words.pop(0)
                self.words.append(word)

    def generate_spam(self, words):
        spammer = MarkovTwitch(words)
        spam_length = np.random.randint(1, self.markov_max_length)
        spam = spammer.generate_text(spam_length)
        if self.verbose:
            print '\n\n%s\n%s\n%s\n\n' % ('*' * 75, spam, '*' * 75)
        return spam

    def _spam_chat_write(self, words):
        spam = self.generate_spam(words)

        if self.output_path:
            self._write_bot_msg(spam)

        # self.chat(spam)  # send message to irc
        self._msg_count = 0  # reset message count

    def action(self, username, msg):
        if self.verbose:
            print '%s: %s' % (username, msg)

        self._update_words(msg)
        self._msg_count += 1

        if (self._msg_count % 50 == 0) & (len(self.words) >= 100):
            self._spam_chat_write(self.words)


if __name__ == '__main__':
    path = '/home/rokkuran/workspace/miscellaneous/twitch/output/'

    markov_echo_bot = MarkovEchoBot(
        channel='#merlinidota',
        output_path=path,
        markov_max_length=10,
        verbose=True)
    markov_echo_bot.run()
