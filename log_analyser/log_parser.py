#!/usr/bin/env python

__author__ = "Po-Chun Lee(mtk10527)"
__version__ = "0.0.1"
__maintainer__ = "Po-Chun Lee(mtk10527)"
__email__ = "po-chun.lee@mediatek.com"

import re
import fnmatch
import os
import multiprocessing

def list_log_files(path):
    matches = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, '*main_log*'):
            matches.append(os.path.join(root, filename))
    return matches

class Patterns(object):
    _TIME_PATTERN = r'(\d+-\d+ \d+:\d+:\d+\.\d+) '
    def __init__(self):
        self._patterns = []

    def add(self, pattern):
        self._patterns.append(re.compile('%s(%s)' %(Patterns._TIME_PATTERN, pattern)))
        return len(self._patterns) -1

    def pattern(self, pattern_type_num):
        return self._patterns[pattern_type_num]

    def patternsa(self):
        return self._patterns
    def num(self):
        return len(self._patterns)

    # TODO (po-chun.lee@mediatek.com): return a generator object of 
    # self.patterns 

class Log:
    def __init__(self, time = "", values = []):
        self.time = time
        self.values = values
        self.scalar = values[0] if len(values) > 0 else None

    def nth(self, n):
        return self.values[n] if len(self.values) > n else None
def f(p):
    return p[0].findall(p[1])
        
class LogParser:
    def __init__(self, path, patterns):
        self.db = {}
        for i in range(patterns.num()):
            self.db[i] = []
        for fname in list_log_files(path):
            self.parse(fname, patterns)
        for i in range(patterns.num()):
            self.db[i].sort(key = lambda _ : _.time)
    
    def parse(self, fname, patterns):
        print "Start to parse log [%s]..." %(fname)
        # TODO (po-chun.lee@mediatek.com): still need to perform refactoring
        log_file = file(fname).read()
        pool = multiprocessing.Pool()
        for i, parsed_logs in enumerate(pool.map(f, map(lambda x: [x, log_file], patterns.patternsa()))):
            self.db[i] += map(lambda _ : Log(_[0], _[2:]) if len(_) > 2 else Log(_[0], []), parsed_logs)
        
        print "Finish parsing"

    # TODO: add new method to return GENERATOR
    def nth_log_of(self, pattern_index, nth):
        return self.db[pattern_index][nth]
    
    def prev_log_of(self, pattern_index, log):
        for i, _ in enumerate(self.db[pattern_index]):
            if _.time > log.time: break
        return self.db[pattern_index][i - 1]
    
    def next_log_of(self, pattern_index, log):
        for i, _ in enumerate(self.db[pattern_index]):
            if _.time > log.time: break
        return self.db[pattern_index][i]

    def logs_between(self, pattern_index, from_log, end_log):
        first_index = last_index = -1
        for i, _ in enumerate(self.db[pattern_index]):
            if _.time > from_log.time and first_index < 0:
                first_index = i - 1
            if _.time > end_log.time:
                last_index = i
                break
        if last_index <= 0: last_index = first_index
        if first_index < 0:
            return []
        else:
            return self.db[pattern_index][first_index:last_index + 1]
    
    def prev_log_before(self, pattern_index, time):
        log = Log()
        for i, _ in enumerate(self.db[pattern_index]):
            if _.time > time:
                if (i > 0):
                    log = self.db[pattern_index][i - 1]
                break
        return log
    
    def prev_log_after(self, pattern_index, time):
        log = Log()
        for i, _ in enumerate(self.db[pattern_index]):
            if _.time > time:
                log = self.db[pattern_index][i]
                break
        return log

    def nth_log_between(self, pattern_index, nth, from_log, end_log):
        first_index = last_index = -1
        for i, _ in enumerate(self.db[pattern_index]):
            if _.time > from_log.time and first_index < 0:
                first_index = i - 1
            if _.time > end_log.time:
                last_index = i
                break
        if last_index <= 0: last_index = first_index
        if first_index < 0:
            return None
        else:
            return self.db[pattern_index][first_index:last_index + 1][nth - 1] 
