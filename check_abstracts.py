#!/usr/bin/python3
#
# ./check_abstracts.py spreadsheet.xlsx
#
# G. Q. Maguire Jr.
#
# 2019.08.08
#
# for each thesis in the spreadsheet check the abstracts for LaTeX and other errors creaping in
#

import requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

import json

import datetime
import isodate                  # for parsing ISO 8601 dates and times
import pytz                     # for time zones
import os                       # to make OS calls, here to get time zone info
from dateutil.tz import tzlocal
import re

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

# to normalize unicoded strings
import unicodedata

#############################
###### EDIT THIS STUFF ######
#############################
global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests


StopWords=[
    u'a',
    u'à',
    u'able',
    u'ad',
    u'after',
    u'all',
    u'allows',
    u'along',
    u'also',
    u'an',
    u'and',
    u'another',
    u'any',
    u'are',
    u'as',
    u'at',
    u'average',
    u'be',
    u'before',
    u'because',
    u'being',
    u'between',
    u'both',
    u'but',
    u'by',
    u'can',
    u'could',
    u'course',
    u'currently',
    u'decrease',
    u'decreasing',
    u'do',
    u'does',
    u'done',
    u'down',
    u'due',
    u'each',
    u'early',
    u'earlier',
    u'easy',
    u'e.g',
    u'eigth',
    u'either',
    u'end',
    u'especially',
    u'etc',
    u'even',
    u'every',
    u'far',
    u'five',
    u'first',
    u'follow',
    u'following',
    u'for',
    u'formerly',
    u'four',
    u'further',
    u'general',
    u'generally',
    u'get',
    u'going',
    u'good',
    u'had',
    u'has',
    u'have',
    u'high',
    u'higher',
    u'hoc',
    u'how',
    u'i.e',
    u'if',
    u'in',
    u'include',
    u'includes',
    u'including',
    u'increase',
    u'increasing',
    u'into',
    u'is',
    u'it',
    u'its',
    u'just',
    u'know',
    u'known',
    u'knows',
    u'last',
    u'later',
    u'large',
    u'least',
    u'like',
    u'long',
    u'longer',
    u'low',
    u'made',
    u'many',
    u'make',
    u'makes',
    u'might',
    u'much',
    u'most',
    u'must',
    u'near',
    u'need',
    u'needs',
    u'needed',
    u'next',
    u'new',
    u'no',
    u'not',
    u'now',
    u'of',
    u'on',
    u'one',
    u'or',
    u'over',
    u'pass',
    u'per',
    u'pg',
    u'pp',
    u'provides',
    u'rather',
    u'require',
    u's',
    u'same',
    u'see',
    u'several',
    u'should',
    u'simply',
    u'since',
    u'six',
    u'small',
    u'so',
    u'some',
    u'such',
    u'take',
    u'takes',
    u'th',
    u'than',
    u'that',
    u'the',
    u'then',
    u'their',
    u'there',
    u'these',
    u'three',
    u'they',
    u'this',
    u'thus',
    u'time',
    u'to',
    u'too',
    u'try',
    u'two',
    u'under',
    u'unit',
    u'until',
    u'up',
    u'used',
    u'verison',
    u'very',
    u'vs',
    u'we',
    u'were',
    u'what',
    u'when',
    u'where',
    u'which',
    u'while',
    u'who',
    u'wide',
    u'will',
    u'with',
    u'within',
    u'you',
    u'your'
    ]

SwedishStopWords=[
    u'aderton',
    u'adertonde',
    u'adjö',
    u'aldrig',
    u'alla',
    u'allas',
    u'allt',
    u'alltid',
    u'alltså',
    u'än',
    u'andra',
    u'andras',
    u'annan',
    u'annat',
    u'ännu',
    u'artonde',
    u'artonn',
    u'åtminstone',
    u'att',
    u'åtta',
    u'åttio',
    u'åttionde',
    u'åttonde',
    u'av',
    u'även',
    u'båda',
    u'bådas',
    u'bakom',
    u'bara',
    u'bäst',
    u'bättre',
    u'behöva',
    u'behövas',
    u'behövde',
    u'behövt',
    u'beslut',
    u'beslutat',
    u'beslutit',
    u'bland',
    u'blev',
    u'bli',
    u'blir',
    u'blivit',
    u'bort',
    u'borta',
    u'bra',
    u'då',
    u'dag',
    u'dagar',
    u'dagarna',
    u'dagen',
    u'där',
    u'därför',
    u'de',
    u'del',
    u'delen',
    u'dem',
    u'den',
    u'deras',
    u'dess',
    u'det',
    u'detta',
    u'dig',
    u'din',
    u'dina',
    u'dit',
    u'ditt',
    u'dock',
    u'du',
    u'efter',
    u'eftersom',
    u'elfte',
    u'eller',
    u'elva',
    u'en',
    u'enkel',
    u'enkelt',
    u'enkla',
    u'enligt',
    u'er',
    u'era',
    u'ert',
    u'ett',
    u'ettusen',
    u'få ',
    u'fanns',
    u'får',
    u'fått ',
    u'fem',
    u'femte',
    u'femtio',
    u'femtionde',
    u'femton',
    u'femtonde',
    u'fick',
    u'fin',
    u'finnas',
    u'finns',
    u'fjärde',
    u'fjorton',
    u'fjortonde',
    u'fler',
    u'flera',
    u'flesta',
    u'följande',
    u'för',
    u'före',
    u'förlåt',
    u'förra',
    u'första',
    u'fram',
    u'framför',
    u'från',
    u'fyra',
    u'fyrtio',
    u'fyrtionde',
    u'gå',
    u'gälla',
    u'gäller',
    u'gällt',
    u'går',
    u'gärna',
    u'gått',
    u'genast',
    u'genom',
    u'gick',
    u'gjorde',
    u'gjort',
    u'god',
    u'goda',
    u'godare',
    u'godast',
    u'gör',
    u'göra',
    u'gott',
    u'ha',
    u'hade',
    u'haft',
    u'han',
    u'hans',
    u'har',
    u'här',
    u'heller',
    u'hellre',
    u'helst',
    u'helt',
    u'henne',
    u'hennes',
    u'hit',
    u'hög',
    u'höger',
    u'högre',
    u'högst',
    u'hon',
    u'honom',
    u'hundra',
    u'hundraen',
    u'hundraett',
    u'hur',
    u'i',
    u'ibland',
    u'idag',
    u'igår',
    u'igen',
    u'imorgon',
    u'in',
    u'inför',
    u'inga',
    u'ingen',
    u'ingenting',
    u'inget',
    u'innan',
    u'inne',
    u'inom',
    u'inte',
    u'inuti',
    u'ja',
    u'jag',
    u'jämfört',
    u'kan',
    u'kanske',
    u'knappast',
    u'kom',
    u'komma',
    u'kommer',
    u'kommit',
    u'kr',
    u'kunde',
    u'kunna',
    u'kunnat',
    u'kvar',
    u'länge',
    u'längre',
    u'långsam',
    u'långsammare',
    u'långsammast',
    u'långsamt',
    u'längst',
    u'långt',
    u'lätt',
    u'lättare',
    u'lättast',
    u'legat',
    u'ligga',
    u'ligger',
    u'lika',
    u'likställd',
    u'likställda',
    u'lilla',
    u'lite',
    u'liten',
    u'litet',
    u'man',
    u'många',
    u'måste',
    u'med',
    u'mellan',
    u'men',
    u'mer',
    u'mera',
    u'mest',
    u'mig',
    u'min',
    u'mina',
    u'mindre',
    u'minst',
    u'mitt',
    u'mittemot',
    u'möjlig',
    u'möjligen',
    u'möjligt',
    u'möjligtvis',
    u'mot',
    u'mycket',
    u'någon',
    u'någonting',
    u'något',
    u'några',
    u'när',
    u'nästa',
    u'ned',
    u'nederst',
    u'nedersta',
    u'nedre',
    u'nej',
    u'ner',
    u'ni',
    u'nio',
    u'nionde',
    u'nittio',
    u'nittionde',
    u'nitton',
    u'nittonde',
    u'nödvändig',
    u'nödvändiga',
    u'nödvändigt',
    u'nödvändigtvis',
    u'nog',
    u'noll',
    u'nr',
    u'nu',
    u'nummer',
    u'och',
    u'också',
    u'ofta',
    u'oftast',
    u'olika',
    u'olikt',
    u'om',
    u'oss',
    u'över',
    u'övermorgon',
    u'överst',
    u'övre',
    u'på',
    u'rakt',
    u'rätt',
    u'redan',
    u'så',
    u'sade',
    u'säga',
    u'säger',
    u'sagt',
    u'samma',
    u'sämre',
    u'sämst',
    u'sedan',
    u'senare',
    u'senast',
    u'sent',
    u'sex',
    u'sextio',
    u'sextionde',
    u'sexton',
    u'sextonde',
    u'sig',
    u'sin',
    u'sina',
    u'sist',
    u'sista',
    u'siste',
    u'sitt',
    u'sjätte',
    u'sju',
    u'sjunde',
    u'sjuttio',
    u'sjuttionde',
    u'sjutton',
    u'sjuttonde',
    u'ska',
    u'skall',
    u'skulle',
    u'slutligen',
    u'små',
    u'smått',
    u'snart',
    u'som',
    u'stor',
    u'stora',
    u'större',
    u'störst',
    u'stort',
    u'tack',
    u'tidig',
    u'tidigare',
    u'tidigast',
    u'tidigt',
    u'till',
    u'tills',
    u'tillsammans',
    u'tio',
    u'tionde',
    u'tjugo',
    u'tjugoen',
    u'tjugoett',
    u'tjugonde',
    u'tjugotre',
    u'tjugotvå',
    u'tjungo',
    u'tolfte',
    u'tolv',
    u'tre',
    u'tredje',
    u'trettio',
    u'trettionde',
    u'tretton',
    u'trettonde',
    u'två',
    u'tvåhundra',
    u'under',
    u'upp',
    u'ur',
    u'ursäkt',
    u'ut',
    u'utan',
    u'utanför',
    u'ute',
    u'vad',
    u'vänster',
    u'vänstra',
    u'var',
    u'vår',
    u'vara',
    u'våra',
    u'varför',
    u'varifrån',
    u'varit',
    u'varken',
    u'värre',
    u'varsågod',
    u'vart',
    u'vårt',
    u'vem',
    u'vems',
    u'verkligen',
    u'vi',
    u'vid',
    u'vidare',
    u'viktig',
    u'viktigare',
    u'viktigast',
    u'viktigt',
    u'vilka',
    u'vilken',
    u'vilket',
    u'vill',
    ]

def split_into_words(txt):
    return re.findall(r"[\w']+", txt)
#
def count_stop_words(words, stop_words):
    sum=0
    for w in words:
        # ignore acronyms
        if w.isupper():
            continue
        if w.lower() in stop_words:
            sum=sum+1
    return sum

def guess_language(abstract):
    words=split_into_words(abstract)
    c1=count_stop_words(words, StopWords)
    c2=count_stop_words(words, SwedishStopWords)
    if c2 > c1:
        return 'sv'
    else:
        return 'en'

def clean_text_of_some_HTML(txt):
    to_remove = ['<p>', '</p>', '<P>', '</P>']
    p = re.compile('|'.join(map(re.escape, to_remove))) # escape to handle metachars
    return p.sub('', txt)

def extract_numbers(cat):
    pattern = re.compile(r"\((\d+)\)")
    return pattern.findall(cat)

def get_json_conditional(s):
    if isinstance(s, str) and len(s) > 0:
        return json.loads(s)
    return []

def corrected_abstract(str1):
    str1=unicodedata.normalize('NFC',str1)
    return str1


def main():
    global Verbose_Flag

    global Use_Local_Time_For_Output_Flag

    # same data used in the program
    Use_Local_Time_For_Output_Flag=True
    Number_of_students_enrolled=0


    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)

    if (len(remainder) < 1):
        print("Insuffient arguments must provide file_name.xlsx\n")
        return

    spreadsheet_file=remainder[0]
    print("file_name='{0}'".format(spreadsheet_file))

    # read the lines from the spreadsheet
    diva_df = pd.read_excel(open(spreadsheet_file, 'rb'))
    #if Verbose_Flag:
    #    print("diva_df={}".format(diva_df))
   
    for index, row in diva_df.iterrows():
        pid=row['PID']
        print("pid is {}".format(pid))

        cat_list=[]
        cat1=row['Categories']
        if (not isinstance(cat1, str)) or len(cat1) < 1: # if there is no category info just loop again
            nbn=row['NBN']
            print("document with PID {0} {1} is missing Categories information".format(pid, nbn))
            continue

        abstract=row['Abstract']
        if (not isinstance(abstract, str)) or len(abstract) < 1: # if there is no abstract just loop again
            continue
        # consider the first two abstracts if they exist
        abstracts=abstract.split('</p>;')
        for ab in abstracts[:2]:                 # just process the first two abstracts
            abstract=clean_text_of_some_HTML(ab)     # remove the '<p>'
            if len(abstract) > 0:
                if Verbose_Flag:
                    print("abstract is {}".format(abstract))
                lang=guess_language(abstract)
                print("lang is {0}".format(lang))
                new_abstract=corrected_abstract(abstract)
                if len(new_abstract) != len(abstract):
                    nbn=row['NBN']
                    print("The {0} abstract for pid {1} {2} could be normalized".format(lang, pid, nbn))
                    entry='corrected_abstract'+'_'+lang
                    diva_df.loc[diva_df['PID'] == row['PID'], entry]=new_abstract

        # if (index > 40):
        #     break;
            
        # set up the output write
        writer = pd.ExcelWriter(spreadsheet_file[:-5]+'_corrected_abstracts.xlsx', engine='xlsxwriter')
        diva_df.to_excel(writer, sheet_name='corrected_abstracts')
        writer.save()
              
if __name__ == "__main__": main()
