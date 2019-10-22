from lingpy import *
from collections import defaultdict
from lingpy.sequence.sound_classes import *
from lingpy import basictypes as bt
from segments import tokenizer, profile
from tabulate import tabulate

def get_init_enit(tokens, debug=False):
    tokens = [t for t in tokens if t != '+']

    prostring = prosodic_string(tokens)
    if 'X' in prostring:
        inidx = prostring.index('X')
    elif 'Y' in prostring and not 'X' in prostring:
        inidx = prostring.index('Y')
    else:
        inidx = 0
        
    if 'Z' in prostring:
        enidx = prostring[::-1].index('Z')
    else:
        if 'Y' in prostring:
            enidx = prostring[::-1].index('Y')
        elif 'X' in prostring:
            enidx = prostring[::-1].index('X')
        else:
            enidx = 0

    init, enit = tokens[:inidx], tokens[-(enidx+1):]
    if debug:
        print(' '.join(tokens))
        print(' '.join(list(prostring)))
        print(' '.join(init)+' +++ '+' '.join(enit))
        input()
    return init, enit


def get_boundaries(wordlist, language, segments='tokens', threshold=0):
    
    inits = defaultdict(int)
    enits = defaultdict(int)
    segm = defaultdict(int)
    
    for tokens in wordlist.get_list(col=language, entry=segments, flat=True):
        sybs = bt.lists(syllabify(tokens))
        tokens = [{'_': '+', '#': '+'}.get(t, t) for t in tokens]

        tokensplit = ' '.join(tokens).split(' + ')
        for token in tokensplit:
        
            init, enit = get_init_enit(token.split())
            if init:
                inits[' '.join(init)] += 1
            if enit:
                enits[' '.join(enit)] += 1

        #print(tokens, prostring, init, enit, inidx, enidx)
        for segment in tokens:
            segm[segment] += 1

    dpoints = []
    for key, vals in inits.items():
        if vals > threshold:
            dpoints += [{'Grapheme': key.replace(' ', ''), 
                'Segments': '← '+key,
                'Frequency': vals}]
            dpoints += [{'Grapheme': '^'+key.replace(' ', ''), 
                'Segments': key,
                'Frequency': vals}]

    for key, vals in enits.items():
        if vals > threshold:
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
    morphemes = defaultdict(list)
    S = {}
    for idx, tokens in zip(
            wordlist.get_list(col=language, flat=True),
            wordlist.get_list(col=language, entry=segments, flat=True)):
        tokens = [{'_': '+', '#': '+'}.get(t, t) for t in tokens]
        segmented, segmented2 = [], []
        for token in ' '.join(tokens).split(' + '):
            tok = ''.join([t for t in token.split() if t != '+'])
            segs = prf('^'+tok+'$', column='Segments')
            #print(' '.join(word), segs)
            sgs = segs.replace(' → ← ', ' + ')
            sgs = sgs.replace(' → ', ' + ')
            sgs = sgs.replace(' ← ', ' + ')
            segmented += [sgs]
            segmented2 += [segs]
        
        sgs = ' + '.join(segmented)
        table += [[''.join(tokens), sgs, prosodic_string(tokens)]]
        morphemes_ = sgs.split(' + ')
        morphemes['^'+morphemes_[0]] += [idx]
        morphemes[morphemes_[-1]+'$'] += [idx]
        for morpheme in morphemes_[1:-1]:
            morphemes[morpheme] += [idx]
        S[idx] = sgs, ' + '.join(segmented2)
    print(tabulate(table))
    
    for morpheme, idxs in sorted(morphemes.items(), key=lambda x: len(x[1])):
        if len(morpheme) > 1:
            print('# {0} ({1})'.format(morpheme, len(idxs)))
            table = []
            for idx in sorted(idxs, key=lambda x: wordlist[x, 'concept']):
                table += [[
                    idx,
                    wordlist[idx, 'concept'],
                    S[idx][1]]]
            print(tabulate(table, headers=['ID', 'Concept', 'Morphemes'],
                tablefmt='pipe'))
    input()

    # write a profile
    return inits, enits, prf
