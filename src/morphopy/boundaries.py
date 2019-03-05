from lingpy import *
from collections import defaultdict
from lingpy.sequence.sound_classes import *
from lingpy import basictypes as bt
from segments import tokenizer, profile
from tabulate import tabulate

def get_init_enit(tokens):
    tokens = [t for t in tokens if t != '+']

    #inits[str(sybs.n[0])] += 1
    #enits[str(sybs.n[-1])] += 1
    prostring = prosodic_string(tokens)
    if 'X' in prostring:
        inidx = prostring.index('X')
    elif 'Y' in prostring and not 'X' in prostring:
        inidx = prostring.index('Y')
    if 'Z' in prostring:
        enidx = prostring[::-1].index('Z')
    else:
        if 'Y' in prostring:
            enidx = prostring[::-1].index('Y')
        else:
            enidx = prostring[::-1].index('X')

    init, enit = tokens[:inidx], tokens[-(enidx):]
    print(' '.join(tokens))
    print(' '.join(list(prostring)))
    print(' '.join(init)+' +++ '+' '.join(enit))
    return init, enit

def get_boundaries(wordlist, language, segments='tokens'):
    
    inits = defaultdict(int)
    enits = defaultdict(int)
    segm = defaultdict(int)
    
    for tokens in wordlist.get_list(col=language, entry=segments, flat=True):
        sybs = bt.lists(syllabify(tokens))

        if init:
            inits[' '.join(init)] += 1
        if enit:
            enits[' '.join(enit)] += 1

        #print(tokens, prostring, init, enit, inidx, enidx)
        for segment in tokens:
            segm[segment] += 1

    dpoints = []
    for key, vals in inits.items():
        dpoints += [{'Grapheme': key.replace(' ', ''), 
            'Segments': '← '+key,
            'Frequency': vals}]
        dpoints += [{'Grapheme': '^'+key.replace(' ', ''), 
            'Segments': key,
            'Frequency': vals}]

    for key, vals in enits.items():
        dpoints += [{'Grapheme': key.replace(' ', ''), 
            'Segments': key+' →',
            'Frequency': vals}]
        dpoints += [{'Grapheme': key.replace(' ', '')+'$', 
            'Segments': key,
            'Frequency': vals}]

    for segment, vals in segm.items():
        dpoints += [{'Grapheme': segment, 
            'Segments': segment, 'Frequency': vals}]

    dpoints += [{'Grapheme': '^', 'Segments': None, 'Frequency': '0'}]
    dpoints += [{'Grapheme': '$', 'Segments': None, 'Frequency': '0'}]

    prf = tokenizer.Tokenizer(profile.Profile(*dpoints))
    
    table = []
    for word in wordlist.get_list(col=language, entry=segments, flat=True):
        tok = ''.join([t for t in word if t != '+'])
        segs = prf('^'+tok+'$', column='Segments')
        #print(' '.join(word), segs)
        table += [[''.join(word), segs, prosodic_string(word)]]
    print(tabulate(table))
    input()
    # write a profile
    return inits, enits, prf
