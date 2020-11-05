#!/usr/bin/python3
#
# ./augment_names_from_profile.py input.json output.json 
#
# uses the KTH profile API to get the names of users as stored in their profile, augments the records with this data
#
# G. Q. Maguire Jr.
#
# 2020-11-05
#
# Example of runinng the program
# ./augment_names_from_profile.py /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_pid_name_aliases-manually_corrected.json /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json
#
#

import requests, time
import pprint
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


global host	# the base URL
global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests

# 
def initialize(options):
       global host, header, payload

       # styled based upon https://martin-thoma.com/configuration-files-in-python/
       if options.config_filename:
              config_file=options.config_filename
       else:
              config_file='config.json'

       try:
              with open(config_file) as json_data_file:
                     configuration = json.load(json_data_file)
                     key=configuration["KTH_API"]["key"]
                     host=configuration["KTH_API"]["host"]
                     header = {'api_key': key, 'Content-Type': 'application/json', 'Accept': 'application/json' }
                     payload = {}
       except:
              print("Unable to open configuration file named {}".format(config_file))
              print("Please create a suitable configuration file, the default name is config.json")
              sys.exit()


def get_user_by_kthid(kthid):
       # Use the KTH API to get the user information give an orcid
       #"#{$kth_api_host}/profile/v1/kthId/#{kthid}"

       url = "{0}/profile/v1/kthId/{1}".format(host, kthid)
       if Verbose_Flag:
              print("url: {}".format(url))

       r = requests.get(url, headers = header)
       if Verbose_Flag:
              print("result of getting profile: {}".format(r.text))

       if r.status_code == requests.codes.ok:
              page_response=r.json()
              return page_response
       return []

def get_alias(entry):
    e=entry.get('entry', False)
    if not e:
        return []
    #
    list_of_aliases=[]
    aliases=e.get('aliases', False)
    if aliases:
        for a in aliases:
            name=a.get('Name', False)
            if name:
                list_of_aliases.append(name)
    return list_of_aliases

def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="execute test code"
    )

    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print("ARGV      : {}".format(sys.argv[1:]))
        print("VERBOSE   : {}".format(options.verbose))
        print("REMAINING : {}".format(remainder))
        print("Configuration file : {}".format(options.config_filename))

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments must provide input.json output.json\n")
        return

    input_file_name=remainder[0]
    outputfile=remainder[1]

    input=[]
    # read the lines from the JSON file
    with open(input_file_name, 'r') as input_FH:
        for line in input_FH:
            input.append(json.loads(line))

    print("length of input={}".format(len(input)))
    # input lines look like
    # {"kthid":"u1d13i2c","entry":{"orcid":"0000-0002-6066-746X","kth":" (KTH [177], Skolan för informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])","aliases":[{"Name":"Maguire Jr., Gerald Q.","PID":[528381,606323,638177,675824,675849,690825,690828,706514,733621,852295,854051,866222,866274,948397,948549,948742,1068493,1087906,1177431,1180496,1184756,1230455,1314634,1367981,1416571]},{"Name":"Maguire, Gerald Q.","PID":[561069]},{"Name":"Maguire Jr., Gerald","PID":[561509]},{"Name":"Maguire, Gerald Q., Jr.","PID":[913155]}]}}

    print("processing input")
    output=[]
    for entry in input:

        kthid=entry.get('kthid', False)
        # check to see there is a KTHID key present, if not present then skip record
        if not kthid:
            continue
        # if the kthid is "", then there is nothing to do, but copy the entry to the output
        if len(kthid) == 0:
            output.append(entry)
            continue

        user=get_user_by_kthid(kthid)
        # returns a response of the form:
        # user={'defaultLanguage': 'en', 'acceptedTerms': True, 'isAdminHidden': False, 'avatar': {'visibility': 'public'}, '_id': 'u1d13i2c', 'kthId': 'u1d13i2c', 'username': 'maguire', 'homeDirectory': '\\\\ug.kth.se\\dfs\\home\\m\\a\\maguire', 'title': {'sv': 'PROFESSOR', 'en': 'PROFESSOR'}, 'streetAddress': 'ISAFJORDSGATAN 26', 'emailAddress': 'maguire@kth.se', 'telephoneNumber': '', 'isStaff': True, 'isStudent': False, 'firstName': 'Gerald Quentin', 'lastName': 'Maguire Jr', 'city': 'Stockholm', 'postalCode': '10044', 'remark': 'COMPUTER COMMUNICATION LAB', 'lastSynced': '2020-10-28T13:36:56.000Z', 'researcher': {'researchGate': '', 'googleScholarId': 'HJgs_3YAAAAJ', 'scopusId': '8414298400', 'researcherId': 'G-4584-2011', 'orcid': '0000-0002-6066-746X'}, ...
        
        firstName=user.get('firstName', False)
        lastName=user.get('lastName', False)
        if firstName and lastName:
            entry['profile']={'firstName': firstName, 'lastName': lastName }
        elif not firstName and lastName:
            entry['profile']={'lastName': lastName }
        elif firstName and not lastName:
            entry['profile']={'firstName': firstName}
        else:
            print("*** KTHID: {0} missing first and last name in {1}".format(kthid, user))
            print("* alias(es)={0}".format(get_alias(entry)))
        output.append(entry)

    print("length of output={}".format(len(output)))
    with open(outputfile, 'w', encoding='utf-8') as output_FH:
        for n in output:
            j_as_string = json.dumps(n)
            print(j_as_string, file=output_FH)

        output_FH.close()
    return

if __name__ == "__main__": main()
