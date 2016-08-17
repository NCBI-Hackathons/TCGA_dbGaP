TCGA --> dbGAP pipeline

##Platform requriements:
Python 2.7 # For installing and configuring python refer to https://www.python.org/download/releases/2.7/
SRA Toolkit # For details check https://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?view=toolkit_doc&f=std

##Required python packages
# To install a package type pip install <package_name> at the commond line
# https://packaging.python.org/installing/
1> requests
2> pandas

##Program descriptions

"tcga_fetch_metadata.py"
INPUT:
This function will take an input of TCGA project ID, file ID, case ID.
Additionally the input can also be a TCGA disease type or experiment stategy.
Allowable arguments are:
    '-i', '--idSearch', type=str, default=None, help=' project/case/file id'
    '-s', '--searchType', required = True, type=str, default='case', help='View results by project/file/case'
    '-d', '--disease', type=str, default=None, help='disease param'
    '-n', '--studyType', type=str, default=None, help='study type param wgs/wxs/rnaseq/etc'
    '-l', '--stringencyLevel', type=str, default="high", help='stringency level of dbGaP term match'

OUTPUT:
The output is a csv file containing dbGAP accession numbers and associated url for related studies.
The default name of the file "OUTPUT.csv"

"fetch_SRRs.py"
INPUT:
Allowable arguments are:
    '-f', '--file', type=str, default=None, help=' <path to file containing dbGap Ids>'
    '-id', '--dbGapIds', type=str, default=None, help='<comma separated list of phs'>'
The file input can be the output from "query_tcga"
OUTPUT:
List of SRRs found for the entered phs'

"sra_query_tool.sh"
INPUT:
File containing list of SRRs
OUTPUT:
SAM files