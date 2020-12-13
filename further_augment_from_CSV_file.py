#!/usr/bin/python3
#
# ./further_augment_from_CSV_file.py xxx.csv xxx.augmented.json [extra_orcid_info.txt]
#
# reads in a CSV spreaadsheet of DiVA entries and uses the information to generates update an augmented JSON file
#
#
# G. Q. Maguire Jr.
#
# 2020-11-14
#
# Example:
# ./further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json
# or
#./further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json /z3/maguire/SemanticScholar/KTH_DiVA/orcid_kth-id_2020-12-04.txt
#
# If the program is called with the extra information about ORCID and KTHIDs it adds this to the augmented_by_kthid dict.
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

def fake_kthid(possible_kthid):
    global fakeid_start
    if possible_kthid.find(fakeid_start) == 0:
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


def main():
    global Verbose_Flag
    global augmented_pid_and_authors
    global kthid_dict
    global pp
    global fakeid_start
    global augmented_by_kthid

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
        return

    spreadsheet_file=remainder[0]
    print("file_name='{0}'".format(spreadsheet_file))

    augmented_json_file_name=remainder[1]
    print("augmented_json_file_name='{0}'".format(augmented_json_file_name))

    if (len(remainder) > 2):
        orcid_fileName=remainder[2]
        print("orcid_fileName='{0}'".format(orcid_fileName))

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    augmented_by_kthid=dict()
    fakeid_number=0
    fakeid_start='⚠⚠'
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

            # move the entry dict elements up to the top level
            entry=j.get('entry', False)
            if entry:
                kth_organization=entry.get('kth', False)
                if kth_organization:
                    j['kth']=kth_organization
                top_level_orcid=j.get('orcid', False)
                entry_orcid=entry.get('orcid', False)
                if entry_orcid:
                    if not top_level_orcid:
                        j['orcid']=entry_orcid
                    elif top_level_orcid != entry_orcid:
                        print("missmatching orcid in {}".format(line))
                    else:
                        print("Should not get here when dealing with ORCIDs")

                entry_aliases=entry.get('aliases', False)
                if entry_aliases:
                    j['aliases']=entry_aliases
                # remove the old entry structure
                del j['entry']

            kthid=j.get('kthid', False)
            if not kthid:
                kthid="{0}{1}".format(fakeid_start, fakeid_number)
                j['kthid']=kthid
                fakeid_number=fakeid_number+1

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
    number_of_entries_with_KTHID_and_ORCID=0
    number_of_entries_with_fake_KTHIDs=0
    number_of_entries_with_fake_KTHIDs_with_ORCID=0
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


    print("total entries={0}, number_of_entries_with_KTHIDs={1}, number_of_entries_with_KTHID_and_ORCID={2}, number_of_entries_with_fake_KTHIDs={3}, number_of_entries_with_fake_KTHIDs_with_ORCID={4}".format(len(augmented_by_kthid),
                                                                                                                                                                                                      number_of_entries_with_KTHIDs,
                                                                                                                                                                                                      number_of_entries_with_KTHID_and_ORCID,
                                                                                                                                                                                                      number_of_entries_with_fake_KTHIDs,
                                                                                                                                                                                                      number_of_entries_with_fake_KTHIDs_with_ORCID))

    # note that the following code is only used if there is a third file argument
    # This file is assumed to contain extra ORCID and KTHID entries 
    if (len(remainder) > 2):
        new_users=0
        already_known_orcid=0
        new_orcid=0
        differing_orcids=0
        # read the lines from the spreadsheet
        if orcid_fileName.endswith('.txt'):
            with open(orcid_fileName, 'r') as spreadsheet_FH:
                for index, line in enumerate(spreadsheet_FH):
                    # format is orcid;kthid
                    fields=line.split(';')
                    if Verbose_Flag:
                        print("fields={}".format(fields))
                    kid=fields[1].strip()
                    noid=fields[0]
                    entry=augmented_by_kthid.get(kid, False)
                    if not entry:
                        if Verbose_Flag:
                            print("Do not have a KTHID of {0} - add KTHID and Orcid={1}".format(kid, noid))
                        make_new_user(kid, noid)
                        new_users=new_users+1
                    else:
                        oid=augmented_by_kthid[kid].get('orcid', False)
                        if oid and (oid == noid):
                            already_known_orcid=already_known_orcid+1
                        elif oid and (oid != noid):
                            differing_orcids=differing_orcids+1
                            print(" for user={0} different ORCID={1} than existing={2}".format(kid, noid, oid))
                        elif not oid:
                            augmented_by_kthid[kid]['orcid']=noid
                            new_orcid=new_orcid+1
                            print("Applying new orcid for user {0}: {1}".format(kid, noid))
                        else:
                            print("Should not have gotten here")

        print("already_known_orcid={0}, new_orcid={1}, differing_orcids={2},new_users={3}".format(already_known_orcid, new_orcid, differing_orcids,new_users))
        print("Finished reading extra ORCID info")

    pid_and_authors=[]
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
                pid_and_authors.append(get_column_values(columns, line))
    else:
        print("Unknown file extension for the spreadsheet")
        return
    print("Finished reading spreadsheet")

    # name_to_look_for='Gaiarin, Simone'
    # z1=augmented_lookup_name(name_to_look_for, augmented_by_kthid)
    # print("z1={}".format(z1))

    # get KTHIDs and ORCID if they exist, output as JSON
    # also keeo track of the alternative names and on which publication they are used
    augmented_pid_and_authors=dict()
    for pna in pid_and_authors:
        if Verbose_Flag:
            print("pna={}".format(pna))
        
        pid_str=pna.get('PID', False)
        if not pid_str:
            print("pna={0} but has no PID - hence the program must stop")
            return
        pid = int(pid_str[:])

        name_records=get_authors_from_authorsString(pna['Name'])
        pna['names']=name_records      # save the parsed authors information

        for name_record in name_records:
            if Verbose_Flag:
                print("pid={0},name_record={1}".format(pid,name_record))

            existing_kthid=False
            existing_orcid=False

            kthid=name_record.get('kthid',False)
            orcid=name_record.get('orcid',False)
            affiliation=name_record.get('affiliation',False)

            # look for lack of affiliations or lack of KTH affiliation and skip such a name_record
            if not affiliation:
                continue
            elif affiliation and affiliation.find('(KTH') < 0:
                kth_affiliation_flag=False
                continue
            else:
                kth_affiliation_flag=True

            if not kthid or fake_diva_kthid(kthid):
                if orcid:       # if there is an orcid, try to look up the user by this
                    possible_id=augmented_lookup_orcid(orcid, augmented_by_kthid)
                    if possible_id:
                        print("PID={0} has a fake DiVA KTHID of {1}, it should be {2} - found by orcid={3} for name_record={4}".format(pid, kthid, possible_id, orcid, name_record))
                        kthid=possible_id

            if not kthid or fake_diva_kthid(kthid):
                # since the kthid was fake, look up the user by name
                possible_id=augmented_lookup_name(name_record['name'], augmented_by_kthid)
                print("id={0}, possible_id={1}".format(pid, possible_id))
                if possible_id and len(possible_id) == 1:
                    possible_email=augmented_by_kthid[possible_id[0]].get('email', False)
                    if possible_email:
                        print("possible_email={}".format(possible_email))
                if not possible_id:
                    print("***** id={0}, possible_id={1}".format(pid, possible_id))
                    # this must be a missing entry
                    kthid="{0}{1}".format(fakeid_start, fakeid_number)
                    fakeid_number=fakeid_number+1
                    new_entry=dict()
                    new_entry['kthid']=kthid
                    new_entry['kth']=affiliation
                    new_entry['aliases']=[{'Name': name_record['name'], 'PID': [pid]}]
                    augmented_by_kthid[kthid]=new_entry
                
                    print("PID={0} has a missing or fake DiVA KTHID of {1} could not figure it out the real KTHID - name_record={2}, so made a new entry={3}".format(pid, kthid, name_record, json.dumps(new_entry)))
                else:           # otherwise there was possible ID
                    if len(possible_id) == 1:
                        print("PID={0} has a fake DiVA KTHID of {1}, it should be {2} - found by name_record={3}".format(pid, kthid, possible_id, name_record))
                        kthid=possible_id[0]
                    else:
                        print("PID={0} has a fake DiVA KTHID of {1}, it should be one of {2} - found by name_record={3}".format(pid, kthid, possible_id, name_record))
                        # there are multiple matches:
                        # they could be the same one
                        if len(possible_id) == 2:
                            if possible_id[0] == possible_id[1]:
                                kthid=possible_id[0]
                            else: # names do not match check of on affiliation matches what we are looking for
                                a1=augmented_by_kthid[possible_id[0]].get('kth', False)
                                a2=augmented_by_kthid[possible_id[1]].get('kth', False)
                                if a1 == affiliation:
                                    kthid=possible_id[0]
                                elif a2 == affiliation:
                                    kthid=possible_id[1]
                                else:
                                    print("neither affiliation ({0}: {1}) or ({2}: {3}) matches what we are looking for {4}".format(possible_id[0], a1, possible_id[1], a2, affiliation))

                                    # this must be a missing entry
                                    kthid="{0}{1}".format(fakeid_start, fakeid_number)
                                    fakeid_number=fakeid_number+1
                                    new_entry=dict()
                                    new_entry['kthid']=kthid
                                    new_entry['kth']=affiliation
                                    new_entry['aliases']=[{'Name': name_record['name'], 'PID': [pid]}]
                                    augmented_by_kthid[kthid]=new_entry

                                    print("PID={0} has a missing or fake DiVA KTHID of {1} could not figure it out the real KTHID - name_record={2}, so made a new entry={3}".format(pid, kthid, name_record, new_entry))

                        else: # length is not 1 or 2, so iterate
                            does_one_affilation_match=False
                            for ai, a in enumerate(possible_id):
                                a1=augmented_by_kthid[a].get('kth', False)
                                if a1 == affiliation:
                                    kthid=a
                                    does_one_affilation_match=True
                                    print("found a matching affilation for ({0}:{1})".format(a, a1))
                            if not does_one_affilation_match:
                                print("none of the KTHIDs had a matching affilations")
                                # this must be a missing entry
                                kthid="{0}{1}".format(fakeid_start, fakeid_number)
                                fakeid_number=fakeid_number+1
                                new_entry=dict()
                                new_entry['kthid']=kthid
                                new_entry['kth']=affiliation
                                new_entry['aliases']=[{'Name': name_record['name'], 'PID': [pid]}]
                                augmented_by_kthid[kthid]=new_entry

                                print("PID={0} has a missing or fake DiVA KTHID of {1} could not figure it out the real KTHID - name_record={2}, so made a new entry={3}".format(pid, kthid, name_record, new_entry))

                        # or they could be ones with different affilations
                        #kthid=possible_id[0] # take the first - improve this later

            if not kthid:
                print("PID={0} has a missing or fake DiVA KTHID of {1} could not figure it out the real KTHID - name_record={2}".format(pid, kthid, name_record))
                # this must be a missing entry
                kthid="{0}{1}".format(fakeid_start, fakeid_number)
                fakeid_number=fakeid_number+1
                new_entry=dict()
                new_entry['kthid']=kthid
                new_entry['kth']=affiliation
                new_entry['aliases']=[{'Name': name_record['name'], 'PID': [pid]}]
                augmented_by_kthid[kthid]=new_entry
                
                print("PID={0} has a missing or fake DiVA KTHID of {1} could not figure it out the real KTHID - name_record={2}, so made a new entry={3}".format(pid, kthid, name_record, new_entry))


            print("kthid we have found is {0}".format(kthid))
            if fake_diva_kthid(kthid):
                print("*#*#* fake KTHID in pid={0},name_record={1}".format(pid, name_record))

            # here kthid should be an ID, even if it is one of my fake ones
            existing_entry=augmented_by_kthid.get(kthid, False)
            if existing_entry:
                existing_kthid=existing_entry.get('kthid', False)
                if existing_kthid == kthid:
                    existing_orcid=existing_entry.get('orcid', False)
                    if kthid and orcid and not existing_orcid:
                        print("PID={0} for kthid={1} name_record={2}, existing_orcid={3}, add orcid {4}".format(pid, kthid, name_record,  existing_orcid, orcid))
                        augmented_by_kthid[kthid]['orcid']=orcid
                else:
                    print("PID={0} has a KTHID of {1} existing entry={2}".format(pid, kthid, existing_kthid))
                    continue
                            


            if Verbose_Flag:
                print("Processing {0} name_record={1}".format(pid, name_record))
                print("PID={0} has a KTHID of {1} existing entry={2}".format(pid, kthid, existing_kthid))
            # add more here



    
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


    print("total entries={0}, number_of_entries_with_KTHIDs={1}, number_of_entries_with_KTHID_and_ORCID={2}, number_of_entries_with_fake_KTHIDs={3}, number_of_entries_with_fake_KTHIDs_with_ORCID={4}".format(len(augmented_by_kthid),
                                                                                                                                                                                                      number_of_entries_with_KTHIDs,
                                                                                                                                                                                                      number_of_entries_with_KTHID_and_ORCID,
                                                                                                                                                                                                      number_of_entries_with_fake_KTHIDs,
                                                                                                                                                                                                      number_of_entries_with_fake_KTHIDs_with_ORCID))


    return                      #  for testing stop here

    output_filename=spreadsheet_file[:-4]+'_pid_name_further.JSON'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for key in sorted(augmented_pid_and_authors.keys()):
            j_dict=dict()
            j_dict['PID']=key
            j_dict['entry']=augmented_pid_and_authors[key]
            j_as_string = json.dumps(j_dict, indent=4)
            print(j_as_string, file=output_FH)

        output_FH.close()
        


    # compute all of the aliases
    kthid_dict=dict()
    missing_kthid_records=dict()

    for key in sorted(augmented_pid_and_authors.keys()):
        entry=augmented_pid_and_authors[key]
        name=entry['Name']
        kthid=entry.get('kthid', False)
        orcid=entry.get('orcid', False)
        kth_affiliation=entry.get('kth', False)
        if kthid:
            existing_entry=kthid_dict.get(kthid, False)
            if not existing_entry:
                kthid_dict[kthid]=dict()
                kthid_dict[kthid]['orcid']=orcid
                kthid_dict[kthid]['kth']=kth_affiliation
                kthid_dict[kthid]['aliases']=list()
                kthid_dict[kthid]['aliases'].append({'Name': name, 'PID': [key]})
            else:
                if orcid and not existing_entry['orcid']: #  if not orcid stored, then store the one you just got
                    kthid_dict[kthid]['orcid'] = orcid
                current_aliases=kthid_dict[kthid]['aliases']
                added_alias=False
                for alias in current_aliases:
                    if alias['Name'] == name:
                        alias['PID'].append(key)
                        added_alias=True
                        break
                if not added_alias: #  it not an existing alias, then add the new one
                    kthid_dict[kthid]['aliases'].append({'Name': name, 'PID': [key]})
        else:
            existing_entry=missing_kthid_records.get(name, False)
            if not existing_entry:
                missing_kthid_records[name]={'orcid': orcid, 'PIDs': [key], 'kth': kth_affiliation}
            else:
                if orcid and not existing_entry['orcid']: #  if no orcid stored, then store the one you just got
                    missing_kthid_records[name]['orcid']=orcid
                if kth_affiliation and not existing_entry['kth']: #  if no affiliation store, then store the one you just got
                    missing_kthid_records[name]['kth']=kth_affiliation

                missing_kthid_records[name]['PIDs'].append(key)

    print("Number of KTH authors with KTHIDs={}".format(len(kthid_dict)))
    output_filename=spreadsheet_file[:-4]+'_pid_name_aliases.JSON'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for kthid in kthid_dict:
            j_dict=dict()
            j_dict['kthid']=kthid
            j_dict['entry']=kthid_dict[kthid]
            j_as_string = json.dumps(j_dict, indent=4)
            print(j_as_string, file=output_FH)

        output_FH.close()


    # entries missing KTHIDs for persons affilated with KTH
    print("Number of KTH authors without KTHIDs={}".format(len(missing_kthid_records)))
    output_filename=spreadsheet_file[:-4]+'_missing_kthids.csv'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        #output_FH.write('Sep=\\t\n')
        outline="Name\tKTHID\tORCID\tPIDs missing KTHIDs for named person\n"
        output_FH.write(outline)
        for entry in sorted(missing_kthid_records.keys()):
            orcid=missing_kthid_records[entry].get('orcid', False)
            if orcid:
                possible_kthid=False
                possible_kthid=try_to_lookup_orcid(orcid)
                #print("found orcid={0} possible_kthid={1}".format(orcid, possible_kthid))
                if not possible_kthid:
                    possible_kthid=try_to_lookup_name(entry)

                if possible_kthid:
                    outline="{0}\t{1}\t[{2}]\t{3}\t{4}\n".format(entry, possible_kthid, orcid, missing_kthid_records[entry]['PIDs'], missing_kthid_records[entry]['kth'])
                else:
                    outline="{0}\t\t[{1}]\t{2}\t{3}\n".format(entry, orcid, missing_kthid_records[entry]['PIDs'], missing_kthid_records[entry]['kth'])
                output_FH.write(outline)
            else:
                outline="{0}\t\t\t{1}\t{2}\n".format(entry, missing_kthid_records[entry]['PIDs'], missing_kthid_records[entry]['kth'])
                output_FH.write(outline)

        output_FH.write('---------\n')
        number_of_aliases_with_fake_kthids=0
        for kthid in kthid_dict: # add the fake KTHID entries to the missing set
            if kthid.find('PI0') == 0:
                outline="----{}-----\n".format(kthid)
                output_FH.write(outline)
                orcid=kthid_dict[kthid].get('orcid', False)
                aliases=kthid_dict[kthid].get('aliases', False)
                #print("kthid={0}, aliases={1}".format(kthid, aliases))
                for alias in aliases:
                    possible_kthid=False
                    possible_kthid=try_to_lookup_name(alias['Name'])
                        
                    if not possible_kthid:
                        outline="{0}\t\t\t{1}\n".format(alias['Name'], alias['PID'])
                    else:
                        orcid=kthid_dict[possible_kthid].get('orcid', False)
                        if orcid:
                            outline="{0}\t{1}\t[{2}\t{3}\n".format(alias['Name'], possible_kthid, orcid, alias['PID'])
                        else:
                            outline="{0}\t{1}\t\t{2}\n".format(alias['Name'], possible_kthid, alias['PID'])

                    output_FH.write(outline)
                    number_of_aliases_with_fake_kthids=number_of_aliases_with_fake_kthids+1

        output_FH.close()
        print("number of aliases with fake kthids={}".format(number_of_aliases_with_fake_kthids))

        
    # output_filename=augmented_json_file_name[:-4]+'_further_augmented.json'
    # with open(output_filename, 'w', encoding='utf-8') as output_FH:


if __name__ == "__main__": main()
