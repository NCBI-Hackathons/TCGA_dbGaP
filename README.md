#TCGA_dbGaP

The repository contains scripts to automatically fetch related dbGaP studies and subsequently the specific sequence files for given TCGA data.

To use download the entire contents of the "bin" folder.

The description for the required scripts is provided below

##Platform requirements:
Python 2.7 -> For installing and configuring python refer to https://www.python.org/download/releases/2.7/

SRA Toolkit -> For details follow the instructions at https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=toolkit_doc&f=std

##Required python packages
###To install a package type pip install <package_name> at the commond line
<url>https://packaging.python.org/installing/</url>
* requests
* pandas

##Program descriptions

###"fetch_dbGaP_with_TCGA.py"
INPUT:

This function will take an input of TCGA project ID, file ID, or case ID.

Additionally the input can also be a TCGA disease type or experiment stategy.

Allowable arguments are:

    '-i', '--idSearch', type=str, default=None, help=' project/case/file id'
    '-r', '--returnType', type=str, default='case', help='View TCGA results by project/file/case'
    '-s', '--searchType', required = True, type=str, default='case', help='Search type for search by id project/file/case'
    '-d', '--disease', type=str, default=None, help='disease param'
    '-n', '--studyType', type=str, default=None, help='study type param wgs/wxs/rnaseq/etc'
    '-l', '--stringencyLevel', type=str, default="high", help='stringency level of dbGaP term match'

OUTPUT:

The output is two .csv files, one containing the ids, urls, and other TCGA information. The other contains dbGAP accession numbers, associated url, and other study information for related studies.
The default name of the TCGA file is "tcga_output.csv" and dbGaP file is "dbGAP_output.csv"

###"fetch_SRRs.py"
INPUT:

Allowable arguments are:

    '-f', '--file', type=str, default=None, help=' <path to file containing dbGap Ids>'
    '-id', '--dbGapIds', type=str, default=None, help='<comma separated list of phs'>'

The file input can directly be the output file "dbGAP_output.csv" from "fetch_dbGaP_with_TCGA.py"

OUTPUT:

List of SRRs found for the entered dbGaP study (accession) numbers

###"sra_query_tool.sh"
INPUT:

File containing list of SRRs.  Default input file name and path is ./SRRlist.txt

Takes the region of interest as argument

OUTPUT:

SAM files containing 

USE EXAMPLE:



