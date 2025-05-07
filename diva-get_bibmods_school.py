#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To fetch and process publication information from DiVA for a school
#
# Input: ./diva-get_bibmods_school.py org_id
#
# Output: outputs org_id_YYYY-YYYY.mods
#
# Example: ./diva-get_bibmods_school.py EECS 2015
#
# You can convert the MODS file to BibTeX, for example:
#    xml2bib xml2bib EECS-2015-2015.mods > EECS-2015-2015.bib
#
# xml2bib is available from https://sourceforge.net/projects/bibutils/
#
# Author: Gerald Q. Maguire Jr.
# 2018.05.27
#
#

import csv
import time
import datetime

#from subprocess import call
#import urllib
import urllib.request

import optparse
import sys

import requests

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
        print("ARGV      :{}".format(sys.argv[1:]))
        print("VERBOSE   :{}".format(options.verbose))
        print("REMAINING :{}".format(remainder))

    school_ids = {
        'KTH': 177,
        'ABE': 5850,
        'CBH': 879224,
        'EECS': 879223,
        'ITM': 6023,
        'SCI': 6091,

        'BIO': 5903,
        'CHE': 5923,
        'CSC': 5956,
        'ECE': 6172,
        'EES': 5977,
        'ICT': 5994,
        'STH': 6161,
    }

    now = datetime.datetime.now()

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide organization ID, such as 879223 or acronym EECS [<start_year> [<end_year>]]\n")
        return

    current_year=str(time.localtime()[0])

    org_id = remainder[0]
    if (not(org_id.isdigit())):     # if a string is entered, then convert it to the appropriate numeric value
        original_org_id=org_id
        org_id=school_ids.get(org_id, -1)
        print('numeric organisation ID = {0}'.format(org_id))
    else:
        original_org_id=str(org_id)

    if (org_id < 0):
          print("Invalid organization ID or acronym, try: ABE, CBH, EECS, ITM, or SCI\n")

    if (len(remainder) < 2):
        start_year = current_year
    else:
        start_year = remainder[1]

    if (len(remainder) < 3):
        end_year = start_year
    else:
        end_year = remainder[2]

    try:

        url='http://kth.diva-portal.org/smash/export.jsf?format=mods&addFilename=true&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":"' + str(start_year) + '","to":"' + str(end_year) + '"}},{"organisationId":' + str(org_id) + ',"organisationId-Xtra":true},{"publicationTypeCode":["bookReview","review","article","artisticOutput","book","chapter","manuscript","collection","other","conferencePaper","patent","conferenceProceedings","report","dataset","dissertation","comprehensiveDoctoralThesis","monographDoctoralThesis","comprehensiveLicentiateThesis","monographLicentiateThesis","studentThesis"]}]]&onlyFullText=false&noOfRows=50000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'

        print("target url is {}".format(url))
        urllib.request.urlretrieve(url, original_org_id+'_'+str(start_year)+ '-' + str(end_year) + '.mods')
    except Exception as e:
        print(str(e))

if __name__ == "__main__": main()







