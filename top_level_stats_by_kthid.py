#!/usr/bin/python3
#
# ./top_level_stats_by_kthid.py spreadsheet.xlsx
#
# Outputs a new file with the name suffixed by '_with_stats' with the statistics added in new columns
#
# G. Q. Maguire Jr.
#
# 2020-02-22
#
# for each thesis in the spreadsheet update a set of columns with the top level statistics for an author
#
# Example of runinng the program
# ./top_level_stats_by_kthid.py ~/Working/RAE-2020/cst_citations-augmented.xlsx 
#
# the above spreadsheet has Sheet1 with a column with the author's KTHID
# there is also a sheet called "Pubs" that contains all of the KTH publications extracted from DiVA using:
# wget -O unspecified-excluding-theses.csv 'https://kth.diva-portal.org/smash/export.jsf?format=csvall2&addFilename=true&aq=[[]]&aqe=[]&aq2=[[{"publicationTypeCode":["bookReview","review","article","artisticOutput","book","chapter","collection","other","conferencePaper","patent","conferenceProceedings","report","dataset"]}]]&onlyFullText=false&noOfRows=5000000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'
#
# On 2020-02-04 the above extracted 92521 publications
# broken down by PublicationType
# 803 Artikel, forskningsöversikt
# 52865 Artikel i tidskrift
#   369 Artikel, recension
#   573 Bok
#    30 Dataset
#  3599 Kapitel i bok, del av antologi
# 29162 Konferensbidrag
#    25 Konstnärlig output
#   547 Övrigt
#   490 Patent
#   227 Proceedings (redaktörskap)
#     1 PublicationType
#  3566 Rapport
#   263 Samlingsverk (redaktörskap)
#
# broken down by ContentType
#     10 Granskad
#     15 Ogranskad
#   2426 Övrig (populärvetenskap, debatt, mm)
#  11612 Övrigt vetenskapligt
#  78426 Refereegranskat
# There were also 31 unspecified


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

# use BeautifulSoup for parsing the HTML of the web page
from bs4 import BeautifulSoup

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

# to normalize unicoded strings
import unicodedata

#############################
###### EDIT THIS STUFF ######
#############################

# PublicationType in KTH dataset (excluding student theses and 3rd cycle theses/disserations)are:
# Artikel, forskningsöversikt
# Artikel i tidskrift
# Artikel, recension
# Bok
# Dataset
# Kapitel i bok, del av antologi
# Konferensbidrag
# Konstnärlig output
# Övrigt
# Patent
# Proceedings (redaktörskap)
# Rapport
# Samlingsverk (redaktörskap)

# ContentType
# Granskad
# Ogranskad
# Övrig (populärvetenskap, debatt, mm)
# Övrigt vetenskapligt
# Refereegranskat

# existing combinations are:
# PublicationType	ContentType
# Artikel, forskningsöversikt	Övrig (populärvetenskap, debatt, mm)
# Artikel, forskningsöversikt	Övrigt vetenskapligt
# Artikel, forskningsöversikt	Refereegranskat
# Artikel i tidskrift	Övrig (populärvetenskap, debatt, mm)
# Artikel i tidskrift	Övrigt vetenskapligt
# Artikel i tidskrift	Refereegranskat
# Artikel, recension	Övrig (populärvetenskap, debatt, mm)
# Artikel, recension	Övrigt vetenskapligt
# Artikel, recension	Refereegranskat
# Bok	Övrig (populärvetenskap, debatt, mm)
# Bok	Övrigt vetenskapligt
# Bok	Refereegranskat
# Dataset	
# Kapitel i bok, del av antologi	Övrig (populärvetenskap, debatt, mm)
# Kapitel i bok, del av antologi	Övrigt vetenskapligt
# Kapitel i bok, del av antologi	Refereegranskat
# Konferensbidrag	Övrig (populärvetenskap, debatt, mm)
# Konferensbidrag	Övrigt vetenskapligt
# Konferensbidrag	Refereegranskat
# Konstnärlig output	Granskad
# Konstnärlig output	Ogranskad
# Övrigt	Övrig (populärvetenskap, debatt, mm)
# Övrigt	Övrigt vetenskapligt
# Övrigt	Refereegranskat
# Patent	Övrig (populärvetenskap, debatt, mm)
# Proceedings (redaktörskap)	Övrig (populärvetenskap, debatt, mm)
# Proceedings (redaktörskap)	Övrigt vetenskapligt
# Proceedings (redaktörskap)	Refereegranskat
# Rapport	Övrig (populärvetenskap, debatt, mm)
# Rapport	Övrigt vetenskapligt
# Rapport	Refereegranskat
# Samlingsverk (redaktörskap)	Övrig (populärvetenskap, debatt, mm)
# Samlingsverk (redaktörskap)	Övrigt vetenskapligt
# Samlingsverk (redaktörskap)	Refereegranskat

def get_stats(kthid,pubs_df):
    #print("kthid is {}".format(kthid))
    stats_for_author=dict()
    for index, row in pubs_df.iterrows():
        name_entry=row['Name']
        if  type(name_entry) == str and len(name_entry) > 0:
            names=name_entry.split(';')
            for n in names:
                match_string="[{}]".format(kthid)
                #print("match_string={}".format(match_string=))
                if n.find(match_string) >=0:
                    pub_type=row['PublicationType']
                    content_type=row['ContentType']
                    pub_type=pub_type+'-'+content_type
                    count_for_type=stats_for_author.get(pub_type,0)
                    stats_for_author[pub_type]=count_for_type+1
        #else:
        #    print("index={0}, PID={1}, name_entry={2} and is of type {3}".format(index, row['PID'], name_entry, type(name_entry)))

    return stats_for_author

def diff_pubs(pubs_df1, pubs_df2):
    # list the entries of the first that are not in the 2nd
    len1=len(pubs_df1)
    len2=len(pubs_df2)
    for index1, row1 in pubs_df1.iterrows():
        pid_entry=row1['PID']
        found_pid=False
        for index2, row2 in pubs_df2.iterrows():
            if pid_entry == row2['PID']:
                found_pid=True
                break
        if not found_pid:
            # print("Missing PID={0} and row1={1}".format(pid_entry, row1))
            print("Missing PID={0} row1={1}".format(pid_entry, row1['Title']))
    return

def add_columns_initialize_to_zero(data_frame, list_of_new_columns):
    for c in list_of_new_columns:
        data_frame[c]=''
    return data_frame

def main():
    global Verbose_Flag

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
    diva_df = pd.read_excel(open(spreadsheet_file, 'rb'), sheet_name='Sheet1')
    #if Verbose_Flag:
    #    print("diva_df={}".format(diva_df))
    pubs_df = pd.read_excel(open(spreadsheet_file, 'rb'), sheet_name='Pubs')

    new_column_name=[
        'Artikel, forskningsöversikt-Övrig (populärvetenskap, debatt, mm)',
        'Artikel, forskningsöversikt-Övrigt vetenskapligt',
        'Artikel, forskningsöversikt-Refereegranskat',
        'Artikel i tidskrift-Övrig (populärvetenskap, debatt, mm)',
        'Artikel i tidskrift-Övrigt vetenskapligt',
        'Artikel i tidskrift-Refereegranskat',
        'Artikel, recension-Övrig (populärvetenskap, debatt, mm)',
        'Artikel, recension-Övrigt vetenskapligt',
        'Artikel, recension-Refereegranskat',
        'Bok-Övrig (populärvetenskap, debatt, mm)',
        'Bok-Övrigt vetenskapligt',
        'Bok-Refereegranskat',
        'Dataset',
        'Kapitel i bok, del av antologi-Övrig (populärvetenskap, debatt, mm)',
        'Kapitel i bok, del av antologi-Övrigt vetenskapligt',
        'Kapitel i bok, del av antologi-Refereegranskat',
        'Konferensbidrag-Övrig (populärvetenskap, debatt, mm)',
        'Konferensbidrag-Övrigt vetenskapligt',
        'Konferensbidrag-Refereegranskat',
        'Konstnärlig output-Granskad',
        'Konstnärlig output-Ogranskad',
        'Övrigt-Övrig (populärvetenskap, debatt, mm)',
        'Övrigt-Övrigt vetenskapligt',
        'Övrigt-Refereegranskat',
        'Patent-Övrig (populärvetenskap, debatt, mm)',
        'Proceedings (redaktörskap)-Övrig (populärvetenskap, debatt, mm)',
        'Proceedings (redaktörskap)-Övrigt vetenskapligt',
        'Proceedings (redaktörskap)-Refereegranskat',
        'Rapport-Övrig (populärvetenskap, debatt, mm)',
        'Rapport-Övrigt vetenskapligt',
        'Rapport-Refereegranskat',
        'Samlingsverk (redaktörskap)-Övrig (populärvetenskap, debatt, mm)',
        'Samlingsverk (redaktörskap)-Övrigt vetenskapligt',
        'Samlingsverk (redaktörskap)-Refereegranskat',
    ]

    diva_df=add_columns_initialize_to_zero(diva_df, new_column_name)

    for index, row in diva_df.iterrows():
        kthid=row['KTHID']
        if type(kthid) != str:
            continue

        print("kthid is {}".format(kthid))
        stats=get_stats(kthid,pubs_df)
        print("stats={}".format(stats))
        for stat in stats:
            diva_df.loc[diva_df['KTHID'] == kthid, stat] = stats[stat]

        #if (index > 4):
        #    break;

    # set up the output write
    writer = pd.ExcelWriter(spreadsheet_file[:-5]+'_with_stats.xlsx', engine='xlsxwriter')
    diva_df.to_excel(writer, sheet_name='Stats')
    writer.save()
              
if __name__ == "__main__": main()
