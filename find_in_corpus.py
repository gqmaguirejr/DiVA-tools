#!/usr/bin/python3
#
# ./find_in_corpus.py targets.json shard_number path_to_corpus
#
# The shard number N (is the digits indicating the piece of the corpus) - for the file s2-corpus-186 N is 186
# The program outputs the following files:
#  matches_corpus_N.json - this contains JSON entries of the form:
#                          PID, Name, DOI, PMID, S2_publication_ID, S2_authors
#  remaining_targets.json - this contains entries of the same form as the input file (having removed the matched entries)
#
# G. Q. Maguire Jr.
#
# 2020-10-24
#
# Example of runinng the program
# ./find_in_corpus.py targets.json  186 /z3/maguire/SemanticScholar/SS_corpus_2020-05-27
#
#

import requests, time
from pprint import pprint
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

    if (len(remainder) < 3):
        print("Insuffient arguments must provide targets.json shard_number path_to_corpus\n")
        return

    targets_json_file=remainder[0]
    shard_number=remainder[1]
    path_to_corpus=remainder[2]

    targets=[]
    
    # read the lines from the JSON file
    with open(targets_json_file, 'r') as targets_FH:
        for line in targets_FH:
            targets.append(json.loads(line))

    print("length of targets={}".format(len(targets)))

    doi_set=set()
    pmid_set=set()
    for t in targets:
        doi=t.get('DOI', False)
        if doi:
            doi_set.add(doi)
        pmid=t.get('PMID', False)
        if pmid:
            pmid_set.add(pmid)

    print("doi_set length={0}, pmid_set length={1}".format(len(doi_set), len(pmid_set)))
    
    shard_filename="{0}/s2-corpus-{1}".format(path_to_corpus, shard_number)
    print("shard_filename={}".format(shard_filename))

    corpus_shard=[]
    with open(shard_filename, 'r') as corpus_shard_FH:
        for line in corpus_shard_FH:
            corpus_shard.append(json.loads(line))

    #  matches_corpus_N.json - this contains JSON entries of the form:
    #                          PID, Name, DOI, PMID, S2_publication_ID, S2_authors

    matches_corpus_json=[]
    print("corpus_shard length={}".format(len(corpus_shard)))
    for ce in corpus_shard:
        doi=ce.get('doi', False)
        pmid=ce.get('pmid', False)

        if doi in doi_set:
            j_dict=matched_diva_entry_doi(targets, doi)
            j_dict['S2_publication_ID']=ce['id']
            j_dict['S2_authors']=ce['authors']
            matches_corpus_json.append(j_dict)
            if Verbose_Flag:
                print("j_dict={}".format(j_dict))
            remove_diva_entry_pid(targets, j_dict['PID'])

    matches_filename="matches_corpus_{}.json".format(shard_number)
    with open(matches_filename, 'w', encoding='utf-8') as matches_FH:
        for m in matches_corpus_json:
            j_as_string = json.dumps(m)
            print(j_as_string, file=matches_FH)

    print("length of remaining targets={}".format(len(targets)))
    remaining_outputfile="remaining_targets.json"
    with open(remaining_outputfile, 'w', encoding='utf-8') as remaining_FH:
        for t in targets:
            j_as_string = json.dumps(t)
            print(j_as_string, file=remaining_FH)

        remaining_FH.close()


if __name__ == "__main__": main()
