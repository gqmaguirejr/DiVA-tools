#!/usr/bin/python3
#
# ./match_names.py targets.json matches_corpus_N.json  [augmented_author_data.json]
#
# The shard number N (is the digits indicating the piece of the corpus) - for the file s2-corpus-186 N is 186
# The program outputs the following files:
#  name.json - this contains JSON entries of the form:
#                          diva_name, S2_author_name, S2_author_ID, PID
#
#
# The option augmented_author_data.json file contains entries of the form:
# {"kthid": "u1d13i2c", "entry": {"orcid": "0000-0002-6066-746X", "kth": " (KTH [177], Skolan f\u00f6r informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])", "aliases": [{"Name": "Maguire Jr., Gerald Q.", "PID": [528381, 606323, ... 1416571]}, {"Name": "Maguire, Gerald Q.", "PID": [561069]}, {"Name": "Maguire Jr., Gerald", "PID": [561509]}, {"Name": "Maguire, Gerald Q., Jr.", "PID": [913155]}]}, "profile": {"firstName": "Gerald Quentin", "lastName": "Maguire Jr"}}
#
# Here the alias data was mined from DiVA and the profile data comes from the user's research profile via the KTH API.
# Note that the list of PID values are current imcomplete - I did not try to be exhaaustive, but simply tried to look at enough publications to try to figure out the user's KTHID and possible ORCID
#
# G. Q. Maguire Jr.
#
# 2020-10-25
#
# Example of runinng the program
# ./match_names.py matches_corpus_186.json /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json
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

def split_names(names):
    name_list=[]
    working_name=''
    paren_count=0
    #
    if names.find(';') < 0:     # if there is no semicolon, it is only one name - simply return it in a list
        name_list.append(names)
        return name_list
    #
    for c in names:
        if c == '(':
            paren_count=paren_count+1
        if c == ')':
            paren_count=paren_count-1
        if c == '"':
            continue
        if (c == ';') and (paren_count == 0):
            name_list.append(working_name)
            working_name=''
            continue
        working_name=working_name+c
    #
    # add last instance of name to the list
    name_list.append(working_name)
    #
    return name_list

def reorder_name(name):         # name is of the form last, first
    #check for the comma
    comma_offset=name.find(',')
    if comma_offset < 0:        # if no comma, simply return the name
        return name
    last=name[0:comma_offset].strip()
    first=name[comma_offset+1:].strip()
    new_name=first+' '+last
    return new_name

def find_s2_name_in_diva_name(s2_name, diva_name):
    global Verbose_Flag
    global diva_name_info_by_kthid

    # a single diva_name is of the form: last_name, first_name [u1xxxxx] [orcid](KTH ....)
    #    Note that the KTHDID and the ORCID identifier are optional.
    #
    # an s2_name is of the form: first_name last_name
    # or
    # first_name middle_name last_name

    kth_affiliation=False
    kth_affiliation=diva_name.find('(KTH') # look for affiliation(s) and remove them
    if kth_affiliation < 0:                # only match for KTH authors
        return False

    kthid=False
    orcid=False
    affiliation=False

    # first processs the diva_name
    first_left_paren=diva_name.find('(') # look for affiliation(s) and remove them
    if first_left_paren> 0:
        diva_name=diva_name[0:first_left_paren-1]

    all_left_brackets=[x.start() for x in re.finditer('\[', diva_name)] # find offset of all left square brackets, note quote the bracket
    if len(all_left_brackets) > 0:
        first_left_bracket=all_left_brackets[0]
        if first_left_bracket > 0:
            first_left_bracket=first_left_bracket+1
            closing_bracket=diva_name.find(']', first_left_bracket)
            if closing_bracket > 0:
                first_substring=diva_name[first_left_bracket:closing_bracket]
                if first_substring.find('-') > 0: # this is an orcid ID
                    orcid=first_substring
                else:
                    kthid=first_substring
            else:
                print("No closing right bracket in {}".format(diva_name))

    if len(all_left_brackets) > 1:
        second_left_bracket=all_left_brackets[1]
        if second_left_bracket > 0:
            second_left_bracket=second_left_bracket+1
            closing_bracket=diva_name.find(']', second_left_bracket)
            if closing_bracket > 0:
                second_substring=diva_name[second_left_bracket:closing_bracket]
                orcid=second_substring
            else:
                print("No closing right bracket in {}".format(diva_name))

    if len(all_left_brackets) > 0: # trim off kthid and orcid; then strip white space
        diva_name=diva_name[0:all_left_brackets[0]-1].strip()

    if Verbose_Flag:
        print("diva_name={0}, kthid={1}, orcid={2}".format(diva_name, kthid, orcid))

    # split_diva_name=diva_name.split(',')
    # reordered_diva_name=split_diva_name[1].strip() + ' ' + split_diva_name[0].strip()
    reordered_diva_name=reorder_name(diva_name)

    ## changes inserted here
    if reordered_diva_name == s2_name: # if the reordered diva_name matches the s2_name, we are done
        n_dict=dict()
        n_dict['diva_name']=reordered_diva_name
        n_dict['S2_author_name']=s2_name
        if kthid:
            n_dict['kthid']=kthid
        if Verbose_Flag:
            print("matched reordered diva name")
        return n_dict

    # match against the firstName and lastName for this kthid
    if kthid:
        diva_name_info_entry=diva_name_info_by_kthid.get(kthid, False)
        if diva_name_info_entry:
            profile=diva_name_info_entry.get('profile', False)
            if profile:
                firstName=profile.get('firstName', False)
                lastName=profile.get('lastName', False)
                profile_name=False
                if firstName and lastName:
                    profile_name=firstName+' '+lastName
                elif firstName and not lastName:
                    profile_name=firstName
                elif not firstName and lastName:
                    profile_name=lastName


                if profile_name == s2_name: # if the reordered profile name matches the s2_name, we are done
                    n_dict=dict()
                    n_dict['diva_name']=profile_name
                    n_dict['S2_author_name']=s2_name
                    n_dict['kthid']=kthid
                    if Verbose_Flag:
                        print("matched profile name")
                    return n_dict

            # now check the aliases
            aliases=diva_name_info_entry.get('aliases', False)
            if aliases:
                for a in aliases:
                    if reorder_name(a) == s2_name: # if the reordered diva_name matches the s2_name, we are done
                        n_dict=dict()
                        n_dict['diva_name']=reordered_diva_name
                        n_dict['S2_author_name']=s2_name
                        n_dict['kthid']=kthid
                        print("matched alias={}".format(a))
                        return n_dict
    
    print("*+**+* diva_name={0}, reordered_diva_name={1}".format(diva_name, reordered_diva_name))

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
        str_difference = damerau_levenshtein_distance(reordered_diva_name, s2_name) 
        if str_difference < 2:
            n_dict=dict()
            n_dict['diva_name']=reordered_diva_name
            n_dict['S2_author_name']=s2_name
            if kthid:
                n_dict['kthid']=kthid
            if str_difference != 0:
                n_dict['partial match']=str_difference
            return n_dict

        else:
            print("string difference between {0} and {1} is {2}".format(reordered_diva_name, s2_name, str_difference))
            return False
    else:
        length_difference=len(reordered_diva_name) - len(s2_name)
        if length_difference < 3:
            # if the names are close, then guess that they are the same
            str_difference = damerau_levenshtein_distance(reordered_diva_name, s2_name) 
            if kthid or str_difference < 4:
                n_dict=dict()
                n_dict['diva_name']=reordered_diva_name
                n_dict['S2_author_name']=s2_name
                if kthid:
                    n_dict['kthid']=kthid
                if str_difference != 0:
                    n_dict['partial match']=str_difference
                    if str_difference > (len(reordered_diva_name)/2):
                        n_dict['unlikey match']="{}%".format(str_difference/len(reordered_diva_name)*100.0)
                    return n_dict
            else:
                print("string difference between {0} and {1} is {2}".format(reordered_diva_name, s2_name, str_difference))
                return False
        print("length difference between {0} and {1} is {2}".format(reordered_diva_name, s2_name, length_difference))
        return False            

    print("Unhandled case in find_s2_name_in_diva_name for {0} and {1}".format(diva_name, s2_name))
    return False

def find_s2_name_in_diva_name_strict(s2_name, diva_name):
    global Verbose_Flag
    global diva_name_info_by_kthid

    # a single diva_name is of the form: last_name, first_name [u1xxxxx] [orcid](KTH ....)
    #    Note that the KTHDID and the ORCID identifier are optional.
    #
    # an s2_name is of the form: first_name last_name
    # or
    # first_name middle_name last_name

    kth_affiliation=False
    kth_affiliation=diva_name.find('(KTH') # look for affiliation(s) and remove them
    if kth_affiliation < 0:                # only match for KTH authors
        return False

    kthid=False
    orcid=False
    affiliation=False

    # first processs the diva_name
    first_left_paren=diva_name.find('(') # look for affiliation(s) and remove them
    if first_left_paren> 0:
        diva_name=diva_name[0:first_left_paren-1]

    all_left_brackets=[x.start() for x in re.finditer('\[', diva_name)] # find offset of all left square brackets, note quote the bracket
    if len(all_left_brackets) > 0:
        first_left_bracket=all_left_brackets[0]
        if first_left_bracket > 0:
            first_left_bracket=first_left_bracket+1
            closing_bracket=diva_name.find(']', first_left_bracket)
            if closing_bracket > 0:
                first_substring=diva_name[first_left_bracket:closing_bracket]
                if first_substring.find('-') > 0: # this is an orcid ID
                    orcid=first_substring
                else:
                    kthid=first_substring
            else:
                print("No closing right bracket in {}".format(diva_name))

    if len(all_left_brackets) > 1:
        second_left_bracket=all_left_brackets[1]
        if second_left_bracket > 0:
            second_left_bracket=second_left_bracket+1
            closing_bracket=diva_name.find(']', second_left_bracket)
            if closing_bracket > 0:
                second_substring=diva_name[second_left_bracket:closing_bracket]
                orcid=second_substring
            else:
                print("No closing right bracket in {}".format(diva_name))

    if len(all_left_brackets) > 0: # trim off kthid and orcid; then strip white space
        diva_name=diva_name[0:all_left_brackets[0]-1].strip()

    if Verbose_Flag:
        print("diva_name={0}, kthid={1}, orcid={2}, s2_name={3}".format(diva_name, kthid, orcid, s2_name))

    # split_diva_name=diva_name.split(',')
    # reordered_diva_name=split_diva_name[1].strip() + ' ' + split_diva_name[0].strip()
    reordered_diva_name=reorder_name(diva_name)

    ## changes inserted here
    if reordered_diva_name == s2_name: # if the reordered diva_name matches the s2_name, we are done
        n_dict=dict()
        n_dict['diva_name']=reordered_diva_name
        n_dict['S2_author_name']=s2_name
        if kthid:
            n_dict['kthid']=kthid
        if Verbose_Flag:
            print("matched reordered diva name")
        return n_dict

    # match against the firstName and lastName for this kthid
    if kthid:
        diva_name_info_entry=diva_name_info_by_kthid.get(kthid, False)
        if diva_name_info_entry:
            profile=diva_name_info_entry.get('profile', False)
            if profile:
                firstName=profile.get('firstName', False)
                lastName=profile.get('lastName', False)
                profile_name=False
                if firstName and lastName:
                    profile_name=firstName+' '+lastName
                elif firstName and not lastName:
                    profile_name=firstName
                elif not firstName and lastName:
                    profile_name=lastName

                if profile_name == s2_name: # if the reordered profile name matches the s2_name, we are done
                    n_dict=dict()
                    n_dict['diva_name']=profile_name
                    n_dict['S2_author_name']=s2_name
                    n_dict['kthid']=kthid
                    if Verbose_Flag:
                        print("matched profile name")
                    return n_dict

            # now check the aliases
            aliases=diva_name_info_entry.get('aliases', False)
            if aliases:
                for a in aliases:
                    if reorder_name(a) == s2_name: # if the reordered diva_name matches the s2_name, we are done
                        n_dict=dict()
                        n_dict['diva_name']=reordered_diva_name
                        n_dict['S2_author_name']=s2_name
                        n_dict['kthid']=kthid
                        print("matched alias={}".format(a))
                        return n_dict
    
    # only do a strict match do not consider insertions/deletions/exchanges
    return False            



def find_all_s2_name_in_diva_name(pid, s2_authors, names):
    # there are multiple s2_authors and multiple DiVA names (in names)
    found_names=[]

    for s2a in s2_authors:
        for diva_name in names:
            found_name=find_s2_name_in_diva_name_strict(s2a['name'], diva_name)
            if found_name:
                found_name['S2_author_ID']=s2a['ids']
                found_name['PID']=pid
                found_names.append(found_name)
                break
    return found_names



# def split_name_on_semicolon(name_str):
#     new_names=[]
#     for i in range(0, name_str.count(',')):
#         first_semicolon=name_str.find(';')
#         if first_semicolon < 0:
#             new_names.append(name_str)
#             return new_names
#         else:
#             first_left_paren=name_str.find('(')
#             if (0 <= first_semicolon ) and (first_semicolon < first_left_paren):
#                 new_names.append(name_str[:first_semicolon-1])
#                 name_str=name_str[first_semicolon+1:]
#             elif first_left_paren < 0:
#                 sn=name_str.split(';')
#                 new_names.extend(sn)
#                 return new_names
#             else:
#                 new_names.append(name_str)
#                 return new_names
#     #
#     #
#     return new_names

# def split_names_on_semicolon(names):
#     wn=[]
#     for n in names:
#         wn.extend(split_name_on_semicolon(n))
#     return wn

def merge_two_diva_name_info_entries(kthid, existing_entry, diva_name_info_entry):
    global Verbose_Flag
    global diva_name_info_by_kthid

    merged_entry=dict()
    e_kthid=existing_entry.get('kthid', False)
    n_kthid=diva_name_info_entry.get('kthid', False)
    if (kthid != e_kthid) or (kthid != n_kthid) or (e_kthid != n_kthid):
        print("error in kthid being merged: {0},{1},[2}".format(kthid, e_kthid, n_kthid))
        return

    merged_entry['kthid']=kthid

    e_orcid=existing_entry.get('orcid', False)
    if e_orcid:                 # all orcid values must be in uppercase
        e_orcid=e_orcid.upper()
    n_orcid=diva_name_info_entry.get('orcid', False)
    if n_orcid:
        n_orcid=n_orcid.upper()

    if e_orcid and n_orcid and (e_orcid != n_orcid):
        print("error for kthid={0} in orcid being merged: {1},{2}".format(kthid, e_orcid, n_orcid))
    elif e_orcid and not n_orcid:
        merged_entry['orcid']=e_orcid
    elif not e_orcid and n_orcid:
        merged_entry['orcid']=n_orcid
    else:
        if Verbose_Flag:
            print("neither entry had an orcid")

    e_profile=existing_entry.get('profile', False)
    n_profile=diva_name_info_entry.get('profile', False)

    if e_profile and not n_profile:
        merged_entry['profile']=e_profile
    elif not e_profile and n_profile:
        merged_entry['profile']=n_profile
    if not e_profile and not n_profile: # no profiles at all
        if Verbose_Flag:
            print("neither entry had an profile")
    else:
        # there are two profiles, check that they are the same
        e_firstName=e_profile.get('firstName', False)
        n_firstName=n_profile.get('firstName', False)

        e_lastName=e_profile.get('lastName', False)
        n_lastName=n_profile.get('lastName', False)

        if (e_firstName != n_firstName) or (e_lastName != n_lastName):
            print("error in first or last names being merged: {0},{1} vs. {2},{3}".format(e_firstName,e_lastName,  n_firstName, n_lastName))

    e_aliases=existing_entry.get('aliases', False)
    n_aliases=diva_name_info_entry.get('aliases', False)

    # a little twist here is that we are going to converthe list of aliases into a set - this will make later processingeasier
    set_of_aliases=set()
    if e_aliases:
        for a in e_aliases:
            set_of_aliases.add(a)
    if n_aliases:
        for a in n_aliases:
            set_of_aliases.add(a)

    merged_entry['aliases']=set_of_aliases
                        
    diva_name_info_by_kthid[kthid]=diva_name_info_entry
    return

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

    if (len(remainder) < 1):
        print("Insuffient arguments must provide matches_corpus_N.json\n")
        return

    augmented_data_filename=False
    if (len(remainder) == 2):
        augmented_data_filename=remainder[1]
        

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    matches_corpus_file=remainder[0]

    shard_number_str=matches_corpus_file[len('matches_corpus_'):]
    shard_number_str=shard_number_str[:-len('.json_')+1:]
    print("processing shard {}".format(shard_number_str))

    matches=[]
    # read the lines from the JSON file
    with open(matches_corpus_file, 'r') as matches_FH:
        for line in matches_FH:
            matches.append(json.loads(line))

    print("length of matches={}".format(len(matches)))

    # place to put augement data about KTH authors
    diva_name_info_by_kthid=dict()
    # entries in this dict will have the form:
    # 'u1d13i2c': {   'aliases': {   'Maguire Jr., Gerald',
    #                                'Maguire Jr., Gerald Q.',
    #                                'Maguire, Gerald Q.',
    #                                'Maguire, Gerald Q., Jr.'},
    #             'kthid': 'u1d13i2c',
    #             'orcid': '0000-0002-6066-746X',
    #             'profile': {   'firstName': 'Gerald Quentin',
    #                            'lastName': 'Maguire Jr'}},


    if augmented_data_filename:
        with open(augmented_data_filename, 'r') as augmented_data_FH:
            for line in augmented_data_FH:
                if options.testing:
                    print("line={}".format(line))
                author_entry=json.loads(line)

                # store aliases and first/last name in a dict by kthid
                diva_name_info_entry=dict()

                # note that kthid and profile are at the top level of the incoming author_entry
                kthid=author_entry.get('kthid', False)
                if not kthid:   #  if no kthid, then skip this
                    continue

                diva_name_info_entry['kthid']=kthid

                profile=author_entry.get('profile', False)
                if profile:
                    diva_name_info_entry['profile']=profile

                entry=author_entry.get('entry', False)
                if entry:
                        orcid=entry.get('orcid', False)
                        if orcid:
                            diva_name_info_entry['orcid']=orcid

                        aliases=entry.get('aliases', False)
                        if aliases and len(aliases) >= 1:
                            # make the alias a set for easier lookup later
                            set_of_aliases=set()
                            for a in aliases:
                                a_name=a.get('Name', False)
                                if a_name:
                                    set_of_aliases.add(a_name)

                            diva_name_info_entry['aliases']=set_of_aliases
                        
                        existing_entry=diva_name_info_by_kthid.get(kthid, False)
                        if not existing_entry:
                            diva_name_info_by_kthid[kthid]=diva_name_info_entry
                        else:
                            merge_two_diva_name_info_entries(kthid, existing_entry, diva_name_info_entry)
                            

        print("length of diva_name_info_by_kthid={}".format(len(diva_name_info_by_kthid)))
        # print("maguire entry={}".format(diva_name_info_by_kthid['u1d13i2c']))

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
    number_of_matches=0

    for m in matches:
        # if options.testing:     # limit the number iterations for testing
        #     if number_of_matches > 300:
        #         break

        diva_name=m['Name']
        names=split_names(diva_name)

        s2_authors=m['S2_authors']

        if (len(s2_authors) == 1) and (len(names) == 1):
            found_name=find_s2_name_in_diva_name(s2_authors[0]['name'], diva_name)
            if found_name:
                print("{0}: found s2_author id: {1} for {2}: S2_publication_ID={3}".format(m['PID'], s2_authors[0]['ids'], s2_authors[0]['name'], m['S2_publication_ID']))
                # the following is to handle an error in shard 185, it has been reported to S2
                if (m['PID'] == 1421768) and (i == 2) and (s2_authors[0]['name'] == 'Yan Zhang'):
                    print("there is an error in the S2 corpus shard 186 for the third author of S2_publication_ID=f7975807a3d0cc87395a38c7a1e9ee65dffdbacc")
                    continue
                found_name['S2_author_ID']=s2_authors[0]['ids']
                found_name['PID']=int(m['PID'])
                name_info.append(found_name)
                continue
            else:
                if Verbose_Flag:
                    print("not found diva author={0} for s2_author={1}".format(diva_name,s2_authors))
                continue

        # if len(s2_authors) > 1:
        #     names=split_names(diva_name)

        if len(s2_authors) !=  len(names):
            ## Section to handle errors/exceptions
            # handle case of [{'ids': ['40952709'], 'name': 'Atlas Collaboration'}]
            if (len(s2_authors) == 1) and (s2_authors[0]['name'] == 'Atlas Collaboration'):
                print("**** special case: {0} vs. list of authors in PID={1}".format(s2_authors[0]['name'], int(m['PID'])))
                continue

            # fnshard 186: ollowing error reported to KTHB
            if (int(m['PID']) == 1272258):
                if (m['DOI'] == "10.1007/s00259-018-4148-3"):
                    print("**** error in DOI {0}: PID={1} - DOI is for the whole conference proceedings".format(m['DOI'], int(m['PID'])))
                continue

            # fnshard 186: following error reported to KTHB
            if (int(m['PID']) == 1183083):
                if (m['DOI'] == "10.1201/9781315157368-80"):
                    print("**** error in DOI {0}: PID={1} - DOI is for the whole conference proceedings".format(m['DOI'], int(m['PID'])))
                continue

            # fnshard 186: following error reported to S2
            # note that even the 4th authors is incorrect as the corpus mixes the affiliations in and does not have the correct 4th name
            if (int(m['PID']) == 560045):
                print("**** error in {0}: number of authors is only 4".format(int(m['PID'])))
                reduceds2_authors=[]
                for i in range(0,4):
                    reduceds2_authors.append(s2_authors[i])

                found_names=find_all_s2_name_in_diva_name(int(m['PID']), reduceds2_authors, names)
                # add the elements of the found_names to the name_info list
                if found_names:
                    print("found one or more names={}".format(found_names))
                    name_info.extend(found_names)
                    continue

            # fnshard 186: following error reported to S2
            if (int(m['PID']) == 1414546):
                print("**** error in {0}: number of authors is ~21, but S2 shows only 5 in the corpus and 6 in the document's page".format(int(m['PID'])))
                continue

            # shard 186: following error reported to KTHB
            if (int(m['PID']) == 1270591):
                print("**** error in DOI {0}: PID={1} - DOI is for the whole conference proceedings - the paper is a workshop paper and has no DOI of its own".format(m['DOI'], int(m['PID'])))
                continue

            # shard 186: following error reported to s2, S2_publication_ID=a1e281115f158a0777852895e80599f6e6fcbb0e):
            if (int(m['PID']) == 779118):
                print("**** error in {0}: number of authors in S2 is 500, but only 8 in DiVA".format(int(m['PID'])))
                continue

            if (int(m['PID']) == 779118):
                # S2_publication_ID=a1e281115f158a0777852895e80599f6e6fcbb0e
                print("**** error in {0}: number of authors in S2 is 500, but in the original source there are 2884 authors".format(int(m['PID'])))
                continue


            print("***** len(s2_authors={0}, length of split names={1}, diva_name={2} for m['PID']={3}, S2_publication_ID={4}".format(len(s2_authors), len(names), diva_name, int(m['PID']), m['S2_publication_ID'])
)

            if len(s2_authors) >  len(names):
                # consider a subset
                found_names=find_all_s2_name_in_diva_name(int(m['PID']), s2_authors, names)
                # add the elements of the found_names to the name_info list
                if found_names:
                    print("found one or more names={}".format(found_names))
                    name_info.extend(found_names)
                    continue

        if (len(s2_authors) < 10) or Verbose_Flag:
                print("S2 authors list when there are less than 10")
                pp.pprint(s2_authors)

        if len(s2_authors) < len(names):
            smaller_length=len(s2_authors)
        else:
            smaller_length=len(names)

        for i in range(0, smaller_length):
            if names[i].find('(KTH') > 0:
                print("i={0}, s2_authors[{0}]['name']= {1}, names[{0}]={2}".format(i, s2_authors[i]['name'], names[i]))
            found_name=find_s2_name_in_diva_name(s2_authors[i]['name'], names[i])
            if found_name:
                print("{0}: found s2_author id: {1} for {2}: S2_publication_ID={3}".format(m['PID'], s2_authors[i]['ids'], s2_authors[i]['name'], m['S2_publication_ID']))
                found_name['S2_author_ID']=s2_authors[i]['ids']
                found_name['PID']=int(m['PID'])
                name_info.append(found_name)
                continue
            else:
                if Verbose_Flag:
                    print("not found s2_author {0} for {1}".format(names[i], s2_authors[i]['name']))
            continue

                

    print("length of name_info={}".format(len(name_info)))

    if len(shard_number_str) >=0 :
        names_outputfile="names-{}.json".format(shard_number_str)
    else:
        names_outputfile="names.json"
    with open(names_outputfile, 'w', encoding='utf-8') as name_FH:
        for n in name_info:
            j_as_string = json.dumps(n)
            print(j_as_string, file=name_FH)

        name_FH.close()
    return

if __name__ == "__main__": main()
