#!/usr/bin/python3
# -*- coding: utf-8 -*-
# -*- mode: python; python-indent-offset: 4 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To fetch and process thesis information from DiVA for an examiner
#
# Input: ./diva-get_bibmods_theses.py KTHID_of_user
#
# Output: outputs user_name_theses.mods
#
# note that spaces in the user's name are converted to "_"
#
# Example: ./diva-get_bibmods_theses.py u1d13i2c
#
# You can convert the MODS file to BibTeX, for example:
#    xml2bib < Maguire_Jr_theses.mods >Maguire_Jr_theses.bib
#
# xml2bib is available from https://sourceforge.net/projects/bibutils/
#
# Author: Gerald Q. Maguire Jr.
# 2018.05.14
#
#

#  codecs, cStringIO
import csv
import datetime
#from subprocess import call
#import urllib
import urllib.request

import optparse
import sys

import requests

# import the following to be able to redirect stdout output to a file
#   while avoiding problems with unicode
import codecs, locale

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
        print("ARGV      :{}".format(sys.argv[1:]))
        print("VERBOSE   :{}".format(options.verbose))
        print("REMAINING :{}".format(remainder))

    now = datetime.datetime.now()

    if (len(remainder) < 1):
        print("Insuffient arguments\n must provide user's KTHID\n")
        return

    users_kthid = remainder[0]
    users_name = get_usersfamilyname_by_kthid(users_kthid)
    users_name = users_name.replace(" ", "_")

    if Verbose_Flag:
        print('users_kthid = {0}, users_name = {1}'.format(users_kthid,users_name))

    #    print argument_string
    #    call(["wget", argument_string])

    try:

        url='http://kth.diva-portal.org/smash/export.jsf?format=mods&addFilename=true&aq=[[{"examinerId":"' + users_kthid +'"}]]&aqe=[]&aq2=[[{"dateIssued":{"from":"1900","to":"3000"}},{"publicationTypeCode":["dissertation","comprehensiveDoctoralThesis","monographDoctoralThesis","comprehensiveLicentiateThesis","monographLicentiateThesis","studentThesis"]}]]&onlyFullText=false&noOfRows=50000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'

        print("target url is {}".format(url))
        urllib.request.urlretrieve(url, users_name+"_theses.mods")
    except Exception as e:
        print(str(e))

if __name__ == "__main__": main()
