#!/usr/bin/python3
# -*- mode: python; python-indent-offset: 4 -*-
#
# ./S2_yet_further_augment_from_CSV_file.py xxx.csv xxx.augmented_further.json [shard_number path_to_corpus]
#
# reads in a CSV spreaadsheet of DiVA entries and uses the information to generate a further updated augmented JSON file
# This program assumes that all of the KTH authors have a KTHID in the name_record for the publication, otherwise they are ignored.
# (This meands that the CSV file has to be corrected or all of the DiVA records have to be corrected.)
#
# The shard number N (is the digits indicating the piece of the corpus) - for the file s2-corpus-186 N is 186
# The focus of this program is to add the the aliases the PIDs from the DiVA spreadsheet.
#
# Note that program assumes that all entries in the JSON file have a value for kthid, even if it is fake ID.
#
#
# G. Q. Maguire Jr.
#
# 2021-01-04
#
# Example:
# ./S2_yet_further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented_further.JSON 186 /z3/maguire/SemanticScholar/SS_corpus_2020-05-27
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

# function returns a kthid (fake or not)
def augmented_lookup_orcid(orcid_to_lookfor, augmented_by_kthid):
    global Verbose_Flag

    # orcid can be at the top level or
    # inside "entry": {"orcid": "0000-0002-6066-746X",
    for e in augmented_by_kthid:
        item=augmented_by_kthid[e]
        orcid=item.get('orcid', False)        
        if orcid and (orcid == orcid_to_lookfor):
            return e
        #
        entry=item.get('entry', False)
        if entry:
            orcid=entry.get('orcid', False)
            if orcid and (orcid == orcid_to_lookfor):
                return e
    #
    if Verbose_Flag:
        print("augmented_lookup_orcid={} failed to find:".format(orcid_to_lookfor))    
    return False

# function returns a kthid (fake or not)
# Note that the name_to_look_for is simple a string of the form: "Lastname, Firstname"
def augmented_lookup_name(name_to_look_for, augmented_by_kthid):
    # names can either be in "profile": {"firstName": "Gerald Quentin", "lastName": "Maguire Jr"}}
    # or in the list of aliases: {"aliases": [{"Name": "Maguire Jr., Gerald Q.", "PID": [528381, ...]}, {"Name": "Maguire, Gerald Q.", "PID": [561069]}, {"Name": "Maguire Jr., Gerald", "PID": [561509]}, {"Name": "Maguire, Gerald Q., Jr.", "PID": [913155]}]}

    # because there are some people who share the same name, the code needs to return a list of matches
    list_of_matches=[]

    print("name_to_look_for={}".format(name_to_look_for))

    for e in augmented_by_kthid:
        if Verbose_Flag:
            print("e={}".format(e))
        item=augmented_by_kthid[e]
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
    global augmented_pid_and_authors

    #print("try_to_lookup_orcid orcid_to_lookfor={}:".format(orcid_to_lookfor))

    possible_kthid=False
    for key in sorted(augmented_pid_and_authors.keys()):
        entry=augmented_pid_and_authors[key]
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
    global augmented_pid_and_authors
    global pp

    possible_kthid=False

    #print("try_to_lookup_name ={}:".format(name_to_lookfor))

    possible_kthid=False
    for key in sorted(augmented_pid_and_authors.keys()):
        entry=augmented_pid_and_authors[key]
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
    global augmented_by_kthid
    global Verbose_Flag

    found_existing_user_by_orcid=0
    existing_user=augmented_lookup_orcid(new_orcid, augmented_by_kthid)
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

        augmented_by_kthid[id]={"kthid": id, "orcid": user_orcid, "profile": profile, "entry": {"kth": False, "orcid": False, "aliases": []}}
        if Verbose_Flag:
            print("new user={0}".format(augmented_by_kthid[id]))
    return

def check_for_PID_in(pid, apids):
    if len(apids) == 0:
        return False
    for p in apids:
        if p == pid:
            return True
    return False

def check_PID_for_name(kthid, name, pid):
    existing_entry=augmented_by_kthid.get(kthid, False)
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

    existing_entry=augmented_by_kthid.get(kthid, False)
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
                                augmented_by_kthid[kthid]['aliases']=existing_aliases
                                return
                # add a missing alias
                existing_aliases.append({'Name': name, 'PID': [pid]})
                augmented_by_kthid[kthid]['aliases']=existing_aliases
                if Verbose_Flag:
                    print("added alias and pid for {0} name={1}".format(kthid, name))
                return
    else:
        # add a missing alias
        augmented_by_kthid[kthid]['aliases']=[{'Name': name, 'PID': [pid]}]
        if Verbose_Flag:
            print("added aliases for {0} name={1}".format(kthid, name))
    return

def get_diva_authors(pid):
    global pid_and_authors
    global Verbose_Flag

    diva_entry=pid_and_authors[pid]
    if Verbose_Flag:
        print("diva_entry={}".format(diva_entry))
               
    name_records=get_authors_from_authorsString(diva_entry['Name'])
    return name_records



def main():
    global Verbose_Flag
    global augmented_pid_and_authors
    global kthid_dict
    global pp
    global fakeid_start
    global fakeid_nonKTH_start
    global augmented_by_kthid
    global pid_and_authors

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
                      )

    parser.add_option("--config", dest="config_filename",
                      help="read configuration from FILE", metavar="FILE")

    parser.add_option('-p', '--pid',
                      dest="pid",
                      default=False,
                      action="store_true",
                      help="If set, removes PID column"
                      )


    options, remainder = parser.parse_args()

    Verbose_Flag=options.verbose
    if Verbose_Flag:
        print('ARGV      :', sys.argv[1:])
        print('VERBOSE   :', options.verbose)
        print('REMAINING :', remainder)
        
    initialize(options)

    pid_Flag=options.pid

    if (len(remainder) < 2):
        print("Insuffient arguments must provide file_name.csv fine_name-augmented.json\n")
        print("or file_name.csv fine_name-augmented.json shard_number path_to_corpus\n")
        return

    spreadsheet_file=remainder[0]
    print("file_name='{0}'".format(spreadsheet_file))

    augmented_json_file_name=remainder[1]
    print("augmented_json_file_name='{0}'".format(augmented_json_file_name))

    if (len(remainder) > 3):
        shard_number=remainder[2]
        path_to_corpus=remainder[3]

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    augmented_by_kthid=dict()
    fakeid_number=100000        # base for fakeIDs created by this program
    fakeid_start='⚠⚠'           # these IDs represent IDs for unknown persons
    fakeid_nonKTH_start='⚑'        # these IDs represent IDs for persons who are not affiliated with KTH

    # read the lines from the JSON file
    with open(augmented_json_file_name, 'r') as augmented_FH:
        for idx, line in enumerate(augmented_FH):
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

            existing_entry=augmented_by_kthid.get(kthid, False)
            if existing_entry:
                print("existing KTHID={0} and a new entry={1} - old entry kept".format(kthid, line))
            else:
                augmented_by_kthid[kthid]=j

    print("length of augmented_by_kthid={}".format(len(augmented_by_kthid)))

    if Verbose_Flag:
        for e in augmented_by_kthid:
            if e.find(fakeid_start) >= 0:
                pp.pprint(augmented_by_kthid[e])

    print("augmented_by_kthid for u1d13i2c={}".format(augmented_by_kthid['u1d13i2c']))

    number_of_entries_with_KTHIDs=0
    number_of_entries_with_fake_KTHIDs=0
    number_of_entries_with_fake_nonKTHIDs=0
    for i in augmented_by_kthid:
        id1=augmented_by_kthid[i].get('kthid', False)
           
        if fake_kthid(i):
            number_of_entries_with_fake_KTHIDs=number_of_entries_with_fake_KTHIDs + 1
        else:
            number_of_entries_with_KTHIDs=number_of_entries_with_KTHIDs+1

        if fake_nonkthid(i):
            number_of_entries_with_fake_nonKTHIDs=number_of_entries_with_fake_nonKTHIDs+1

    print("total entries={0}, number_of_entries_with_KTHIDs={1}, number_of_entries_with_fake_KTHIDs={2} of these number_of_entries_with_fake_nonKTHIDs={3}, thus {4} unknown IDs".format(len(augmented_by_kthid),number_of_entries_with_KTHIDs,number_of_entries_with_fake_KTHIDs,number_of_entries_with_fake_nonKTHIDs,number_of_entries_with_fake_KTHIDs-number_of_entries_with_fake_nonKTHIDs))

    pid_and_authors=dict()
    diva_dois=dict()
    diva_pmis=dict()
    diva_titles=dict()
    all_PIDs=set()
    # read the lines from the spreadsheet
    if spreadsheet_file.endswith('.csv'):
        with open(spreadsheet_file, 'r') as spreadsheet_FH:
            for index, line in enumerate(spreadsheet_FH):
                if index == 0:  # process header line
                    column_headings=line.split(',')
                    # create columns={'PID': 0, 'Name': 1, 'PublicationType': 2, ... }
                    columns=dict()
                    # I suspect there is a byte order code FEFF at the start of the file
                    if column_headings[0] == '\ufeffPID':
                           column_headings[0] = 'PID'
                    for idx, col_name in enumerate(column_headings):
                           columns[col_name]=idx
                    continue
                col_values=get_column_values(columns, line)
                pid_str=col_values.get('PID', False)
                if pid_str:
                    pid=int(pid_str[:])
                    all_PIDs.add(pid)       # add this PID to the set of all PIDs processed
                    pid_and_authors[pid]=col_values

                    # save some information to be able to quickly find if a given DOI, PMI, ... has a DIVA entry
                    doi=col_values.get('DOI', False)
                    if doi and len(doi) > 0:
                        diva_dois[doi]=pid

                    pmi=col_values.get('PMID', False)
                    if pmi and len(pmi) > 0:
                        diva_pmis[pmi]=pid

                    title=col_values.get('Title', False)
                    if title and len(title) > 0:
                        diva_titles[title]=pid

                else:
                    print("Error in PID of {}".format(line))

    else:
        print("Unknown file extension for the spreadsheet")
        return

    print("Finished reading spreadsheet")

    if Verbose_Flag:
        for doi in diva_dois:
            print("doi={0}: {1}".format(doi, diva_dois[doi]))

        for pmid in diva_pmis:
            print("pmid={0}: {1}".format(pmid, diva_pmis[pmid]))

        for title in diva_titles:
            print("title={0}: {1}".format(title, diva_titles[title]))

    # get S2 information from a shard
    shard_filename="{0}/s2-corpus-{1}".format(path_to_corpus, shard_number)
    print("shard_filename={}".format(shard_filename))

    corpus_shard=[]
    with open(shard_filename, 'r') as corpus_shard_FH:
        for line in corpus_shard_FH:
            corpus_shard.append(json.loads(line))

    print("corpus_shard length={}".format(len(corpus_shard)))

    matches_corpus_json=[]
    for ce in corpus_shard:
        s2_doi=ce.get('doi', False)
        s2_pmid=ce.get('pmid', False)
        s2_title=ce.get('title', False)

        # check for matching doi, pmid, or title; otherwise ignore
        matching_pid=diva_dois.get(s2_doi, False)
        if matching_pid:
            print("matched doi: {0}".format(s2_doi))
        else:            
            matching_pid=diva_pmis.get(s2_pmid, False)
            if matching_pid:
                print("matched pmid: {0}".format(s2_pmid))
            else:
                matching_pid=diva_titles.get(s2_title, False)
                if matching_pid:
                    diva_doi=pid_and_authors[matching_pid].get('DOI', False)
                    if diva_doi == s2_doi:
                        print("matched title: {0}".format(s2_title))
                    else:
                        matching_pid=False
                        
        if not matching_pid:
            continue

        # found a S2 publication that matches a DiVA prublication, remeber the information
        pid_and_authors[matching_pid]['S2_publication_ID']=ce['id']
        pid_and_authors[matching_pid]['S2_authors']=ce['authors']

        name_records=get_diva_authors(matching_pid)

        num_s2_authors=len(ce['authors'])
        num_diva_authors=len(name_records)
        print("len(ce['authors'])={0} len(name_records)= {1}".format(num_s2_authors,num_diva_authors))

        print("{0}:{1} {2} corresponding to {3}".format(matching_pid, ce['id'], ce['authors'], name_records))

    
    return

    output_filename=augmented_json_file_name[:-5]+'_further.JSON'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for e in sorted(augmented_by_kthid.keys()):
            j_dict=augmented_by_kthid[e]
            j_as_string = json.dumps(j_dict, ensure_ascii=False)#, indent=4
            print(j_as_string, file=output_FH)

        output_FH.close()

    print("At end of processing (number of entries - represents 'unique' authors):")
    number_of_entries_with_KTHIDs=0
    number_of_entries_with_KTHID_and_ORCID=0
    number_of_entries_with_fake_KTHIDs=0
    number_of_entries_with_fake_KTHIDs_with_ORCID=0
    number_of_entries_with_fake_nonKTHIDs=0

    all_PIDs_with_KTH_authors=set()

    for i in augmented_by_kthid:
        id1=augmented_by_kthid[i].get('kthid', False)
        oid=augmented_by_kthid[i].get('orcid', False)
           
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

        existing_entry=augmented_by_kthid.get(i, False)
        if existing_entry:
            # collect PIDs for aliases
            existing_aliases=existing_entry.get('aliases', False)
            if existing_aliases:
                for alias in existing_aliases:
                    apids=alias.get('PID', False)
                    if apids:
                        for p in apids:
                            all_PIDs_with_KTH_authors.add(p)

    print("total entries={0}, number_of_entries_with_KTHIDs={1}, number_of_entries_with_KTHID_and_ORCID={2}, number_of_entries_with_fake_KTHIDs={3}, number_of_entries_with_fake_KTHIDs_with_ORCID={4}, number_of_entries_with_fake_nonKTHIDs={5}".format(len(augmented_by_kthid),number_of_entries_with_KTHIDs,number_of_entries_with_KTHID_and_ORCID,number_of_entries_with_fake_KTHIDs,number_of_entries_with_fake_KTHIDs_with_ORCID,number_of_entries_with_fake_nonKTHIDs))

    # of all_PIDs, which have no KTH authors (including fake IDs)
    print("len(all_PIDs)={0} len(all_PIDs_with_KTH_authors)={1}".format(len(all_PIDs), len(all_PIDs_with_KTH_authors)))
    diffset=all_PIDs.difference(all_PIDs_with_KTH_authors)
    print("{0} PIDs not associated with KTHIDs (even fake ones)={1}".format(len(diffset), diffset))
    print("Most of the above PIDs have no authors, but do have contributors; but these have not been processed (yet)")

if __name__ == "__main__": main()
