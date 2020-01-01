#!/usr/bin/python3
#
# ./process_diva_export_xlsx_files.py all_student_theses_kth.xlsx [working_directory]
#
# reads in xlsx file and processes each publication
# gets each of the full-text files and saves them locally in the working_directory (default is '/tmp/theses')
#
# G. Q. Maguire Jr.
#
# 2019.12.03
#

import csv, requests, time
from pprint import pprint
import optparse
import sys
import os
import math                     #  to get isnan()

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
              return

       input_file=remainder[0]

       if (len(remainder) < 2):
              working_directory=remainder[1]
       else:
              working_directory='/tmp/theses'
       
       # read the sheet of Students in
       pubs_df = pd.read_excel(open(input_file, 'rb'))
       column_names=pubs_df.columns
       print("number of columns is {0}".format(len(column_names)))
                     
       if not os.path.exists(working_directory):
              os.makedirs(working_directory)
       for index, row in  pubs_df.iterrows():
              year=row['Year']
              year_directory="{0}/{1}".format(working_directory, year)
              if not os.path.exists(year_directory):
                     os.makedirs(year_directory)

              full_text_link=row['FullTextLink']
              nbn=row['NBN']                          # has the form urn:nbn:se:kth:diva-253051
              diva_prefix,diva_number=nbn.split('-')
              if full_text_link and isinstance(full_text_link, str):
                     print("fetching {0} full text for diva_number={1}".format(year, diva_number))
                     cmd="wget -O {0}/thesis-{1}.pdf {2}".format(year_directory, diva_number, full_text_link)
                     os.system(cmd)

       
if __name__ == "__main__": main()

