from sys import argv
from lingpy import *
from lingpy import basictypes as bt
from tabulate import tabulate

def check_length(wordlist, columns):
    
    types = {
            'morphemes': bt.strings,
            'cogid': int,
            'cogids': bt.ints,
            'crossids': bt.ints,
            'tokens': bt.lists,
            'segments': bt.lists,
            'rootids': bt.ints,
            'alignment': bt.lists
            }

    if len(columns) == len([x for x in wordlist.columns if x in columns]):
        pass
    else:
        for c in columns:
            if c not in wordlist.columns:
                print('[!] column {0} not found in wordlist'.format(c))
        print('[!] ... aborting.')
        return

    for idx in wordlist:
        values, forms = [], []
        for c in columns:
            data = types.get(c, bt.strings)(wordlist[idx, c])
            if hasattr(data, 'n'):
                values += [len(data.n)]
            else:
                values += [len(data)]
            forms += [data]
        if len(set(values)) != 1:
            print('Problems in {0} ({1}, «{2}»):'.format(idx, wordlist[idx,
                'doculect'], wordlist[idx, 'concept']))
            table = []
            for f, s, c in zip(forms, values, columns):
                table += [[c, f, s]]
            print(tabulate(table, headers=['column', 'value', 'length']))
            input('press ENTER to continue')
    

def main():

    if 'check-list' in argv:
        clidx = argv.index('check-list')+1
        wordlist = Wordlist(argv[clidx])
        columns = argv[clidx+1:]
        check_length(wordlist, columns)
