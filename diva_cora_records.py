#!/usr/bin/python3
#
# ./diva_cora_records.py
#
# Experiments with the new DiVA Cora Record API
#
# G. Q. Maguire Jr.
#
# 2025-05-04
#
# Example of runinng the program
#
#

import requests, time
import pprint
import optparse
import sys

from io import StringIO, BytesIO

import json

import datetime
import os                       # to make OS calls, here to get time zone info
import re

# use BeautifulSoup for parsing the HTML of the web page
from bs4 import BeautifulSoup

# Use Python Pandas to create XLSX files
import pandas as pd

# to use math.isnan(x) function
import math

# to normalize unicoded strings
import unicodedata

authToken='f30f0413-900d-4c80-bf9d-fc2c478309f0'


import logging
import http.client
LOG = []
class ListLoggerHandler(logging.Handler):
    def emit(self, record):
        msg = self.format(record)
        global LOG
        LOG.append(msg)
def httpclient_log_func(*args):
    LOG.append(args)
list_logging_handler = ListLoggerHandler()
root = logging.getLogger()
root.addHandler(list_logging_handler)
root.setLevel(logging.DEBUG)
http.client.HTTPConnection.debuglevel = 1
http.client.print = httpclient_log_func


#############################
###### EDIT THIS STUFF ######
#############################

global header	# the header for all HTML requests
global payload	# place to store additionally payload when needed for options to HTML requests


baseUrl='https://pre.diva-portal.org/'
#baseUrl='https://cora.diva-portal.org/diva/rest/'

#'Content-Type': 'application/json', 'Accept': 'application/json'

header= {
    'Content-Type': 'application/vnd.uub.record+xml',
    #'Accept': "application/vnd.uub.record+json",
    'Accept': 'application/vnd.uub.record+xml',
    'Accept': "application/vnd.uub.recordList+xml",
    #'Accept': '*/*',
    #'authToken': authToken
}

# from https://github.com/lsu-ub-uu/cora-therest/blob/master/src/main/java/se/uu/ub/cora/therest/record/RecordEndpointRead.java
# private static final String APPLICATION_XML = "application/xml";
# private static final String APPLICATION_XML_QS01 = "application/xml;qs=0.1";
# private static final String APPLICATION_VND_UUB_RECORD_XML = "application/vnd.uub.record+xml";
# private static final String APPLICATION_VND_UUB_RECORD_JSON = "application/vnd.uub.record+json";
# private static final String APPLICATION_VND_UUB_RECORD_JSON_QS09 = "application/vnd.uub.record+json;qs=0.9";
# private static final String TEXT_PLAIN_CHARSET_UTF_8 = "text/plain; charset=utf-8";

# from https://github.com/lsu-ub-uu/cora-therest/blob/master/src/main/java/se/uu/ub/cora/therest/record/RecordEndpointSearch.java
# private static final String APPLICATION_VND_UUB_RECORD_LIST_XML = "application/vnd.uub.recordList+xml";
# private static final String APPLICATION_VND_UUB_RECORD_LIST_JSON = "application/vnd.uub.recordList+json";
# private static final String APPLICATION_VND_UUB_RECORD_LIST_JSON_QS09 = "application/vnd.uub.recordList+json;qs=0.9";
# private static final String TEXT_PLAIN_CHARSET_UTF_8 = "text/plain; charset=utf-8";

payload = {}

def get_recordType(rt):
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    page_response=None
    #
    
    # set the content-type
    header= {
        'Content-Type': 'application/vnd.uub.record+json',
        'Accept':       'application/vnd.uub.record+json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9'
    }
    url=f"{baseUrl}rest/record/recordType/{rt}"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    print(f"{r.status_code=}")
    if r.status_code == requests.codes.ok:
        page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print("r.status_code is {r.status_code} and r.text is {r.text}")
    return page_response

def get_searchResult_publicTextSearch(search_data):
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    page_response=None
    #
    
    # set the content-type
    header= {
        'Content-Type': 'application/vnd.uub.recordList+json',
        'Accept':       'application/vnd.uub.recordList+json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9',
    }

    url=f"{baseUrl}rest/record/searchResult/publicTextSearch"
    if Verbose_Flag:
        print(f"{url=}")
    search_data_as_string=json.dumps(search_data, separators=(',', ':'))
    print(f"'{search_data_as_string}'| {len(search_data_as_string)=} last char is {search_data_as_string[-1]}")
    payload={'searchData': search_data_as_string}
    print(f"{payload=}")
    r = requests.get(url, headers = header, params=payload)
    #
    print(f"{r.status_code=}")
    if r.status_code == requests.codes.ok:
        page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"r.status_code is {r.status_code} and r.text is {r.text}")
    return page_response


def get_record(rt, id):
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    page_response=None
    #
    
    # set the content-type
    header= {
        'Content-Type': 'application/vnd.uub.record+json',
        'Accept':       'application/vnd.uub.record+json',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9'
    }
    url=f"{baseUrl}rest/record/recordType/{rt}"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    print(f"{r.status_code=}")
    if r.status_code == requests.codes.ok:
        page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print("r.status_code is {r.status_code} and r.text is {r.text}")
    return page_response


def data_accessible_to_user():
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    page_response=''
    #
    
    # set the content-type
    header= {
        'Content-Type': 'application/vnd.uub.recordList+xml',
        'Accept':       'application/vnd.uub.recordList+xml',
        #'Accept':       '*/*',
        'accept-encoding': 'gzip, deflate, br, zstd',
        'accept-language': 'en-US,en;q=0.9'
    }
    url=f"{baseUrl}rest/record/diva-person/"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    print(f"{r.status_code=}")
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        #print(f"{r.headers=}")
        page_response=r.text
        #page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response


def get_user_as_json(id):
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    page_response=dict()
    # set the content-type
    header= {
    'Content-Type': 'application/vnd.uub.record+json',
    'Accept':       'application/vnd.uub.record+json'
    }

    # user /rest/record/user/161616
    url=f"{baseUrl}rest/record/user/{id}"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    if r.status_code == requests.codes.ok:
        if Verbose_Flag:
            print(f"{r.text=}")
        page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response



def person(id):
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    page_response=''
    #
    url=f"{baseUrl}rest/record/diva-person/{id}"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        page_response=r.text
        #page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response

def diva_person():
    global Verbose_Flag
    global baseUrl
    global header
    global payload
    page_response=''
    #
    url=f"{baseUrl}rest/record/diva-person"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        page_response=r.text
        #page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response

def list_all_record_types():
    global Verbose_Flag
    global baseUrl
    global header
    global payload
    page_response=''
    #
    url=f"{baseUrl}rest/record/recordType"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        page_response=r.text
        #page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response

def read_single_record(record_type, id):
    global Verbose_Flag
    global baseUrl
    global header
    global payload
    page_response=''
    #
    url=f"{baseUrl}rest/record/{record_type}/{id}"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        page_response=r.text
        #page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response
    
def read_single_record_json(record_type, id):
    global Verbose_Flag
    global baseUrl
    global header
    global payload
    page_response=''
    #
    url=f"{baseUrl}rest/record/{record_type}/{id}"
    if Verbose_Flag:
        print(f"{url=}")
    r = requests.get(url, headers = header)
    #
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        #page_response=r.text
        page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response
    

def searchResult_search(search_id, search_data):
    global Verbose_Flag
    global baseUrl
    global header
    global payload
    page_response=''
    #
    url=f"{baseUrl}rest/record/searchResult/{search_id}"
    if Verbose_Flag:
        print(f"{url=}")
    # header = {'Content-Type':'application/vnd.uub.workorder+json',
    #           'Accept':'application/vnd.uub.recordList+xml'}
    header= {
        'Content-Type': 'application/json',
        'Accept': 'application/vnd.uub.recordList+xml'
    }

    

    payload={'searchData': json.dumps(search_data, separators=(',', ':'))}
    print(f"{payload=}")
    r = requests.get(url, headers = header, params=payload)
    #
    pprint.pprint(LOG)
    if r.status_code == requests.codes.ok:
        print(f"{r.text=}")
        page_response=r.text
        #page_response=json.loads(r.text)
    else:
        if Verbose_Flag:
            print(f"{r.status_code=} {r.text=}")
    return page_response
    
urlSpecificDomain = 'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={"name":"search","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"divaOrganisationDomainSearchTerm","value":"polar"}]}]}]}'


def search():
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(urlSpecificDomain, headers=headers)
    return(response.text)


def main():
    global Verbose_Flag
    global baseUrl
    global header
    global payload

    # some data used in the program
    Use_Local_Time_For_Output_Flag=True

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

    # if (len(remainder) < 1):
    #     print("Insuffient arguments must provide file_name.xlsx\n")
    #     return

    # spreadsheet_file=remainder[0]
    # print(f"file_name='{spreadsheet_file}'")


    # getting the recordType information works as follows
    rt='diva-person'
    rt_info=get_recordType(rt)
    print(f"recordType information for {rt}")
    pprint.pprint(rt_info)

    # try to do a search for publicText, currently returns a 401 saying:  <!doctype html><html lang="en"><head><title>HTTP Status 401 – Unauthorized</title><style type="text/css">body {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:white;background-color:#525D76;} h1 {font-size:22px;} h2 {font-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:black;} .line {height:1px;background-color:#525D76;border:none;}</style></head><body><h1>HTTP Status 401 – Unauthorized</h1><hr class="line" /><p><b>Type</b> Status Report</p><p><b>Message</b> Unauthorized</p><p><b>Description</b> The request has not been applied to the target resource because it lacks valid authentication credentials for that resource.</p><hr class="line" /><h3>Apache Tomcat/11.0.2</h3></body></html>
    search_data={"name": "textSearch",
                 "children": [{"name":"include",
                               "children": [{"name":"includePart",
                                             "children":[{"name":"translationSearchTerm","value":"kth"}]
                                             }]
                               }]
                }
    sr=get_searchResult_publicTextSearch(search_data)
   
    # the following returns '<?xml version="1.0" encoding="UTF-8"?><dataList><fromNo>0</fromNo><toNo>0</toNo><totalNo>0</totalNo><containDataOfType>diva-person</containDataOfType><data/></dataList>'
    accessible_data=data_accessible_to_user()
    print(f"{accessible_data=}")

    # r.status_code=406 r.text='<!doctype html><html lang="en"><head><title>HTTP Status 406 – Not Acceptable</title><style type="text/css">body {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:white;background-color:#525D76;} h1 {font-size:22px;} h2 {font-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:black;} .line {height:1px;background-color:#525D76;border:none;}</style></head><body><h1>HTTP Status 406 – Not Acceptable</h1><hr class="line" /><p><b>Type</b> Status Report</p><p><b>Message</b> Not Acceptable</p><p><b>Description</b> The target resource does not have a current representation that would be acceptable to the user agent, according to the proactive negotiation header fields received in the request, and the server is unwilling to supply a default representation.</p><hr class="line" /><h3>Apache Tomcat/11.0.2</h3></body></html>'
    person_id='001'
    pr=person(person_id)
    print(f"{person_id}: {pr=}")

    # The following works well
    #header['Accept']='*/*'
    header['Accept']='application/vnd.uub.record+json'
    record_type='system'
    #id='kthTestDiVAwr'
    id='divaPre'
    rr=read_single_record_json(record_type, id)
    print(f"{record_type=} {id=}: {rr=}")
    pprint.pprint(rr)

    # The following works well
    record_type='login'
    id='kthTestDiVAwr'
    rr=read_single_record_json(record_type, id)
    print(f"{record_type=} {id=}: {rr=}")
    pprint.pprint(rr)
    d1a=rr['record']['data']['attributes']
    print(f"type of login is {d1a['type']}") # should be  'webRedirect'
    d1c=rr['record']['data']['children']
    for c in d1c:
        if c['name'] == 'loginName':
            login_name=c['value']
            print(f"loginName is '{login_name}'")
        if c['name'] == 'url':
            print(f"url is {c['value']}")
        if c.get('children'):
            cc=c.get('children')
            for ccc in cc:
                if ccc.get('name'):
                    ccc_name=ccc.get('name')
                    if ccc_name == 'id':
                        print(f"id={ccc.get('value')}")
                    elif ccc_name == 'type':
                        print(f"type children: {ccc.get('children')} actionlinks: {ccc.get('actionLinks')}")
                    elif ccc_name == 'validationType':
                        print(f"validationType children: {ccc.get('children')} actionlinks: {ccc.get('actionLinks')}")
                    elif ccc_name == 'dataDivider':
                        print(f"dataDivider children: {ccc.get('children')} actionlinks: {ccc.get('actionLinks')}")
                    elif ccc_name == 'updated':
                        print(f"updated children: {ccc.get('children')} actionlinks: {ccc.get('actionLinks')}")
                    elif ccc_name == 'createdBy':
                        cccc=ccc.get('children')
                        if cccc:
                            for ccccc in cccc:
                                print(f"createdBy {ccccc['name']} -- {ccccc['value']}")
            
                    else:
                        ccc_value=ccc.get('value')
                        print(f"ccc name {ccc_name} {ccc_value}")

    # record_type='user'
    # id='141414'
    #record_type='text'
    #id='divaTextDefText'
    #id='diva-organisationText'
    record_type='diva-organisation'
    id='177'

    rr=read_single_record(record_type, id)
    print(f"{rr=}")

    # the following all fail with r.status_code=401 r.text='<!doctype html><html lang="en"><head><title>HTTP Status 401 – Unauthorized</title><style type="text/css">body {font-family:Tahoma,Arial,sans-serif;} h1, h2, h3, b {color:white;background-color:#525D76;} h1 {font-size:22px;} h2 {font-size:16px;} h3 {font-size:14px;} p {font-size:12px;} a {color:black;} .line {height:1px;background-color:#525D76;border:none;}</style></head><body><h1>HTTP Status 401 – Unauthorized</h1><hr class="line" /><p><b>Type</b> Status Report</p><p><b>Message</b> Unauthorized</p><p><b>Description</b> The request has not been applied to the target resource because it lacks valid authentication credentials for that resource.</p><hr class="line" /><h3>Apache Tomcat/11.0.2</h3></body></html>'
    #header['user-agent']='Mozilla/5.0'
    for u in ['161616', '131313', 'user:15433802151162560', 'guest']:
        u_json=get_user_as_json(u)
        print(f"{u} user information")
        pprint.pprint(u_json)

    pprint.pprint(LOG)
    return


    # search_data="<search><criteria>person</criteria></search>"
    # sr=searchResult_search(search_data)
    # print(f"{sr=}")

    #'https://pre.diva-portal.org/rest/record/searchResult/publicOrganisationSearch?searchData={"name":"search","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"divaOrganisationDomainSearchTerm","value":"kth"}]}]}]}'

    #'https://cora.diva-portal.org/diva/rest/record/searchResult/publicOrganisationSearch?searchData={"name":"search","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"divaOrganisationDomainSearchTerm","value":"kth"}]}]}]}'

    search_data={
        'name': 'search',
        'children': [{'name':'include',
                      'children': [{'name':'includePart',
                                    'children': [{'name':'divaOrganisationDomainSearchTerm',
                                                  'value':'kth'}]
                                    }]
                      }]
    }

    

    sr=searchResult_search('publicOrganisationSearch', search_data)


    #print(f"{search()=}")

    #baseUrl='https://cora.diva-portal.org/diva/rest/'
    u=f'{baseUrl}'+'record/searchResult/publicOrganisationSearch?searchData={"name":"search","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"divaOrganisationDomainSearchTerm","value":"kth"}]}]}]}'
    headers = {'User-Agent': 'Mozilla/5.0'}

    print(f"{u=}")
    response = requests.get(u, headers=headers)
    if response.status_code == requests.codes.ok:
        print(f"{response.text=}")

    print(f"{response.text}")

    # rectypes=list_all_record_types()
    # print(f"All record types: {rectypes=}")




if __name__ == "__main__": main()
