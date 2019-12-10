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

Purpose: reads in xlsx file and processes each publication, then outputs a dictionary with some statistical data about the use languages for each type of document

Input:
```
./pub_language.py xxxx.xlsx
```

Output: outputs a spreadhseet (in the above case the file will be called "all_student_theses_kth.augmented.xlsx") augmented with the information that has been added and outputs text that was computed

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




