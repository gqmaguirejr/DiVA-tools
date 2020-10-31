#!/usr/bin/python3
#
# ./get_pid_and_names.py diva_spreadsheet.csv
#
# reads in a CSV spreaadsheet of DiVA entries and uses the information to generates several output files.
# These files identify publications with has information about publications and their KTH authors,
# information about KTH authors who do not have a KTHID in the DiVA record for one or more publications, and
# a summary of all the names and "aliases" of a KTH author (indicating whicih publications this name/alias has been used for).
#
#kth-exluding-theses-all-level2-2012-2019_pid_name.csv - which contains entries of the for PID and authors:
#"913155","Olivecrona, Henrik (Karolinska Institutet, Sweden) (Department of Molecular Medicine and Surgery, Section of Orthopaedics and Sport Medicine);Maguire, Gerald Q., Jr. [u1d13i2c] [0000-0002-6066-746X] (KTH [177], Skolan för informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998], Radio Systems Laboratory (RS Lab) [13053]);Noz, Marilyn E. [0000-0002-2442-1622] (New York University,  Department of Radiology) (Nuclear Medicine);Zeleznik, Michael P. [0000-0002-0706-1805] (University of Utah) (School of Computing, College of Engineering);Kesteris, Uldis (Department of Orthopedics, Skåne University Hospital);Weidenhielm, Lars [0000-0002-4280-1178] (Karolinska Institutet at Karolinska University Hospital Solna) (Department of Molecular Medicine and Surgery)"
#
# kth-exluding-theses-all-level2-2012-2019_pid_name.JSON which contains entires of the form:
# {
#     "PID": 528381,
#     "entry": {
#         "Name": "Maguire Jr., Gerald Q.",
#         "kthid": "u1d13i2c",
#         "orcid": "0000-0002-6066-746X",
#         "kth": " (KTH [177], Skolan f\u00f6r informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])"
#     }
# }
#
#  kth-exluding-theses-all-level2-2012-2019_missing_kthids.csv which contains entries of the form:
#Name	KTHID	ORCID	PIDs missing KTHIDs for named person
# ..
# Gross, J			[1055431]	 (KTH [177], Skolan för elektro- och systemteknik (EES) [5977])
# ...
#
#  kth-exluding-theses-all-level2-2012-2019_pid_name_aliases.JSON which contains entries of the form:
# {
#     "kthid": "u1d13i2c",
#     "entry": {
#         "orcid": "0000-0002-6066-746X",
#         "kth": " (KTH [177], Skolan f\u00f6r informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])",
#         "aliases": [
#             {
#                 "Name": "Maguire Jr., Gerald Q.",
#                 "PID": [
#                     528381,
#                     606323,
#                     638177,
#                     675824,
#                     675849,
# ...
#                     1314634,
#                     1367981,
#                     1416571
#                 ]
#             },
#             {
#                 "Name": "Maguire, Gerald Q.",
#                 "PID": [
#                     561069
#                 ]
#             },
#             {
#                 "Name": "Maguire Jr., Gerald",
#                 "PID": [
#                     561509
#                 ]
#             },
#             {
#                 "Name": "Maguire, Gerald Q., Jr.",
#                 "PID": [
#                     913155
#                 ]
#             }
#         ]
#     }
# }
#
#
# G. Q. Maguire Jr.
#
# 2020-10-27
#
# Example of runinng the program
# ./get_pid_and_names.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019.csv
#
# the above spreadsheet has Sheet1
#  wget -O kth-exluding-theses-all-level2-2012-2019.csv 'https://kth.diva-portal.org/smash/export.jsf?format=csvall2&addFilename=true&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":"2012","to":"2019"}},{"organisationId":"177","organisationId-Xtra":true},{"publicationTypeCode":["bookReview","review","article","artisticOutput","book","chapter","manuscript","collection","other","conferencePaper","patent","conferenceProceedings","report","dataset"]}]]&onlyFullText=false&noOfRows=5000000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'
#
#  wget -O eecs-exluding-theses-all-level2-2012-2019.csv 'https://kth.diva-portal.org/smash/export.jsf?format=csvall2&addFilename=true&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":"2012","to":"2019"}},{"organisationId":"879223","organisationId-Xtra":true},{"publicationTypeCode":["bookReview","review","article","artisticOutput","book","chapter","manuscript","collection","other","conferencePaper","patent","conferenceProceedings","report","dataset"]}]]&onlyFullText=false&noOfRows=5000000&sortOrder=title_sort_asc&sortOrder2=title_sort_asc'
#
# for the example command it produces:
#  kth-exluding-theses-all-level2-2012-2019_missing_kthids.csv
#  kth-exluding-theses-all-level2-2012-2019_pid_name_aliases.JSON
#  kth-exluding-theses-all-level2-2012-2019_pid_name.JSON
#
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

    if (len(remainder) < 1):
        print("Insuffient arguments must provide file_name.csv\n")
        return

    spreadsheet_file=remainder[0]
    print("file_name='{0}'".format(spreadsheet_file))

    pp = pprint.PrettyPrinter(indent=4) # configure prettyprinter

    pid_and_authors=[]

    # read the lines from the spreadsheet
    if spreadsheet_file.endswith('.csv'):
        with open(spreadsheet_file, 'r') as spreadsheet_FH:
            for index, line in enumerate(spreadsheet_FH):
                if index == 0:  # skip header line
                    continue
                pid_and_author=dict()
                all_quotemarks=[x.start() for x in re.finditer('"', line)] # find offset of all quotmarks
                pid_and_author['PID'] =line[all_quotemarks[0]:all_quotemarks[1]+1]
                pid_and_author['Name']=line[all_quotemarks[2]:all_quotemarks[3]+1]
                pid_and_authors.append(pid_and_author)

    else:
        print("Unknown file extension for the spreadsheet")
        return
    print("Finished reading spreadsheet")

    if pid_Flag:
        output_filename=spreadsheet_file[:-4]+'_name.csv'
    else:
        output_filename=spreadsheet_file[:-4]+'_pid_name.csv'
    with open(output_filename, 'w', encoding='utf-8') as output_FH:
        for pna in pid_and_authors:
            if not pid_Flag:
                outline="{0},{1}\n".format(pna['PID'], pna['Name'])
                output_FH.write(outline)
            else:
                names=pna['Name']
                names=split_names(names[1:-1]) # remove the quotes from around the string
                for name in names:
                    outline="{0}\n".format(name.strip())
                    output_FH.write(outline)
            
        output_FH.close()


    # get KTHIDs and ORCID if they exist, output as JSON
    # also keeo track of the alternative names and on which publication they are used
    augmented_pid_and_authors=dict()
    for pna in pid_and_authors:
        pid_str=pna['PID']
        pid = int(pid_str[1:-1])

        names=pna['Name']
        names=split_names(names[1:-1]) # remove the quotes from around the string
        for name in names:
            kthid=False
            orcid=False
            kth_affiliation=False

            kth_affiliation_flag=name.find('(KTH') # look for affiliations and skip them
            if kth_affiliation_flag < 0:
                continue

            first_left_paren=name.find('(KTH') # look for affiliations and remove them
            if first_left_paren> 0:
                kth_affiliation=name[first_left_paren-1:] # save the affiliation information
                name=name[0:first_left_paren-1]


            all_left_brackets=[x.start() for x in re.finditer('\[', name)] # find offset of all left square brackets, note quote the bracket
            if len(all_left_brackets) > 0:
                first_left_bracket=all_left_brackets[0]
                if first_left_bracket > 0:
                    first_left_bracket=first_left_bracket+1
                    closing_bracket=name.find(']', first_left_bracket)
                    if closing_bracket > 0:
                        first_substring=name[first_left_bracket:closing_bracket]
                        if first_substring.find('-') > 0: # this is an orcid ID
                            orcid=first_substring
                        else:
                            kthid=first_substring
                    else:
                        print("No closing right bracket in {}".format(name))

            if len(all_left_brackets) > 1:
                second_left_bracket=all_left_brackets[1]
                if second_left_bracket > 0:
                    second_left_bracket=second_left_bracket+1
                    closing_bracket=name.find(']', second_left_bracket)
                    if closing_bracket > 0:
                        second_substring=name[second_left_bracket:closing_bracket]
                        orcid=second_substring
                    else:
                        print("No closing right bracket in {}".format(name))

            if len(all_left_brackets) > 0: # trim off kthid and orcid
                name=name[0:all_left_brackets[0]-1].strip()

            if kthid and orcid:
                augmented_pid_and_authors[pid]={'Name': name, 'kthid': kthid, 'orcid': orcid, 'kth': kth_affiliation}
            elif kthid:
                augmented_pid_and_authors[pid]={'Name': name, 'kthid': kthid, 'kth': kth_affiliation}
            elif orcid:
                augmented_pid_and_authors[pid]={'Name': name, 'orcid': orcid, 'kth': kth_affiliation}
            else:
                augmented_pid_and_authors[pid]={'Name': name, 'kth': kth_affiliation}

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

if __name__ == "__main__": main()
