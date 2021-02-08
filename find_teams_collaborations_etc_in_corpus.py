#!/usr/bin/python3
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./find_teams_collaborations_etc_in_corpus.py reduced_corpus.JSON
#
# reads in a corpus in JSON format and extract information about teams, collaboration, etc.
#
# G. Q. Maguire Jr.
#
# 2021-02-08
#
# Example:
#time ./find_teams_collaborations_etc_in_corpus.py /z3/maguire/SemanticScholar/KTH_DiVA/reduced_corpus-MA_deduplicated_of_authors.JSON
#

import requests, time
import pprint
import optparse
import sys

# for use with reading csv files
#from io import StringIO, BytesIO
import io

import requests
import json

import datetime
import os                       # to make OS calls, here to get time zone info
import re

import locale 
locale.setlocale(locale.LC_ALL, 'sv_SE.UTF-8')

target_words=['Collaboration', 'collaboration',
              'Contributors',  'contributors', 
              'Group', 'group', 
              'NorPM',
              'Scoap',
              'Project', 'project',
              'Team', 'team' ]

def process_corpus(corpus_file):
    global Verbose_Flag
    global colaboration_team_info
    global colaboration_team_ids
    
    # get S2 information from a shard

    corpus_shard=[]
    with open(corpus_file, 'r') as corpus_FH:
        for line in corpus_FH:
            try:
                corpus_shard.append(json.loads(line))
            except:
                print("line={}".format(line))

    print("entires in reduced corpus={}".format(len(corpus_shard)))

    for ce in corpus_shard:
        if Verbose_Flag:
            print("id={0}".format(ce['id']))
        id = ce['id']

        s2_doi=ce.get('doi', False)
        s2_pmid=ce.get('pmid', False)
        s2_title=ce.get('title', False)
        s2_authors=ce.get('authors', []) # s2_authors is a list of s2 authors
        s2_year=ce.get('year', False)

        # compute the set of all the publications author IDs
        interesting_s2_authors=[]
        for a in s2_authors:
            author_name=a['name']
            for target in target_words:
                if author_name.find(target) >= 0:
                    existing_info=colaboration_team_info.get(author_name, False)
                    if existing_info:
                        existing_info.append(id)
                    else:
                        colaboration_team_info[author_name]=[id]

                    existing_ids=colaboration_team_ids.get(author_name, False)
                    if existing_ids:
                        for i in a['ids']:
                            existing_ids.add(i)
                    else:
                        new_set=set()
                        for i in a['ids']:
                            new_set.add(i)
                        colaboration_team_ids[author_name]=new_set

def main():
    global Verbose_Flag
    global pp
    global colaboration_team_info
    global colaboration_team_ids
    
    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
                      )

    parser.add_option('-a', '--all',
                      dest="all",
                      default=False,
                      action="store_true",
                      help="If set, processes all shard starting shard on the command line"
                      )

    parser.add_option('-t', '--testing',
                      dest="testing",
                      default=False,
                      action="store_true",
                      help="If set, processes only 10 shards"
                      )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        
    if (len(remainder) < 1):
        print("Insuffient arguments must provide corpus.JSON\n")
        return

    corpus_file=remainder[0]

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    colaboration_team_info=dict()
    colaboration_team_ids=dict()
    process_corpus(corpus_file)
    if len(colaboration_team_info) > 0:
        print("Potential collaborations, teams, etc.")
        for key in sorted(colaboration_team_info.keys()):
            print("key={0}; ids={1}, value={2}".format(key, colaboration_team_ids[key], colaboration_team_info[key]))

    if Verbose_Flag:
        print("xxx {0}{1}".format())

    print("Finished")

if __name__ == "__main__": main()
