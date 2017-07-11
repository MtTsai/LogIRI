#!/usr/bin/env python

__author__ = "Po-Chun Lee(mtk10527)"
__version__ = "0.0.1"
__maintainer__ = "Po-Chun Lee(mtk10527)"
__email__ = "po-chun.lee@mediatek.com"

import re
import fnmatch
import os
import pickle
from multiprocessing.dummy import Pool as ThreadPool
import bisect
import collections

import logging

def list_log_files(path):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*main_log*'):
            matches.append(os.path.join(root, filename))
    return matches

class LogDB:
    def __init__(self):
        self._db = collections.defaultdict(list)

    def dump(self, fname):
        with open(fname, 'wb') as outfile:
            pickle.dump(self._db, fname)

    def load(self, fname):
        with open(fname, 'rb') as outfile:
            self._db = pickle.load(fname)

    def add(self, key, log):
        # TODO (po-chun.lee@mediatek.com): binary insertion
        self._db[key].append(log)

    def search(self, key):
        return self._db[key]

    def sort(self):
        # TODO (po-chun.lee@mediatek.com): To remove after binary insertion supported
        for _logs in self._db.values():
            _logs.sort(key = lambda _ : _.time)
        

class Patterns(object):
    _TIME_PATTERN = r'(\d+-\d+ \d+:\d+:\d+\.\d+) '
    def __init__(self):
        self._patterns = []

    def add(self, pattern):
        self._patterns.append(re.compile('%s(%s)' %(Patterns._TIME_PATTERN, pattern)))
        return len(self._patterns) -1

    def pattern(self, pattern_type_num):
        return self._patterns[pattern_type_num]

    def patterns(self):
        return iter(self._patterns)

    def num(self):
        return len(self._patterns)

    # TODO (po-chun.lee@mediatek.com): return a generator object of 
    # self.patterns 

class Log:
    def __init__(self, time = "", values = [], line = ""):
        self.time = time
        self.values = values
        self.scalar = values[0] if len(values) > 0 else None
        self.entire_line = line

    def nth(self, n):
        return self.values[n] if len(self.values) > n else None
        
class LogParser:

    @staticmethod
    def search_logs(p):
        return map(lambda _ : Log(_[0], _[2:]) if len(_) > 2 else Log(_[0], []), p[0].findall(p[1]))

    def __init__(self, patterns):
        self._db = LogDB()
        self._patterns = patterns

    def parse(self, fnames):
        logging.info('Start to parse log...')
        # TODO (po-chun.lee@mediatek.com): still need to perform refactoring
        # pool = multiprocessing.Pool()
        pool = ThreadPool(8)
        for fname in fnames:
            log_file = file(fname).read()
            for i, parsed_logs in enumerate(pool.map(LogParser.search_logs, map(lambda x: [x, log_file], self._patterns.patterns()))):
                for log in parsed_logs:
                    self._db.add(i, log)
        self._db.sort()
        pool.close()
        pool.join()
        logging.info('Finish parsing')

    def logs_of(self, pattern_index):
        return iter(self._db.search(pattern_index))

    # TODO: add new method to return GENERATOR
    def nth_log_of(self, pattern_index, nth):
        return self._db.search(pattern_index)[nth]

    def prev_log_of(self, pattern_index, log):
        for i, _ in enumerate(self._db.search(pattern_index)):
            if _.time > log.time: break
        return self._db.search(pattern_index)[i - 1]

    def next_log_of(self, pattern_index, log):
        for i, _ in enumerate(self._db.search(pattern_index)):
            if _.time > log.time: break
        return self._db.search(pattern_index)[i]

    def logs_between(self, pattern_index, from_log, end_log):
        first_index = last_index = -1
        for i, _ in enumerate(self._db.search(pattern_index)):
            if _.time > from_log.time and first_index < 0:
                first_index = i - 1
            if _.time > end_log.time:
                last_index = i
                break
        if last_index <= 0: last_index = first_index
        if first_index < 0:
            return []
        else:
            return self._db.search(pattern_index)[first_index:last_index + 1]

    def prev_log_before(self, pattern_index, time):
        log = Log()
        for i, _ in enumerate(self._db.search(pattern_index)):
            if _.time > time:
                if (i > 0):
                    log = self._db.search(pattern_index)[i - 1]
                break
        return log

    def prev_log_after(self, pattern_index, time):
        log = Log()
        for i, _ in enumerate(self.db.search(pattern_index)):
            if _.time > time:
                log = self._db.search(pattern_index)[i]
                break
        return log

    def nth_log_between(self, pattern_index, nth, from_log, end_log):
        first_index = last_index = -1
        for i, _ in enumerate(self._db.search(pattern_index)):
            if _.time > from_log.time and first_index < 0:
                first_index = i - 1
            if _.time > end_log.time:
                last_index = i
                break
        if last_index <= 0: last_index = first_index
        if first_index < 0:
            return None
        else:
            return self._db.search(pattern_index)[first_index:last_index + 1][nth - 1] 
