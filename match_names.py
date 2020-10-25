#!/usr/bin/python3
#
# ./match_names.py targets.json matches_corpus_N.json
#
# The shard number N (is the digits indicating the piece of the corpus) - for the file s2-corpus-186 N is 186
# The program outputs the following files:
#  name.json - this contains JSON entries of the form:
#                          diva_name, S2_author_name, S2_author_ID, PID
#
# G. Q. Maguire Jr.
#
# 2020-10-25
#
# Example of runinng the program
# ./match_names.py matches_corpus_186.json
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

def remove_diva_entry_pid(targets, pid):
    for i in range(0,len(targets)):
        if targets[i]['PID'] == pid:
            del targets[i]
            return targets


def matched_diva_entry_doi(targets, doi):
    j_dict=dict()
    for t in targets:
        diva_doi=t.get('DOI', False)
        if diva_doi == doi:
            j_dict['PID']=t['PID']
            j_dict['Name']=t['Name']
            j_dict['DOI']=diva_doi
            pmid=t.get('PMID', False)
            if pmid:
                j_dict['PMID']=pmid
    return j_dict

def matched_diva_entry_pmid(targets, pmid):
    j_dict=dict()
    for t in targets:
        diva_pmid=t.get('PMID', False)
        if diva_pmid == pmid:
            j_dict['PID']=t['PID']
            j_dict['Name']=t['Name']
            j_dict['PMID']=pmid
            diva_doi=t.get('DOI', False)
            if diva_doi:
                j_dict['DOI']=diva_doi
    return j_dict

# the function below is from https://www.guyrutenberg.com/2008/12/15/damerau-levenshtein-distance-in-python/
# Note that xrange (a python2 function) was replaced by range (a python3 equivalent)
# Compute the Damerau-Levenshtein distance between two given strings (s1 and s2)
def damerau_levenshtein_distance(s1, s2):
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = j+1
    #
    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition
    #
    return d[lenstr1-1,lenstr2-1]


def find_s2_name_in_diva_name(s2_name, diva_name):
    global Verbose_Flag

    kthid=False
    # a single diva_name is of the form: last_name, first_name [u1xxxxx] (KTH ....)
    # an s2_name is of the form: first_name last_name
    # or
    # first_name middle_name last_name
    first_left_paren=diva_name.find('(')
    first_left_bracket=diva_name.find('[')
    if first_left_bracket > 0 and first_left_paren > first_left_bracket: # last_name, first_name [u1xxxxx] (KTH ....)
        diva_name=diva_name[:first_left_paren-1].strip()

        pattern = re.compile('[0-9a-z]*\]')
        look_for_kthid=pattern.match(diva_name,first_left_bracket+1)
        if look_for_kthid:
            kthid=look_for_kthid.group(0)[:-1]
            print("kthid={}".format(kthid))

        trimmed_diva_name=diva_name[:first_left_bracket-1].strip()
        split_diva_name=trimmed_diva_name.split(',')
        reordered_diva_name=split_diva_name[1].strip() + ' ' + split_diva_name[0].strip()
        print("reordered_diva_name={}".format(reordered_diva_name))
        if len(reordered_diva_name) >= len(s2_name):
            offset=reordered_diva_name.find(s2_name)
            if offset >= 0:
                n_dict=dict()
                n_dict['diva_name']=reordered_diva_name
                n_dict['S2_author_name']=s2_name
                if kthid:
                    n_dict['kthid']=kthid
                return n_dict
            # if the names are close, then guess that they are the same
            if damerau_levenshtein_distance(reordered_diva_name, s2_name) < 2:
                n_dict=dict()
                n_dict['diva_name']=reordered_diva_name
                n_dict['S2_author_name']=s2_name
                if kthid:
                    n_dict['kthid']=kthid
                return n_dict
        return False

def split_name_on_semicolon(name_str):
    new_names=[]
    for i in range(0, name_str.count(',')):
        first_semicolon=name_str.find(';')
        if first_semicolon < 0:
            new_names.append(name_str)
            return new_names
        else:
            first_left_paren=name_str.find('(')
            if (0 <= first_semicolon ) and (first_semicolon < first_left_paren):
                new_names.append(name_str[:first_semicolon-1])
                name_str=name_str[first_semicolon+1:]
    #
    return new_names

def split_names_on_semicolon(names):
    wn=[]
    for n in names:
        wn.extend(split_name_on_semicolon(n))
    return wn


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
        print("Insuffient arguments must provide matches_corpus_N.json\n")
        return

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    matches_corpus_file=remainder[0]

    matches=[]
    # read the lines from the JSON file
    with open(matches_corpus_file, 'r') as matches_FH:
        for line in matches_FH:
            matches.append(json.loads(line))

    print("length of matches={}".format(len(matches)))

    #  matches_corpus_N.json - this contains JSON entries of the form:
    #                          PID, Name, DOI, PMID, S2_publication_ID, S2_authors
    # the match entries are of the form
    #    {"PID": 1262880.0,
    #     "Name": "Ong, Yen Chin [u1qnpub1] (KTH [177], Centra [12851], Nordic Institute for Theoretical Physics NORDITA [12850]) (Center for Gravitation and Cosmology, College of Physical Science and Technology, Yangzhou University, Yangzhou 225009, China; School of Physics and Astronomy, Shanghai Jiao Tong University, Shanghai 200240, China)",
    #     "DOI": "10.1016/j.physletb.2018.08.065",
    #     "S2_publication_ID": "b972a4e41ca0a561b0cfa4abeb6316c9681052a8",
    #     "S2_authors": [{"name": "Yen Chin Ong", "ids": ["31287468"]}]}
    #	{"PID": 769565.0,
    #    "Name": "Li, Fusheng [u16naruo] [0000-0003-3455-0855] (KTH [177], Skolan f\u00f6r kemivetenskap (CHE) [5923], Kemi [5924]);Li, Lin [u1yny31f] (KTH [177], Skolan f\u00f6r kemivetenskap (CHE) [5923], Kemi [5924], Organisk kemi [5928]);Tong, Lianpeng [u1zevfmf] (KTH [177], Skolan f\u00f6r kemivetenskap (CHE) [5923], Kemi [5924], Organisk kemi [5928]);Daniel, Quentin [u17aeo5z] (KTH [177], Skolan f\u00f6r kemivetenskap (CHE) [5923], Kemi [5924]);G\u00f6thelid, Mats [u1uq5dqb] (KTH [177], Skolan f\u00f6r informations- och kommunikationsteknik (ICT) [5994], Material- och nanofysik [13000], Materialfysik, MF [13304]);Sun, Licheng [u1umfd9h] [0000-0002-4521-2870] (KTH [177], Skolan f\u00f6r kemivetenskap (CHE) [5923], Kemi [5924], Organisk kemi [5928]) (KTH [177], Skolan f\u00f6r kemivetenskap (CHE) [5923], Centra [5948], Molekyl\u00e4r elektronik, CMD [5950])",
    #	 "DOI": "10.1039/c4cc06959e",
    #    "PMID": 25265253,
    #    "S2_publication_ID": "e075226fec9a3802f259a3d6c25606c1d5cac9b0",
    #    "S2_authors": [{"name": "Fusheng Li", "ids": ["46494267"]}, {"name": "Lin Li", "ids": ["50703860"]}, {"name": "Lianpeng Tong", "ids": ["33454012"]}, {"name": "Quentin Daniel", "ids": ["145011312"]}, {"name": "Mats G\u00f6thelid", "ids": ["12846166"]}, {"name": "Licheng Sun", "ids": ["143649634"]}]}

    print("process matches")
    name_info=[]
    for m in matches:
        diva_name=m['Name']
        s2_authors=m['S2_authors']

        if len(s2_authors) == 1:
            found_name=find_s2_name_in_diva_name(s2_authors[0]['name'], diva_name)
            if found_name:
                print("found s2_author id: {0} for {1}".format(s2_authors[0]['ids'], s2_authors[0]['name']))
                found_name['S2_author_ID']=s2_authors[0]['ids']
                found_name['PID']=int(m['PID'])
                name_info.append(found_name)
                continue
            else:
                print("not found s2_author id: {0} for {1}".format(s2_authors[0]['ids'], s2_authors[0]['name']))
                continue

        if len(s2_authors) > 1:
            if diva_name.find(');') >=0:
                names=diva_name.split(');')
            else:
                names=diva_name
            names=split_names_on_semicolon(names)

        if len(s2_authors) !=  len(names):
            print("len(s2_authors={0}, length of split names={1}, diva_name={2}".format(len(s2_authors), len(names), diva_name))
            pp.pprint(s2_authors)
        else:
            for i in range(0, len(names)):
                found_name=find_s2_name_in_diva_name(s2_authors[i]['name'], names[i])
                if found_name:
                    print("found s2_author id: {0} for {1}".format(s2_authors[i]['ids'], s2_authors[i]['name']))
                    found_name['S2_author_ID']=s2_authors[i]['ids']
                    found_name['PID']=int(m['PID'])
                    name_info.append(found_name)
                    continue
                else:
                    print("not found s2_author id: {0} for {1}".format(s2_authors[0]['ids'], s2_authors[0]['name']))
                    continue

                

    print("length of name_info={}".format(len(name_info)))
    names_outputfile="names.json"
    with open(names_outputfile, 'w', encoding='utf-8') as name_FH:
        for n in name_info:
            j_as_string = json.dumps(n)
            print(j_as_string, file=name_FH)

        name_FH.close()
    return

if __name__ == "__main__": main()
