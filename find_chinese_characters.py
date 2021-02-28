#!/usr/bin/python3
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./find_chinese_characters.py authors_file.JSON 
#
# reads in a JSON of authors names and outputs the entries with Chinese characters in the name
#
# G. Q. Maguire Jr.
#
# 2021-02-25
#
# Example:
# 
#time ./find_chinese_characters.py /z3/maguire/SemanticScholar/KTH_DiVA/authors-MA-RC.JSON
#


import requests, time
import pprint
import optparse
import sys

import json

import re

def cjk_detect(texts):
    if not isinstance(texts, str):
        return None

    # korean
    if re.search("[\uac00-\ud7a3]", texts):
        return "ko"
    # japanese
    if re.search("[\u3040-\u30ff]", texts):
        return "ja"
    # chinese
    if re.search("[\u4e00-\u9FFF]", texts):
        return "zh"
    return None

def main():
    global Verbose_Flag

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
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
        
    file_name=remainder[0]

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    authors=[]
    with open(file_name, 'r') as authors_FH:
        for line in authors_FH:
            try:
                if cjk_detect(line):
                    print("found CJK in {0}".format(line))
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
            if f and cjk_detect(f):
                print("kthid={0} firstName={1}".format(id, f))
            if l and cjk_detect(l):
                print("kthid={0} lastName={1}".format(id, l))

        if aliases:
            for alias in aliases:
                if alias and cjk_detect(alias['Name']):
                    print("kthid={0} alias={1}".format(id, alias))
                
    print("Finished")

if __name__ == "__main__": main()
