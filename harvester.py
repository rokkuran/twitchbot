from bot import Bot

import yaml
import csv
import sys

from datetime import datetime


try:
    CHAN = sys.argv[1]
except Exception as e:
    raise e


class Harvester(Bot):
    """"""
    def __init__(self, output_path, verbose=True, **kwargs):
        super(Harvester, self).__init__(**kwargs)
        self.output_path = output_path
        self.verbose = verbose

    def action(self, username, msg):
        if self.verbose:
            print('%s: %s' % (username, msg))

        filepath = '{}/{}.csv'.format(self.output_path, self.channel)
        with open(filepath, 'a', newline='') as f:
            writer = csv.writer(f)
            t = datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S')
            try:
                writer.writerow([t, username, msg])
            except UnicodeEncodeError as e:
                print('\n%s\n' % e)


if __name__ == '__main__':
    # path = '/home/rokkuran/workspace/miscellaneous/twitch/output/'
    path = 'c:/workspace/twitchbot/output/'
    harvester = Harvester(channel=CHAN, output_path=path)
    harvester.run()
