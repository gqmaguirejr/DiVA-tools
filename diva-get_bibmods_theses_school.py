#!/usr/bin/python3
# -*- coding: utf-8 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To fetch and process thesis information from DiVA for a school
#
# Input: ./diva-get_bibmods_theses_school.py org_id
#
# Output: outputs org_id_theses-YYYY-YYYY.mods
#
# Example: ./diva-get_bibmods_theses_school.py EECS 2015
#
# You can convert the MODS file to BibTeX, for example:
#    xml2bib xml2bib EECS_theses-2015-2015.mods > EECS_theses-2015-2015.bib
#
# xml2bib is available from https://sourceforge.net/projects/bibutils/
#
# Author: Gerald Q. Maguire Jr.
# 2018.05.27
#
# Updated 2019.05.09 to support python3
#
#

import csv
#import codecs, cStringIO
import time
import datetime

#from subprocess import call
#import urllib
import urllib3

# import the shutil library to have optimized copy of file like objects
import shutil

import optparse
import sys

import requests

def empty_school_tuple():
    return {'Thesis_count': 0, 'Abstracts_eng_swe': 0, 'Abstracts_eng': 0, 'Abstracts_swe': 0, 'Abstracts_missing': 0,}

Schools = dict()

def get_usersfamilyname_by_kthid(users_kthid):
    url='https://www.kth.se/api/profile/1.1/' + users_kthid
    r = requests.get(url)

    if r.status_code == requests.codes.ok:
        page_response=r.json()
        familyname=page_response['familyName']
        return familyname
    return []


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
        print('ARGV      :{0}'.format(sys.argv[1:]))
        print('VERBOSE   :{0}'.format(options.verbose))
        print('REMAINING :{0}'.format(remainder))

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

    #users_name = get_usersfamilyname_by_kthid(users_kthid)
    #users_name = users_name.replace(" ", "_")

    #if Verbose_Flag:
    #    print('users_kthid = {0}, users_name = {1}'.format(users_kthid,users_name))

    #    print argument_string
    #    call(["wget", argument_string])

    try:

        url='http://kth.diva-portal.org/smash/export.jsf?format=mods&addFilename=true&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":"' + str(start_year) + '","to":"' + str(end_year) + '"}},{"organisationId":' + str(org_id) + ',"organisationId-Xtra":true},{"publicationTypeCode":["dissertation","comprehensiveDoctoralThesis","monographDoctoralThesis","comprehensiveLicentiateThesis","monographLicentiateThesis","studentThesis"]}]]&onlyFullText=false&noOfRows=50000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'

        print('url={}'.format(url))
        path=original_org_id+'_theses-'+str(start_year)+ '-' + str(end_year) + '.mods'
        http = urllib3.PoolManager()
        with http.request('GET', url, preload_content=False) as r, open(path, 'wb') as out_file:       
            shutil.copyfileobj(r, out_file)

    except Exception as e:
        print(str(e))

if __name__ == "__main__": main()
