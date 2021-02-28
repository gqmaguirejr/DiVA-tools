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



        # compute the set of all the publications author IDs
        interesting_s2_authors=[]
        for a in s2_authors:
            author_name=a['name']
            for target in target_words:
                if author_name.find(target) >= 0:
                    existing_info=colaboration_team_info.get(author_name, False)
                    if existing_info:
                        existing_info.add(id)
                    else:
                        colaboration_team_info[author_name]={id}

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
        print("Insuffient arguments must provide authors.JSON\n")
        return

    file_name=remainder[0]

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    authors=[]
    with open(file_name, 'r') as authors_FH:
        for line in authors_FH:
            try:
                authors.append(json.loads(line))
            except:
                print("line={}".format(line))

    print("entires in authors={}".format(len(authors)))

    for a in authors:
        if Verbose_Flag:
            print("kthid={0}".format(a['kthid']))
        id = a['kthid']

        profile=a.get('profile', False)
        aliases=a.get('aliases', False)

        if profile:
            f=profile.get('firstName', False)
            l=profile.get('lastName', False)
            if re.findall(r'[\u4e00-\u9fff]+', f):
                print("kthid={0} firstName={1}".format(id, f))
            if re.findall(r'[\u4e00-\u9fff]+', l):
                print("kthid={0} lastName={1}".format(id, l))

        if aliases:
            for alias in aliases:
                if re.findall(r'[\u4e00-\u9fff]+', alias):
                print("kthid={0} alias={1}".format(id, alias))


                
    print("Finished")

if __name__ == "__main__": main()
