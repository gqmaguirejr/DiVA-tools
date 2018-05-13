#!/usr/bin/python
# -*- coding: utf-8 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To fetch and process thesis information from DiVA for yearA to yearB
#            (To get information about keywords and abstracts)
#
# Input: ./diva-theses-year-range.py --start yearA --end yearB
#
# Output: outputs a spreadhseet of the information
#
# note that "year" should be in the form dddd
# 
# note that the "-v" (verbose) argument will generate a lot of output
#
# Author: Gerald Q. Maguire Jr.
# 2016.04.10
#
#

import csv, codecs, cStringIO
import datetime
#from subprocess import call
import urllib

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def empty_school_tuple():
    return {'Thesis_count': 0, 'Abstracts_eng_swe': 0, 'Abstracts_eng': 0, 'Abstracts_swe': 0, 'Abstracts_missing': 0,}

Schools = dict()

import optparse
import sys
# import the following to be able to redirect stdout output to a file
#   while avoiding problems with unicode
import codecs, locale

parser = optparse.OptionParser()
parser.add_option('-s', '--start', 
                  dest="starting_year", 
                  default="9999",
                  )
parser.add_option('-e', '--end', 
                  dest="ending_year", 
                  default="9999",
                  )

parser.add_option('-o', '--output', 
                  dest="output_filename", 
                  default="default.out",
                  )

parser.add_option('-v', '--verbose',
                  dest="verbose",
                  default=False,
                  action="store_true",
                  help="Print lots of output to stdout"
                  )

options, remainder = parser.parse_args()

Verbose_Flag=options.verbose
if Verbose_Flag:
    print 'ARGV      :', sys.argv[1:]
    print 'VERBOSE   :', options.verbose
    print 'START     :', options.starting_year
    print 'END       :', options.ending_year
    print 'OUTPUT    :', options.output_filename
    print 'REMAINING :', remainder

               
#    headings = ['Year', 'School', 'Thesis_count', 'Abstracts_eng_swe', 'Abstracts_eng', 'Abstracts_swe', 'Abstracts_missing', 'Abstracts_nor', 'Abstracts_ger', 'Keywords_eng_swe', 'Keywords_eng', 'Keywords_swe', 'Keywords_missing']


now = datetime.datetime.now()

if (int(options.starting_year)) == 9999:
    starting_year=now.year
else:
    starting_year = int(options.starting_year)

if (int(options.ending_year)) == 9999:
    ending_year=now.year
else:
    ending_year = int(options.ending_year)

if (starting_year > ending_year):
    print "Error: starting year is after ending year, using ending year"
    starting_year = ending_year

if (ending_year < starting_year  ):
    print "Error: ending year is before starting year, using starting year"
    ending_year = starting_year

if Verbose_Flag:
    print "starting_year " +  str(starting_year)
if Verbose_Flag:
    print "ending_year " +    str(ending_year)

for year in range(starting_year,ending_year+1):
    if Verbose_Flag:
        print "year " + str(year)

    quoted_year = '"' + str(year) + '"'

    try:
        url = 'http://kth.diva-portal.org/smash/export.jsf?format=mods&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":' + quoted_year + ',"to":' + quoted_year + '}},{"publicationTypeCode":["studentThesis"]}]]&onlyFullText=false&noOfRows=5000&sortOrder=title_sort_asc'
        print url
        urllib.urlretrieve(url, str(year)+".mods")
    except Exception as e:
        print(str(e))
