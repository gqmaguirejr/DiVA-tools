#!/usr/bin/python3
#
# ./preprocess_for_corpus.py spreadsheet.xlsx
#
# reads in a spreaadsheet of DiVA entries and generates and
# output a file (targets.json) containing JSON with entries containing:
#   PID, Name, Title, Year, DOI, PMID
#
# G. Q. Maguire Jr.
#
# 2020-10-24
#
# Example of runinng the program
# ./preprocess_for_corpus.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019.xlsx
#
# the above spreadsheet has Sheet1
#  wget -O kth-exluding-theses-all-level2-2012-2019.csv 'https://kth.diva-portal.org/smash/export.jsf?format=csvall2&addFilename=true&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":"2012","to":"2019"}},{"organisationId":"177","organisationId-Xtra":true},{"publicationTypeCode":["bookReview","review","article","artisticOutput","book","chapter","manuscript","collection","other","conferencePaper","patent","conferenceProceedings","report","dataset"]}]]&onlyFullText=false&noOfRows=5000000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'
#
#

import requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

import requests
import json

import datetime
import os                       # to make OS calls, here to get time zone info
import re

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

# to normalize unicoded strings
#import unicodedata

#############################
###### EDIT THIS STUFF ######
#############################


def main():
    global Verbose_Flag

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
    with open(spreadsheet_file, 'rb') as spreadsheet_FH:
        diva_df = pd.read_excel(spreadsheet_FH)

    print("Read spreadsheet")

    output_filename='targets.json'
    with open(output_filename, 'w') as output_FH:
        for index, row in diva_df.iterrows():
            j_dict=dict()
            # if there is no PID then you have reached the end of the table (although there might be more calculations after it)
            # print("{0}: row['PID']={1} of type{2}".format(index, row['PID'], type(row['PID'])))
            if not isinstance(row['PID'], int):
                break
            j_dict['PID']=row['PID']
            j_dict['Name']=row['Name']
            j_dict['Title']=row['Title']

            # as either of the following two might be empty, check before including them
            if isinstance(row['DOI'], str):
                j_dict['DOI']=row['DOI']
            if isinstance(row['PMID'], str):
                j_dict['PMID']=row['PMID']

            # j_as_string = json.dumps(j_dict, indent=4)
            j_as_string = json.dumps(j_dict)
            print(j_as_string, file=output_FH)

        output_FH.close()

if __name__ == "__main__": main()
