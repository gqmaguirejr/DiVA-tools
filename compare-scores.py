#!/usr/bin/python3
#
# ./compare-scores.py spreadsheet.xlsx
#
# G. Q. Maguire Jr.
#
# 2019.08.06
#
# for each thesis in the spreadsheet compare the manually assigned category or categories with the scores from LiU's service
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
    diva_df = pd.read_excel(open(spreadsheet_file, 'rb'), sheet_name='new_codes')
    #if Verbose_Flag:
    #    print("diva_df={}".format(diva_df))

    diva_df['LiU 2_en_compared']=''
    diva_df['LiU 2_sv_compared']=''
    diva_df['LiU 3_en_compared']=''
    diva_df['LiU 3_sv_compared']=''
    
    for index, row in diva_df.iterrows():
        pid=row['PID']
        print("pid is {}".format(pid))

        cat_list=[]
        cat1=row['Categories']
        # extract the numbers in the field
        cat=extract_numbers(cat1)
        if len(cat) > 0:
            if Verbose_Flag:
                print("categories is {}".format(cat))

            diva_df.loc[diva_df['PID'] == row['PID'], 'DiVA_Categories']=', '.join(str(x) for x in cat)
            # get the LiU scores
            en2=get_json_conditional(row['LiU category2_en'])
            en3=get_json_conditional(row['LiU category3_en'])
            sv2=get_json_conditional(row['LiU category2_sv'])
            sv3=get_json_conditional(row['LiU category3_sv'])
            LiU_2_en_compared=0
            LiU_2_sv_compared=0
            LiU_3_en_compared=0
            LiU_3_sv_compared=0
        
            for i, s in enumerate(en2):
                for s1 in cat:
                    if s == s1:
                        print("i is {0} and s is {1} and s1 is {2}".format(i,s, s1))
                        LiU_2_en_compared=LiU_2_en_compared+(2**(5-i))

            for i, s in enumerate(en3):
                for s1 in cat:
                    if s == s1:
                        print("i is {0} and s is {1} and s1 is {2}".format(i,s, s1))
                        LiU_3_en_compared=LiU_3_en_compared+(2**(5-i))

            for i, s in enumerate(sv2):
                for s1 in cat:
                    if s == s1:
                        print("i is {0} and s is {1} and s1 is {2}".format(i,s, s1))
                        LiU_2_sv_compared=LiU_2_sv_compared+(2**(5-i))

            for i, s in enumerate(sv3):
                for s1 in cat:
                    if s == s1:
                        print("i is {0} and s is {1} and s1 is {2}".format(i,s, s1))
                        LiU_3_sv_compared=LiU_3_sv_compared+(2**(5-i))

            diva_df.loc[diva_df['PID'] == row['PID'], 'LiU 2_en_compared']=LiU_2_en_compared
            diva_df.loc[diva_df['PID'] == row['PID'], 'LiU 3_en_compared']=LiU_2_en_compared
            diva_df.loc[diva_df['PID'] == row['PID'], 'LiU 2_sv_compared']=LiU_2_sv_compared
            diva_df.loc[diva_df['PID'] == row['PID'], 'LiU 3_sv_compared']=LiU_3_sv_compared


        # if (index > 40):
        #     break;
            
        # set up the output write
        writer = pd.ExcelWriter('output2.xlsx', engine='xlsxwriter')
        diva_df.to_excel(writer, sheet_name='new_codes')
        writer.save()
              
if __name__ == "__main__": main()
