#!/usr/bin/python3
#
# ./further_augment_from_CSV_file.py xxx.csv xxx.augmented.json
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

def get_author_from_authorString(author):
    entry=dict()
    firstLeftParen=author.find('(')
    firstLeftBracket=author.find('[')
    str_length=len(author)
    #
    # name [xx] [yy-yy-yy] (affiliation)
    if (firstLeftBracket < 0) and (firstLeftParen < 0): #  no brackets or parens, then just a name
        entry['name']=author[:].strip()
        return entry
    #
    if (firstLeftBracket < 0) and  (firstLeftParen > 0): #  if paren, then just a name (affiliation)
        entry['name']=author[:firstLeftParen-1].strip()
        entry['affiliation']=author[firstLeftParen:].strip()
        return entry
    #
    if (firstLeftBracket > 0) and  (firstLeftParen > 0): #  if paren, then just a name [xx] [yy] (affiliation) or  name [xx] (affiliation)
        entry['name']=author[:firstLeftBracket-1].strip()
        entry['affiliation']=author[firstLeftParen:].strip()
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
    print("augmented_lookup_orcid={} failed to find:".format(orcid_to_lookfor))    
    return False

# function returns a kthid (fake or not)
def augmented_lookup_name(name_to_look_for, augmented_by_kthid):
    # names can either be in "profile": {"firstName": "Gerald Quentin", "lastName": "Maguire Jr"}}
    # or in the list of aliases: "entry": {"aliases": [{"Name": "Maguire Jr., Gerald Q.", "PID": [528381, ...]}, {"Name": "Maguire, Gerald Q.", "PID": [561069]}, {"Name": "Maguire Jr., Gerald", "PID": [561509]}, {"Name": "Maguire, Gerald Q., Jr.", "PID": [913155]}]}
    for e in augmented_by_kthid:
        item=augmented_by_kthid[e]
        profile=item.get('profile', False)
        if profile:
            firstName=profile.get('firstName', False)
            lastName=profile.get('lastName', False)
            if firstName and lastName:
                combined_name="{0}, {1}".format(lastName, firstName)
                if combined_name == name_to_look_for:
                    return e
            elif firstName and not lastName:
                combined_name="{0}".format(firstName)
                if combined_name == name_to_look_for:
                    return e
            elif not firstName and lastName:
                combined_name="{0}".format(lastName)
                if combined_name == name_to_look_for:
                    return e
            else:
                print("Error:: Profile, but no firstname or lastname")
        #
        entry=item.get('entry', False)
        if entry:
            aliases=entry.get('aliases', False)
            if aliases:
                for a in aliases:
                    if not a.get('Name', False):
                        print("a={}".format(a))

                    if a['Name'] == name_to_look_for:
                        return e                        
    return False

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
    # default to True, i.e., it is fake
    return True

def fake_kthid(possible_kthid):
    if possible_kthid.find('⚠⚠') == 0:
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
        pid_and_author_entry[c]=line[all_quotemarks[c_start]:all_quotemarks[c_end]+1]
    return pid_and_author_entry



def main():
    global Verbose_Flag
    global augmented_pid_and_authors
    global kthid_dict
    global pp

    parser = optparse.OptionParser()

    parser.add_option('-v', '--verbose',
                      dest="verbose",
                      default=False,
                      action="store_true",
                      help="Print lots of output to stdout"
    )

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

    pid_Flag=options.pid

    if (len(remainder) < 2):
        print("Insuffient arguments must provide file_name.csv fine_name-augmented.json\n")
        return

    spreadsheet_file=remainder[0]
    print("file_name='{0}'".format(spreadsheet_file))

    augmented_json_file_name=remainder[1]
    print("augmented_json_file_name='{0}'".format(augmented_json_file_name))

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    augmented_by_kthid=dict()
    fakeid_number=0
    fakeid_start='⚠⚠'
    # read the lines from the JSON file
    with open(augmented_json_file_name, 'r') as augmented_FH:
        for line in augmented_FH:
            if Verbose_Flag:
                print(line)
            try:
                j=json.loads(line)
            except:
                print("error in line: {}".format(line))
                print({}.format(sys.exc_info()))
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
            augmented_by_kthid[kthid]=j

    print("length of augmented_by_kthid={}".format(len(augmented_by_kthid)))

    if Verbose_Flag:
        for e in augmented_by_kthid:
            if e.find(fakeid_start) >= 0:
                pp.pprint(augmented_by_kthid[e])

    print("augmented_by_kthid for u1d13i2c={}".format(augmented_by_kthid['u1d13i2c']))

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

    # get KTHIDs and ORCID if they exist, output as JSON
    # also keeo track of the alternative names and on which publication they are used
    augmented_pid_and_authors=dict()
    for pna in pid_and_authors:
        pid_str=pna['PID']
        pid = int(pid_str[1:-1])

        names=get_authors_from_authorsString(pna['Name'])
        pna['names']=names      # save the parse authors information

        for name in names:
            existing_kthid=False
            existing_orcid=False

            kthid=name.get('kthid',False)
            orcid=name.get('orcid',False)
            affiliation=name.get('affiliation',False)

            # look for affiliations and skip them
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
                        print("PID={0} has a fake DiVA KTHID of {1}, it should be {2} - found by orcid={3} for name={4}".format(pid, kthid, possible_id, orcid, name))
                        kthid=possible_id

                # since the kthid was fake, look up the user by name
                possible_id=augmented_lookup_name(name, augmented_by_kthid)
                if possible_id:
                    print("PID={0} has a fake DiVA KTHID of {1}, it should be {2} - found by name={3}".format(pid, kthid, possible_id, name))
                    kthid=possible_id

                if not kthid:
                    print("PID={0} has a missing or fake DiVA KTHID of {1} could not figure it out the real KTHID - name={2}".format(pid, kthid, name))
                    continue

            # here kthid should be an ID, even if it is one of my fake ones
            existing_entry=augmented_by_kthid.get(kthid, False)
            if existing_entry:
                existing_kthid=existing_entry.get('kthid', False)
                if existing_kthid == kthid:
                    existing_orcid=existing_entry.get('orcid', False)
                    if kthid and orcid and not existing_orcid:
                        print("PID={0} for kthid={1} name={2}, existing_orcid={3}, add orcid {4}".format(pid, kthid, name,  existing_orcid, orcid))
                        augmented_by_kthid[kthid]['orcid']=orcid
                else:
                    print("PID={0} has a KTHID of {1} existing entry={2}".format(pid, kthid, existing_kthid))
                    continue
                            


            if Verbose_Flag:
                print("Processing {0} name={1}".format(pid, name))
                print("PID={0} has a KTHID of {1} existing entry={2}".format(pid, kthid, existing_kthid))
            # add more here


    return                      #  for testing stop here

    output_filename=spreadsheet_file[:-4]+'_pid_name.JSON'
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
