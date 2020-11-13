#!/usr/bin/python3
#
# ./check_augmented_names.py kthids.csv augmented_author_data.json
#
# The program outputs the following file:
#    missing_kthids.json
#
# G. Q. Maguire Jr.
#
# 2020-11-13
#
# Example of runinng the program
# ./check_augmented_names.py /z3/maguire/SemanticScholar/KTH_DiVA/z1uniq.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json
#
# Note that the z1uniq.csv was computed by finding the [u1xxxxxx] strings in the csv file, saving them as z1.csv and then doing a:
# cat z1.csv | sort | uniq >z1uniq.csv
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


def main():
    global Verbose_Flag
    global diva_name_info_by_kthid

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
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)

    initialize(options)

    if (len(remainder) < 2):
        print("Insuffient arguments must provide  kthids.csv augmented_author_data.json\n")
        return

    kthids_file=remainder[0]
    augmented_data_filename=remainder[1]
        
    kthids=set()
    # read the lines from the csv file
    with open(kthids_file, 'r') as kthids_FH:
        for line in kthids_FH:
            line=line.strip()
            id=line[1:-1]
            if len(id) != 8:
                print("error in line={0}".format(line))
            else:
                kthids.add(id)
            
    print("length of kthids={}".format(len(kthids)))

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    augmented=[]
    # read the lines from the JSON file
    with open(augmented_data_filename, 'r') as augmented_FH:
        for line in augmented_FH:
            augmented.append(json.loads(line))

    print("length of augmented={}".format(len(augmented)))


    found_kthids=set()
    for entry in augmented:
        # note that kthid and profile are at the top level of the incoming author_entry
        kthid=entry.get('kthid', False)
        if not kthid:   #  if no kthid, then skip this
            continue
        else:
            found_kthids.add(kthid)

    print("length of found_kthids={0}".format(len(found_kthids)))

    missing_kthids=set()
    for id in kthids:
        if id in found_kthids:
            #print("found id {0} in augmented data".format(id))
            continue
        else:
            missing_kthids.add(id)
            print("missing id {0} in augmented data".format(id))

    print("KTHIDs in original csv of publications={0}, found in augmented={1}, missing={2}".format(len(kthids), len(found_kthids), len(missing_kthids)))

    if len(missing_kthids) > 0 :
        missingfilename="missing_kthids.json".format()
        with open(missingfilename, 'w', encoding='utf-8') as ids_FH:
            for id in sorted(missing_kthids):
                id_dict=dict()
                profile=dict()

                user=get_user_by_kthid(id)
                # returns a response of the form:
                # user={'defaultLanguage': 'en', 'acceptedTerms': True, 'isAdminHidden': False, 'avatar': {'visibility': 'public'}, '_id': 'u1d13i2c', 'kthId': 'u1d13i2c', 'username': 'maguire', 'homeDirectory': '\\\\ug.kth.se\\dfs\\home\\m\\a\\maguire', 'title': {'sv': 'PROFESSOR', 'en': 'PROFESSOR'}, 'streetAddress': 'ISAFJORDSGATAN 26', 'emailAddress': 'maguire@kth.se', 'telephoneNumber': '', 'isStaff': True, 'isStudent': False, 'firstName': 'Gerald Quentin', 'lastName': 'Maguire Jr', 'city': 'Stockholm', 'postalCode': '10044', 'remark': 'COMPUTER COMMUNICATION LAB', 'lastSynced': '2020-10-28T13:36:56.000Z', 'researcher': {'researchGate': '', 'googleScholarId': 'HJgs_3YAAAAJ', 'scopusId': '8414298400', 'researcherId': 'G-4584-2011', 'orcid': '0000-0002-6066-746X'}, ...
        
                firstName=user.get('firstName', False)
                lastName=user.get('lastName', False)
                if firstName and lastName:
                    profile={'firstName': firstName, 'lastName': lastName }
                elif not firstName and lastName:
                    profile={'lastName': lastName }
                elif firstName and not lastName:
                    profile={'firstName': firstName}
                else:
                    print("*** KTHID: {0} missing first and last name in {1}".format(id, user))

                user_researcher=user.get('researcher', False)
                if user_researcher:
                    user_orcid=user_researcher.get('orcid', False)
                else:
                    user_orcid=False

                #"entry":{"kth":"(KTH [177], Centra [12851], Nordic Institute for Theoretical Physics NORDITA [12850])","orcid":"","aliases":[{"Name":"Anastasiou, Alexandros","PID":[1130981,1255535]},{"Name":"Anastasiou, A.","PID":[1269339]}]}}

                id_dict[id]={"kthid": id, "orcid": user_orcid, "profile": profile, "entry": {"kth": False, "orcid": False, "aliases": []}}
                j_as_string = json.dumps(id_dict[id])
                print(j_as_string, file=ids_FH)

        ids_FH.close()
    return

if __name__ == "__main__": main()
