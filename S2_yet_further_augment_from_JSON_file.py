#!/usr/bin/python3
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./S2_yet_further_augment_from_JSON_file.py diva_entries.JSON authors_file.JSON reduced_corpus.JSON
#
# reads in a JSON of DiVA entries and uses the information to generate a further updated JSON files
# This program assumes that all of the KTH authors have a KTHID in the name_record for the publication, otherwise they are ignored.
# (This meands that the JSON file has to be corrected or all of the DiVA records have to be corrected.)
#
# Note that program assumes that all entries in the authors_file.JSON have a value for kthid, even if it is fake ID.
#
# Note that this program utilizes a reduced copus file - rather than the full corpus.
#
# G. Q. Maguire Jr.
#
# 2021-01-09
#
# Example:
# using the new reduced corpus and an initial set of author information
#time ./S2_yet_further_augment_from_JSON_file.py /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected_pubs_S2.JSON /z3/maguire/SemanticScholar/KTH_DiVA/authors-2012-2019_augmented_by_S2-20210109_S2_0.JSON /z3/maguire/SemanticScholar/KTH_DiVA/authors-2012-2019_augmented_by_S2-20210109_reduced_corpus.JSON
#
#time ./S2_yet_further_augment_from_JSON_file.py /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected_pubs_S2_augmented_from_reduced_corpus-manually-augmented.JSON /z3/maguire/SemanticScholar/KTH_DiVA/authors-2012-2019_augmented_by_S2-20210109_S2_0_augmented_from_reduced_corpus-manually-augmented.JSON /z3/maguire/SemanticScholar/KTH_DiVA/authors-2012-2019_augmented_by_S2-20210109_reduced_corpus-manually-augmented.JSON > logfile20210109n.txt

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
        # if c == '"':
        #     continue
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


def get_author_from_authorString(author):
    entry=dict()
    # special case for the following author - due to inclusion of maiden name in parens
    if author.find('Rachlew (Källne), Elisabeth') >= 0:
        firstLeftParen=author.find('(', 28)
    elif author.find('Lillqvist (nee Laine), Kristiina') >= 0:
        firstLeftParen=author.find('(', 32)
    else:
        firstLeftParen=author.find('(')
    firstLeftBracket=author.find('[')
    str_length=len(author)
    #
    #print("firstLeftParen={0}, firstLeftBracket={1}".format(firstLeftParen, firstLeftBracket))
    # name
    if (firstLeftBracket < 0) and (firstLeftParen < 0): #  no brackets or parens, then just a name
        entry['name']=author[:].strip()
        return entry
    #
    # name [xx] [yyy]
    if (firstLeftBracket > 0) and (firstLeftParen < 0): #  no parens, then a name and KTHID or ORCID
        entry['name']=author[:firstLeftBracket-1].strip()
        author=author[firstLeftBracket:]
        numberofLeftBrackets=author.count('[')
        firstLeftBracket=author.find('[')
        firstRightBracket=author.find(']')
        if numberofLeftBrackets == 1:
            if firstRightBracket > 0:
                kth_or_orcid_string=author[firstLeftBracket+1:firstRightBracket]
                if kth_or_orcid_string.count('-') > 1:
                    entry['orcid']=kth_or_orcid_string
                elif kth_or_orcid_string.count('@') == 1:
                    entry['email']=kth_or_orcid_string
                else:
                    entry['kthid']=kth_or_orcid_string
                return entry
            else:
                print("Missing a right square bracket")
                return entry
        if numberofLeftBrackets == 2:
            if firstRightBracket > 0:
                kth_or_orcid_string=author[firstLeftBracket+1:firstRightBracket]
                if kth_or_orcid_string.count('-') > 1:
                    entry['orcid']=kth_or_orcid_string
                elif kth_or_orcid_string.count('@') == 1:
                    entry['email']=kth_or_orcid_string
                else:
                    entry['kthid']=kth_or_orcid_string
            else:
                print("Missing a right square bracket")
                return entry
            #
            secondLeftBracket=author.find('[', firstRightBracket)
            secondRightBracket=author.find(']', secondLeftBracket)
            if (secondLeftBracket > 0) and (secondRightBracket > 0):
                kth_or_orcid_string=author[secondLeftBracket+1:secondRightBracket]
                if kth_or_orcid_string.count('-') > 1:
                    entry['orcid']=kth_or_orcid_string
                elif kth_or_orcid_string.count('@') == 1:
                    entry['email']=kth_or_orcid_string
                else:
                    entry['kthid']=kth_or_orcid_string
            else:
                print("Missing a right square bracket")
            return entry
        return entry
    #
    if (firstLeftBracket < 0) and  (firstLeftParen > 0): #  if paren, then just a name (affiliation)
        entry['name']=author[:firstLeftParen-1].strip()
        entry['affiliation']=author[firstLeftParen:].strip()
        return entry
    #
    # if (firstLeftBracket > 0) and (firstLeftBracket > firstLeftParen)and  (firstLeftParen > 0): #  if paren, then just a name (affiliation) - note the affiliation can have a left bracket, but it is part of the affiliation
    #     print("author={0}, firstLeftParen={1}".format(author, firstLeftParen))
    #     entry['name']=author[:firstLeftParen-1].strip()
    #     entry['affiliation']=author[firstLeftParen:].strip()
    #     return entry
    # #
    if (firstLeftBracket > 0) and  (firstLeftParen > 0): #  if paren, then just a name [xx] [yy] (affiliation) or  name [xx] (affiliation) or name (affilation_with_a_leftbracket)
        entry['affiliation']=author[firstLeftParen:].strip()
        if (firstLeftBracket > firstLeftParen): # the left beacket is in the affilation, so select the name only up to the paren
            entry['name']=author[:firstLeftParen-1].strip()
            return entry            
        entry['name']=author[:firstLeftBracket-1].strip()
        #
        author=author[firstLeftBracket:firstLeftParen-1]
        numberofLeftBrackets=author.count('[')
        firstLeftBracket=author.find('[')
        firstRightBracket=author.find(']')
        if numberofLeftBrackets == 1:
            if firstRightBracket > 0:
                kth_or_orcid_string=author[firstLeftBracket+1:firstRightBracket]
                if kth_or_orcid_string.count('-') > 1:
                    entry['orcid']=kth_or_orcid_string
                elif kth_or_orcid_string.count('@') == 1:
                    entry['email']=kth_or_orcid_string
                else:
                    entry['kthid']=kth_or_orcid_string
                return entry
            else:
                print("Missing a right square bracket")
                return entry
        if numberofLeftBrackets == 2:
            if firstRightBracket > 0:
                kth_or_orcid_string=author[firstLeftBracket+1:firstRightBracket]
                if kth_or_orcid_string.count('-') > 1:
                    entry['orcid']=kth_or_orcid_string
                elif kth_or_orcid_string.count('@') == 1:
                    entry['email']=kth_or_orcid_string
                else:
                    entry['kthid']=kth_or_orcid_string
            else:
                print("Missing a right square bracket")
                return entry
            #
            secondLeftBracket=author.find('[', firstRightBracket)
            secondRightBracket=author.find(']', secondLeftBracket)
            if (secondLeftBracket > 0) and (secondRightBracket > 0):
                kth_or_orcid_string=author[secondLeftBracket+1:secondRightBracket]
                if kth_or_orcid_string.count('-') > 1:
                    entry['orcid']=kth_or_orcid_string
                elif kth_or_orcid_string.count('@') == 1:
                    entry['email']=kth_or_orcid_string
                else:
                    entry['kthid']=kth_or_orcid_string
            else:
                print("Missing a right square bracket")
            return entry
    return entry

def get_authors_from_authorsString(authors):
    authors_list=[]
    list_of_authors=split_names(authors)
    #
    for a in list_of_authors:
        authors_list.append(get_author_from_authorString(a))
        #
    return authors_list

def add_kthid_to_kthids_per_publication(pid, kthid):
    global Verbose_Flag
    global kthids_per_publication

    current_kthids=kthids_per_publication.get(pid, set())
    current_kthids.add(kthid)
    kthids_per_publication[pid]=current_kthids

    

def compute_kthids_per_publication():
    global diva_authors_info
    global kthids_per_publication

    # each entry of this will contain a set or KTHIDs who are authors for the publication
    kthids_per_publication=dict()

    for e in diva_authors_info:
        item=diva_authors_info[e]
        diva_author_aliases=item.get('aliases', False)
        if not diva_author_aliases:
            continue
        for alias in diva_author_aliases:
            pids_for_alias=alias.get('PID', False)
            if pids_for_alias:
                for p in pids_for_alias:
                    add_kthid_to_kthids_per_publication(p, e)


# function returns a set of kthids (fake or not)
def lookup_diva_authors_by_pid(pid):
    global Verbose_Flag
    global diva_authors_info
    global kthids_per_publication

    possible_author_kthids=kthids_per_publication.get(pid, [])
    if Verbose_Flag and not possible_author_kthids:
        print("lookup_diva_authors_by_pid({}) found not possible authors".format(pid))
    return possible_author_kthids

# function returns a kthid (fake or not)
def lookup_diva_author_by_s2_author_ids(s2_author_ids_set):
    global Verbose_Flag
    global diva_authors_info

    for e in diva_authors_info:
        item=diva_authors_info[e]
        diva_author_s2_ids=item.get('s2_author_ids', [])
        diva_author_s2_ids_set=set(diva_author_s2_ids)
        # Is there one or more common ID?
        common_s2_ids=s2_author_ids_set.intersection(diva_author_s2_ids_set)
        if len(common_s2_ids) > 0:
            return e
    #
    if Verbose_Flag:
        print("lookup_diva_author_by_s2_author_ids() failed to find one or more of {}".format(s2_author_ids_set))
    return False

# function returns a kthid (fake or not)
def lookup_diva_author_by_orcid(orcid_to_lookfor):
    global Verbose_Flag
    global diva_authors_info

    for e in diva_authors_info:
        item=diva_authors_info[e]
        orcid=item.get('orcid', False)        
        if orcid and (orcid == orcid_to_lookfor):
            return e
    #
    if Verbose_Flag:
        print("lookup_diva_author_by_orcid={} failed to find".format(orcid_to_lookfor))    
    return False

def reordered_name_match(s2_name, diva_name):
    # the s2_name is in normal name order, while the diva_name is in Lastname, Firstname order
    # the s2_name is in normal name order, while the diva_name is in Lastname, Firstname order
    num_space_in_name=s2_name.count(' ')
    if num_space_in_name == 0:  # s2_name is a single string
        return s2_name == diva_name
    elif num_space_in_name == 1: # s2_name is firstname lastname
        split_s2=s2_name.split(' ')
        reorder_s2="{1}, {0}".format(split_s2[0], split_s2[1])
        return reorder_s2 == diva_name
    elif num_space_in_name == 2: # s2_name is firstname middle lastname
        split_s2=s2_name.split(' ')
        reorder_s2="{2}, {0} {1}".format(split_s2[0], split_s2[1], split_s2[2])
        if reorder_s2 == diva_name:
            return True
        reorder_s2=" {1} {2}, {0}".format(split_s2[0], split_s2[1], split_s2[2])
        if reorder_s2 == diva_name:
            return True
    elif num_space_in_name == 3: # s2_name is firstname middle lastname postfix
        split_s2=s2_name.split(' ')
        if diva_name.count(',') == 1:
            reorder_s2="{2} {3}, {0} {1}".format(split_s2[0], split_s2[1], split_s2[2], split_s2[3])
            if reorder_s2 == diva_name:
                return True
        if diva_name.count(',') == 2:
            reorder_s2="{2}, {0} {1}, {3}".format(split_s2[0], split_s2[1], split_s2[2], split_s2[3])
            if reorder_s2 == diva_name:
                return True
    else:
        print("reordered_name_match({0},{1}) don't know what to do".format(s2_name, diva_name))
    return False

# function returns a list of kthids (fake or not)
# Note that the name_to_look_for is in s2 name order, i.e., of the form: "Firstname Lastname"
def match_s2_author_name_against_diva_author_names(kthid, name_to_look_for):
    global Verbose_Flag
    global diva_authors_info
    # diva names can either be in "profile": {"firstName": "Gerald Quentin", "lastName": "Maguire Jr"}}
    # or in the list of aliases: {"aliases": [{"Name": "Maguire Jr., Gerald Q.", "PID": [528381, ...]}, {"Name": "Maguire, Gerald Q.", "PID": [561069]}, {"Name": "Maguire Jr., Gerald", "PID": [561509]}, {"Name": "Maguire, Gerald Q., Jr.", "PID": [913155]}]}
    print("name_to_look_for={}".format(name_to_look_for))
    item=diva_authors_info.get(kthid, False)
    if not item:
        print("Error in match_s2_author_name_against_diva_author_names({0},{1})".format(kthid, name_to_look_for))
        return False
    profile=item.get('profile', False)
    if profile:
        firstName=profile.get('firstName', False)
        lastName=profile.get('lastName', False)
        if firstName and lastName:
            combined_name="{0} {1}".format(firstName, lastName)
            if combined_name == name_to_look_for:
                return kthid
        elif firstName and not lastName:
            combined_name="{0}".format(firstName)
            if combined_name == name_to_look_for:
                return kthid
        elif not firstName and lastName:
            combined_name="{0}".format(lastName)
            if combined_name == name_to_look_for:
                return kthid
        else:
            print("Error:: Profile, but no firstname or lastname")
    # now check each alias
    aliases=item.get('aliases', False)
    if aliases:
        for a in aliases:
            if Verbose_Flag:
                print("a={}".format(a))
            if not a.get('Name', False): # sanity check to make sure there is a Name key and value
                print("a={}".format(a))
            #
            if reordered_name_match(name_to_look_for, a['Name']):
                return kthid
            if name_to_look_for.endswith('.'): # try looking for the name without a terminal "."
                if reordered_name_match(name_to_look_for[:-1], a['Name']):
                    return kthid
    return False

# function returns a kthid (fake or not)
# Note that the name_to_look_for is simple a string of the form: "Lastname, Firstname"
def lookup_diva_author_by_name(name_to_look_for):
    global Verbose_Flag
    global diva_authors_info

    # names can either be in "profile": {"firstName": "Gerald Quentin", "lastName": "Maguire Jr"}}
    # or in the list of aliases: {"aliases": [{"Name": "Maguire Jr., Gerald Q.", "PID": [528381, ...]}, {"Name": "Maguire, Gerald Q.", "PID": [561069]}, {"Name": "Maguire Jr., Gerald", "PID": [561509]}, {"Name": "Maguire, Gerald Q., Jr.", "PID": [913155]}]}

    # because there are some people who share the same name, the code needs to return a list of matches
    list_of_matches=[]

    print("name_to_look_for={}".format(name_to_look_for))

    for e in diva_authors_info:
        if Verbose_Flag:
            print("e={}".format(e))
        item=diva_authors_info[e]
        profile=item.get('profile', False)
        if profile:
            firstName=profile.get('firstName', False)
            lastName=profile.get('lastName', False)
            if firstName and lastName:
                combined_name="{0}, {1}".format(lastName, firstName)
                if combined_name == name_to_look_for:
                    list_of_matches.append(e)
                    continue
            elif firstName and not lastName:
                combined_name="{0}".format(firstName)
                if combined_name == name_to_look_for:
                    list_of_matches.append(e)
                    continue
            elif not firstName and lastName:
                combined_name="{0}".format(lastName)
                if combined_name == name_to_look_for:
                    list_of_matches.append(e)
                    continue
            else:
                print("Error:: Profile, but no firstname or lastname")
        #
        aliases=item.get('aliases', False)
        if aliases:
            for a in aliases:
                if Verbose_Flag:
                    print("a={}".format(a))
                if type(a) is int:
                    print("the alias {0} a is not a dict, a={1}, e={2}".format(aliases, a, e))
                    continue
                if not a.get('Name', False): # sanity check to make sure there is a Name key and value
                    print("a={}".format(a))
                #
                if a['Name'] == name_to_look_for:
                    list_of_matches.append(e)

    return list_of_matches

def fake_diva_kthid(possible_kthid):
    if possible_kthid == '-':
        return True
    if possible_kthid.find('PI') == 0:
        return True
    if possible_kthid.find('pi') == 0:
        return True
    if possible_kthid.find('P') == 0:
        return True
    if possible_kthid.find('u1') == 0:
        return False
    if possible_kthid.find(fakeid_start) == 0:
        return False
    # default to True, i.e., it is fake
    return True

# consider both fake KTHids and fake non:KTHids as fake IDs
def fake_kthid(possible_kthid):
    global fakeid_start
    global fakeid_nonKTH_start
    if possible_kthid.find(fakeid_start) == 0:
        return True
    if possible_kthid.find(fakeid_nonKTH_start) == 0:
        return True
    return False

def fake_nonkthid(possible_kthid):
    global fakeid_nonKTH_start
    if possible_kthid.find(fakeid_nonKTH_start) == 0:
        return True
    return False

def try_to_lookup_orcid(orcid_to_lookfor):
    global augmented_diva_publications

    #print("try_to_lookup_orcid orcid_to_lookfor={}:".format(orcid_to_lookfor))

    possible_kthid=False
    for key in sorted(augmented_diva_publications.keys()):
        entry=augmented_diva_publications[key]
        name=entry['Name']
        kthid=entry.get('kthid', False)
        orcid=entry.get('orcid', False)
        kth_affiliation=entry.get('kth', False)
        if kthid and kthid.find('PI0') == 0 :
            continue

        if orcid:
            if orcid == orcid_to_lookfor:
                return kthid

    return possible_kthid

def try_to_lookup_name(name_to_lookfor):
    global kthid_dict
    global augmented_diva_publications
    global pp

    possible_kthid=False

    #print("try_to_lookup_name ={}:".format(name_to_lookfor))

    possible_kthid=False
    for key in sorted(augmented_diva_publications.keys()):
        entry=augmented_diva_publications[key]
        name=entry['Name']
        kthid=entry.get('kthid', False)
        orcid=entry.get('orcid', False)
        kth_affiliation=entry.get('kth', False)
        if not kthid:           #  of there is no kthid, then skip
            continue
        if kthid and kthid.find('PI0') == 0 :
            continue


        current_aliases=kthid_dict[kthid].get('aliases', False)
        if not current_aliases:
            print("kthid without aliases={}".format())
        for alias in current_aliases:
            if alias['Name'] == name_to_lookfor:
                return kthid

    return possible_kthid


def get_column_values(columns, line):
    pid_and_author_entry=dict()
    all_quotemarks=[x.start() for x in re.finditer('"', line)] # find offset of all quotmarks
    for c in columns:
        c_start=2*columns[c]
        c_end=c_start+1
        try:
            pid_and_author_entry[c]=line[all_quotemarks[c_start]+1:all_quotemarks[c_end]]
        except:
            print("line={}".format(line))

    return pid_and_author_entry


def make_new_user(id, new_orcid):
    global diva_authors_info
    global Verbose_Flag

    found_existing_user_by_orcid=0
    existing_user=lookup_diva_author_by_orcid(new_orcid)
    if existing_user and existing_user == id:
        found_existing_user_by_orcid=found_existing_user_by_orcid+1
        return
    elif existing_user and existing_user != id:
        print("for id={0} and orcid={1}, found user={2}".format(id, new_orcid, existing_user))
        return
    else:
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
            if user_orcid != new_orcid:
                print("for user {0} existing orcid={1], new orcid {2}".format(user, user_orcid, new_orcid))
            else:
                user_orcid=new_orcid
        #"entry":{"kth":"(KTH [177], Centra [12851], Nordic Institute for Theoretical Physics NORDITA [12850])","orcid":"","aliases":[{"Name":"Anastasiou, Alexandros","PID":[1130981,1255535]},{"Name":"Anastasiou, A.","PID":[1269339]}]}}

        diva_authors_info[id]={"kthid": id, "orcid": user_orcid, "profile": profile, "entry": {"kth": False, "orcid": False, "aliases": []}}
        if Verbose_Flag:
            print("new user={0}".format(diva_authors_info[id]))
    return

def check_for_PID_in(pid, apids):
    if len(apids) == 0:
        return False
    for p in apids:
        if p == pid:
            return True
    return False

def check_PID_for_name(kthid, name, pid):
    existing_entry=diva_authors_info.get(kthid, False)
    if existing_entry:
        existing_kthid=existing_entry.get('kthid', False)
        if existing_kthid == kthid:
            # check aliases for name and then PID
            existing_aliases=existing_entry.get('aliases', False)
            if existing_aliases:
                for alias in existing_aliases:
                    aname=alias.get('Name', False)
                    if aname and aname == name:
                        apids=alias.get('PID', False)
                        if apids:
                            apid_found=check_for_PID_in(pid, apids)
                            if apid_found:
                                return True
                        else:
                            if Verbose_Flag:
                                print("No PIDs for {0} name={1}".format(kthid, name))
            else:
                if Verbose_Flag:
                    print("No aliases for {0} name={1}".format(kthid, name))
    return False

def add_PID_for_name(kthid, name, pid):
    global Verbose_Flag

    existing_entry=diva_authors_info.get(kthid, False)
    if existing_entry:
        existing_kthid=existing_entry.get('kthid', False)
        if existing_kthid == kthid:
            # check aliases for name and then PID
            existing_aliases=existing_entry.get('aliases', False)
            if existing_aliases:
                for idx, alias in enumerate(existing_aliases):
                    aname=alias.get('Name', False)
                    if aname and aname == name:
                        apids=alias.get('PID', False)
                        if apids:
                            apid_found=check_for_PID_in(pid, apids)
                            if not apid_found:
                                apids.append(pid)
                                existing_aliases[idx]={'Name': name, 'PID': apids}
                                diva_authors_info[kthid]['aliases']=existing_aliases
                                return
                # add a missing alias
                existing_aliases.append({'Name': name, 'PID': [pid]})
                diva_authors_info[kthid]['aliases']=existing_aliases
                if Verbose_Flag:
                    print("added alias and pid for {0} name={1}".format(kthid, name))
                return
    else:
        # add a missing alias
        diva_authors_info[kthid]['aliases']=[{'Name': name, 'PID': [pid]}]
        if Verbose_Flag:
            print("added aliases for {0} name={1}".format(kthid, name))
    return

def get_diva_authors(pid):
    global diva_publications
    global Verbose_Flag

    diva_entry=diva_publications[pid]
    if Verbose_Flag:
        print("diva_entry={}".format(diva_entry))
               
    name_records=get_authors_from_authorsString(diva_entry['Name'])
    return name_records


def update_diva_author_with_s2_author_ids(diva_author_kthid, s2_author_ids_set):
    global Verbose_Flag
    global diva_authors_info

    item=diva_authors_info.get(diva_author_kthid, False)
    if not item:
        print("No diva author info for diva_author_kthid={}".format(diva_author_kthid))
        return False

    diva_author_s2_ids=item.get('s2_author_ids', [])
    diva_author_s2_ids_set=set(diva_author_s2_ids)

    # Is there one or more common ID?
    common_s2_ids=s2_author_ids_set.intersection(diva_author_s2_ids_set)
    # if diva_author_kthid == 'u101oxae':
    #     print("diva_author_kthid={0}, common_s2_ids={1}, diva_author_s2_ids_set={2}".format(diva_author_kthid, common_s2_ids, diva_author_s2_ids_set))

    if len(common_s2_ids) > 0:
        new_s2_ids=list(s2_author_ids_set.union(diva_author_s2_ids_set))
    else:
        # update the list of IDs
        new_s2_ids=list(s2_author_ids_set)

    # possibly update the list of IDs
    diva_authors_info[diva_author_kthid]['s2_author_ids']=new_s2_ids
    #if Verbose_Flag:
    print("update_diva_author_with_s2_author_ids({0}, {1})".format(diva_author_kthid, s2_author_ids_set))
    return {'kthid': diva_author_kthid, 's2_author_ids': new_s2_ids}

# the function returns a dict of KTHID and list of s2_author_ids; or returns False if there is not KTHID
def match_s2_and_diva_names(pid, s2_author, diva_author):
    global Verbose_Flag
    global diva_authors_info

    # diva_author is of the form {'affiliation': '(KTH [177], Skolan för kemi, bioteknologi och hälsa (CBH) [879224], Proteinvetenskap [879309], Protein Engineering [879347])', 'name': 'Westerlund, Kristina', 'kthid': 'u12tu7v5', 'orcid': '0000-0003-4334-9360'}

    # names can either be in "profile": {"firstName": "Gerald Quentin", "lastName": "Maguire Jr"}}
    # or in the list of aliases: {"aliases": [{"Name": "Maguire Jr., Gerald Q.", "PID": [528381, ...]}, {"Name": "Maguire, Gerald Q.", "PID": [561069]}, {"Name": "Maguire Jr., Gerald", "PID": [561509]}, {"Name": "Maguire, Gerald Q., Jr.", "PID": [913155]}]}

    s2_author_name=s2_author['name']
    s2_author_ids=s2_author['ids'] # note that this is a list of IDs
    s2_author_ids_set=set(s2_author_ids)

    # only process KTH affiliated authors
    diva_author_affiliation=diva_author.get('affiliation', False)
    if not diva_author_affiliation or diva_author_affiliation.find("(KTH") < 0:
        if Verbose_Flag:
            print("NonKTH author={}".format(diva_author))
        return False

    diva_author_name=diva_author.get('name', False)
    if not diva_author_name:
        print("No diva_author name in {}".format(diva_author))
        return False

    diva_author_kthid=diva_author.get('kthid', False)
    # if there is a KTHID, then process the S2_author_IDs
    if diva_author_kthid:
        matching_id=match_s2_author_name_against_diva_author_names(diva_author_kthid, s2_author_name)
        if matching_id:
            if Verbose_Flag:
                print("found by KTHID: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
            return update_diva_author_with_s2_author_ids(matching_id, s2_author_ids_set)

        # if Verbose_Flag:
        #     print("found by KTHID: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
        # return update_diva_author_with_s2_author_ids(diva_author_kthid, s2_author_ids_set)
       
    diva_author_orcid=diva_author.get('orcid', False)
    # if there is a orcid, then lookup the diva author by their orcid and then process the S2_author_IDs
    if diva_author_orcid:
        diva_author_kthid=lookup_diva_author_by_orcid(diva_author_orcid)
        if diva_author_kthid:
            matching_id=match_s2_author_name_against_diva_author_names(diva_author_kthid, s2_author_name)
            if matching_id:
                if Verbose_Flag:
                    print("found by ORCID: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
            return update_diva_author_with_s2_author_ids(matching_id, s2_author_ids_set)

            # if Verbose_Flag:
            #     print("found by ORCID: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
            # return update_diva_author_with_s2_author_ids(diva_author_kthid, s2_author_ids_set)
       
    # as there was no KTHID or ORCID, see if there is a diva author with one of the s2_author_ids
    diva_author_kthid=lookup_diva_author_by_s2_author_ids(s2_author_ids_set)
    if diva_author_kthid:
        matching_id=match_s2_author_name_against_diva_author_names(diva_author_kthid, s2_author_name)
        if matching_id:
            if Verbose_Flag: 
                print("found by s2_author_id: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
        return update_diva_author_with_s2_author_ids(matching_id, s2_author_ids_set)

        # if Verbose_Flag:
        #     print("found by s2_author_id: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
        # return update_diva_author_with_s2_author_ids(diva_author_kthid, s2_author_ids_set)

    # as there was no KTHID or ORCID, we have to match based upon the s2_author_name
    possible_author_kthids=lookup_diva_authors_by_pid(pid)
    if possible_author_kthids:
        for id in possible_author_kthids:
            matching_id=match_s2_author_name_against_diva_author_names(id, s2_author_name)
            if matching_id:
                if Verbose_Flag:
                    print("found by s2_author_id: s2_author_name={0}, s2_author_ids={1}, diva_author_kthid={2}, diva_author_name={3}".format(s2_author_name, s2_author_ids, diva_author_kthid, diva_author_name))
                return update_diva_author_with_s2_author_ids(matching_id, s2_author_ids_set)
    return False

Names_of_collaborations=[
    'ATLAS Collaboration',
    'Fermi-LAT Collaboration',
    'The Fermi LAT Collaboration',
    'Jet Contributors',
    'JET-EFDA contributors',
    'Scoap',

    "The ATLAS Collaboration"
]

# return true of this is a known collaboration
def handle_collaboration(id, s2_authors, name_records):
    if id == "7eca66ea0be9f291011ebd0461f1e83cf9346a53":
        collaboration="The ATLAS Collaboration"
        return collaboration

    return False

def remove_last_N_s2_authors(s2_authors, n):
    for i in range(0,n):
        del s2_authors[-1]
    return s2_authors

def put_ids_in_set(ids):
    # existing_ids_set=set()
    # for id in ids:
    #     existing_ids_set.add(id)
    existing_ids_set=set(ids)
    return existing_ids_set
    
def compare_sets(s, t):
    return sorted(s) == sorted(t)

def remove_duplicated_author_names(s2_authors):
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
                print("duplicate author name={0} with same ids={1}".format(author_name, existing_ids))
            else:
                print("duplicate author name={0} with different ids existing_ids={1}, prior_ids={2}".format(author_name, existing_ids, prior_ids))
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
    

def process_corpus(corpus_file, diva_dois, diva_pmis, diva_titles, diva_s2_authors):
    global Verbose_Flag
    global diva_publications
    global diva_authors_info
    global number_of_matching_documents

    common_titles_to_ignore_for_mismatches_in_authors=[
        'Background',
        'Change of Editor-in-Chief',
        'Commentary',
        'Conclusions',
        'Editorial',
        "Editor's comments",
        'Foreword',
        'Guest Editorial',
        'Guest editorial',
        'Introduction',
        'Letter from the chairs',
        'Letter to the editors',
        'Message from the Chairs',
        'Message from the chairs',
        'Message from the Program Chairs',
        'Message from the program chairs',
        'Message from the technical program chairs',
        'Message from the workshops chairs',
        'Preface',
        'Preview',
        'Reflections']
    
    # get S2 information from a shard

    corpus_shard=[]
    with open(corpus_file, 'r') as corpus_FH:
        for line in corpus_FH:
            try:
                corpus_shard.append(json.loads(line))
            except:
                print("line={}".format(line))

    print("entires in reduced corpus={}".format(len(corpus_shard)))

    number_of_matching_documents=0
    matches_corpus_json=[]

    for ce in corpus_shard:
        if Verbose_Flag:
            print("id={0}".format(ce['id']))
        if ce['id'] == 'e9f0b2305f83313b462e811d57c6f3eea87b446c': # error missing authors in S2
            continue
        if ce['id'] == '6cdb40461dc7358dc7c122485086c6f9c721a373': # error in 3rd author's name and an affiliation as 4th author in S2
            continue

        s2_doi=ce.get('doi', False)
        s2_pmid=ce.get('pmid', False)
        s2_title=ce.get('title', False)
        s2_authors=ce.get('authors', []) # s2_authors is a list of s2 authors
        s2_year=ce.get('year', False)

        # compute the set of all the publications author IDs
        set_of_s2_authors_ids=set()
        for a in s2_authors:
            aids=a.get('ids', [])
            for i in aids:
                set_of_s2_authors_ids.add(i)

        # check for matching doi, pmid, or title; otherwise ignore
        matched_by_doi=diva_dois.get(s2_doi, False)
        matched_by_pmid=diva_pmis.get(s2_pmid, False)
        matched_by_title=diva_titles.get(s2_title, False)

        # if one of the s2_author IDs matches an s2_author_id in the DiVA set, this S2 record is possibly relevant
        possible_interesting_author=set_of_s2_authors_ids.intersection(diva_s2_authors)

        matching_pids=set()     #  this will be the set of DiVA publications that might match this S2 record
        if matched_by_doi:
            matching_pids=matching_pids.union(matched_by_doi)
        if matched_by_pmid:
            matching_pids=matching_pids.union(matched_by_pmid)
        if matched_by_title:
            matching_pids=matching_pids.union(matched_by_title)

        # if there were no matches with DIVA based on DOI, PMID, or title and
        # no interesting authors, then simple skip this S2 record
        
        if not matching_pids and not possible_interesting_author:
            continue

        reason_for_match=''
        if matched_by_doi:
            reason_for_match=reason_for_match+"matched doi: {0}".format(s2_doi)+"|"
            print("matched_by_doi={0}, matching_pids={1}".format(matched_by_doi, matching_pids))

        if matched_by_pmid:
            reason_for_match=reason_for_match+"matched pmid: {0}".format(s2_pmid)+"|"

        if matched_by_title:
            reason_for_match=reason_for_match+"matched title: {0}".format(s2_title)+"|"
                        
        if possible_interesting_author:
            reason_for_match=reason_for_match+"IA: {0}".format(possible_interesting_author)+"|"

        # diva_doi=diva_publications[matching_pid].get('DOI', False)
        # if diva_doi == s2_doi:
        #     common_doi=True
        
        # if there is not a matching_pid but there is an interesting author, then perhaps this is a publication missing from DiVA
        # or a publication done by the author while not at KTH
        if Verbose_Flag and not matching_pids:
            if s2_year:
                print("reason_for_match={0}year={1}|".format(reason_for_match, s2_year))
            else:
                print("reason_for_match={0}".format(reason_for_match))

        if matching_pids:
            if s2_year:
                print("reason_for_match={0}year={1}|".format(reason_for_match, s2_year))
            else:
                print("reason_for_match={0}".format(reason_for_match))

        if Verbose_Flag:
            print("matching_pids={}".format(matching_pids))

        # handle errors cases where there are too many s2_authors (i., the last N author are not actual authors)
        if id == '6cb7a74174d1fe1c9a008755b3819adade906257':
            s2_authors = remove_last_N_s2_authors(s2_authors, 2)

        #process each of the DIVA records that might be relevant
        for matching_pid in matching_pids:
            name_records=get_diva_authors(matching_pid)

            num_s2_authors=len(s2_authors)
            # add the following to handle the fact that in the 2021-01-01 corpus many names have two spaces between the first and last names
            for a in s2_authors:
                a['name']=' '.join(a['name'].split())
            
            num_diva_authors=len(name_records)
            if num_s2_authors == num_diva_authors:
                print("len(s2_authors)={0} len(name_records)= {1}".format(num_s2_authors,num_diva_authors))
            else:
                # handle common titles - to ignore them (when there is a mismatch in number of authors
                if not matched_by_doi and not matched_by_pmid and matched_by_title:
                    if s2_title in common_titles_to_ignore_for_mismatches_in_authors:
                        continue


                # handle consortia - such as {'name': 'ATLAS Collaboration', 'ids': ['40952709']
                collaboration=handle_collaboration(id, s2_authors, name_records)
                if collaboration:
                    print("id={0}, collaboration={1}".format(id, collaboration))
                    continue
                
                print("Mismatchin number of authors: len(s2_authors)={0} len(name_records)= {1}".format(num_s2_authors,num_diva_authors))
                print("{0}:{1} {2} corresponding to {3}".format(matching_pid, ce['id'], s2_authors, name_records))

                # handle repeated S2 author name with same IDS
                s2_authors = remove_duplicated_author_names(s2_authors)
                num_s2_authors=len(s2_authors)

            atleast_one_author_with_kthid=False
            if num_s2_authors == num_diva_authors:
                for i in range(0,num_s2_authors):
                    s2_author_id=match_s2_and_diva_names(matching_pid,  s2_authors[i], name_records[i])
                    if s2_author_id:
                        print("s2_author_id={0} name_records[{1}]={2}".format(s2_author_id, i, name_records[i]))
                        atleast_one_author_with_kthid=True
            if matched_by_title and atleast_one_author_with_kthid:
                # found a S2 publication that possibly matches a DiVA prublication, remeber the information
                # only include matched by title documents if there was a matching author
                number_of_matching_documents=number_of_matching_documents+1
                diva_publications[matching_pid]['S2_publication_ID']=ce['id']
                diva_publications[matching_pid]['S2_authors']=s2_authors
            else:
                # found a S2 publication that possibly matches a DiVA prublication, remeber the information
                number_of_matching_documents=number_of_matching_documents+1
                diva_publications[matching_pid]['S2_publication_ID']=ce['id']
                diva_publications[matching_pid]['S2_authors']=ce['authors']
            
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
        
    initialize(options)

    if (len(remainder) < 3):
        print("Insuffient arguments must provide diva_entries.JSON authors_file.JSON reduced_corpus.JSON\n")
        return

    diva_entries_file=remainder[0]
    print("file_name='{0}'".format(diva_entries_file))

    authors_file=remainder[1]
    print("authors_file='{0}'".format(authors_file))

    corpus_file=remainder[2]

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    diva_authors_info=dict()
    fakeid_number=100000        # base for fakeIDs created by this program
    fakeid_start='⚠⚠'           # these IDs represent IDs for unknown persons
    fakeid_nonKTH_start='⚑'        # these IDs represent IDs for persons who are not affiliated with KTH

    diva_s2_authors=set()

    # read the information about authors
    with open(authors_file, 'r') as authors_FH:
        for idx, line in enumerate(authors_FH):
            if Verbose_Flag:
                print(line)
            try:
                j=json.loads(line)
            except:
                print("error in line (#{0}): {1}".format(idx, line))
                print("{}".format(sys.exc_info()))
                return

            kthid=j.get('kthid', False)
            if not kthid:
                kthid="{0}{1}".format(fakeid_start, fakeid_number)
                j['kthid']=kthid
                fakeid_number=fakeid_number+1
                print("assigned a new fake ID={0} to {1}".format(fakeid_number, line))

            existing_entry=diva_authors_info.get(kthid, False)
            if existing_entry:
                print("existing KTHID={0} and a new entry={1} - old entry kept".format(kthid, line))
            else:
                diva_authors_info[kthid]=j

            # collect the set of all s2_author_ids
            s2_author_info=j.get('s2_author_ids', [])
            if s2_author_info:
                for s2aid in s2_author_info:
                    diva_s2_authors.add(s2aid)

    print("length of diva_authors_info={0}; number of diva_s2_authors={1}".format(len(diva_authors_info), len(diva_s2_authors)))
    if Verbose_Flag:
        for e in diva_authors_info:
            if e.find(fakeid_start) >= 0:
                pp.pprint(diva_authors_info[e])

    print("diva_authors_info for u1d13i2c={}".format(diva_authors_info['u1d13i2c']))

    compute_kthids_per_publication()

    number_of_entries_with_KTHIDs=0
    number_of_entries_with_fake_KTHIDs=0
    number_of_entries_with_fake_nonKTHIDs=0
    for i in diva_authors_info:
        id1=diva_authors_info[i].get('kthid', False)
           
        if fake_kthid(i):
            number_of_entries_with_fake_KTHIDs=number_of_entries_with_fake_KTHIDs + 1
        else:
            number_of_entries_with_KTHIDs=number_of_entries_with_KTHIDs+1

        if fake_nonkthid(i):
            number_of_entries_with_fake_nonKTHIDs=number_of_entries_with_fake_nonKTHIDs+1

    print("total entries={0}, number_of_entries_with_KTHIDs={1}, number_of_entries_with_fake_KTHIDs={2} of these number_of_entries_with_fake_nonKTHIDs={3}, thus {4} unknown IDs".format(len(diva_authors_info),number_of_entries_with_KTHIDs,number_of_entries_with_fake_KTHIDs,number_of_entries_with_fake_nonKTHIDs,number_of_entries_with_fake_KTHIDs-number_of_entries_with_fake_nonKTHIDs))

    diva_publications=dict()

    # the following dictionaries contain a set of PIDs associated with a given DOI, PMID, or title
    diva_dois=dict()
    diva_pmis=dict()
    diva_titles=dict()

    all_PIDs=set()
    # read the diva_entries JSON file
    with open(diva_entries_file, 'r') as diva_entries_FH:
        for idx, line in enumerate(diva_entries_FH):
            if Verbose_Flag:
                print(line)
            try:
                j=json.loads(line)
            except:
                print("error in line (#{0}): {1}".format(idx, line))
                print("{}".format(sys.exc_info()))
                return

            pid_str=j.get('PID', False)
            if not pid_str:
                print("error in line (#{0}): {1}".format(idx, line))
                continue

            pid=int(pid_str[:])
            all_PIDs.add(pid)       # add this PID to the set of all PIDs processed

            existing_entry=diva_authors_info.get(pid, False)
            if existing_entry:
                print("existing PID={0} and a new entry={1} - old entry kept".format(pid, line))
                continue

            diva_publications[pid]=j

            # save some information to be able to quickly find if a given DOI, PMID, ... has a DIVA entry
            # note that we do not assume that DOI, PMID, or titles are unique
            doi=diva_publications[pid].get('DOI', False)
            if doi and len(doi) > 0:
                existing_pids_for_doi=diva_dois.get(doi, False)
                if not existing_pids_for_doi:
                    diva_dois[doi]={pid}
                else:
                    if Verbose_Flag:
                        print("duplicate DOI ({0}) in {1} and {2}".format(doi, existing_pids_for_doi, pid))
                    diva_dois[doi]=existing_pids_for_doi.add(pid)

            pmi=diva_publications[pid].get('PMID', False)
            if pmi and len(pmi) > 0:
                existing_pids_for_pmi=diva_pmis.get(doi, False)
                if not existing_pids_for_pmi:
                    diva_pmis[pmi]={pid}
                else:
                    if Verbose_Flag:
                        print("duplicate PMID ({0}) in {1} and {2}".format(doi, existing_pids_for_pmi, pid))
                    diva_pmis[pmi]=existing_pids_for_pmi.add(pid)

            title=diva_publications[pid].get('Title', False)
            if title and len(title) > 0:
                existing_pids_for_title=diva_titles.get(doi, False)
                if not existing_pids_for_title:
                    diva_titles[title]={pid}
                else:
                    diva_titles[title]=existing_pids_for_title.add(pid)

    print("Finished reading DiVA entries")

    if Verbose_Flag:
        for doi in diva_dois:
            print("doi={0}: {1}".format(doi, diva_dois[doi]))

        for pmid in diva_pmis:
            print("pmid={0}: {1}".format(pmid, diva_pmis[pmid]))

        for title in diva_titles:
            print("title={0}: {1}".format(title, diva_titles[title]))

    process_corpus(corpus_file, diva_dois, diva_pmis, diva_titles, diva_s2_authors)

    # output updated publication data
    output_filename=diva_entries_file[:-5]+'_augmented_from_reduced_corpus.JSON'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for e in sorted(diva_publications.keys()):
            j_dict=diva_publications[e]
            j_as_string = json.dumps(j_dict, ensure_ascii=False)#, indent=4
            print(j_as_string, file=output_FH)

    # output updated authors data
    output_filename=authors_file[:-5]+'_augmented_from_reduced_corpus.JSON'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for e in sorted(diva_authors_info.keys()):
            j_dict=diva_authors_info[e]
            j_as_string = json.dumps(j_dict, ensure_ascii=False)#, indent=4
            print(j_as_string, file=output_FH)

    print("At end of processing (number of entries - represents 'unique' authors):")
    number_of_entries_with_KTHIDs=0
    number_of_entries_with_KTHID_and_ORCID=0
    number_of_entries_with_fake_KTHIDs=0
    number_of_entries_with_fake_KTHIDs_with_ORCID=0
    number_of_entries_with_fake_nonKTHIDs=0
    number_of_entries_with_s2_author_ids=0

    all_PIDs_with_KTH_authors=set()

    for i in diva_authors_info:
        id1=diva_authors_info[i].get('kthid', False)
        oid=diva_authors_info[i].get('orcid', False)
           
        s2_author_id=diva_authors_info[i].get('s2_author_ids', False)
        if s2_author_id:
            number_of_entries_with_s2_author_ids=number_of_entries_with_s2_author_ids+1

        if fake_kthid(i):
            number_of_entries_with_fake_KTHIDs=number_of_entries_with_fake_KTHIDs + 1
            if oid:
                number_of_entries_with_fake_KTHIDs_with_ORCID=number_of_entries_with_fake_KTHIDs_with_ORCID + 1
        else:
            number_of_entries_with_KTHIDs=number_of_entries_with_KTHIDs + 1 
            if oid:
                   number_of_entries_with_KTHID_and_ORCID=number_of_entries_with_KTHID_and_ORCID + 1

        if fake_nonkthid(i):
            number_of_entries_with_fake_nonKTHIDs=number_of_entries_with_fake_nonKTHIDs+1

        existing_entry=diva_authors_info.get(i, False)
        if existing_entry:
            # collect PIDs for aliases
            existing_aliases=existing_entry.get('aliases', False)
            if existing_aliases:
                for alias in existing_aliases:
                    apids=alias.get('PID', False)
                    if apids:
                        for p in apids:
                            all_PIDs_with_KTH_authors.add(p)

    print("total entries={0}, number_of_entries_with_KTHIDs={1}, number_of_entries_with_KTHID_and_ORCID={2}, number_of_entries_with_fake_KTHIDs={3}, number_of_entries_with_fake_KTHIDs_with_ORCID={4}, number_of_entries_with_fake_nonKTHIDs={5}".format(len(diva_authors_info),number_of_entries_with_KTHIDs,number_of_entries_with_KTHID_and_ORCID,number_of_entries_with_fake_KTHIDs,number_of_entries_with_fake_KTHIDs_with_ORCID,number_of_entries_with_fake_nonKTHIDs))

    print("number_of_entries_with_s2_author_ids={}".format(number_of_entries_with_s2_author_ids))
    print("number_of_matching_documents".format(number_of_matching_documents))

    if Verbose_Flag:
        # of all_PIDs, which have no KTH authors (including fake IDs)
        print("len(all_PIDs)={0} len(all_PIDs_with_KTH_authors)={1}".format(len(all_PIDs), len(all_PIDs_with_KTH_authors)))
        diffset=all_PIDs.difference(all_PIDs_with_KTH_authors)
        print("{0} PIDs not associated with KTHIDs (even fake ones)={1}".format(len(diffset), diffset))
        print("Most of the above PIDs have no authors, but do have contributors; but these have not been processed (yet)")

    print("Finished")

if __name__ == "__main__": main()
