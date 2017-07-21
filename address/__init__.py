#!/usr/bin/python
# -*- coding: utf-8 -*-

import pycrfsuite
import os
import re
import warnings
from collections import OrderedDict
import sqlite3
from metaphone import doublemetaphone

#  _____________________
# |1. CONFIGURE LABELS! |
# |_____________________| 
#     (\__/) || 
#     (•ㅅ•) || 
#     / 　 づ
LABELS = ['state', 'district', 'mandal', 'city', 'village', 'pin', 'locality', 'street', 'landmark', 'number' ] # The labels should be a list of strings

#***************** OPTIONAL CONFIG ***************************************************
PARENT_LABEL  = 'TokenSequence'               # the XML tag for each labeled string
GROUP_LABEL   = 'Collection'                  # the XML tag for a group of strings
NULL_LABEL    = 'Null'                        # the null XML tag
MODEL_FILE    = 'learned_settings.crfsuite'   # filename for the crfsuite settings file
#************************************************************************************


try :
    TAGGER = pycrfsuite.Tagger()
    TAGGER.open(os.path.split(os.path.abspath(__file__))[0]+'/'+MODEL_FILE)
except IOError :
    TAGGER = None
    warnings.warn('You must train the model (parserator train [traindata] [modulename]) to create the %s file before you can use the parse and tag methods' %MODEL_FILE)

def parse(raw_string):
    if not TAGGER:
        raise IOError('\nMISSING MODEL FILE: %s\nYou must train the model before you can use the parse and tag methods\nTo train the model annd create the model file, run:\nparserator train [traindata] [modulename]' %MODEL_FILE)

    tokens = tokenize(raw_string)
    if not tokens :
        return []

    features = tokens2features(tokens)

    tags = TAGGER.tag(features)
    return list(zip(tokens, tags))

def tag(raw_string) :
    tagged = OrderedDict()
    for token, label in parse(raw_string) :
        tagged.setdefault(label, []).append(token)

    for token in tagged :
        component = ' '.join(tagged[token])
        component = component.strip(' ,;')
        tagged[token] = component

    return tagged


#  _____________________
# |2. CONFIGURE TOKENS! |
# |_____________________| 
#     (\__/) || 
#     (•ㅅ•) || 
#     / 　 づ
def tokenize(raw_string):
    # this determines how any given string is split into its tokens
    # handle any punctuation you want to split on, as well as any punctuation to capture

    if isinstance(raw_string, bytes):
        try:
            raw_string = str(raw_string, encoding='utf-8')
        except:
            raw_string = str(raw_string)
    
    #re_tokens = re.compile( r'[^,]+', re.VERBOSE | re.UNICODE)
    #tokens = re_tokens.findall(raw_string)

    #if not tokens :
    #    return []

    separated = raw_string.split(", ")
    separated = filter(lambda s: len(s) > 1, separated)

    return separated


#  _______________________
# |3. CONFIGURE FEATURES! |
# |_______________________| 
#     (\__/) || 
#     (•ㅅ•) || 
#     / 　 づ
def tokens2features(tokens):
    # this should call tokenFeatures to get features for individual tokens,
    # as well as define any features that are dependent upon tokens before/after
    
    feature_sequence = [tokenFeatures(tokens[0])]
    previous_features = feature_sequence[-1].copy()

    for token in tokens[1:] :
        # set features for individual tokens (calling tokenFeatures)
        token_features = tokenFeatures(token)
        current_features = token_features.copy()

        # features for the features of adjacent tokens
        feature_sequence[-1]['next'] = current_features
        token_features['previous'] = previous_features        
        
        # DEFINE ANY OTHER FEATURES THAT ARE DEPENDENT UPON TOKENS BEFORE/AFTER
        # for example, a feature for whether a certain character has appeared previously in the token sequence
        
        feature_sequence.append(token_features)
        previous_features = current_features

    if len(feature_sequence) > 1 :
        # these are features for the tokens at the beginning and end of a string
        feature_sequence[0]['rawstring.start'] = True
        feature_sequence[-1]['rawstring.end'] = True
        feature_sequence[1]['previous']['rawstring.start'] = True
        feature_sequence[-2]['next']['rawstring.end'] = True

    else : 
        # a singleton feature, for if there is only one token in a string
        feature_sequence[0]['singleton'] = True

    return feature_sequence
STREET_NAMES = {
        'allee', 'alley', 'ally', 'aly', 'anex', 'annex', 'annx', 'anx',
        'arc', 'arcade', 'av', 'ave', 'aven', 'avenu', 'avenue', 'avn', 'avnue',
        'bayoo', 'bayou', 'bch', 'beach', 'bend', 'bg', 'bgs', 'bl', 'blf',
        'blfs', 'bluf', 'bluff', 'bluffs', 'blvd', 'bnd', 'bot', 'bottm',
        'bottom', 'boul', 'boulevard', 'boulv', 'br', 'branch', 'brdge', 'brg',
        'bridge', 'brk', 'brks', 'brnch', 'brook', 'brooks', 'btm', 'burg',
        'burgs', 'byp', 'bypa', 'bypas', 'bypass', 'byps', 'byu', 'camp', 'canyn',
        'canyon', 'cape', 'causeway', 'causwa', 'causway', 'cen', 'cent',
        'center', 'centers', 'centr', 'centre', 'ci', 'cir', 'circ', 'circl',
        'circle', 'circles', 'cirs', 'ck', 'clb', 'clf', 'clfs', 'cliff',
        'cliffs', 'club', 'cmn', 'cmns', 'cmp', 'cnter', 'cntr', 'cnyn', 'common',
        'commons', 'cor', 'corner', 'corners', 'cors', 'course', 'court',
        'courts', 'cove', 'coves', 'cp', 'cpe', 'cr', 'crcl', 'crcle', 'crecent',
        'creek', 'cres', 'crescent', 'cresent', 'crest', 'crk', 'crossing',
        'crossroad', 'crossroads', 'crscnt', 'crse', 'crsent', 'crsnt', 'crssing',
        'crssng', 'crst', 'crt', 'cswy', 'ct', 'ctr', 'ctrs', 'cts', 'curv',
        'curve', 'cv', 'cvs', 'cyn', 'dale', 'dam', 'div', 'divide', 'dl', 'dm',
        'dr', 'driv', 'drive', 'drives', 'drs', 'drv', 'dv', 'dvd', 'est',
        'estate', 'estates', 'ests', 'ex', 'exp', 'expr', 'express', 'expressway',
        'expw', 'expy', 'ext', 'extension', 'extensions', 'extn', 'extnsn',
        'exts', 'fall', 'falls', 'ferry', 'field', 'fields', 'flat', 'flats',
        'fld', 'flds', 'fls', 'flt', 'flts', 'ford', 'fords', 'forest', 'forests',
        'forg', 'forge', 'forges', 'fork', 'forks', 'fort', 'frd', 'frds',
        'freeway', 'freewy', 'frg', 'frgs', 'frk', 'frks', 'frry', 'frst', 'frt',
        'frway', 'frwy', 'fry', 'ft', 'fwy', 'garden', 'gardens', 'gardn',
        'gateway', 'gatewy', 'gatway', 'gdn', 'gdns', 'glen', 'glens', 'gln',
        'glns', 'grden', 'grdn', 'grdns', 'green', 'greens', 'grn', 'grns',
        'grov', 'grove', 'groves', 'grv', 'grvs', 'gtway', 'gtwy', 'harb',
        'harbor', 'harbors', 'harbr', 'haven', 'havn', 'hbr', 'hbrs', 'height',
        'heights', 'hgts', 'highway', 'highwy', 'hill', 'hills', 'hiway', 'hiwy',
        'hl', 'hllw', 'hls', 'hollow', 'hollows', 'holw', 'holws', 'hrbor', 'ht',
        'hts', 'hvn', 'hway', 'hwy', 'inlet', 'inlt', 'is', 'island', 'islands',
        'isle', 'isles', 'islnd', 'islnds', 'iss', 'jct', 'jction', 'jctn',
        'jctns', 'jcts', 'junction', 'junctions', 'junctn', 'juncton', 'key',
        'keys', 'knl', 'knls', 'knol', 'knoll', 'knolls', 'ky', 'kys', 'la',
        'lake', 'lakes', 'land', 'landing', 'lane', 'lanes', 'lck', 'lcks', 'ldg',
        'ldge', 'lf', 'lgt', 'lgts', 'light', 'lights', 'lk', 'lks', 'ln', 'lndg',
        'lndng', 'loaf', 'lock', 'locks', 'lodg', 'lodge', 'loop', 'loops', 'lp',
        'mall', 'manor', 'manors', 'mdw', 'mdws', 'meadow', 'meadows', 'medows',
        'mews', 'mi', 'mile', 'mill', 'mills', 'mission', 'missn', 'ml', 'mls',
        'mn', 'mnr', 'mnrs', 'mnt', 'mntain', 'mntn', 'mntns', 'motorway',
        'mount', 'mountain', 'mountains', 'mountin', 'msn', 'mssn', 'mt', 'mtin',
        'mtn', 'mtns', 'mtwy', 'nck', 'neck', 'opas', 'orch', 'orchard', 'orchrd',
        'oval', 'overlook', 'overpass', 'ovl', 'ovlk', 'park', 'parks', 'parkway',
        'parkways', 'parkwy', 'pass', 'passage', 'path', 'paths', 'pike', 'pikes',
        'pine', 'pines', 'pk', 'pkway', 'pkwy', 'pkwys', 'pky', 'pl', 'place',
        'plain', 'plaines', 'plains', 'plaza', 'pln', 'plns', 'plz', 'plza',
        'pne', 'pnes', 'point', 'points', 'port', 'ports', 'pr', 'prairie',
        'prarie', 'prk', 'prr', 'prt', 'prts', 'psge', 'pt', 'pts', 'pw', 'pwy',
        'rad', 'radial', 'radiel', 'radl', 'ramp', 'ranch', 'ranches', 'rapid',
        'rapids', 'rd', 'rdg', 'rdge', 'rdgs', 'rds', 'rest', 'ri', 'ridge',
        'ridges', 'rise', 'riv', 'river', 'rivr', 'rn', 'rnch', 'rnchs', 'road',
        'roads', 'route', 'row', 'rpd', 'rpds', 'rst', 'rte', 'rue', 'run', 'rvr',
        'shl', 'shls', 'shoal', 'shoals', 'shoar', 'shoars', 'shore', 'shores',
        'shr', 'shrs', 'skwy', 'skyway', 'smt', 'spg', 'spgs', 'spng', 'spngs',
        'spring', 'springs', 'sprng', 'sprngs', 'spur', 'spurs', 'sq', 'sqr',
        'sqre', 'sqrs', 'sqs', 'squ', 'square', 'squares', 'st', 'sta', 'station',
        'statn', 'stn', 'str', 'stra', 'strav', 'strave', 'straven', 'stravenue',
        'stravn', 'stream', 'street', 'streets', 'streme', 'strm', 'strt',
        'strvn', 'strvnue', 'sts', 'sumit', 'sumitt', 'summit', 'te', 'ter',
        'terr', 'terrace', 'throughway', 'tl', 'tpk', 'tpke', 'tr', 'trace',
        'traces', 'track', 'tracks', 'trafficway', 'trail', 'trailer', 'trails',
        'trak', 'trce', 'trfy', 'trk', 'trks', 'trl', 'trlr', 'trlrs', 'trls',
        'trnpk', 'trpk', 'trwy', 'tunel', 'tunl', 'tunls', 'tunnel', 'tunnels',
        'tunnl', 'turn', 'turnpike', 'turnpk', 'un', 'underpass', 'union',
        'unions', 'uns', 'upas', 'valley', 'valleys', 'vally', 'vdct', 'via',
        'viadct', 'viaduct', 'view', 'views', 'vill', 'villag', 'village',
        'villages', 'ville', 'villg', 'villiage', 'vis', 'vist', 'vista', 'vl',
        'vlg', 'vlgs', 'vlly', 'vly', 'vlys', 'vst', 'vsta', 'vw', 'vws', 'walk',
        'walks', 'wall', 'way', 'ways', 'well', 'wells', 'wl', 'wls', 'wy', 'xc',
        'xg', 'xing', 'xrd', 'xrds'
        }
def tokenFeatures(token) :
    # this defines a dict of features for an individual token
    h = heirarchy(token)

    features = {   # DEFINE FEATURES HERE. some examples:
            'len': len(token),
            'heirarchy': h,
            'soundslike': soundslike(token) if not h else h,
            'street': token.split(' ')[-1].lower() in STREET_NAMES,
            'isdigit': token.isdigit(),
            'containsdigits': bool(re.compile('\d').search(token)),
            }

    return features

# define any other methods for features. this is an example to get the casing of a token

con = sqlite3.Connection('names.sqlite')
cur = con.cursor()
def heirarchy(token):
    table_names = ['States', 'Cities', 'Mandals', 'Districts', 'Villages']
    for i in range(5):
        cur.execute('SELECT * FROM ' + table_names[i] + ' WHERE name ="' + token.upper() + '" LIMIT 1')
        if cur.fetchone():
            return table_names[i]

    return False

def soundslike(token):
    table_names = ['States', 'Cities', 'Mandals', 'Districts', 'Villages']
    metaphones = doublemetaphone(token)
    for i in range(5):
        m1 = cur.execute('SELECT * FROM ' + table_names[i] + ' WHERE metaphone1 ="' + metaphones[0] + '" LIMIT 1').fetchone()
        m2 = cur.execute('SELECT * FROM ' + table_names[i] + ' WHERE metaphone2 ="' + metaphones[0] + '" LIMIT 1').fetchone()
        if m1 or m2:
            return table_names[i]
    return False
