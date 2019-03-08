from sys import argv
from lingpy import *
from lingpy import basictypes as bt
from tabulate import tabulate
import networkx as nx
from collections import defaultdict

from morphopy.boundaries import get_boundaries

def check_morphemes(wordlist):
    #This checks for every morpheme in morphemes whether it corresponds to more than one crossIDs and outputs those cases.
    morphemes = defaultdict(list)
    for idx, doculect, morps, crossids in wordlist.iter_rows(
            'doculect', 'morphemes', 'crossids'):
        for morp, crossid in zip(
                bt.lists(morps),
                bt.ints(crossids)):
            morphemes[doculect, morp] += [(idx, str(crossid))]

    for (doc, morp), values in sorted(morphemes.items(), key=lambda x: x[0]):
        crossids = [x[1] for x in values]
        if len(set(crossids)) != 1:
            print('# {0} / {1}'.format(doc, morp))
            table = []
            for idx, crossid in values:
                table += [[
                    idx,
                    wordlist[idx, 'doculect'],
                    wordlist[idx, 'concept'],
                    bt.lists(wordlist[idx, 'morphemes']),
                    morp,
                    crossid
                    ]]
            print(tabulate(table, headers=['id', 'doculect', 'concept', 'morpheme', 'morphemes', 'crossid'], tablefmt='pipe'))
            input()
	
def check_tokens(wordlist):
    #This checks for every morpheme in morphemes whether it corresponds to more than one morpheme in tokens and outputs those cases.
    morphemes = defaultdict(list)
    for idx, doculect, morps, toks in wordlist.iter_rows(
            'doculect', 'morphemes', 'tokens'):
        for morp, tok in zip(
                bt.lists(morps),
                bt.lists(toks).n):
            morphemes[doculect, morp] += [(idx, str(tok))]

    for (doc, morp), values in sorted(morphemes.items(), key=lambda x: x[0]):
        toks = [x[1] for x in values]
        if len(set(toks)) != 1:
            print('# {0} / {1}'.format(doc, morp))
            table = []
            for idx, tok in values:
                table += [[idx, tok, ' '.join(wordlist[idx, 'tokens'])]]
            print(tabulate(table, headers=['idx', 'token', 'tokens'],
                tablefmt='pipe'))
            input()
		
def check_rootids(wordlist):
    #this checks for every crossID whether it corresponds to more than one rootID and outputs those cases.
    for idx in wordlist:
        for c in ['crossids', 'rootids']:
            wordlist[idx, c] = bt.ints(wordlist[idx, c])

    etd_cross = wordlist.get_etymdict(ref='crossids')
    etd_root = wordlist.get_etymdict(ref='rootids')

    for key, values in etd_cross.items():
        data = []
        for v in values:
            if v:
                for idx in v:
                    crossids = wordlist[idx, 'crossids']
                    crossidx = crossids.index(key)
                    rootid = wordlist[idx, 'rootids'][crossidx]
                    data += [(idx, crossidx, rootid)]
        rootids = [x[2] for x in data]
        if len(set(rootids)) != 1:
            print('# crossid {0}'.format(key))
            table = []
            for idx, crossidx, rootid in data:
                table += [[
                    idx,
                    wordlist[idx, 'doculect'],
                    wordlist[idx, 'concept'],
                    bt.lists(wordlist[idx, 'tokens']),
                    bt.lists(wordlist[idx, 'tokens']).n[crossidx],
                    crossidx,
                    rootid
                    ]]
            print(tabulate(table, headers=['id', 'doculect', 'concept', 
                'tokens', 'morpheme', 'crossidx', 'rootid'], tablefmt='pipe'))
            input()

def check_crossids(wordlist):
    #this checks for every cogID whether it corresponds to more than one crossID and outputs those cases.
    for idx in wordlist:
        for c in ['cogids', 'crossids']:
            wordlist[idx, c] = bt.ints(wordlist[idx, c])

    etd_cogs = wordlist.get_etymdict(ref='cogids')
    etd_crss = wordlist.get_etymdict(ref='crossids')

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

    if 'check-rootids' in argv:
        clidx = argv.index('check-rootids')+1
        wordlist = Wordlist(argv[clidx])
        check_rootids(wordlist)
	
    if 'check-crossids' in argv:
        clidx = argv.index('check-crossids')+1
        wordlist = Wordlist(argv[clidx])
        check_crossids(wordlist)
        
    if 'check-tokens' in argv:
        clidx = argv.index('check-tokens')+1
        wordlist = Wordlist(argv[clidx])
        check_tokens(wordlist)
	
    if 'check-morphemes' in argv:
        clidx = argv.index('check-morphemes')+1
        wordlist = Wordlist(argv[clidx])
        check_morphemes(wordlist)

    if 'find-morphemes' in argv:
        clidx = argv.index('find-morphemes')+1
        wordlist = Wordlist(argv[clidx])
        language = argv[clidx+1]
        return get_boundaries(wordlist, language)
