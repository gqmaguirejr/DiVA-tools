#!/usr/bin/python3
#
# ./nation_subject_test.py spreadsheet.xlsx
#
# G. Q. Maguire Jr.
#
# 2019.08.06
#
# for each thesis in the spreadsheet, the program sends the abstract to Linköping University Electronic Press called: “Find a Detailed-level National Subject Area”
# see http://www.ep.liu.se/hsv_categories/index.en.asp 
#

import requests, time
from pprint import pprint
import optparse
import sys
# import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

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
#############################
###### EDIT THIS STUFF ######
#############################
global baseUrl	# the base URL used for access to Canvas
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# HTTP POST "abstract", "issn", "language" (the latter "en" or "sv") and "subjectlevel" (the latter a "2" or "3") to 
def get_categories2(abstract, lang):
    page_response=''
    url='http://www.ep.liu.se/subject_categories/Default.aspx'
    payload={'abstract': abstract,
             'issn': "",
             'language': lang,
             'subjectlevel': 2
    }

    r = requests.post(url, data=payload)

    if r.status_code == requests.codes.ok:
        page_response=r.text
    else:
        if Verbose_Flag:
            print("r.status_code is {0} and r.text is {1}".format(r.status_code, r.text))
    return page_response

def get_categories3(abstract, lang):
    page_response=''
    url='http://www.ep.liu.se/subject_categories/Default.aspx'
    payload={'abstract': abstract,
             'issn': "",
             'language': lang,
             'subjectlevel': 3
    }

    r = requests.post(url, data=payload)

    if r.status_code == requests.codes.ok:
        page_response=r.text
    else:
        if Verbose_Flag:
            print("r.status_code is {0} and r.text is {1}".format(r.status_code, r.text))
    return page_response

def get_codes_and_scores(response):
    # r1.text is <results>
    # <hsv-all>
    #   <subject>
    #     <code>207</code>
    #     <topic>Medical Engineering</topic>
    #     <score>0,07210935</score>
    #   </subject>
    #   <subject>
    #     <code>202</code>
    #     <topic>Electrical Engineering, Electronic Engineering, Information Engineering</topic>
    #     <score>0,06453624</score>
    #   </subject>
    #   <subject>
    #     <code>211</code>
    #     <topic>Other Engineering and Technologies</topic>
    #     <score>0,05474341</score>
    #   </subject>
    #   <subject>
    #     <code>201</code>
    #     <topic>Civil Engineering</topic>
    #     <score>0,0422397</score>
    #   </subject>
    #   <subject>
    #     <code>203</code>
    #     <topic>Mechanical Engineering</topic>
    #     <score>0,04139797</score>
    #   </subject>
    # </hsv-all>
    # <Message> Invalid ISSN.</Message>
    # </results>

    v1=dict()

    if (not response):  # there was an error in the response, so ignore this entry
        return v1
    parsed_xml=BeautifulSoup(response, 'lxml-xml')
    if Verbose_Flag:
        print("parsed_xml = {}".format(parsed_xml.prettify()))
    subjects=parsed_xml.find_all("subject")
    if Verbose_Flag:
        print("subjects = {}".format(subjects))

    for s in subjects:
        v1[s.code.text]={'topic': s.topic.text, 'score': s.score.text}

    if Verbose_Flag:
        print("v1 is {}".format(v1))
    return v1

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
        if w in stop_words:
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
    diva_df = pd.read_excel(open(spreadsheet_file, 'rb'), sheet_name='EECS-2018')
    #if Verbose_Flag:
    #    print("diva_df={}".format(diva_df))

    diva_df['LiU category2_en']="" # add an empty column to put data into
    diva_df['LiU category2_sv']="" # add an empty column to put data into
    diva_df['LiU category3_en']="" # add an empty column to put data into
    diva_df['LiU category3_sv']="" # add an empty column to put data into
    
    for index, row in diva_df.iterrows():
        pid=row['PID']
        print("pid is {}".format(pid))

        abstract=row['Abstract']
        # consider the first two abstracts if they exist
        abstracts=abstract.split('</p>;')
        for ab in abstracts:
            abstract=clean_text_of_some_HTML(ab)     # remove the '<p>'
            if len(abstract) > 0:
                if Verbose_Flag:
                    print("abstract is {}".format(abstract))
                lang=guess_language(abstract)
                print("lang is {0}".format(lang))
                response=get_categories2(abstract, lang)
                if (len(response) > 0):
                    if Verbose_Flag:
                        print("response={0}".format(response))
                    entry='LiU category2'+lang
                    diva_df.loc[diva_df['PID'] == row['PID'], entry]=json.dumps(get_codes_and_scores(response))

                response=get_categories3(abstract, lang)
                if (len(response) > 0):
                    if Verbose_Flag:
                        print("response={0}".format(response))
                    entry='LiU category3'+lang
                    diva_df.loc[diva_df['PID'] == row['PID'], entry]=json.dumps(get_codes_and_scores(response))

        # if (index > 200):
        #     break;
            
        # set up the output write
        writer = pd.ExcelWriter('output.xlsx', engine='xlsxwriter')
        diva_df.to_excel(writer, sheet_name='new_codes')
        writer.save()
              
if __name__ == "__main__": main()
