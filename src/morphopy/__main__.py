from sys import argv
from lingpy import *
from lingpy import basictypes as bt
from tabulate import tabulate
import networkx as nx
from collections import defaultdict

from morphopy.boundaries import get_boundaries

def check_morphemes(wordlist):
    for idx,  tokens, morphemes in wordlist.iter_rows('tokens','morphemes'):
         morphemes, tokens = (bt.strings(morphemes), bt.lists(tokens))

    etd_mrph = wordlist.get_etymdict(ref='morphemes')
    etd_tkns = wordlist.get_etymdict(ref='tokens')

    for key, values in etd_lect.items():
        data = []
        for v in values:
            if v:
                for idx in v:
                    morpheme = wordlist[idx, 'morpheme']
                    morphemex = morpheme.index(key)
                    token = wordlist[idx, 'tokens'][morphemex]
                    data += [(idx, morphemex, token)]
        tokens = [x[2] for x in data]
        if len(set(tokens)) != 1:
            print('# doculect {0}'.format(key))
            table = []
            for idx, morphemex, token in data:
                table += [[
                    idx,
                    wordlist[idx, 'doculect'],
                    wordlist[idx, 'concept'],
                    bt.lists(wordlist[idx, 'tokens']),
                    bt.lists(wordlist[idx, 'tokens']).n[morphemex],
                    morphemex
                    ]]
            print(tabulate(table, headers=['id', 'doculect', 'concept', 
                'tokens', 'morpheme'], tablefmt='pipe'))
            input()

def check_cogids(wordlist):

    for idx in wordlist:
        for c in ['cogids', 'crossids', 'rootids']:
            wordlist[idx, c] = bt.ints(wordlist[idx, c])

    etd_cogs = wordlist.get_etymdict(ref='cogids')
    etd_crss = wordlist.get_etymdict(ref='crossids')
    etd_root = wordlist.get_etymdict(ref='rootids')

    for key, values in etd_cogs.items():
        data = []
        for v in values:
            if v:
                for idx in v:
                    cogids = wordlist[idx, 'cogids']
                    cogidx = cogids.index(key)
                    crossid = wordlist[idx, 'crossids'][cogidx]
                    data += [(idx, cogidx, crossid)]
        crossids = [x[2] for x in data]
        if len(set(crossids)) != 1:
            print('# cogid {0}'.format(key))
            table = []
            for idx, cogidx, crossid in data:
                table += [[
                    idx,
                    wordlist[idx, 'doculect'],
                    wordlist[idx, 'concept'],
                    bt.lists(wordlist[idx, 'tokens']),
                    bt.lists(wordlist[idx, 'tokens']).n[cogidx],
                    cogidx,
                    crossid
                    ]]
            print(tabulate(table, headers=['id', 'doculect', 'concept', 
                'tokens', 'morpheme', 'cogidx', 'crossid'], tablefmt='pipe'))
            input()



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
            print('## Problems in {0} ({1}, «{2}»):'.format(idx, wordlist[idx,
                'doculect'], wordlist[idx, 'concept']))
            table = []
            for f, s, c in zip(forms, values, columns):
                table += [[c, f, s]]
            print(tabulate(table, headers=['column', 'value', 'length'],
                tablefmt='pipe'))
            print('')
            #input('press ENTER to continue\n')

def word_families(wordlist, morphemes='morphemes'):
    
    wf = defaultdict(list)
    for idx, tokens, morphemes, rootids in wordlist.iter_rows('tokens',
            'morphemes', 'rootids'):
        tokens, morphemes, rootids = (
                bt.lists(tokens), bt.strings(morphemes), bt.ints(rootids)
                )
        wordlist[idx, 'tokens'] = tokens
        wordlist[idx, 'morphemes'] = morphemes
        wordlist[idx, 'rootids'] = rootids

        for tok, morph, rootid in zip(tokens.n, morphemes, rootids):
            if not morph.startswith('_'):
                wf[rootid] += [(idx, str(tok), morph)]

    for rootid, vals in sorted(wf.items(), key=lambda x: len(x[1])):
        
        print('# ROOT {0}'.format(rootid))
        table = []
        for (idx, tok, morph) in sorted(vals, key=lambda x: x[1]):
            table += [[
                idx, 
                wordlist[idx, 'doculect'], 
                wordlist[idx, 'concept'],
                tok,
                morph,
                wordlist[idx, 'tokens'], 
                wordlist[idx, 'morphemes'],
                ]]
        print(tabulate(table, headers=['ID', 'Doculect', 'Concept', 'RootForm',
            'RootConcept', 'Tokens', 
            'Morphemes'], tablefmt='pipe'))
        print('')
    

def main():

    if 'check-length' in argv:
        clidx = argv.index('check-length')+1
        wordlist = Wordlist(argv[clidx])
        columns = argv[clidx+1:]
        check_length(wordlist, columns)

    if 'word-families' in argv:
        clidx = argv.index('word-families')+1
        wordlist = Wordlist(argv[clidx])
        word_families(wordlist)

    if 'check-cogids' in argv:
        clidx = argv.index('check-cogids')+1
        wordlist = Wordlist(argv[clidx])
        check_cogids(wordlist)
        
    if 'check-morphemes' in argv:
        clidx = argv.index('check-morphemes')+1
        wordlist = Wordlist(argv[clidx])
        check_morphemes(wordlist)

    if 'find-morphemes' in argv:
        clidx = argv.index('find-morphemes')+1
        wordlist = Wordlist(argv[clidx])
        language = argv[clidx+1]
        return get_boundaries(wordlist, language)
