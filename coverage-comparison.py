#!/usr/bin/python3
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./coverage-comparison.py xxxx.JSON
#
# Reads in publication data and computes coverage of ISI (i.e., WoS), Scopus, and S2
#
# G. Q. Maguire Jr.
#
# 2021-01-08
#
# Example:
# ./coverage-comparison.py /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected_pubs_S2.JSON

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
        print("Insuffient arguments must provide file_name.json\n")
        return

    json_file=remainder[0]
    print("file_name='{0}'".format(json_file))

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    documents=dict()
    with open(json_file, 'r') as json_FH:
        for line in json_FH:
            j=json.loads(line)
            pid=j.get('PID', False)
            if not pid:
                continue
            documents[pid]=j

    total_num_in_ISI=0
    total_num_in_Scopus=0
    total_num_in_S2=0

    num_in_ISI_Scopus_S2=0      # 111
    num_in_ISI_Scopus=0         # 110
    num_in_ISI_S2=0             # 101
    num_in_ISI_only=0           # 100
    num_in_Scopus_S2=0          # 011
    num_in_Scopus_only=0        # 010
    num_in_S2_only=0            # 001
    not_in_any=0                # 000

    for key in sorted(documents.keys()):
        entry=documents[key]
        isi=entry.get('ISI', False)
        scopus=entry.get('ScopusId', False)
        s2=entry.get('S2_publication_ID', False)

        if isi:
            total_num_in_ISI+=1
        if scopus:
            total_num_in_Scopus+=1
        if s2:
            total_num_in_S2+=1

        if isi and scopus and s2:
            num_in_ISI_Scopus_S2+=1      # 111
        if isi and scopus and not s2:
            num_in_ISI_Scopus+=1         # 110
        if isi and not scopus and s2:
            num_in_ISI_S2+=1             # 101
        if isi and not scopus and not s2:
            num_in_ISI_only+=1           # 100
        if not isi and scopus and s2:
            num_in_Scopus_S2+=1          # 011
        if not isi and scopus and not s2:
            num_in_Scopus_only+=1        # 010
        if not isi and not scopus and s2:
            num_in_S2_only+=1            # 001
        if not isi and not scopus and not s2:
            not_in_any+=1                # 000


    print("Finished reading publication data")

    number_of_documents=len(documents)
    print("number of documents={0}".format(number_of_documents))


    print("total_num_in_ISI=    {0}	{1:.2f}%".format(total_num_in_ISI, total_num_in_ISI*(100.0/number_of_documents)))
    print("total_num_in_Scopus= {0}	{1:.2f}%".format(total_num_in_Scopus, total_num_in_Scopus*(100.0/number_of_documents)))
    print("total_num_in_S2=     {0}	{1:.2f}%".format(total_num_in_S2, total_num_in_S2*(100.0/number_of_documents)))

    print("num_in_ISI_Scopus_S2={0}	{1:.2f}%".format(num_in_ISI_Scopus_S2, num_in_ISI_Scopus_S2*(100.0/number_of_documents)))
    print("num_in_ISI_Scopus=   {0}	{1:.2f}%".format(num_in_ISI_Scopus, num_in_ISI_Scopus*(100.0/number_of_documents)))
    print("num_in_ISI_S2=       {0}	{1:.2f}%".format(num_in_ISI_S2, num_in_ISI_S2*(100.0/number_of_documents)))
    print("num_in_ISI_only=     {0}	{1:.2f}%".format(num_in_ISI_only, num_in_ISI_only*(100.0/number_of_documents)))
    print("num_in_Scopus_S2=    {0}	{1:.2f}%".format(num_in_Scopus_S2, num_in_Scopus_S2*(100.0/number_of_documents)))
    print("num_in_Scopus_only=  {0}	{1:.2f}%".format(num_in_Scopus_only, num_in_Scopus_only*(100.0/number_of_documents)))
    print("num_in_S2_only=      {0}	{1:.2f}%".format(num_in_S2_only, num_in_S2_only*(100.0/number_of_documents)))
    print("not_in_any=          {0}	{1:.2f}%".format(not_in_any, not_in_any*(100.0/number_of_documents)))


if __name__ == "__main__": main()
