# DiVA-tools
A set of tools for working with DiVA (specifically the KTH Publication
Database instance of DiVA ![DiVA web logo](DiVA-star_green-web.jpg)).

DiVA contains publications produced by the researchers and students and is
used by quite a number of universities, university colleges, and research
institutes. The search interface for KTH's DiVA portal is
[http://kth.diva-portal.org](http://kth.diva-portal.org). Via this web
interface it is also possible to create feeds in a variety of formats.

An interface to more DiVA functionality can be found at [https://kth.diva-portal.org/dream/info.jsf](https://kth.diva-portal.org/dream/info.jsf).

DiVA can import and export references in a number of formats, one of these is The Library of Congress's [Metadata Object Description Schema (MODS) XML format](http://www.loc.gov/standards/mods/).

You can find the description of DiVA's MODS format at [
https://wiki.epc.ub.uu.se/display/divainfo/Formatspecifikation+och+systembeskrivning](https://wiki.epc.ub.uu.se/display/divainfo/Formatspecifikation+och+systembeskrivning)

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
