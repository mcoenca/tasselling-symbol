#!/usr/bin/env python3

import re
import codecs

def main():
    films = dict()
    patternstr = '^ +([0-9.*]+) +([0-9]+) +([0-9]?[0-9][.][0-9]) +(".*"|.*) +\(.....*\) *({.*}|\(.*\)|)$'
    pattern = re.compile(patternstr)
    with codecs.open('ratings.list', 'r', 'latin1') as f:
        for line in f:
            tokens = pattern.findall(line)
            tokens = tokens[0]
            votes = int(tokens[1])
            title = tokens[3]
            if title[0] == '"':
                title = title[1:-1]
            oldvotes = films.get(title, -1)
            if oldvotes < votes:
                films[title] = votes
    numfilms = len(films)
    sorted_films = sorted(films.items(), key = lambda tup : -tup[1])
    for title,count in sorted_films[:20000]:
        print(title)

if __name__ == '__main__':
    main()