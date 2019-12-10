#!/usr/bin/python3
#
# ./pub_language.py xxxx.xlsx
#
# reads in xlsx file and processes each publication
# outputs a dictionary with some statistical data about the use languages for each type of document
#
# G. Q. Maguire Jr.
#
# 2019.12.10
#
# example:
# ./pub_language.py /tmp/KTH-2012-2019-pub-excluding-theses-and-disserations.xlsx
#

import csv, requests, time
from pprint import pprint
import optparse
import sys

from io import StringIO, BytesIO

from lxml import html

import json

# Use Python Pandas to create XLSX files
import pandas as pd

def get_dict(entry, dictionary):
       e=dictionary.get(entry, [])
       return e

def increment_dict(entry, dictionary):
       e=dictionary.get(entry, [])
       if e:
              v=e+1
       else:
              v=1
       dictionary[entry]=v
       return v


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
              print("Insuffient arguments\n must provide input_file\n")
       else:
              input_file=remainder[0]

              # read the sheet of publications
              pubs_df = pd.read_excel(open(input_file, 'rb'))
              column_names=pubs_df.columns
              print("number of columns is {0}".format(len(column_names)))


              #pubs_df['Title_len']=0 # add new column and set the default value to zero

              #languages={}
              dictionaries={}

              pub_types={}
              pub_content_types={}

              for index, row in  pubs_df.iterrows():
                     pub_type=row['PublicationType']
                     pub_content_type=row['ContentType']
                     
                     # if the field is empty do not process
                     if pub_type and isinstance(pub_type, str) and pub_content_type and isinstance(pub_content_type, str):
                            if not dictionaries.get(pub_type, []):
                                   dictionaries[pub_type]={}
                            dictionaries[pub_type][pub_content_type]={}

              #print("dictionaries={0}".format(dictionaries))

              for index, row in  pubs_df.iterrows():
                     pub_lang=row['Language']
                     pub_type=row['PublicationType']
                     pub_content_type=row['ContentType']

                     if pub_lang and pub_type and isinstance(pub_type, str) and pub_content_type and isinstance(pub_content_type, str):
                            increment_dict(pub_lang, dictionaries[pub_type][pub_content_type])
              
              print("dictionaries={0}".format(dictionaries))
              
if __name__ == "__main__": main()

