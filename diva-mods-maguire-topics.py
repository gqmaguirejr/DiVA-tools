#!/usr/bin/python
# -*- coding: utf-8 -*-
# the above encoding information is as per http://www.python.org/dev/peps/pep-0263/
#
# Purpose: To parse and extract information from MODS files from DiVA
#          specifically information about the abstracts and their language
#
# Input: ./diva-mods-maguire-topics.py -i xxxx.mods > xxxx.mods.a.csv
# Output: outputs a spreadhseet of the information and another spreadsheet named thesis_YEAR.csv
#
# note that you have to manually set "year" to the year as dddd - to get the correct output file
# 
# note that the "-v" (verbose) argument will generate a lot of output
#
# output from the feed:
# wget 'http://kth.diva-portal.org/smash/export.jsf?format=mods&aq=[[]]&aqe=[]&aq2=[[{"dateIssued":{"from":"2015","to":"2015"}},{"publicationTypeCode":["studentThesis"]}]]&onlyFullText=false&noOfRows=5000&sortOrder=title_sort_asc' -O 2015.mods
#
# Author: Gerald Q. Maguire Jr.
# 2015.05.14
#
#
from eulxml import xmlmap
from eulxml.xmlmap import load_xmlobject_from_file, mods
import lxml.etree as etree

from collections import defaultdict

import csv, codecs, cStringIO

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def empty_school_tuple():
    return {'Thesis_count': 0, 'Abstracts_eng_swe': 0, 'Abstracts_eng': 0, 'Abstracts_swe': 0, 'Abstracts_missing': 0, 'Abstracts_nor': 0, 'Abstracts_ger': 0,  'Keywords_eng_swe':0, 'Keywords_eng':0, 'Keywords_swe':0, 'Keywords_missing':0, }

Schools = dict()

import optparse
import sys
# import the following to be able to redirect stdout output to a file
#   while avoiding problems with unicode
import codecs, locale

parser = optparse.OptionParser()
parser.add_option('-i', '--input', 
                  dest="input_filename", 
                  default="default.mods",
                  )
parser.add_option('-y', '--year', 
                  dest="year", 
                  default="9999",
                  )

#parser.add_option('-o', '--output', 
#                  dest="output_filename", 
#                  default="default.out",
#                  )
parser.add_option('-v', '--verbose',
                  dest="verbose",
                  default=False,
                  action="store_true",
                  help="Print lots of output to stdout"
                  )

options, remainder = parser.parse_args()

Verbose_Flag=options.verbose
if Verbose_Flag:
    print 'ARGV      :', sys.argv[1:]
    print 'VERBOSE   :', options.verbose
    print 'INPUT     :', options.input_filename
    print 'YEAR      :', options.year
    print 'REMAINING :', remainder



#set sdout so that it can output UTF-8
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

#fileHandle=open('mods-maguire.mods', 'r')
fileHandle=open( options.input_filename, 'r')
tree=load_xmlobject_from_file(fileHandle, mods.MODS)

#<name type="personal"><namePart type="family">Abad Caballero</namePart><namePart type="given">Israel Manuel</namePart><namePart type="date">1978-</namePart><role><roleTerm type="code" authority="marcrelator">aut</roleTerm></role><affiliation>KTH, Mikroelektronik och Informationsteknik, IMIT</affiliation><affiliation>CCSlab</affiliation></name><name type="corporate"><namePart>CCSlab</namePart><role><roleTerm type="code" authority="marcrelator">oth</roleTerm></role><description>Research Group</description></name>

affiliation=''
author_affiliation=''
name_family=''
name_given=''
author_name_family=''
author_name_given=''
supervisor_name_family=''
supervisor_name_given=''
supervisor_affiliation=''
examiner_name_family=''
examiner_name_given=''
examiner_affiliation=''
corporate_name=''
publisher_name=''
thesis_dateIssued=''
thesis_title=''
thesis_abstract_language=[]
list_of_topics_English=[]
list_of_topics_Swedish=[]
current_subject_language=''
English_Abstract=''
Swedish_Abstract=''
role=''
name_type=''

def new_output_record():
    global role
    global affiliation, author_affiliation, supervisor_affiliation, examiner_affiliation
    global name_family, name_given, author_name_family, author_name_given, supervisor_name_family, supervisor_name_given
    global examiner_name_family, examiner_name_given, corporate_name, publisher_name
    global thesis_title, thesis_abstract_language
    global thesis_dateIssued
    global thesis_url
    global thesis_url_fulltext
    global thesis_recordOrigin
    global list_of_topics_English
    global list_of_topics_Swedish
    global current_subject_language
    global English_Abstract
    global Swedish_Abstract
    global name_type
#

    affiliation=''
    author_affiliation=''
    supervisor_affiliation=''
    examiner_affiliation=''
    name_family=''
    name_given=''
    author_name_family=''
    author_name_given=''
    supervisor_name_family=''
    supervisor_name_given=''
    examiner_name_family=''
    examiner_name_given=''
    corporate_name=''
    publisher_name=''
    thesis_dateIssued=''
    thesis_url=''
    thesis_recordOrigin=''
    thesis_title=''
    thesis_abstract_language=[]
    thesis_url_fulltext=''
    list_of_topics_English=[]
    list_of_topics_Swedish=[]
    English_Abstract=''
    Swedish_Abstract=''
    role=''
    name_type='Unknown'

def output_column_heading():
# set the serparator to tab
    print "sep=\\t"
# output the column headings
    print "author_name_family" + "\t" + "author_name_given" + "\t" + "author_affiliation" + "\t" + "supervisor_name_family" + "\t" + "supervisor_name_given" + "\t" + "supervisor_affiliation" + "\t" + "examiner_name_family" + "\t" +  "examiner_name_given" + "\t" + "examiner_affiliation" + "\t" + "publisher_name" + "\t" + "thesis_dateIssued" + "\t" + "thesis_url"  +"\t" + "thesis_url_fulltext" + "\t" + "thesis_recordOrigin" + "\t" + "thesis_title" + "\t" + "thesis_abstract_language" + "\t" + "list_of_topics_English" +"\t" "list_of_topics_Swedish" +"\t" + "English_Abstract" +"\t" + "Swedish_Abstract"


def output_current_record():
    global affiliation, author_affiliation, supervisor_affiliation, examiner_affiliation
    global name_family, name_given, author_name_family, author_name_given, supervisor_name_family, supervisor_name_given
    global examiner_name_family, examiner_name_given, corporate_name, publisher_name
    global thesis_title, thesis_abstract_language
    global thesis_dateIssued
    global thesis_url
    global thesis_recordOrigin
    global thesis_url_fulltext
    global English_Abstract
    global Swedish_Abstract
#
#    print name_family
#    print name_given
    print author_name_family + "\t" + author_name_given + "\t" + author_affiliation + "\t" + supervisor_name_family + "\t" + supervisor_name_given + "\t" + supervisor_affiliation + "\t" + examiner_name_family + "\t" +  examiner_name_given + "\t" + examiner_affiliation + "\t" + publisher_name + "\t" + thesis_dateIssued + "\t" + thesis_url + "\t" + thesis_url_fulltext + "\t" + thesis_recordOrigin + "\t" + thesis_title + "\t" + str(sorted(thesis_abstract_language)) + "\t" + str(list_of_topics_English) +"\t" + str(list_of_topics_Swedish) + "\t" + English_Abstract +"\t" + Swedish_Abstract

# for a given publisher update their statistical entry regarding the languages used for abstracts
def Update_schools_statistics():
    global thesis_abstract_language
    global publisher_name
    eng_found=0
    swe_found=0

    global list_of_topics_English
    global list_of_topics_Swedish

#
    if Verbose_Flag:
        print "Update_schools_statistics " + publisher_name + " " + str(sorted(thesis_abstract_language))
#
    if publisher_name not in Schools:
#        Schools[publisher_name] = {'Thesis_count': 0, 'Abstracts_eng_swe': 0, 'Abstracts_eng': 0, 'Abstracts_swe': 0, 'Abstracts_missing': 0, 'Abstracts_nor': 0, 'Abstracts_ger': 0,}
        Schools[publisher_name] = empty_school_tuple()
#
#
    Schools[publisher_name]['Thesis_count'] = int(Schools[publisher_name]['Thesis_count']) + 1
    if Verbose_Flag:
        print 'Schools['+publisher_name+']=' + str(Schools[publisher_name])
        print 'Thesis_count'
        print Schools[publisher_name]['Thesis_count']
#
    if Verbose_Flag:
        print "thesis_abstract_language=" + str(sorted(thesis_abstract_language))
#
    if len(thesis_abstract_language) == 0:
        Schools[publisher_name]['Abstracts_missing'] = int(Schools[publisher_name]['Abstracts_missing']) + 1
        if Verbose_Flag:
            print 'Missing abstracts'
    else:
        abstract_language=sorted(thesis_abstract_language)
        for i in range(0, len(abstract_language)):
            if abstract_language[i] == 'eng':
                # the following check is because I found a thesis that had two abstracts, but claimed both were in English, when only one was
                if not eng_found:
                    Schools[publisher_name]['Abstracts_eng'] = int(Schools[publisher_name]['Abstracts_eng']) + 1
                    eng_found=1
            if abstract_language[i] == 'swe':
                if not swe_found:
                    Schools[publisher_name]['Abstracts_swe'] = int(Schools[publisher_name]['Abstracts_swe']) + 1
                    swe_found=1
            if abstract_language[i] == 'nor':
                Schools[publisher_name]['Abstracts_nor'] = int(Schools[publisher_name]['Abstracts_nor']) + 1
            if abstract_language[i] == 'ger':
                Schools[publisher_name]['Abstracts_ger'] = int(Schools[publisher_name]['Abstracts_ger']) + 1
#
    if  eng_found and swe_found:
        Schools[publisher_name]['Abstracts_eng_swe'] = int(Schools[publisher_name]['Abstracts_eng_swe']) + 1



    if (len(list_of_topics_English) > 0) and (len(list_of_topics_Swedish) > 0):
        Schools[publisher_name]['Keywords_eng_swe'] = int(Schools[publisher_name]['Keywords_eng_swe']) + 1

    if len(list_of_topics_English) > 0:
        Schools[publisher_name]['Keywords_eng'] = int(Schools[publisher_name]['Keywords_eng']) + 1

    if len(list_of_topics_Swedish) > 0:
        Schools[publisher_name]['Keywords_swe'] = int(Schools[publisher_name]['Keywords_swe']) + 1

    if (len(list_of_topics_English) == 0) and (len(list_of_topics_Swedish) == 0):
        Schools[publisher_name]['Keywords_missing'] = int(Schools[publisher_name]['Keywords_missing']) + 1


# 'Abstracts_eng_swe': 0, 'Abstracts_eng': 0, 'Abstracts_swe': 0, 'Abstracts_missing': 0,}

def Output_statistics():
    if Verbose_Flag:
        print "Statistics"
#
    year=options.year
    output_file  = open('theses_'+str(year)+'.csv', "wb")
    writer = UnicodeWriter(output_file)
#output the special command line as the first line of the file to Excel that the spearator is a tab                                      
#        output_file.write('sep=\t\n')                                                                                                       
#        print "Thesis_count	Abstracts_eng_swe	Abstracts_eng	Abstracts_swe	Abstracts_missing"
               
    headings = ['Year', 'School', 'Thesis_count', 'Abstracts_eng_swe', 'Abstracts_eng', 'Abstracts_swe', 'Abstracts_missing', 'Abstracts_nor', 'Abstracts_ger', 'Keywords_eng_swe', 'Keywords_eng', 'Keywords_swe', 'Keywords_missing']
    writer.writerow(headings)

    keylist = Schools.keys()
    keylist.sort()
    for key in keylist:
        entry=Schools[key]
        out_row = [year, key, str(entry['Thesis_count']), str(entry['Abstracts_eng_swe']), str(entry['Abstracts_eng']), str(entry['Abstracts_swe']), str(entry['Abstracts_missing']), str(entry['Abstracts_nor']), str(entry['Abstracts_ger']),  str(entry['Keywords_eng_swe']), str(entry['Keywords_eng']), str(entry['Keywords_swe']), str(entry['Keywords_missing']),]
#
        if Verbose_Flag:
            print out_row
        writer.writerow(out_row)
#
    output_file.close()


    

def print_namePart(np):
    global name_family, name_given
    global name_type
    global affiliation
    global corporate_name
#
    affiliation=''
    if Verbose_Flag:
        print "namePart: " + np.text
    if len(np.attrib) > 0:
        if Verbose_Flag:
            print np.attrib
            print "name_type" + name_type
        if (name_type is not None):
            if Verbose_Flag:
                print "name_type" + name_type
                print "(name_type.count('personal') =" + str(name_type.count('personal'))
        if (name_type is not None) and (name_type.count('personal') == 1):
            if np.attrib['type']:
                if np.attrib['type'].count('family') == 1 :
                    name_family=np.text
                    if Verbose_Flag:
                        print "name_family: "+ name_family
                elif np.attrib['type'].count('given') == 1 :
                    name_given=np.text
                    if Verbose_Flag:
                        print "name_given: " + name_given
                else:
                    if Verbose_Flag:
                        print np.attrib['type'] + " " + np.text
    elif (name_type is not None) and (name_type.count('corporate')  ==  1):
        if len(corporate_name) > 0:
            corporate_name = corporate_name + "," + np.text
        else:
            corporate_name = np.text


def print_role_term(rt):
    global role
    global affiliation, author_affiliation, supervisor_affiliation, examiner_affiliation
    global name_family, name_given, author_name_family, author_name_given, supervisor_name_family, supervisor_name_given
    global examiner_name_family, examiner_name_given, corporate_name, publisher_name
#
    if Verbose_Flag:
        print "roleTerm: "
    if len(rt.attrib) > 0:
        if Verbose_Flag:
            print rt.attrib
    if rt.text is not None:
        if Verbose_Flag:
            print rt.text
    if rt.text.count('aut') == 1:
        author_name_family = name_family
        author_name_given = name_given
        role = 'aut'
        if Verbose_Flag:
            print "author_name_family: " + author_name_family
            print "author_name_given: " + author_name_given
    elif rt.text.count('ths') == 1:
        supervisor_name_family = name_family
        supervisor_name_given = name_given
        role = 'ths'
        if Verbose_Flag:
            print "supervisor_name_family: " + supervisor_name_family
            print "supervisor_name_given: " + supervisor_name_given
    elif rt.text.count('mon') == 1:
        examiner_name_family = name_family
        examiner_name_given = name_given
        role = 'mon'
        if Verbose_Flag:
            print "examiner_name_family: " + examiner_name_family
            print "examiner_name_given: " + examiner_name_given
    elif rt.text.count('pbl') == 1:
        publisher_name = corporate_name
        role = 'pbl'
        if Verbose_Flag:
            print "publisher_name: " + publisher_name
    elif rt.text.count('oth') == 1:
        # clear the corporate_name if this is a "oth" role
        corporate_name=''
#
    if Verbose_Flag:
        print "name_family: " + name_family
        print "name_given: " + name_given

#<role><roleTerm
def print_role(r):
    if Verbose_Flag:
        print "role :"
    if len(r.attrib) > 0:
        if Verbose_Flag:
            print r.attrib
    if r.text is not None:
        if Verbose_Flag:
            print r.text
    for i in range(0, len(r)):
        rt=r[i]
        if rt.tag.count("}roleTerm") == 1:
            print_role_term(rt)
        else:
            if Verbose_Flag:
                print "rt[" + str(i) +"]"
                print rt

            
def print_affiliation(a):
    global role
    global affiliation, author_affiliation, supervisor_affiliation, examiner_affiliation
    if Verbose_Flag:
        print "affiliation :"
    if len(a.attrib) > 0:
        if Verbose_Flag:
            print a.attrib
    if a.text is not None:
        if len(affiliation) > 0:
            affiliation = affiliation + ' ,' + a.text
        else:
            affiliation=a.text
        if role.count('aut') == 1:
            author_affiliation = affiliation
        elif role.count('ths') == 1:
            supervisor_affiliation = affiliation
        elif role.count('mon') == 1:
            examiner_affiliation = affiliation
        if Verbose_Flag:
            print a.text

def print_description(d):
    if Verbose_Flag:
        print "description: "
    if len(d.attrib) > 0:
        if Verbose_Flag:
            print d.attrib
    if d.text is not None:
        if Verbose_Flag:
            print d.text

def print_name(mod_elem):
    global name_type
#
    name_type = 'Unknown'
#
    if Verbose_Flag:
        print "Name: "
        print "Name attribute: " + str(mod_elem.attrib)
        print "Name text: " + str(mod_elem)
    if len(mod_elem.attrib) > 0:
        if Verbose_Flag:
            print "Name: " + mod_elem.attrib['type'] + " its type is=" + str(type(mod_elem.attrib['type']))
        if mod_elem.attrib['type'] is not None:
            if Verbose_Flag:
                print "mod_elem.attrib['type'] is not None"
                print "mod_elem.attrib['type'].count('personal')=" + str(mod_elem.attrib['type'].count('personal'))
            if (mod_elem.attrib['type'].count('corporate')) > 0:
                name_type='corporate'
            elif (mod_elem.attrib['type'].count('personal')) > 0:
                    name_type='personal'
    else:
        name_type='unknown'
#
    if Verbose_Flag:
        print "in print_name - 2, name_type=" + name_type
#
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}namePart") == 1:
            print_namePart(elem)
        elif elem.tag.count("}role") == 1:
            print_role(elem)
        elif elem.tag.count("}affiliation") == 1:
            print_affiliation(elem)
        elif elem.tag.count("}description") == 1:
            print_description(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(n) +"]"
                print elem

def print_title(elem):
    global thesis_title
    if Verbose_Flag:
        print "title: "
    if len(elem.attrib) > 0:
        if Verbose_Flag:
            print elem.attrib
    if elem.text is not None:
        thesis_title=elem.text
        if Verbose_Flag:
            print elem.text


def print_titleInfo(mod_elem):
    if Verbose_Flag:
        print "TitleInfo: "
    if len(mod_elem.attrib) > 0:
        if Verbose_Flag:
            print mod_elem.attrib
    if mod_elem.text is not None:
        if Verbose_Flag:
            print mod_elem.text
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}title") == 1:
            print_title(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem


def print_languageTerm(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print "LanguageTerm: "
            print elem.text
    
def print_language(mod_elem):
    if Verbose_Flag:
        print "Language: "
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}languageTerm") == 1:
            print_languageTerm(elem)
        elif elem.tag.count("}dateIssued") == 1:
            print_dateIssued(elem)
        elif elem.tag.count("}dateOther") == 1:
            print_datedateOther(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem


def print_dateIssued(elem):
    global thesis_dateIssued
    if elem.text is not None:
        thesis_dateIssued=elem.text
        if Verbose_Flag:
            print "dateIssued: "
            print elem.text


def print_datedateOther(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print "dateOther: "
            print elem.attrib
            print elem.text

def print_originInfo(mod_elem):
    if Verbose_Flag:
        print "originInfo: "
#       print mod_elem
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}languageTerm") == 1:
            print_languageTerm(elem)
        elif elem.tag.count("}dateIssued") == 1:
            print_dateIssued(elem)
        elif elem.tag.count("}dateOther") == 1:
            print_datedateOther(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem

def print_identifier(elem):
    global thesis_url
    if elem.text is not None:
        thesis_url=elem.text
        if Verbose_Flag:
            print "identifier: "
            print elem.text


def print_abstract(mod_elem):
    global thesis_abstract_language
    global English_Abstract
    global Swedish_Abstract
#
    if Verbose_Flag:
        print "Abstract: "
        print "Attrib: "
    if len(mod_elem.attrib) > 0:
        thesis_abstract_language.append(mod_elem.attrib['lang'])
        if Verbose_Flag:
            print mod_elem.attrib
    if mod_elem.text is not None:
        if Verbose_Flag:
            print mod_elem
    if mod_elem.attrib['lang'] == 'eng':
        English_Abstract=mod_elem.text
    elif mod_elem.attrib['lang'] == 'swe':
        Swedish_Abstract=mod_elem.text

def print_recordOrigin(elem):
    global thesis_recordOrigin
    if elem.text is not None:
        thesis_recordOrigin=elem.text
        if Verbose_Flag:
            print elem.text

def print_recordContentSource(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text

def print_recordCreationDate(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text

def print_recordChangeDate(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text


def print_recordIdentifier(elem):
    if elem.text is not None:
        if Verbose_Flag:
            print elem.text


#<recordContentSource>kth</recordContentSource><recordCreationDate>2012-04-11</recordCreationDate><recordChangeDate>2013-09-09</recordChangeDate><recordIdentifier>diva2:515038</recordIdentifier></recordInfo>
def print_recordInfo(mod_elem):
    if Verbose_Flag:
        print "recordInfo: "
        print mod_elem
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}recordOrigin") == 1:
            print_recordOrigin(elem)
        elif elem.tag.count("}recordContentSource") == 1:
            print_recordContentSource(elem)
        elif elem.tag.count("}recordCreationDate") == 1:
            print_recordCreationDate(elem)
        elif elem.tag.count("}recordChangeDate") == 1:
            print_recordChangeDate(elem)
        elif elem.tag.count("}recordIdentifier") == 1:
            print_recordIdentifier(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem
        

def print_topic(mod_elem):
    global list_of_topics_English
    global list_of_topics_Swedish
    global current_subject_language
#
    if mod_elem.text is not None:
        if current_subject_language == 'eng':
            list_of_topics_English.append(mod_elem.text)
        if current_subject_language == 'swe':
            list_of_topics_Swedish.append(mod_elem.text)
        if Verbose_Flag:
            print "topic: "
            print mod_elem.tag
            print mod_elem.text

def print_subject(mod_elem):
    global current_subject_language
#
    if len(mod_elem.attrib) > 0:
        current_subject_language=mod_elem.attrib['lang']
        xlink=len(mod_elem.attrib)-1
        if xlink:
            current_subject_language=''
        if Verbose_Flag:
            print "current_subject_language=" + str(current_subject_language)
#
    if Verbose_Flag:
        print "subject: "
        print mod_elem.tag
        print mod_elem.text
        if len(mod_elem.attrib) > 0:
            print mod_elem.attrib
        if Verbose_Flag:
            print mod_elem.attrib

    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}topic") == 1:
            print_topic(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem

def print_typeOfResource(mod_elem):
    if Verbose_Flag:
        print "typeOfResource: "
        print mod_elem.tag
        print mod_elem.text
        for i in range(0, len(mod_elem)):
            elem=mod_elem[i]
            if elem.tag.count("}subject") == 1:
                print_topic(elem)
            else:
                if Verbose_Flag:
                    print "mod_emem[" + str(i) +"]"
                    print elem

def print_url(elem):
    global thesis_url_fulltext
    if elem.text is not None:
        thesis_url_fulltext=elem.text
        if Verbose_Flag:
            print "url: "
            print elem.text


def print_location(mod_elem):
#    print "location: "
#    print mod_elem.tag
#    print mod_elem.text
    for i in range(0, len(mod_elem)):
        elem=mod_elem[i]
        if elem.tag.count("}url") == 1:
            print_url(elem)
        else:
            if Verbose_Flag:
                print "mod_emem[" + str(i) +"]"
                print elem

#tree.node
#<Element {http://www.loc.gov/mods/v3}modsCollection at 0x34249b0>
#>>> tree.node[1]
#<Element {http://www.loc.gov/mods/v3}mods at 0x3d46aa0>

output_column_heading()
for i in range(0, len(tree.node)):
    if tree.node[i].tag.count("}modsCollection") == 1:
# case of a modsCollection
        if Verbose_Flag:
            print "Tag: " + tree.node[i].tag
            print "Attribute: "
            print tree.node[i].attrib
# case of a mods
    elif tree.node[i].tag.count("}mods") == 1:
        if Verbose_Flag:
            print "new mods Tag: " + tree.node[i].tag
#  print "Attribute: " + etree.tostring(tree.node[i].attrib, pretty_print=True) 
            print "Attribute: " 
            print tree.node[i].attrib
#
# print information about the publication
#
        new_output_record()
#
        current_mod=tree.node[i]
        if Verbose_Flag:
            print "Length of mod: "+ str(len(current_mod))
        for mod_element in range(0, len(current_mod)):
            current_element=current_mod[mod_element]
            if Verbose_Flag:
                print "TAG: " 
                print current_element
            if current_element.tag.count("}name") == 1:
                print_name(current_element)
            elif current_element.tag.count("}titleInfo") == 1:
                print_titleInfo(current_element)
            elif current_element.tag.count("}language") == 1:
                print_language(current_element)
            elif current_element.tag.count("}originInfo") == 1:
                print_originInfo(current_element)
            elif current_element.tag.count("}identifier") == 1:
                print_identifier(current_element)
            elif current_element.tag.count("}abstract") == 1:
                print_abstract(current_element)
            elif current_element.tag.count("}subject") == 1:
                print_subject(current_element)
            elif current_element.tag.count("}recordInfo") == 1:
                print_recordInfo(current_element)
            elif current_element.tag.count("}location") == 1:
                print_location(current_element)
            elif current_element.tag.count("}typeOfResource") == 1:
                print_typeOfResource(current_element)
#
        output_current_record()
        Update_schools_statistics()
    else:
        if Verbose_Flag:
            print "Tag: " + tree.node[i].tag


Output_statistics()
