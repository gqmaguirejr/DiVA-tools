#!/usr/bin/python3
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./S2_remove_dumplicate_authors.py reduced_corpus.JSON
#
# reads in a JSON of S2 records and write new file after removing duplicate authors
#
# G. Q. Maguire Jr.
#
# 2021-01-21
#
# Example:
# using the new reduced corpus and an initial set of author information
#time ./S2_remove_dumplicate_authors.py /z3/maguire/SemanticScholar/KTH_DiVA/reduced_corpus-MA.JSON
#
# time ./S2_remove_dumplicate_authors.py /z3/maguire/SemanticScholar/KTH_DiVA/reduced_corpus-MA.JSON > logfile-20210121.txt

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

def compare_sets(s, t):
    return sorted(s) == sorted(t)

def remove_duplicated_author_names(id, s2_authors):
    new_s2_authors=[]
    already_seen_author_name=dict()
    for a in s2_authors:
        author_name=a['name']
        if author_name in already_seen_author_name:
            existing_ids=a['ids']
            #print("existing_ids={}".format(existing_ids))
            existing_ids=set(existing_ids)
            prior_ids=already_seen_author_name.get(author_name, False)
            if prior_ids:
                prior_ids=set(prior_ids['ids'])
            #
            if compare_sets(prior_ids, existing_ids):
                print("In {0} duplicate author name={1} with same ids={2}".format(id, author_name, existing_ids))
            else:
                print("In {0} duplicate author name={1} with different ids existing_ids={2}, prior_ids={3}".format(id, author_name, existing_ids, prior_ids))
                a['ids']=list(prior_ids.union(existing_ids))
                already_seen_author_name[author_name]=a
        else:
            already_seen_author_name[author_name]=a
    #
    #print("already_seen_author_name={}".format(already_seen_author_name))
    for a in already_seen_author_name:
        new_s2_authors.append(already_seen_author_name[a])
    #
    return new_s2_authors
    

            
def main():
    global Verbose_Flag
    global kthid_dict
    global pp
    global fakeid_start
    global fakeid_nonKTH_start
    global diva_authors_info
    global diva_publications
    global kthids_per_publication
    global number_of_matching_documents
    
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
                      help="If set, processes only 10 shards"
                      )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        

    if (len(remainder) < 1):
        print("Insuffient arguments must provide reduced_corpus.JSON\n")
        return

    corpus_file=remainder[0]

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

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

        s2_authors=ce.get('authors', []) # s2_authors is a list of s2 authors
        initial_num_s2_authors=len(s2_authors)

        # handle repeated S2 author name with same IDS
        s2_authors = remove_duplicated_author_names(ce['id'], s2_authors)
        num_s2_authors=len(s2_authors)

        if initial_num_s2_authors < num_s2_authors:
            ce['authors']=s2_authors
            
    print("entires in filtered reduced corpus={}".format(len(corpus_shard)))

    # output updated corpus
    output_filename=corpus_file[:-5]+'_deduplicated_of_authors.JSON'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for e in corpus_shard:
            j_as_string = json.dumps(e, ensure_ascii=False)
            print(j_as_string, file=output_FH)


    print("Finished")

if __name__ == "__main__": main()
