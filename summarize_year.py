#!/usr/bin/python
# -*- coding: utf-8 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To summarize the data from theses_XXXX.csv for yearA to yearB
#            (To collect information about keywords and abstracts)
#
# reads a csv file with lines of the form:
#Year,School,Thesis_count,Abstracts_eng_swe,Abstracts_eng,Abstracts_swe,Abstracts_missing,Abstracts_nor,Abstracts_ger,Keywords_eng_swe,Keywords_eng,Keywords_swe,Keywords_missing
#2010,"KTH,Skolan för arkitektur och samhällsbyggnad (ABE)",1,0,1,0,0,0,0,0,1,0,0
#...
#
#
# Input: ./summarize_year.py --start yearA --end yearB
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
#
#
import csv,codecs,cStringIO

class UTF8Recoder:
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)
    def __iter__(self):
        return self
    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)
    def next(self):
        '''next() -> unicode
        This function reads and returns the next line as a Unicode string.
        '''
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]
    def __iter__(self):
        return self

class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        '''writerow(unicode) -> None
        This function takes a Unicode string and encodes it to the output.
        '''
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)

def empty_school_tuple():
    return {'Year': 0, 'Thesis_count': 0, 'Abstracts_eng_swe': 0, 'Abstracts_eng': 0, 'Abstracts_swe': 0, 'Abstracts_missing': 0, 'Abstracts_nor': 0, 'Abstracts_ger': 0,  'Keywords_eng_swe':0, 'Keywords_eng':0, 'Keywords_swe':0, 'Keywords_missing':0, }

def trim_school_name(long_name):
    if long_name is None:
        return "Unknown school"
    if len(long_name) == 0:
        return "Unknown school"
    if long_name.startswith('KTH,', 0, 4):
        shorter_name=long_name[4:]
        if Verbose_Flag:
            print "shorter_name :" + shorter_name
        found=shorter_name.find("),")
        if (found >= 0):
            return shorter_name[0:found+1]
        return  shorter_name
    else:
        return long_name

import optparse
import sys
import locale
import datetime

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


def process_one_year(year):
    global Schools
    global Header
    input_filename = 'theses_'+str(year)+'.csv'
    line_number=0
    try:
        with open(input_filename,'rb') as input_file:
            reader = UnicodeReader(input_file )
            for line in reader:
                if (line_number == 0):
                    if Verbose_Flag:
                        print "Header :" + str(line)
                    Header = line
                    line_number = line_number+1
                    continue
                Year = int( line[0] )

                School = line[1]
                publisher_name = trim_school_name(School)
                if publisher_name not in Schools:
                    Schools[publisher_name] = empty_school_tuple()

                    if Verbose_Flag:
                        print Schools

                if Schools[publisher_name]['Year'] == 0:
                    Schools[publisher_name]['Year'] = Year


                Thesis_count = int( line[2] )
                Schools[publisher_name]['Thesis_count'] = int(Schools[publisher_name]['Thesis_count']) + Thesis_count

                Abstracts_eng_swe = int( line[3] )
                Schools[publisher_name]['Abstracts_eng_swe'] = int(Schools[publisher_name]['Abstracts_eng_swe']) + Abstracts_eng_swe

                Abstracts_eng = int( line[4] )
                Schools[publisher_name]['Abstracts_eng'] = int(Schools[publisher_name]['Abstracts_eng']) + Abstracts_eng

                Abstracts_swe = int( line[5] )
                Schools[publisher_name]['Abstracts_swe'] = int(Schools[publisher_name]['Abstracts_swe']) + Abstracts_swe

                Abstracts_missing = int( line[6] )
                Schools[publisher_name]['Abstracts_missing'] = int(Schools[publisher_name]['Abstracts_missing']) + Abstracts_missing

                Abstracts_nor = int( line[7] )
                Schools[publisher_name]['Abstracts_nor'] = int(Schools[publisher_name]['Abstracts_nor']) + Abstracts_nor

                Abstracts_ger = int( line[8] )
                Schools[publisher_name]['Abstracts_ger'] = int(Schools[publisher_name]['Abstracts_ger']) + Abstracts_ger

                Keywords_eng_swe = int( line[9] )
                Schools[publisher_name]['Keywords_eng_swe'] = int(Schools[publisher_name]['Keywords_eng_swe']) + Keywords_eng_swe

                Keywords_eng = int( line[10] )
                Schools[publisher_name]['Keywords_eng'] = int(Schools[publisher_name]['Keywords_eng']) + Keywords_eng

                Keywords_swe = int( line[11] )
                Schools[publisher_name]['Keywords_swe'] = int(Schools[publisher_name]['Keywords_swe']) + Keywords_swe

                Keywords_missing = int( line[12] )
                Schools[publisher_name]['Keywords_missing'] = int(Schools[publisher_name]['Keywords_missing']) + Keywords_missing

    except csv.Error, e:
        sys.exit('file %s, line %d: %s' % (filename, reader.line_num, e))
    else:
        return 1

def output_one_year(year, writer):
    global Schools
    global Header
    global Header_has_been_output

    if not Header_has_been_output:
        writer.writerow(Header)
        Header_has_been_output = True

    keylist = Schools.keys()

    keylist.sort()
    if Verbose_Flag:
        print "keylist : "
        print keylist

    for key in keylist:
        if Verbose_Flag:
            print "key :"
            print key

        entry=Schools[key]
        if Verbose_Flag:
            print entry

        out_row = [str(entry['Year']), key, str(entry['Thesis_count']), str(entry['Abstracts_eng_swe']), str(entry['Abstracts_eng']), str(entry['Abstracts_swe']), str(entry['Abstracts_missing']), str(entry['Abstracts_nor']), str(entry['Abstracts_ger']),  str(entry['Keywords_eng_swe']), str(entry['Keywords_eng']), str(entry['Keywords_swe']), str(entry['Keywords_missing']),]

        writer.writerow(out_row)

Verbose_Flag=options.verbose
if Verbose_Flag:
    print 'ARGV      :', sys.argv[1:]
    print 'VERBOSE   :', options.verbose
    print 'START     :', options.starting_year
    print 'END       :', options.ending_year
    print 'OUTPUT    :', options.output_filename
    print 'REMAINING :', remainder

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

output_filename = 'schools_'+str(starting_year)+'_'+str(ending_year)+'.csv'
output_file = open(output_filename,'wb')
writer = UnicodeWriter(output_file,quoting=csv.QUOTE_ALL)

Header_has_been_output = False

for year in range(starting_year,ending_year+1):
    if Verbose_Flag:
        print "year " + str(year)

    Schools = dict()
    process_one_year(year)
    output_one_year(year, writer)
