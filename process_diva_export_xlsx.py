#!/usr/bin/python3
#
# ./process_diva_export_xlsx.py all_student_theses_kth.xlsx
#
# reads in xlsx file and processes each publication
# outputs a new spreadsheet with some data calculated based on the publications
#
# G. Q. Maguire Jr.
#
# 2019.12.03
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

              # read the sheet of Students in
              pubs_df = pd.read_excel(open(input_file, 'rb'))
              column_names=pubs_df.columns
              print("number of columns is {0}".format(len(column_names)))

              languages={}
              title_lengths={}
              pubs_df['Title_len']=0 # add new column and set the default value to zero

              for index, row in  pubs_df.iterrows():
                     pub_lang=row['Language']
                     if pub_lang:
                            increment_dict(pub_lang, languages)
                     #
                     title=row['Title']
                     if title:
                            title_len=len(title)
                            pubs_df.at[index, 'Title_len']=title_len
                            increment_dict(title_len, title_lengths)
              #
              print("frequency of languages ={0}".format(languages))
              print("title_lengths = {0}".format(title_lengths))
                     
              # the following was inspired by the section "Using XlsxWriter with Pandas" on http://xlsxwriter.readthedocs.io/working_with_pandas.html
              # set up the output write
              output_file=input_file[:-4]+"augmented.xlsx"
              writer = pd.ExcelWriter(output_file, engine='xlsxwriter')

              pubs_df.to_excel(writer, sheet_name='augmented')

              # Close the Pandas Excel writer and output the Excel file.
              writer.save()

if __name__ == "__main__": main()

