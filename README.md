# DiVA-tools
A set of tools for working with DiVA (specifically the KTH Publication
Database instance of DiVA. The DiVA-logga grön webb logo <img width="48" height="48" src="DiVA-star_green-web.jpg"> appears under CC Attribution-NonCommercial 3.0 Unported (CC BY-NC 3.0).

DiVA contains publications produced by the researchers and students and is
used by quite a number of universities, university colleges, and research
institutes. The search interface for KTH's DiVA portal is
[http://kth.diva-portal.org](http://kth.diva-portal.org). Via this web
interface it is also possible to create feeds in a variety of formats.

An interface to more DiVA functionality can be found at [https://kth.diva-portal.org/dream/info.jsf](https://kth.diva-portal.org/dream/info.jsf).

DiVA can import and export references in a number of formats, one of these is
The Library of Congress's [Metadata Object Description Schema (MODS) XML
format](http://www.loc.gov/standards/mods/). Documentation for importing
references is in [Import References to DiVA](http://www.ub.umu.se/sites/default/files/dokument/import_references_to_diva.pdf).

You can find the description of DiVA's MODS format at [
https://wiki.epc.ub.uu.se/display/divainfo/Formatspecifikation+och+systembeskrivning](https://wiki.epc.ub.uu.se/display/divainfo/Formatspecifikation+och+systembeskrivning)

The Library of Congress » Standards » MODS Official Web Site
Metadata Object Description Schema: Official Web Site: [MARC 21 to MODS 3.6
Mapping, March 2016](http://www.loc.gov/standards/mods/mods-mapping.html).

======================================================================
## diva-get_bibmods.py

Purpose: To fetch and process publication information from DiVA for an author

Input:
```
./diva-get_bibmods.py KTHID_of_user
```

Output: outputs user_name.mods

Note that spaces in the user's name are converted to "_"

Example:
```
./diva-get_bibmods.py u1d13i2c
```

You can convert the MODS file to BibTeX, for example:
```
xml2bib < Maguire_Jr.mods >Maguire_Jr.bib
```

xml2bib is available from [https://sourceforge.net/projects/bibutils/](https://sourceforge.net/projects/bibutils/)
alternatively a version adapted for English and Swedish at [https://github.com/gqmaguirejr/bibutils_6.2_for_DiVA](https://github.com/gqmaguirejr/bibutils_6.2_for_DiVA)

## diva-get_bibmods_theses.py

Purpose: To fetch and process thesis information from DiVA for an examiner

Input:
```
./diva-get_bibmods_theses.py KTHID_of_user
```

Output: outputs user_name_theses.mods

Note that spaces in the user's name are converted to "_".

Example:
```
./diva-get_bibmods_theses.py u1d13i2c
```

## diva-get_bibmods_theses_school.py
Purpose: To fetch and process thesis information from DiVA for a school

Input
```
./diva-get_bibmods_theses_school.py org_id [start_year] [end_year]
```
Output: outputs org_id_theses-YYYY-YYYY.mods

Example:
```
./diva-get_bibmods_theses_school.py EECS 2015
```
You can convert the MODS file to BibTeX, for example:
```
xml2bib xml2bib EECS_theses-2015-2015.mods > EECS_theses-2015-2015.bib
```

## diva-get_bibmods_school.py
Purpose: To fetch and process publication information from DiVA for a school

Input
```
./diva-get_bibmods_school.py org_id [start_year] [end_year]
```
Output: outputs org_id_YYYY-YYYY.mods

Example:
```
./diva-get_bibmods_school.py EECS 2018
```
You can convert the MODS file to BibTeX, for example:
```
xml2bib EECS_2018-2018.mods > EECS_2018-2018.bib
```


## diva-mods-maguire-topics.py

Purpose: To parse and extract information from MODS files from DiVA
          specifically information about the abstracts and their language

Input:
```
./diva-mods-maguire-topics.py -i xxxx.mods > xxxx.mods.a.csv
```
Output: outputs a spreadhseet of the information and another spreadsheet named thesis_YEAR.csv

Note that you have to manually set "year" to the year as dddd - to get the correct output file.
 
Note that the "-v" (verbose) argument will generate a lot of output.


## diva-theses-year-range.py

Purpose: To fetch and process thesis information from DiVA for yearA to yearB
            (To get information about keywords and abstracts)

Input:
```
./diva-theses-year-range.py --start yearA --end yearB
```

Output: outputs a spreadhseet of the information

Note that "year" should be in the form dddd

## summarize_year.py

Purpose: To summarize the data from theses_XXXX.csv for yearA to yearB
            (To collect information about keywords and abstracts)

reads a csv file with lines of the form:
```
Year,School,Thesis_count,Abstracts_eng_swe,Abstracts_eng,Abstracts_swe,Abstracts_missing,Abstracts_nor,Abstracts_ger,Keywords_eng_swe,Keywords_eng,Keywords_swe,Keywords_missing
#2010,"KTH,Skolan för arkitektur och samhällsbyggnad (ABE)",1,0,1,0,0,0,0,0,1,0,0
...
```

Input:
```
./summarize_year.py --start yearA --end yearB
```

Output: outputs a spreadhseet of the information

Note that "year" should be in the form dddd

## do_mods.bash

A simple bash script to iterate calling one of the programs
```
#!/bin/bash
for i in {2010..2018}
do
   ./diva-mods-maguire-topics.py -y $i -i $i.mods > $i.mods.a.csv
done
```

## compare-scores.py

Purpose: To compare the manually assigned national subject categories with those computed by LiU's tools


Input:
```
./compare-scores.py input_spreadsheet
```

Output: outputs a spreadhseet augmented with the information

## check_abstracts.py

Purpose: To compare the manually assigned national subject categories with those computed by LiU's tools


Input:
```
./check_abstracts.py spreadsheet.xlsx
```

Output: outputs a new spreadhseet augmented with the normalized text for the abstracts
and outputs lines such as:

The sv abstract for pid 1202682 urn:nbn:se:kth:diva-226955 could be normalized
document with PID 1203913 urn:nbn:se:kth:diva-227247 is missing Categories information

Note that it only guesses the language correctly for English and Swedish.

## nation_subject_test-a.py

Purpose: To augment a spreadsheet of DiVA data with the Linköping University server's sujects and scores data


Input:
```
./nation_subject_test-a.py input_spreadsheet.csv
or
./nation_subject_test-a.py input_spreadsheet.xlsx
```

Output: outputs a spreadhseet augmented with the information

## Putting together a set of commands to process DiVA records for National Subject Categories

Use the DiVA GUI to create a feed of type "CSV all meta data version 2".


```
Use wget -O filename.csv feed_string

./nation_subject_test-a.py filename.csv
The above outputs filename-_with_LiU_scores.xlsx

./compare-scores.py  filename_with_LiU_scores.xlsx
The above outputs filename_with_LiU_scores_compared.xlsx

```

## process_diva_export_xlsx.py

Purpose: process the output of a DiVA feed containg CSV data. We assume the spreadsheet has been loaded into Excel or similar tool and saved in XLSX format.

The tool illustrates how to use python pandas to process each of the rows for some purpose. Examples are given of simply computing data and outputting this data and an example of computing something and adding it to the spreadsheet as a new column.

Input:
```
./process_diva_export_xlsx.py all_student_theses_kth.xlsx
```

Output: outputs a spreadhseet (in the above case the file will be called "all_student_theses_kth.augmented.xlsx") augmented with the information that has been added and outputs text that was computed

Example:
```
./process_diva_export_xlsx.py /tmp/all_student_theses_kth.xlsx
number of columns is 68
frequency of languages ={'ita': 1, 'fre': 1, 'ara': 2, 'nob': 1, 'eng': 16484, 'nor': 12, 'swe': 7868}
title_lengths = {2: 2, 3: 1, 4: 2, 5: 2, 6: 6, 7: 5, 8: 15, 9: 13, 10: 12, 11: 16, 12: 20, 13: 24, 14: 25, 15: 30, 16: 27, 17: 38, 18: 39, 19: 54, 20: 39, 21: 44, 22: 49, 23: 59, 24: 55, 25: 51, 26: 49, 27: 54, 28: 74, 29: 70, 30: 116, 31: 84, 32: 91, 33: 76, 34: 145, 35: 90, 36: 120, 37: 113, 38: 99, 39: 153, 40: 109, 41: 175, 42: 156, 43: 148, 44: 161, 45: 169, 46: 190, 47: 165, 48: 161, 49: 160, 50: 191, 51: 150, 52: 217, 53: 183, 54: 193, 55: 173, 56: 196, 57: 220, 58: 202, 59: 217, 60: 220, 61: 211, 62: 207, 63: 181, 64: 201, 65: 238, 66: 224, 67: 229, 68: 199, 69: 197, 70: 182, 71: 218, 72: 203, 73: 201, 74: 204, 75: 236, 76: 219, 77: 228, 78: 205, 79: 225, 80: 197, 81: 189, 82: 190, 83: 198, 84: 202, 85: 180, 86: 206, 87: 194, 88: 169, 89: 166, 90: 181, 91: 211, 92: 177, 93: 173, 94: 190, 95: 152, 96: 163, 97: 167, 98: 167, 99: 189, 100: 184, 101: 163, 102: 145, 103: 143, 104: 168, 105: 134, 106: 157, 107: 125, 108: 142, 109: 130, 110: 150, 111: 130, 112: 131, 113: 139, 114: 126, 115: 133, 116: 142, 117: 130, 118: 137, 119: 114, 120: 137, 121: 130, 122: 111, 123: 121, 124: 105, 125: 111, 126: 99, 127: 88, 128: 121, 129: 103, 130: 89, 131: 113, 132: 87, 133: 101, 134: 92, 135: 105, 136: 80, 137: 95, 138: 88, 139: 92, 140: 94, 141: 74, 142: 77, 143: 92, 144: 84, 145: 93, 146: 77, 147: 81, 148: 83, 149: 88, 150: 78, 151: 74, 152: 76, 153: 87, 154: 97, 155: 70, 156: 68, 157: 83, 158: 55, 159: 79, 160: 78, 161: 57, 162: 64, 163: 68, 164: 61, 165: 57, 166: 74, 167: 66, 168: 56, 169: 54, 170: 65, 171: 65, 172: 48, 173: 53, 174: 44, 175: 56, 176: 46, 177: 49, 178: 52, 179: 48, 180: 51, 181: 46, 182: 48, 183: 45, 184: 50, 185: 52, 186: 54, 187: 48, 188: 51, 189: 42, 190: 51, 191: 42, 192: 46, 193: 46, 194: 43, 195: 43, 196: 47, 197: 44, 198: 40, 199: 37, 200: 50, 201: 41, 202: 32, 203: 35, 204: 42, 205: 43, 206: 30, 207: 27, 208: 41, 209: 35, 210: 44, 211: 35, 212: 29, 213: 37, 214: 46, 215: 27, 216: 23, 217: 31, 218: 33, 219: 30, 220: 27, 221: 38, 222: 25, 223: 31, 224: 27, 225: 28, 226: 18, 227: 25, 228: 29, 229: 32, 230: 33, 231: 17, 232: 21, 233: 25, 234: 23, 235: 30, 236: 18, 237: 25, 238: 29, 239: 21, 240: 35, 241: 24, 242: 25, 243: 24, 244: 26, 245: 13, 246: 23, 247: 15, 248: 31, 249: 16, 250: 14, 251: 23, 252: 17, 253: 18, 254: 17, 255: 15, 256: 14, 257: 14, 258: 18, 259: 16, 260: 17, 261: 17, 262: 22, 263: 14, 264: 14, 265: 14, 266: 8, 267: 13, 268: 11, 269: 9, 270: 14, 271: 10, 272: 15, 273: 12, 274: 9, 275: 7, 276: 11, 277: 11, 278: 12, 279: 11, 280: 10, 281: 14, 282: 8, 283: 5, 284: 6, 285: 13, 286: 6, 287: 7, 288: 4, 289: 10, 290: 11, 291: 7, 292: 9, 293: 8, 294: 12, 295: 4, 296: 6, 297: 10, 298: 7, 299: 8, 300: 3, 301: 11, 302: 6, 303: 5, 304: 3, 305: 5, 306: 8, 307: 2, 308: 12, 309: 7, 310: 4, 311: 6, 312: 8, 313: 7, 314: 8, 315: 3, 316: 2, 317: 3, 318: 7, 319: 8, 320: 5, 321: 2, 322: 5, 323: 2, 324: 6, 325: 3, 326: 5, 327: 5, 328: 4, 329: 3, 330: 6, 331: 6, 332: 2, 333: 3, 334: 3, 335: 10, 336: 4, 337: 4, 338: 6, 339: 3, 340: 2, 341: 2, 342: 3, 343: 5, 344: 1, 345: 2, 346: 4, 347: 2, 348: 3, 349: 3, 350: 2, 351: 5, 352: 2, 353: 1, 354: 4, 355: 3, 356: 2, 357: 4, 358: 3, 359: 1, 360: 2, 362: 3, 363: 1, 364: 1, 365: 2, 366: 4, 367: 1, 368: 1, 369: 2, 370: 3, 371: 2, 372: 2, 373: 3, 374: 2, 375: 2, 376: 2, 377: 3, 379: 2, 380: 2, 381: 1, 382: 2, 384: 1, 388: 1, 389: 2, 390: 1, 391: 1, 392: 1, 393: 2, 395: 2, 396: 1, 398: 1, 401: 1, 404: 1, 405: 1, 406: 1, 407: 1, 409: 1, 410: 1, 414: 2, 416: 2, 418: 1, 419: 2, 426: 1, 432: 1, 439: 1, 441: 1, 444: 2, 445: 1, 452: 1, 460: 1, 483: 1, 489: 1, 494: 1, 496: 1, 498: 1, 510: 1, 550: 1, 595: 1, 1005: 1}
```
Note that the above will also output some warning due to the fact that there are some fields where the URL is longer than Excel's limits for URLs.

# process_diva_export_xlsx_files.py

Purpose: fetch the full text of publications via DiVA

Input:
```
./process_diva_export_xlsx_files.py all_student_theses_kth.xlsx [working_directory]
```

Output: The theses will be output to the working_directory (by default '/tmp/theses') in subdirectories by year.

Example:
```
./process_diva_export_xlsx_files.py /tmp/all_student_theses_kth_sorted-eecs-2019.xlsx /tmp/theses
number of columns is 70
fetching 2019 full text for diva_number=247301
--2019-12-09 13:47:38--  http://kth.diva-portal.org/smash/get/diva2:1298315/FULLTEXT01.pdf
Resolving kth.diva-portal.org (kth.diva-portal.org)... 130.238.7.114
Connecting to kth.diva-portal.org (kth.diva-portal.org)|130.238.7.114|:80... connected.
HTTP request sent, awaiting response... 200 OK
Length: 1482791 (1.4M) [application/pdf]
Saving to: ‘/tmp/theses/2019/thesis-247301.pdf’

/tmp/theses/2019/thesis-247301.pd 100%[===========================================================>]   1.41M  --.-KB/s    in 0.1s    

2019-12-09 13:47:39 (10.7 MB/s) - ‘/tmp/theses/2019/thesis-247301.pdf’ saved [1482791/1482791]
...
```

# pub_language.py

Purpose: reads in xlsx file (exported from DiVA in CSV with all meta data; converted to XLSX) and processes each publication

Input:
```
./pub_language.py xxxx.xlsx
```

Output: , then outputs a dictionary with some statistical data about the use languages for each type of document

Example:
```
./pub_language.py /tmp/KTH-2012-2019-pub-excluding-theses-and-disserations.xlsx
dictionaries={
'Artikel i tidskrift': {
	  'Övrig (populärvetenskap, debatt, mm)': {'dan': 3, 'eng': 37, 'est': 2, 'fin': 2, 'nor': 3, 'spa': 1, 'swe': 231},
	  'Övrigt vetenskapligt': {'eng': 1049, 'fre': 1, 'swe': 44},
	  'Refereegranskat': {'chi': 5, 'dut': 2, 'eng': 22623, 'est': 1, 'ger': 11, 'por': 2, 'spa': 1, 'swe': 48, 'tur': 1}},
'Artikel, forskningsöversikt': {
	  'Övrig (populärvetenskap, debatt, mm)': {'eng': 3, 'swe': 6},
	  'Övrigt vetenskapligt': {'eng': 6, 'swe': 2},
	  'Refereegranskat': {'eng': 416, 'swe': 2}},
'Artikel, recension': {
	  'Övrig (populärvetenskap, debatt, mm)': {'eng': 3, 'nor': 1, 'swe': 28},
	  'Övrigt vetenskapligt': {'eng': 77, 'ger': 1, 'swe': 9},
	  'Refereegranskat': {'eng': 16, 'swe': 2}},
'Bok': {
          'Övrig (populärvetenskap, debatt, mm)': {'eng': 5, 'ita': 1, 'swe': 18},
          'Övrigt vetenskapligt': {'dan': 1, 'dut': 1, 'eng': 64, 'swe': 34},
          'Refereegranskat': {'eng': 43, 'ger': 1, 'nor': 1, 'swe': 10}},
'Kapitel i bok, del av antologi': {
          'Övrig (populärvetenskap, debatt, mm)': {'eng': 18, 'ita': 1, 'swe': 43},
          'Övrigt vetenskapligt': {'dan': 1, 'eng': 462, 'fre': 2, 'ger': 5, 'ita': 3, 'nor': 1, 'por': 1, 'swe': 108},
          'Refereegranskat': {'chi': 2, 'dan': 1, 'eng': 744, 'est': 1, 'ita': 1, 'jpn': 1, 'nor': 1, 'por': 1, 'swe': 28}},
'Konferensbidrag': {
          'Övrig (populärvetenskap, debatt, mm)': {'eng': 33, 'ger': 2, 'jpn': 2, 'swe': 42},
	  'Övrigt vetenskapligt': {'eng': 834, 'fre': 1, 'ger': 5, 'spa': 2, 'swe': 82},
	  'Refereegranskat': {'eng': 10651, 'est': 1, 'fre': 1, 'ger': 7, 'ita': 1, 'pol': 1, 'spa': 5, 'swe': 61}},
'Konstnärlig output': {
	  'Granskad': {'eng': 5, 'swe': 3},
	  'Ogranskad': {'eng': 13, 'swe': 2}},
'Manuskript (preprint)': {
	  'Övrig (populärvetenskap, debatt, mm)': {'eng': 1},
	  'Övrigt vetenskapligt': {'eng': 105}},
'Övrigt': {
	  'Övrig (populärvetenskap, debatt, mm)': {'dut': 3, 'eng': 41, 'fin': 1, 'fre': 1, 'ita': 2, 'nor': 4, 'swe': 97},
	  'Övrigt vetenskapligt': {'eng': 48, 'ita': 1, 'swe': 13},
	  'Refereegranskat': {'eng': 10}},
'Patent': {'Övrig (populärvetenskap, debatt, mm)': {'eng': 55, 'rus': 2, 'swe': 3}},
'Proceedings (redaktörskap)': {
          'Övrig (populärvetenskap, debatt, mm)': {'eng': 2, 'swe': 1},
	  'Övrigt vetenskapligt': {'eng': 16, 'swe': 1},
	  'Refereegranskat': {'eng': 39}},
'Rapport': {
	  'Övrig (populärvetenskap, debatt, mm)': {'eng': 27, 'spa': 1, 'swe': 79},
	  'Övrigt vetenskapligt': {'eng': 484, 'fre': 1, 'nor': 4, 'swe': 273},
	  'Refereegranskat': {'eng': 60, 'swe': 11}},
'Samlingsverk (redaktörskap)': {
          'Övrig (populärvetenskap, debatt, mm)': {'eng': 2, 'swe': 4},
	  'Övrigt vetenskapligt': {'eng': 32, 'swe': 12},
	  'Refereegranskat': {'eng': 56, 'ger': 1, 'swe': 3}}
}

```

# pub_language_theses.py

Purpose: reads in xlsx file (exported from DiVA in CSV with all meta data; converted to XLSX) and processes each publication

Input:
```
./pub_language_theses.py xxxx.xlsx
```

Output: a dictionary with some statistical data about the use languages for each type of thesis

Example:
```
./pub_language_theses.py ~/Working/E-learning/all_student_theses_kth.xlsx
number of columns is 68
dictionaries={'Självständigt arbete på avancerad nivå (yrkesexamen)': {'20 poäng / 30 hp': {'eng': 1089, 'swe': 602}, '10 poäng / 15 hp': {'swe': 201, 'eng': 105}, '300 hp': {'eng': 2, 'swe': 2}, '30 poäng / 45 hp': {'eng': 3, 'swe': 8}, '40 poäng / 60 hp': {'eng': 1}}, 'Självständigt arbete på avancerad nivå (magisterexamen)': {'10 poäng / 15 hp': {'eng': 325, 'swe': 174, 'nor': 2}, '20 poäng / 30 hp': {'eng': 234, 'swe': 68}, '15 poäng / 22,5 hp': {'eng': 15, 'swe': 2}, '40 poäng / 60 hp': {'eng': 23, 'swe': 8}, '12 poäng / 18 hp': {'eng': 1}, '60 poäng / 90 hp': {'eng': 7}, '5 poäng / 7,5 hp': {'eng': 1}, '30 poäng / 45 hp': {'eng': 9, 'swe': 1}, '180 hp': {'eng': 2}}, 'Självständigt arbete på avancerad nivå (masterexamen)': {'20 poäng / 30 hp': {'swe': 1845, 'eng': 11279, 'fre': 1, 'ita': 1}, '80 poäng / 120 hp': {'eng': 122, 'swe': 1}, '30 poäng / 45 hp': {'eng': 67, 'swe': 3}, '300 hp': {'eng': 19, 'swe': 5}, '10 poäng / 15 hp': {'eng': 81, 'swe': 15}, '25 poäng / 37,5 hp': {'eng': 2, 'swe': 1}, '330 hp': {'eng': 1}, '20hp': {'eng': 13, 'swe': 1}, '10 hp': {'eng': 1}, '40 poäng / 60 hp': {'eng': 6}, '5 hp': {'eng': 3}, '180 hp': {'eng': 3}, '10,5 poäng / 16 hp': {'eng': 1}, '60 poäng / 90 hp': {'eng': 4}}, 'Självständigt arbete på grundnivå (kandidatexamen)': {'20 poäng / 30 hp': {'eng': 33, 'swe': 4}, '10 poäng / 15 hp': {'eng': 2518, 'swe': 3258, 'nor': 1}, '15 poäng / 22,5 hp': {'eng': 2, 'swe': 1}, '80 poäng / 120 hp': {'swe': 1}, '180 hp': {'swe': 1}, '12 poäng / 18 hp': {'swe': 1}, '5 poäng / 7,5 hp': {'swe': 1}, '10,5 poäng / 16 hp': {'eng': 2}, '10 hp': {'eng': 1}}, 'Studentarbete övrigt': {'5 poäng / 7,5 hp': {'eng': 1}, '10 poäng / 15 hp': {'eng': 1, 'swe': 2}, '20 poäng / 30 hp': {'eng': 78, 'swe': 1}}, 'Självständigt arbete på grundnivå (yrkesexamen)': {'20 poäng / 30 hp': {'eng': 57, 'swe': 65}, '10 poäng / 15 hp': {'eng': 126, 'swe': 326}, '30 poäng / 45 hp': {'swe': 9, 'eng': 2}, '180 hp': {'swe': 1}, '12 poäng / 18 hp': {'swe': 1}, '5 poäng / 7,5 hp': {'swe': 1}}, 'Självständigt arbete på grundnivå (högskoleexamen)': {'10 poäng / 15 hp': {'swe': 1132, 'eng': 108}, '20 poäng / 30 hp': {'swe': 34, 'eng': 27}, '5 poäng / 7,5 hp': {'swe': 69, 'eng': 4}, '12 hp': {'swe': 2}, '15 poäng / 22,5 hp': {'swe': 1, 'eng': 1}, '180 hp': {'swe': 3}, '80 poäng / 120 hp': {'swe': 1}}, 'Självständigt arbete på avancerad nivå (masterexamen);Självständigt arbete på avancerad nivå (masterexamen)': {'20 poäng / 30 hp;20 poäng / 30 hp': {'eng': 38, 'swe': 9}, '80 poäng / 120 hp;80 poäng / 120 hp': {'eng': 1}}, 'Självständigt arbete på avancerad nivå (masterexamen);Självständigt arbete på avancerad nivå (yrkesexamen)': {'20 poäng / 30 hp;20 poäng / 30 hp': {'eng': 13}}, 'Självständigt arbete på avancerad nivå (yrkesexamen);Självständigt arbete på avancerad nivå (masterexamen)': {'20 poäng / 30 hp;20 poäng / 30 hp': {'eng': 26, 'swe': 1}}, 'Självständigt arbete på grundnivå (kandidatexamen);Självständigt arbete på grundnivå (yrkesexamen)': {'10 poäng / 15 hp;10 poäng / 15 hp': {'eng': 2, 'swe': 1}}, 'Självständigt arbete på grundnivå (högskoleexamen);Självständigt arbete på grundnivå (högskoleexamen)': {'10 poäng / 15 hp;10 poäng / 15 hp': {'swe': 3, 'eng': 1}}, 'Självständigt arbete på grundnivå (kandidatexamen);Självständigt arbete på grundnivå (kandidatexamen)': {'10 poäng / 15 hp;10 poäng / 15 hp': {'swe': 5, 'eng': 3}, '10 poäng / 15 hp;12 poäng / 18 hp': {'swe': 1}}, 'Självständigt arbete på grundnivå (konstnärlig högskoleexamen)': {'20 poäng / 30 hp': {'eng': 1}, '10 poäng / 15 hp': {'swe': 2}}, 'Självständigt arbete på avancerad nivå (masterexamen);Självständigt arbete på avancerad nivå (magisterexamen)': {'20 poäng / 30 hp;20 poäng / 30 hp': {'eng': 1}}, 'Studentarbete andra termin': {'20 poäng / 30 hp': {'eng': 5}}, 'Självständigt arbete på avancerad nivå (masterexamen);Självständigt arbete på avancerad nivå (masterexamen);Självständigt arbete på avancerad nivå (masterexamen)': {'20 poäng / 30 hp;20 poäng / 30 hp;20 poäng / 30 hp': {'eng': 1}}, 'Självständigt arbete på grundnivå (konstnärlig kandidatexamen)': {'10 poäng / 15 hp': {'swe': 1}}, 'Självständigt arbete på avancerad nivå (masterexamen);': {'20 poäng / 30 hp;': {'eng': 1}}, 'Studentarbete första termin': {'20 poäng / 30 hp': {'eng': 1}}, 'Självständigt arbete på grundnivå (yrkesexamen);Självständigt arbete på grundnivå (kandidatexamen)': {'10 poäng / 15 hp;10 poäng / 15 hp': {'swe': 1}}}
```
# top_level_stats_by_kthid.py

Purpose: compute top-level statistics from a spreadsheet of DiVA data

Input:
```
 ./top_level_stats_by_kthid.py spreadsheet.xlsx
```

Output: A new file with the name suffixed by '_with_stats' with the statistics added in new columns

Example:
```
./top_level_stats_by_kthid.py ~/Working/RAE-2020/cst_citations-augmented.xlsx 
```

# preprocess_for_corpus.py
Purpose: reads in a spreaadsheet of DiVA entries and generates and
	 output a file (targets.json) containing JSON with entries containing:
	    PID, Name, Title, Year, DOI, PMID

Input:
```
./preprocess_for_corpus.py spreadsheet.xlsx
```
ExampleL
```
./preprocess_for_corpus.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019.xlsx
```

# find_in_corpus.py

Purpose: using the information from the output of preprocess_for_corpus.py (information extracted from DiVA), find the publications that exist in a particulare shard of the Semantic Scholar (s2)  corpus and outputs a reduced version of the file of information from DiVA.

Input:
```
./find_in_corpus.py targets.json shard_number path_to_distroy_with_corpus
```

The shard number N (is the digits indicating the piece of the corpus) - for the file s2-corpus-186 N is 186
The program outputs the following files:
  matches_corpus_N.json - this contains JSON entries of the form:
                          PID, Name, DOI, PMID, S2_publication_ID, S2_authors
  remaining_targets.json - this contains entries of the same form as the input file (having removed the matched entries)

Example:
```
 ./find_in_corpus.py targets.json  186 /z3/maguire/SemanticScholar/SS_corpus_2020-05-27
```

# Adding_Semantic_Scholar_data_to_KTH_ÅBU.docx
Adding_Semantic_Scholar_data_to_KTH_ÅBU.docx provides information about my experiments regarding S2 information

# get_pid_and_names.py
Purpose: using the information from the output of preprocess_for_corpus.py (information extracted from DiVA), find the publications that exist in a particulare shard of the Semantic Scholar (s2)  corpus and outputs a reduced version of the file of information from DiVA.

Input:
```
./get_pid_and_names.py spreadsheet.csv
```

The program outputs the following files (for the example command shown later):
* kth-exluding-theses-all-level2-2012-2019_pid_name.csv - which contains entries of the for PID and authors:
```
"913155","Olivecrona, Henrik (Karolinska Institutet, Sweden) (Department of Molecular Medicine and Surgery, Section of Orthopaedics and Sport Medicine);Maguire, Gerald Q., Jr. [u1d13i2c] [0000-0002-6066-746X] (KTH [177], Skolan för informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998], Radio Systems Laboratory (RS Lab) [13053]);Noz, Marilyn E. [0000-0002-2442-1622] (New York University,  Department of Radiology) (Nuclear Medicine);Zeleznik, Michael P. [0000-0002-0706-1805] (University of Utah) (School of Computing, College of Engineering);Kesteris, Uldis (Department of Orthopedics, Skåne University Hospital);Weidenhielm, Lars [0000-0002-4280-1178] (Karolinska Institutet at Karolinska University Hospital Solna) (Department of Molecular Medicine and Surgery)"

```

* kth-exluding-theses-all-level2-2012-2019_pid_name.JSON - which contains entires of the form:
```
 {
     "PID": 528381,
     "entry": {
         "Name": "Maguire Jr., Gerald Q.",
         "kthid": "u1d13i2c",
         "orcid": "0000-0002-6066-746X",
         "kth": " (KTH [177], Skolan f\u00f6r informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])"
     }
 }
```
* kth-exluding-theses-all-level2-2012-2019_missing_kthids.csv which contains entries of the form:
```
Name	KTHID	ORCID	PIDs missing KTHIDs for named person
...
Gross, J			[1055431]	 (KTH [177], Skolan för elektro- och systemteknik (EES) [5977])
...
```
* kth-exluding-theses-all-level2-2012-2019_pid_name_aliases.JSON 
```
{
    "kthid": "u1d13i2c",
    "entry": {
        "orcid": "0000-0002-6066-746X",
        "kth": " (KTH [177], Skolan f\u00f6r informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])",
        "aliases": [
            {
                "Name": "Maguire Jr., Gerald Q.",
                "PID": [
                    528381,
                    606323,
                    638177,
                    675824,
                    675849,
...
                    1314634,
                    1367981,
                    1416571
                ]
            },
            {
                "Name": "Maguire, Gerald Q.",
                "PID": [
                    561069
                ]
            },
            {
                "Name": "Maguire Jr., Gerald",
                "PID": [
                    561509
                ]
            },
            {
                "Name": "Maguire, Gerald Q., Jr.",
                "PID": [
                   913155
                ]
            }
        ]
    }
}

```

Example:
```
./get_pid_and_names.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019.csv 
```

## augment_names_from_profile.py

Purpose: using the information from the output of get_pid_and_names.py and augmented with manual lookup of KTHIDs for users then filter to unique entries - then apply this program to add the user's first and last name information using the KTH profile API (note that you need an applicaiton key for this).

Input:
```
./augment_names_from_profile.py input.json output.json 
```

Example:
```
cat kth-exluding-theses-all-level2-2012-2019_pid_name_aliases-manually_corrected.json | jq -c '.' > z1; cat z1| sort | uniq >pubs-2012-2019_pid_name_aliases-manually_corrected.json

./augment_names_from_profile.py pubs-2012-2019_pid_name_aliases-manually_corrected.json pubs-2012-2019_augmented.json
length of input=5114
processing input
*** KTHID: xxxxxxxx missing first and last name in {'username': None}
* alias(es)=['xx, yy]
...
length of output=4841

```

## ./check_augmented_names.py
Purpose: check for missing KTHIDs and add them to an output file.

Input:
```
./check_augmented_names.py kthids.csv augmented_author_data.json
```
The program outputs the following file:
    missing_kthids.json

Example of runinng the program
...
./check_augmented_names.py /z3/maguire/SemanticScholar/KTH_DiVA/z1uniq.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json
...
Note that the z1uniq.csv was computed by finding the [u1xxxxxx] strings in the csv file, saving them as z1.csv and then doing a:
  cat z1.csv | sort | uniq >z1uniq.csv

Output
...
error in line=[u105878]
length of kthids=8796
length of augmented=4984
length of found_kthids=4712
missing id u1q5qlvv in augmented data
...
missing id u1eun6xb in augmented data
KTHIDs in original csv of publications=8796, found in augmented=4712, missing=4091
*** KTHID: u11w5qab missing first and last name in {'username': None}
...

Note that the string [u105878] is too short to be a valid KTHID. There are 8796 in the z1uniq.csv file and 4984 entries in the augmented.json file. The result is that there are 4712 KTHIDs (or something that looks like a KTHID) that does not yet exist in the augmented.-json fule.

The lines "missing id u1xxxxxx in augmented data" mean that this KTHID was not already in the augmented.json file.

KTHIDs, such as "u11w5qab" that are missing user information generally mean that the KTHID string is not valid.

## further_augment_from_CSV_file.py

Purpose: reads in a CSV spreaadsheet of DiVA entries and uses the information to generates update an augmented JSON file

Input:
```
# ./further_augment_from_CSV_file.py xxx.csv xxx.augmented.json [extra_orcid_info.txt]
```

Output: augmented JSON file(s)



Example:
```
./further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json

```
Running a version of the program with the file of ORCID;KTHID values provided by Anders Wändahl of KTHB was done as follows:

```
./further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json /z3/maguire/SemanticScholar/KTH_DiVA/orcid_kth-id_2020-12-04.txt

file_name='/z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv'
augmented_json_file_name='/z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented.json'
orcid_fileName='/z3/maguire/SemanticScholar/KTH_DiVA/orcid_kth-id_2020-12-04.txt'
length of augmented_by_kthid=9467
augmented_by_kthid for u1d13i2c={'kthid': 'u1d13i2c', 'profile': {'firstName': 'Gerald Quentin', 'lastName': 'Maguire Jr'}, 'kth': '(KTH [177], Skolan för informations- och kommunikationsteknik (ICT) [5994], Kommunikationssystem, CoS [5998])', 'orcid': '0000-0002-6066-746X', 'aliases': [{'Name': 'Maguire Jr., Gerald Q.', 'PID': [528381, 606323, 638177, 675824, 675849, 690825, 690828, 706514, 733621, 852295, 854051, 866222, 866274, 948397, 948549, 948742, 1068493, 1087906, 1177431, 1180496, 1184756, 1230455, 1314634, 1367981, 1416571]}, {'Name': 'Maguire, Gerald Q.', 'PID': [561069]}, {'Name': 'Maguire Jr., Gerald', 'PID': [561509]}, {'Name': 'Maguire, Gerald Q., Jr.', 'PID': [913155]}]}
total entries=9467, number_of_entries_with_KTHIDs=8846, number_of_entries_with_KTHID_and_ORCID=3553, number_of_entries_with_fake_KTHIDs=621, number_of_entries_with_fake_KTHIDs_with_ORCID=34
u17jh27g: 0000-0001-5905-8467
 for user=u18xqygi different ORCID=0000-0001-7020-1551 than existing=0000-0002-4830-7832
 for user=u1viadzh different ORCID=0000-0001-9314-545X than existing=0000-0001-9314-545x
 for user=u1b2c0lu different ORCID=0000-0001-9567-155X than existing=0000-0001-9567-155x
 for user=u165ghxx different ORCID=0000-0002-0697-846X than existing=0000-0002-0697-846x
u1337frh: 0000-0002-1409-6352
for id=u1cmhq5l and orcid=0000-0002-3937-9359, found user=⚠⚠277
 for user=u1opd8t3 different ORCID=0000-0002-4477-971X than existing=0000-0002-4477-971x
 for user=u145n239 different ORCID=0000-0002-4501-695X than existing=0000-0002-4501-695x
for id=u1wab1qn and orcid=0000-0002-5050-5176, found user=⚠⚠280
u1qgi0an: 0000-0002-6461-439X
u17dwg3s: 0000-0002-7422-3966
 for user=u1xbdlaj different ORCID=0000-0002-7987-1567 than existing=0000-0003-2432-7617
 for user=u1i928wd different ORCID=0000-0002-8170-379X than existing=0000-0002-8170-379x
u1h4jl4h: 0000-0002-9432-254X
 for user=u1670dm5 different ORCID=0000-0003-1377-565X than existing=0000-0003-1377-565x
 for user=u1hxruli different ORCID=0000-0003-1443-403X than existing=0000-0003-1443-403x
 for user=u167dmzs different ORCID=0000-0003-1654-841X than existing=0000-0003-1654-841x
u1huwj6n: 0000-0003-1693-1320
 for user=u1dypakr different ORCID=0000-0003-3070-794X than existing=0000-0003-3070-794x
already_know_orcid=2911, new_orcid=6, differing_orcids=12,new_users=740
Finished reading extra ORCID info

```
Note that the above run of the program (which purposely returns after processing the extra ORCID information) gave me:
KTHIDs for two users that I did not have:
    for id=u1cmhq5l and orcid=0000-0002-3937-9359, found user=⚠⚠277
    for id=u1wab1qn and orcid=0000-0002-5050-5176, found user=⚠⚠280

2911 already known ORCIDs

740 new users

6 new ORCIDs for authors I already had:

    u17jh27g: 0000-0001-5905-8467
    u1337frh: 0000-0002-1409-6352
    u1qgi0an: 0000-0002-6461-439X
    u17dwg3s: 0000-0002-7422-3966
    u1h4jl4h: 0000-0002-9432-254X
    u1huwj6n: 0000-0003-1693-1320

12 mis-matches versus what I already had:

   for 10 of these the difference is that the DiVA record(s) had a "x" rather than an "X" in the check character:
     for user=u1viadzh different ORCID=0000-0001-9314-545X than existing=0000-0001-9314-545x
     for user=u1b2c0lu different ORCID=0000-0001-9567-155X than existing=0000-0001-9567-155x
     for user=u165ghxx different ORCID=0000-0002-0697-846X than existing=0000-0002-0697-846x
     for user=u1opd8t3 different ORCID=0000-0002-4477-971X than existing=0000-0002-4477-971x
     for user=u145n239 different ORCID=0000-0002-4501-695X than existing=0000-0002-4501-695x
     for user=u1i928wd different ORCID=0000-0002-8170-379X than existing=0000-0002-8170-379x
     for user=u1670dm5 different ORCID=0000-0003-1377-565X than existing=0000-0003-1377-565x
     for user=u1hxruli different ORCID=0000-0003-1443-403X than existing=0000-0003-1443-403x
     for user=u167dmzs different ORCID=0000-0003-1654-841X than existing=0000-0003-1654-841x
     for user=u1dypakr different ORCID=0000-0003-3070-794X than existing=0000-0003-3070-794x

Two users where there is a difference:
    for user=u18xqygi different ORCID=0000-0001-7020-1551 than existing=0000-0002-4830-7832
    for user=u1xbdlaj different ORCID=0000-0002-7987-1567 than existing=0000-0003-2432-7617

For the first of these the user actually has two ORCIDs. Her KTH profile page  https://www.kth.se/profile/olga points to ORCID: https://orcid.org/0000-0001-7020-1551

However, there are many record in DiVA (such as the following that shows another ORCID for this user):

"1307966","Kordas, Olga [u18xqygi] [0000-0002-4830-7832] (KTH [177], Skolan för arkitektur och samhällsbyggnad (ABE) [5850], Hållbar utveckling, miljövetenskap och teknik [13604]) (UrbanT);

Note that https://orcid.org/0000-0002-4830-7832 - seems to be much more complete.

For the second, kTH profile shows:
    user={'defaultLanguage': 'en', 'acceptedTerms': True, 'isAdminHidden': False, 'avatar': {'visibility': 'public'}, '_id': 'u1xbdlaj', 'kthId': 'u1xbdlaj', 'username': 'chrdan', 'homeDirectory': '\\\\ug.kth.se\\dfs\\home\\c\\h\\chrdan', 'title': {'sv': 'FORSKARE', 'en': 'RESEARCHER'}, 'streetAddress': 'OSQUARS BACKE 5', 'emailAddress': 'christina.bodin.danielsson@arch.kth.se', 'telephoneNumber': '087908541', 'isStaff': True, 'isStudent': False, 'firstName': 'Christina', 'lastName': 'Bodin Danielsson', 'city': 'Stockholm', 'postalCode': '10044', 'remark': '', 'lastSynced': '2020-09-10T06:29:20.000Z', 'researcher': {'researchGate': '', 'googleScholarId': '', 'scopusId': '', 'researcherId': '', 'orcid': '0000-0002-7987-1567'}, 'courses': {'visibility': 'public', 'codes': [], 'items': []}, 'worksFor': {'items': [{'key': 'app.katalog3.A.AD', 'path': 'a/ad', 'location': 'OSQUARS BACKE 5, 10044 STOCKHOLM', 'name': 'ARKITEKTURSKOLAN', 'nameEn': 'ARCHITECTURE'}, {'key': 'app.katalog3.A.AD.ADE', 'path': 'a/ad/ade', 'location': 'OSQUARS BACKE 5, 10044 STOCKHOLM', 'name': 'ARKITEKTUR FORSKNING EXTERN', 'nameEn': ''}]},  ...

hence I used this in my entry:
    {"kthid": "u1xbdlaj", "entry": {"orcid": "0000-0003-2432-7617", "kth": "(KTH [177], Skolan för arkitektur och samhällsbyggnad (ABE) [5850], Arkitektur [5851]) (Arc plan)", "aliases": [{"Name": "Bodin Danielsson, Christina", "PID": [704686, 842404, 1055759]}, {"Name": "Danielsson, Christina", "PID": [1359413]}]}, "profile": {"firstName": "Christina", "lastName": "Bodin Danielsson"}}

While https://orcid.org/0000-0002-7987-1567 shows:
    Given Names Deactivated Family Name Deactivated
    ORCID iD
    https://orcid.org/0000-0002-7987-1567

    This account has been deprecated, please see account https://orcid.org/0000-0003-2432-7617 for the latest information

So the one ORCID has been replaced by another and the ORCID I was using was correct.

## yet_further_augment_from_CSV_file.py

Purpose: reads in a CSV spreaadsheet of DiVA entries and uses the information to generate a further updated augmented JSON file

The focus of this program is to add the the aliases the PIDs from the DiVA spreadsheet.

Note that program assumes that all entries in the JSON file have a value for kthid, even if it is fake ID.


Input:
```
# ./yet_further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented_further.JSON
```

Output: augmented JSON file

# S2_yet_further_augment_from_CSV_file.py

Input:
```
./S2_yet_further_augment_from_CSV_file.py xxx.csv xxx.augmented_further.json [shard_number path_to_corpus]
```

Purpose: reads in a CSV spreaadsheet of DiVA entries and uses the information to generate a further updated augmented JSON file
This program assumes that all of the KTH authors have a KTHID in the name_record for the publication, otherwise they are ignored.
(This meands that the CSV file has to be corrected or all of the DiVA records have to be corrected.)

The shard number N (is the digits indicating the piece of the corpus) - for the file s2-corpus-186 N is 186
The focus of this program is to add the the aliases the PIDs from the DiVA spreadsheet.

Note that program assumes that all entries in the JSON file have a value for kthid, even if it is fake ID.

Example:
```
./S2_yet_further_augment_from_CSV_file.py  /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected.csv /z3/maguire/SemanticScholar/KTH_DiVA/pubs-2012-2019_augmented_further.JSON 186 /z3/maguire/SemanticScholar/SS_corpus_2020-05-27
```

## coverage-comparison.py 

Purpose: read a JSON file of publication data (for example, output by S2_yet_further_augment_from_CSV_file.py) and compute som simple coverage statistics.

Input:
```
./coverage-comparison.py xxxx.JSON
```

Example:
```
./coverage-comparison.py /z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected_pubs_S2.JSON
file_name='/z3/maguire/SemanticScholar/KTH_DiVA/kth-exluding-theses-all-level2-2012-2019-corrected_pubs_S2.JSON'
Finished reading publication data
number of documents=41634
total_num_in_ISI=    29316	70.41%
total_num_in_Scopus= 32811	78.81%
total_num_in_S2=     35550	85.39%
num_in_ISI_Scopus_S2=26506	63.66%
num_in_ISI_Scopus=   1164	2.80%
num_in_ISI_S2=       1078	2.59%
num_in_ISI_only=     568	1.36%
num_in_Scopus_S2=    3571	8.58%
num_in_Scopus_only=  1570	3.77%
num_in_S2_only=      4395	10.56%
not_in_any=          2782	6.68%
```
# ./S2_remove_dumplicate_authors.py
Purpose: reads in a JSON of S2 records and write new file after removing duplicate authors

Input: ./S2_remove_dumplicate_authors.py reduced_corpus.JSON
```
# 
```

Output: augmented JSON file(s)
prints out information about duplicate entries in the form:
In 75710ecf5389f5cc68eb5be9e85c0268506f7cb5 duplicate author name=Y  T with same ids={'46761978'}
In 75710ecf5389f5cc68eb5be9e85c0268506f7cb5 duplicate author name=T  Z with different ids existing_ids={'51135908'}, prior_ids={'2000909863'}


Example:
```
./S2_remove_dumplicate_authors.py /z3/maguire/SemanticScholar/KTH_DiVA/reduced_corpus-MA.JSON

./S2_remove_dumplicate_authors.py /z3/maguire/SemanticScholar/KTH_DiVA/reduced_corpus-MA.JSON > logfile-20210121.txt
```

## find_teams_collaborations_etc_in_corpus.py
Purpose: reads in a corpus in JSON format and extract information about possible teams, collaboration, etc.

Input:
```
./find_teams_collaborations_etc_in_corpus.py reduced_corpus.JSON
```

Example:
```
./find_teams_collaborations_etc_in_corpus.py /z3/maguire/SemanticScholar/KTH_DiVA/reduced_corpus-MA_deduplicated_of_authors.JSON
```

Output:
```
entires in reduced corpus=377952
Potential collaborations, teams, etc.
key=A.  Group; ids={'1410912208'}, value=['0d56e76911ddce3092256cf486cdfb6661a86b98']
...
key=the nTOF Collaboration; ids={'103064449'}, value=['7a01c2e8a0bf32ed74b8252f1eb6a4cfb864024d']
key=transatlantic  contributors; ids={'1846466409'}, value=['759679cba92d3a20bb3b6e599b247dae73424e02']
Finished

```

## find_chinese_characters.py
Purpose: reads in an author JSON file and check for CJK characters in the names

Input:
```
./find_chinese_characters.py authors_file.JSON 
```

Example:
```
time ./find_chinese_characters.py /z3/maguire/SemanticScholar/KTH_DiVA/authors-MA-RC.JSON
```

Output:
```
found CJK in {"kthid": "xxx", "profile": {"firstName": "X", "lastName": "Y"}, "aliases": [{"Name": "Y, X.", "PID": [1313937]}, {"Name": "刘", "PID": [xyz]}]}

entires in authors=10172
kthid=xxxx alias={'Name': '刘', 'PID': [xyz]}
...
key=the nTOF Collaboration; ids={'103064449'}, value=['7a01c2e8a0bf32ed74b8252f1eb6a4cfb864024d']
key=transatlantic  contributors; ids={'1846466409'}, value=['759679cba92d3a20bb3b6e599b247dae73424e02']
Finished

```
## ./diva_cora_records.py
Purpose: reads some information from the new DiVA based on Cora 

Input:
```
./diva_cora_records.py
```

Output:
```
r.status_code=200
recordType information for diva-person
{'record': {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                     'rel': 'read',
                                     'requestMethod': 'GET',
                                     'url': 'https://pre.diva-portal.org/rest/record/recordType/diva-person'},
                            'read_incoming_links': {'accept': 'application/vnd.uub.recordList+json',
                                                    'rel': 'read_incoming_links',
                                                    'requestMethod': 'GET',
                                                    'url': 'https://pre.diva-portal.org/rest/record/recordType/diva-person/incomingLinks'}},
            'data': {'children': [{'children': [{'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/validationType/recordType'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'validationType'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'recordType'}],
                                                 'name': 'validationType'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/system/diva'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'system'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'diva'}],
                                                 'name': 'dataDivider'},
                                                {'name': 'id',
                                                 'value': 'diva-person'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/recordType/recordType'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'recordType'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'recordType'}],
                                                 'name': 'type'},
                                                {'children': [{'name': 'linkedRecordType',
                                                               'value': 'user'},
                                                              {'name': 'linkedRecordId',
                                                               'value': '161616'}],
                                                 'name': 'createdBy'},
                                                {'name': 'tsCreated',
                                                 'value': '2024-09-17T10:03:45.276089Z'},
                                                {'children': [{'name': 'tsUpdated',
                                                               'value': '2025-04-17T12:31:45.366104Z'},
                                                              {'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': '161616'}],
                                                               'name': 'updatedBy'}],
                                                 'name': 'updated',
                                                 'repeatId': '0'}],
                                   'name': 'recordInfo'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/metadata/personUpdateGroup'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'metadata'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'personUpdateGroup'}],
                                   'name': 'metadataId'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/presentation/personUpdateOutputPGroup'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'presentation'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'personUpdateOutputPGroup'}],
                                   'name': 'presentationViewId'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/presentation/diva-personMenuPGroup'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'presentation'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'diva-personMenuPGroup'}],
                                   'name': 'menuPresentationViewId'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/presentation/diva-personListPGroup'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'presentation'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'diva-personListPGroup'}],
                                   'name': 'listPresentationViewId'},
                                  {'name': 'userSuppliedId', 'value': 'false'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/text/diva-personText'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'text'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'diva-personText'}],
                                   'name': 'textId'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/text/diva-personDefText'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'text'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'diva-personDefText'}],
                                   'name': 'defTextId'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/search/diva-personSearch'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'search'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'diva-personSearch'}],
                                   'name': 'search'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/presentation/diva-personAutocompletePGroup'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'presentation'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'diva-personAutocompletePGroup'}],
                                   'name': 'autocompletePresentationView'},
                                  {'name': 'groupOfRecordType',
                                   'repeatId': '0',
                                   'value': 'controlledLists'},
                                  {'name': 'public', 'value': 'true'},
                                  {'name': 'storeInArchive', 'value': 'true'},
                                  {'name': 'usePermissionUnit',
                                   'value': 'false'},
                                  {'name': 'useVisibility', 'value': 'false'},
                                  {'name': 'recordTypeCategory',
                                   'repeatId': '2',
                                   'value': 'clientNavigation'}],
                     'name': 'recordType'}}}
'{"name":"textSearch","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"translationSearchTerm","value":"kth"}]}]}]}'| len(search_data_as_string)=149 last char is }
payload={'searchData': '{"name":"textSearch","children":[{"name":"include","children":[{"name":"includePart","children":[{"name":"translationSearchTerm","value":"kth"}]}]}]}'}
r.status_code=401
r.status_code=200
r.text='<?xml version="1.0" encoding="UTF-8"?><dataList><fromNo>0</fromNo><toNo>0</toNo><totalNo>0</totalNo><containDataOfType>diva-person</containDataOfType><data/></dataList>'
accessible_data='<?xml version="1.0" encoding="UTF-8"?><dataList><fromNo>0</fromNo><toNo>0</toNo><totalNo>0</totalNo><containDataOfType>diva-person</containDataOfType><data/></dataList>'
001: pr=''
r.text='{"record":{"data":{"children":[{"children":[{"name":"id","value":"divaPre"},{"children":[{"name":"linkedRecordType","value":"recordType"},{"name":"linkedRecordId","value":"system"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/recordType/system","accept":"application/vnd.uub.record+json"}},"name":"type"},{"children":[{"name":"linkedRecordType","value":"validationType"},{"name":"linkedRecordId","value":"system"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/validationType/system","accept":"application/vnd.uub.record+json"}},"name":"validationType"},{"children":[{"name":"linkedRecordType","value":"system"},{"name":"linkedRecordId","value":"divaPre"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/system/divaPre","accept":"application/vnd.uub.record+json"}},"name":"dataDivider"},{"repeatId":"0","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"161616"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2024-04-22T12:18:16.037653Z"}],"name":"updated"},{"repeatId":"1","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"161616"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2024-04-22T12:20:42.663339Z"}],"name":"updated"},{"repeatId":"2","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"161616"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2024-04-25T07:28:24.711029Z"}],"name":"updated"},{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"161616"}],"name":"createdBy"},{"name":"tsCreated","value":"2024-04-22T12:18:16.037653Z"}],"name":"recordInfo"},{"name":"systemName","value":"DiVAPreSystem"},{"children":[{"name":"linkedRecordType","value":"text"},{"name":"linkedRecordId","value":"divaPreText"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/text/divaPreText","accept":"application/vnd.uub.record+json"}},"name":"textId"},{"children":[{"name":"linkedRecordType","value":"text"},{"name":"linkedRecordId","value":"divaPreDefText"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/text/divaPreDefText","accept":"application/vnd.uub.record+json"}},"name":"defTextId"}],"name":"system"},"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/system/divaPre","accept":"application/vnd.uub.record+json"},"read_incoming_links":{"requestMethod":"GET","rel":"read_incoming_links","url":"https://pre.diva-portal.org/rest/record/system/divaPre/incomingLinks","accept":"application/vnd.uub.recordList+json"}}}}'
record_type='system' id='divaPre': rr={'record': {'data': {'children': [{'children': [{'name': 'id', 'value': 'divaPre'}, {'children': [{'name': 'linkedRecordType', 'value': 'recordType'}, {'name': 'linkedRecordId', 'value': 'system'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/recordType/system', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'type'}, {'children': [{'name': 'linkedRecordType', 'value': 'validationType'}, {'name': 'linkedRecordId', 'value': 'system'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/validationType/system', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'validationType'}, {'children': [{'name': 'linkedRecordType', 'value': 'system'}, {'name': 'linkedRecordId', 'value': 'divaPre'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/system/divaPre', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'dataDivider'}, {'repeatId': '0', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '161616'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-04-22T12:18:16.037653Z'}], 'name': 'updated'}, {'repeatId': '1', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '161616'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-04-22T12:20:42.663339Z'}], 'name': 'updated'}, {'repeatId': '2', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '161616'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-04-25T07:28:24.711029Z'}], 'name': 'updated'}, {'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '161616'}], 'name': 'createdBy'}, {'name': 'tsCreated', 'value': '2024-04-22T12:18:16.037653Z'}], 'name': 'recordInfo'}, {'name': 'systemName', 'value': 'DiVAPreSystem'}, {'children': [{'name': 'linkedRecordType', 'value': 'text'}, {'name': 'linkedRecordId', 'value': 'divaPreText'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/text/divaPreText', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'textId'}, {'children': [{'name': 'linkedRecordType', 'value': 'text'}, {'name': 'linkedRecordId', 'value': 'divaPreDefText'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/text/divaPreDefText', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'defTextId'}], 'name': 'system'}, 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/system/divaPre', 'accept': 'application/vnd.uub.record+json'}, 'read_incoming_links': {'requestMethod': 'GET', 'rel': 'read_incoming_links', 'url': 'https://pre.diva-portal.org/rest/record/system/divaPre/incomingLinks', 'accept': 'application/vnd.uub.recordList+json'}}}}
{'record': {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                     'rel': 'read',
                                     'requestMethod': 'GET',
                                     'url': 'https://pre.diva-portal.org/rest/record/system/divaPre'},
                            'read_incoming_links': {'accept': 'application/vnd.uub.recordList+json',
                                                    'rel': 'read_incoming_links',
                                                    'requestMethod': 'GET',
                                                    'url': 'https://pre.diva-portal.org/rest/record/system/divaPre/incomingLinks'}},
            'data': {'children': [{'children': [{'name': 'id',
                                                 'value': 'divaPre'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/recordType/system'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'recordType'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'system'}],
                                                 'name': 'type'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/validationType/system'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'validationType'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'system'}],
                                                 'name': 'validationType'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/system/divaPre'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'system'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'divaPre'}],
                                                 'name': 'dataDivider'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': '161616'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2024-04-22T12:18:16.037653Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '0'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': '161616'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2024-04-22T12:20:42.663339Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '1'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': '161616'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2024-04-25T07:28:24.711029Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '2'},
                                                {'children': [{'name': 'linkedRecordType',
                                                               'value': 'user'},
                                                              {'name': 'linkedRecordId',
                                                               'value': '161616'}],
                                                 'name': 'createdBy'},
                                                {'name': 'tsCreated',
                                                 'value': '2024-04-22T12:18:16.037653Z'}],
                                   'name': 'recordInfo'},
                                  {'name': 'systemName',
                                   'value': 'DiVAPreSystem'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/text/divaPreText'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'text'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'divaPreText'}],
                                   'name': 'textId'},
                                  {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                            'rel': 'read',
                                                            'requestMethod': 'GET',
                                                            'url': 'https://pre.diva-portal.org/rest/record/text/divaPreDefText'}},
                                   'children': [{'name': 'linkedRecordType',
                                                 'value': 'text'},
                                                {'name': 'linkedRecordId',
                                                 'value': 'divaPreDefText'}],
                                   'name': 'defTextId'}],
                     'name': 'system'}}}
r.text='{"record":{"data":{"children":[{"children":[{"name":"id","value":"kthTestDiVAwr"},{"children":[{"name":"linkedRecordType","value":"recordType"},{"name":"linkedRecordId","value":"login"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/recordType/login","accept":"application/vnd.uub.record+json"}},"name":"type"},{"children":[{"name":"linkedRecordType","value":"validationType"},{"name":"linkedRecordId","value":"loginWebRedirect"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/validationType/loginWebRedirect","accept":"application/vnd.uub.record+json"}},"name":"validationType"},{"children":[{"name":"linkedRecordType","value":"system"},{"name":"linkedRecordId","value":"divaPre"}],"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/system/divaPre","accept":"application/vnd.uub.record+json"}},"name":"dataDivider"},{"repeatId":"0","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"coraUser:4412982402853626"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2020-10-16T10:47:55.864547Z"}],"name":"updated"},{"repeatId":"1","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"coraUser:4412982402853626"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2020-10-16T10:51:16.374927Z"}],"name":"updated"},{"repeatId":"2","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"coraUser:490742519075086"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2021-03-04T10:07:20.960605Z"}],"name":"updated"},{"repeatId":"3","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"coraUser:490742519075086"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2023-03-03T13:24:51.152890Z"}],"name":"updated"},{"repeatId":"4","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"161616"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2024-04-22T13:06:12.198769Z"}],"name":"updated"},{"repeatId":"5","children":[{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"141414"}],"name":"updatedBy"},{"name":"tsUpdated","value":"2024-05-21T07:06:31.098947Z"}],"name":"updated"},{"children":[{"name":"linkedRecordType","value":"user"},{"name":"linkedRecordId","value":"coraUser:4412982402853626"}],"name":"createdBy"},{"name":"tsCreated","value":"2020-10-16T10:47:55.864547Z"}],"name":"recordInfo"},{"name":"loginName","value":"DiVA Test KTH"},{"name":"url","value":"https://pre.diva-portal.org/Shibboleth.sso/Login/kth?target=https://pre.diva-portal.org/idplogin/login"}],"name":"login","attributes":{"type":"webRedirect"}},"actionLinks":{"read":{"requestMethod":"GET","rel":"read","url":"https://pre.diva-portal.org/rest/record/login/kthTestDiVAwr","accept":"application/vnd.uub.record+json"},"read_incoming_links":{"requestMethod":"GET","rel":"read_incoming_links","url":"https://pre.diva-portal.org/rest/record/login/kthTestDiVAwr/incomingLinks","accept":"application/vnd.uub.recordList+json"}}}}'
record_type='login' id='kthTestDiVAwr': rr={'record': {'data': {'children': [{'children': [{'name': 'id', 'value': 'kthTestDiVAwr'}, {'children': [{'name': 'linkedRecordType', 'value': 'recordType'}, {'name': 'linkedRecordId', 'value': 'login'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/recordType/login', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'type'}, {'children': [{'name': 'linkedRecordType', 'value': 'validationType'}, {'name': 'linkedRecordId', 'value': 'loginWebRedirect'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/validationType/loginWebRedirect', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'validationType'}, {'children': [{'name': 'linkedRecordType', 'value': 'system'}, {'name': 'linkedRecordId', 'value': 'divaPre'}], 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/system/divaPre', 'accept': 'application/vnd.uub.record+json'}}, 'name': 'dataDivider'}, {'repeatId': '0', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:4412982402853626'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2020-10-16T10:47:55.864547Z'}], 'name': 'updated'}, {'repeatId': '1', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:4412982402853626'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2020-10-16T10:51:16.374927Z'}], 'name': 'updated'}, {'repeatId': '2', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:490742519075086'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2021-03-04T10:07:20.960605Z'}], 'name': 'updated'}, {'repeatId': '3', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:490742519075086'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2023-03-03T13:24:51.152890Z'}], 'name': 'updated'}, {'repeatId': '4', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '161616'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-04-22T13:06:12.198769Z'}], 'name': 'updated'}, {'repeatId': '5', 'children': [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '141414'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-05-21T07:06:31.098947Z'}], 'name': 'updated'}, {'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:4412982402853626'}], 'name': 'createdBy'}, {'name': 'tsCreated', 'value': '2020-10-16T10:47:55.864547Z'}], 'name': 'recordInfo'}, {'name': 'loginName', 'value': 'DiVA Test KTH'}, {'name': 'url', 'value': 'https://pre.diva-portal.org/Shibboleth.sso/Login/kth?target=https://pre.diva-portal.org/idplogin/login'}], 'name': 'login', 'attributes': {'type': 'webRedirect'}}, 'actionLinks': {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/login/kthTestDiVAwr', 'accept': 'application/vnd.uub.record+json'}, 'read_incoming_links': {'requestMethod': 'GET', 'rel': 'read_incoming_links', 'url': 'https://pre.diva-portal.org/rest/record/login/kthTestDiVAwr/incomingLinks', 'accept': 'application/vnd.uub.recordList+json'}}}}
{'record': {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                     'rel': 'read',
                                     'requestMethod': 'GET',
                                     'url': 'https://pre.diva-portal.org/rest/record/login/kthTestDiVAwr'},
                            'read_incoming_links': {'accept': 'application/vnd.uub.recordList+json',
                                                    'rel': 'read_incoming_links',
                                                    'requestMethod': 'GET',
                                                    'url': 'https://pre.diva-portal.org/rest/record/login/kthTestDiVAwr/incomingLinks'}},
            'data': {'attributes': {'type': 'webRedirect'},
                     'children': [{'children': [{'name': 'id',
                                                 'value': 'kthTestDiVAwr'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/recordType/login'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'recordType'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'login'}],
                                                 'name': 'type'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/validationType/loginWebRedirect'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'validationType'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'loginWebRedirect'}],
                                                 'name': 'validationType'},
                                                {'actionLinks': {'read': {'accept': 'application/vnd.uub.record+json',
                                                                          'rel': 'read',
                                                                          'requestMethod': 'GET',
                                                                          'url': 'https://pre.diva-portal.org/rest/record/system/divaPre'}},
                                                 'children': [{'name': 'linkedRecordType',
                                                               'value': 'system'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'divaPre'}],
                                                 'name': 'dataDivider'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': 'coraUser:4412982402853626'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2020-10-16T10:47:55.864547Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '0'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': 'coraUser:4412982402853626'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2020-10-16T10:51:16.374927Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '1'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': 'coraUser:490742519075086'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2021-03-04T10:07:20.960605Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '2'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': 'coraUser:490742519075086'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2023-03-03T13:24:51.152890Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '3'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': '161616'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2024-04-22T13:06:12.198769Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '4'},
                                                {'children': [{'children': [{'name': 'linkedRecordType',
                                                                             'value': 'user'},
                                                                            {'name': 'linkedRecordId',
                                                                             'value': '141414'}],
                                                               'name': 'updatedBy'},
                                                              {'name': 'tsUpdated',
                                                               'value': '2024-05-21T07:06:31.098947Z'}],
                                                 'name': 'updated',
                                                 'repeatId': '5'},
                                                {'children': [{'name': 'linkedRecordType',
                                                               'value': 'user'},
                                                              {'name': 'linkedRecordId',
                                                               'value': 'coraUser:4412982402853626'}],
                                                 'name': 'createdBy'},
                                                {'name': 'tsCreated',
                                                 'value': '2020-10-16T10:47:55.864547Z'}],
                                   'name': 'recordInfo'},
                                  {'name': 'loginName',
                                   'value': 'DiVA Test KTH'},
                                  {'name': 'url',
                                   'value': 'https://pre.diva-portal.org/Shibboleth.sso/Login/kth?target=https://pre.diva-portal.org/idplogin/login'}],
                     'name': 'login'}}}
type of login is webRedirect
id=kthTestDiVAwr
type children: [{'name': 'linkedRecordType', 'value': 'recordType'}, {'name': 'linkedRecordId', 'value': 'login'}] actionlinks: {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/recordType/login', 'accept': 'application/vnd.uub.record+json'}}
validationType children: [{'name': 'linkedRecordType', 'value': 'validationType'}, {'name': 'linkedRecordId', 'value': 'loginWebRedirect'}] actionlinks: {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/validationType/loginWebRedirect', 'accept': 'application/vnd.uub.record+json'}}
dataDivider children: [{'name': 'linkedRecordType', 'value': 'system'}, {'name': 'linkedRecordId', 'value': 'divaPre'}] actionlinks: {'read': {'requestMethod': 'GET', 'rel': 'read', 'url': 'https://pre.diva-portal.org/rest/record/system/divaPre', 'accept': 'application/vnd.uub.record+json'}}
updated children: [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:4412982402853626'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2020-10-16T10:47:55.864547Z'}] actionlinks: None
updated children: [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:4412982402853626'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2020-10-16T10:51:16.374927Z'}] actionlinks: None
updated children: [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:490742519075086'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2021-03-04T10:07:20.960605Z'}] actionlinks: None
updated children: [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': 'coraUser:490742519075086'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2023-03-03T13:24:51.152890Z'}] actionlinks: None
updated children: [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '161616'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-04-22T13:06:12.198769Z'}] actionlinks: None
updated children: [{'children': [{'name': 'linkedRecordType', 'value': 'user'}, {'name': 'linkedRecordId', 'value': '141414'}], 'name': 'updatedBy'}, {'name': 'tsUpdated', 'value': '2024-05-21T07:06:31.098947Z'}] actionlinks: None
createdBy linkedRecordType -- user
createdBy linkedRecordId -- coraUser:4412982402853626
ccc name tsCreated 2020-10-16T10:47:55.864547Z
loginName is 'DiVA Test KTH'
url is https://pre.diva-portal.org/Shibboleth.sso/Login/kth?target=https://pre.diva-portal.org/idplogin/login
rr=''
161616 user information
{}
131313 user information
{}
user:15433802151162560 user information
{}
guest user information
{}
['Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/recordType/diva-person HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.record+json\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.record+json\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 200 OK\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'application/vnd.uub.record+json'),
 ('header:', 'Content-Length:', '4770'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '88769877'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Accept-Ranges:', 'bytes'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/recordType/diva-person '
 'HTTP/1.1" 200 4770',
 'Encoding detection: ascii is most likely the one.',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET "
  '/rest/record/searchResult/publicTextSearch?searchData=%7B%22name%22%3A%22textSearch%22%2C%22children%22%3A%5B%7B%22name%22%3A%22include%22%2C%22children%22%3A%5B%7B%22name%22%3A%22includePart%22%2C%22children%22%3A%5B%7B%22name%22%3A%22translationSearchTerm%22%2C%22value%22%3A%22kth%22%7D%5D%7D%5D%7D%5D%7D '
  'HTTP/1.1\\r\\nHost: pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.recordList+json\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.recordList+json\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 401 Unauthorized\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/html;charset=utf-8'),
 ('header:', 'Content-Language:', 'en'),
 ('header:', 'Content-Length:', '720'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '82614534'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET '
 '/rest/record/searchResult/publicTextSearch?searchData=%7B%22name%22%3A%22textSearch%22%2C%22children%22%3A%5B%7B%22name%22%3A%22include%22%2C%22children%22%3A%5B%7B%22name%22%3A%22includePart%22%2C%22children%22%3A%5B%7B%22name%22%3A%22translationSearchTerm%22%2C%22value%22%3A%22kth%22%7D%5D%7D%5D%7D%5D%7D '
 'HTTP/1.1" 401 720',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/diva-person/ HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.recordList+xml\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.recordList+xml\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 200 OK\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'application/vnd.uub.recordList+xml'),
 ('header:', 'Content-Length:', '168'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '88769880'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Accept-Ranges:', 'bytes'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/diva-person/ HTTP/1.1" 200 '
 '168',
 'Encoding detection: utf_8 is most likely the one.',
 'Encoding detection: utf_8 is most likely the one.',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/diva-person/001 HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.recordList+xml\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.recordList+xml\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 406 Not Acceptable\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/html;charset=utf-8'),
 ('header:', 'Content-Language:', 'en'),
 ('header:', 'Content-Length:', '846'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '82614537'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/diva-person/001 HTTP/1.1" '
 '406 846',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/system/divaPre HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.record+json\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.recordList+xml\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 200 OK\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'application/vnd.uub.record+json'),
 ('header:', 'Content-Length:', '2862'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '88769883'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Accept-Ranges:', 'bytes'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/system/divaPre HTTP/1.1" '
 '200 2862',
 'Encoding detection: ascii is most likely the one.',
 'Encoding detection: ascii is most likely the one.',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/login/kthTestDiVAwr HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.record+json\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.recordList+xml\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 200 OK\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'application/vnd.uub.record+json'),
 ('header:', 'Content-Length:', '3240'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '82614540'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Accept-Ranges:', 'bytes'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/login/kthTestDiVAwr '
 'HTTP/1.1" 200 3240',
 'Encoding detection: ascii is most likely the one.',
 'Encoding detection: ascii is most likely the one.',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/diva-organisation/177 HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\naccept-encoding: gzip, deflate, br, '
  'zstd\\r\\nAccept: application/vnd.uub.record+json\\r\\nConnection: '
  'keep-alive\\r\\nContent-Type: '
  'application/vnd.uub.recordList+xml\\r\\naccept-language: '
  "en-US,en;q=0.9\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 404 Not Found\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/plain;charset=utf-8'),
 ('header:', 'Content-Length:', '126'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '88769886'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/diva-organisation/177 '
 'HTTP/1.1" 404 126',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/user/161616 HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\nAccept-Encoding: gzip, deflate\\r\\nAccept: '
  'application/vnd.uub.record+json\\r\\nConnection: '
  "keep-alive\\r\\nContent-Type: application/vnd.uub.record+json\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 401 Unauthorized\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/html;charset=utf-8'),
 ('header:', 'Content-Language:', 'en'),
 ('header:', 'Content-Length:', '720'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '82614543'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/user/161616 HTTP/1.1" 401 '
 '720',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/user/131313 HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\nAccept-Encoding: gzip, deflate\\r\\nAccept: '
  'application/vnd.uub.record+json\\r\\nConnection: '
  "keep-alive\\r\\nContent-Type: application/vnd.uub.record+json\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 401 Unauthorized\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:09 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/html;charset=utf-8'),
 ('header:', 'Content-Language:', 'en'),
 ('header:', 'Content-Length:', '720'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '88769889'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/user/131313 HTTP/1.1" 401 '
 '720',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/user/user:15433802151162560 HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\nAccept-Encoding: gzip, deflate\\r\\nAccept: '
  'application/vnd.uub.record+json\\r\\nConnection: '
  "keep-alive\\r\\nContent-Type: application/vnd.uub.record+json\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 401 Unauthorized\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:10 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/html;charset=utf-8'),
 ('header:', 'Content-Language:', 'en'),
 ('header:', 'Content-Length:', '720'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '82614546'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET '
 '/rest/record/user/user:15433802151162560 HTTP/1.1" 401 720',
 'Starting new HTTPS connection (1): pre.diva-portal.org:443',
 ('send:',
  "b'GET /rest/record/user/guest HTTP/1.1\\r\\nHost: "
  'pre.diva-portal.org\\r\\nUser-Agent: '
  'python-requests/2.31.0\\r\\nAccept-Encoding: gzip, deflate\\r\\nAccept: '
  'application/vnd.uub.record+json\\r\\nConnection: '
  "keep-alive\\r\\nContent-Type: application/vnd.uub.record+json\\r\\n\\r\\n'"),
 ('reply:', "'HTTP/1.1 401 Unauthorized\\r\\n'"),
 ('header:', 'Date:', 'Wed, 07 May 2025 05:08:10 GMT'),
 ('header:', 'Server:', 'Apache/2.4.63 (Unix) mod_qos/11.63'),
 ('header:', 'Content-Type:', 'text/html;charset=utf-8'),
 ('header:', 'Content-Language:', 'en'),
 ('header:', 'Content-Length:', '720'),
 ('header:', 'Strict-Transport-Security:', 'max-age=31536000'),
 ('header:', 'X-Varnish:', '88769892'),
 ('header:', 'Age:', '0'),
 ('header:', 'Via:', '1.1 varnish (Varnish/7.1)'),
 ('header:', 'Connection:', 'keep-alive'),
 'https://pre.diva-portal.org:443 "GET /rest/record/user/guest HTTP/1.1" 401 '
 '720']
```
