#!/usr/bin/env python
import argparse, sys, re, time, json
import requests

from argparse import RawTextHelpFormatter
from tcga_to_dbGaB_mapping_dictionary import Mapping

__author__ = " Abhijit Badve and Jessica Kurata"
__version__ = "Revision: 0.0.3 "
__date__ = "Date: 2016-09-07"

# --------------------------------------
# define functions
def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\
 TCGA DBGAP METADATA HARMONIZATION\n\
 author: " + __author__ + "\n\
 version: " + __version__ + "\n\
 description: Search tcga by project/study/file/samples/customSearch")
    subparsers = parser.add_subparsers(help="use commands 'id' or 'term' to query by GDC id or by disease/experimental strategy")

    parser_id = subparsers.add_parser("id", help="query using GDC project, case or file  id")
    parser_id.add_argument('-i', '--idSearch', required=True, type=str, default=None, help=' project/case/file id')
    parser_id.add_argument('-s', '--searchType',required=True, type=str, choices=["project", "case", "file"], help="type of id used")
    parser_id.add_argument('-l', '--stringencyLevel', type=str, default='high', choices=['high', 'medium', 'low'],
                           help='level of stringency to use when mapping between GDC and dbGaP terms')
    
    parser_term = subparsers.add_parser("term", help="query using disease(s) and/or study type(s)")
    parser_term.add_argument('-r', '--returnType', type=str, default='case', help='View TCGA results by project/file/case')
    parser_term.add_argument('-d', '--disease', type=str, default=None, help='disease param')
    parser_term.add_argument('-n', '--studyType', type=str, default=None, help='study type param wgs/wxs/rnaseq/etc')
    parser_term.add_argument('-l', '--stringencyLevel', type=str, default='high', choices=['high', 'medium', 'low'],
                           help='level of stringency to use when mapping between GDC and dbGaP terms')
    # parse the arguments
    args = parser.parse_args()
    # if no input,exit
    if len(sys.argv) <= 1:        
        parser.print_help()
        sys.exit(1)
    # send back the user input
    return args
# --------------------------------------
    
def check_tcga():
    """
        Checks the status of TCGA to ensure it is up
    """
    status_endpt = 'https://gdc-api.nci.nih.gov/status'
    response = requests.get(status_endpt)
    response = response.json()
    status = response[u"status"]
    if status == u"OK":
        return True
    else:
        return False

def query_by_id(submittedID, searchType):
    """
        Queries the TCGA API by project name, file ID or case ID
        Returns the json response (needs to include disease and 
    """
    # Fields to return based on return type
    returnDict = {"project":"disease_type,project_id,released,state,primary_site,dbgap_accession_number,summary.experimental_strategies.experimental_strategy,summary.data_categories.data_category",
                  "file":"file_id,experimental_strategy,data_type,cases.summary.data_categories.data_category,cases.project.dbgap_accession_number,cases.project.disease_type,cases.project.released,cases.project.state,cases.project.primary_site,cases.project.project_id,cases.project.name,cases.case_id",
                  "case": "project.dbgap_accession_number,project.disease_type,project.released,project.state,project.primary_site,project.project_id,project.name,case_id,sample_ids,files.experimental_strategy"}
    contentList ={"op":"=",
                  "content":{
                      "field": searchType+"_id",
                      "value":[submittedID]
                      }
                  }
    params = {'filters': json.dumps(contentList),'fields': returnDict[searchType]}
    url = "https://gdc-api.nci.nih.gov/"+searchType+"s"
    responseRAW = requests.get(url, params=params)
    response = responseRAW.json()
    return response

def query_by_filter(searchDict, returnType):
    """
        Queries the TCGA API by disease or study type(s)
    """

    # Field to search based on search type and return type 
    fieldsDict = {"disease": {"project":"disease_type", "file":"cases.project.disease_type", "case": "project.disease_type"},
                  "studyType": {"project":"summary.experimental_strategies.experimental_strategy", "file":"experimental_strategy", "case":"files.experimental_strategy"}}
    # Fields to return based on return type
    returnDict = {"project":"disease_type,project_id,released,state,primary_site,dbgap_accession_number,summary.experimental_strategies.experimental_strategy,summary.data_categories.data_category",
                  "file":"file_id,experimental_strategy,data_type,cases.summary.data_categories.data_category,cases.project.dbgap_accession_number,cases.project.disease_type,cases.project.released,cases.project.state,cases.project.primary_site,cases.project.project_id,cases.project.name,cases.case_id",
                  "case": "project.dbgap_accession_number,project.disease_type,project.released,project.state,project.primary_site,project.project_id,project.name,case_id,sample_ids,files.experimental_strategy"}

    if returnType not in ["project", "file", "case"]:
        return "Please enter a valid return type: project, file or case"

    if searchDict["disease"] != []:
        # Finds the field based on the return type asked for
        field = fieldsDict["disease"][returnType]
        diseaseListing = { "op":"in",
                "content": {
                "field": field,
                "value": searchDict["disease"]
                }}
        contentList = diseaseListing
    if searchDict["studyType"] != []:
        # Finds the field to search by based on the return type asked for
        field = fieldsDict["studyType"][returnType]
        studyListing = { "op":"in",
                "content": {
                "field": field,
                "value": searchDict["studyType"]
                }}
        contentList = studyListing

    # if both are being searched
    try:
        contentList = {"op": "and",
                       "content": [diseaseListing] + [studyListing]}
    except UnboundLocalError:
        pass

    params = {'filters': json.dumps(contentList),'fields': returnDict[returnType]}
    url = "https://gdc-api.nci.nih.gov/"+returnType+"s"
    responseRAW = requests.get(url, params=params)
    response = responseRAW.json()
    return response

def project(jsonObj):
    projectDict = {"project_id":jsonObj['project_id'], "released": jsonObj['released'],
                   "state":jsonObj['state'], "primary_site":jsonObj['primary_site'],
                   "dbgap":jsonObj['dbgap_accession_number'], "disease_type":jsonObj['disease_type']}
    try:
        summary = jsonObj['summary']
        projectDict["strategies_list"] = list(set([exp['experimental_strategy'] for exp in summary['experimental_strategies']]))
        projectDict["data_category"] = [cat['data_category'] for cat in summary['data_categories']]
    except KeyError:
        pass
    return projectDict

def tcgaFile(jsonObj):
    fileDict = {"data_type":jsonObj["data_type"], "strategies_list":[jsonObj["experimental_strategy"]], "file_id":jsonObj["file_id"]}

    caseDict = case(jsonObj["cases"][0], nested=True)
    fileDict.update(caseDict) # Joins the case and project level information with the file level information

    return fileDict
    
def case(jsonObj, nested=False):
    caseDict = {"case_id":jsonObj['case_id']}
    if not nested:
        caseDict["strategies_list"] = list(set([exp['experimental_strategy'] for exp in jsonObj['files']])) # Creates a list of unique experimental strategies

    projDict = project(jsonObj['project']) 

    caseDict.update(projDict) # Joins the project level information with the case level information

    return caseDict

def query_dbGaP(stringency, diseases=[], studyTypes=[], terms={}):
    """
        Queries dbGaP using Eutils API
        Input:
            stringency: the stringency of the matching between TCGA and dbGaP (high, medium, low)
            diseases: a list of TCGA disease
            studyType: a list of TCGA study types (experimental strategies)
            terms: dictionary of other terms to search by
        Output:
            returns xml response
    """
    # Create a mapping object from tcga_to_dbGaB_mapping.py
    mapObj = Mapping()
    diseaseDict, studyDict = mapObj.main(stringency)
    strTerms = ""
    
    if diseases != []:
        dbGaPTerms = []
        dbTerms = []
        for dis in diseases:
            dbGaPTerms += diseaseDict[dis.lower()]
        for term in dbGaPTerms:
            term = term.replace(" ","+")
            dbTerms += [term]
        diseaseTerms = "%22"+"%22[Disease]+OR+%22".join(dbTerms)+"%22[Disease]"
        strTerms += diseaseTerms

    if studyTypes != []:
        dbGaPTypes = []
        dbTypes = []
        for study in studyTypes:
            dbGaPTypes += studyDict[study]
        for types in dbGaPTypes:
            term = term.replace(" ","+")
            dbTypes += [types]
        studyTerms = "%22"+"%22[Molecular+Data+Type]+OR+%22".join(dbTypes)+"%22[Molecular+Data+Type]"
        if strTerms == "":
            strTerms = studyTerms
        else:
            strTerms = "("+strTerms+")+AND+("+studyTerms+")"

    response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gap&term=' + strTerms)
    resultCount = re.search("<eSearchResult><Count>([0-9]+)</Count>", response.content)
    count = int(resultCount.group(1))
    if count < 100000:
        print str(count)+" matches found in dbGaP for the terms "+strTerms
        response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gap&retmax='+str(count)+'&term=' + strTerms)
    else:
        return "Over 100,000 records in dbGaP match your search terms, please increase the specificity of your search"
    xmlParse(response)

def xmlParse(xml):
    entrezIds = list()
    phsIds = list()
    harmony = dict()
    for ele in xml.content.split('\n'):
        if '<Id>' in ele:
            dbID = ele.lstrip('<Id>')
            dbID = dbID.rstrip('</Id>')
            entrezIds.append(dbID)
            res = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gap&id=' + dbID + '&version=2.0')
            for line in res.content.split('\n'):
                if "<d_study_id>" in line:
                    studyID = line.replace("\t", "").replace("<d_study_id>", "").replace("</d_study_id>", "")
                    phsIds += [studyID]
                    harmony[dbID] = {"study_id":studyID, "study_name": "", "disease_name":""}
                elif "d_study_name" in line:
                    studyName = line.replace("\t", "").replace("</d_study_name>", "").replace("<d_study_name>", "")
                    harmony[dbID]["study_name"] = studyName
                elif "d_disease_name" in line:
                    diseaseName = line.replace("\t", "").replace("<d_disease_name>", "").replace("</d_disease_name>", "")
                    harmony[dbID]["disease_name"] = diseaseName
    if len(phsIds)==0:
        print "dbGaP result is null"
    else:
        try:
            with open('dbGAP_output.csv','w') as f:
                f.write('dbGaP_accession_num,web_address,study_name,disease_name\n')
                for key in harmony.keys():
                    outStr = harmony[key]["study_id"]+",http://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id="+harmony[key]["study_id"]+","+harmony[key]["study_name"]+","+harmony[key]["disease_name"]+"\n"
                    f.write(outStr)
        except IOError:
            print "Could not open file for writing"
            sys.exit(0)
        
# main function

def main():
    """
        This function:
        - parses the command line arguments
        - checks TCGA is up
        - search type 
    """

    # parse the command line args
    args = get_args()

    # If TCGA/GDC not up
    if not check_tcga():
        return "TCGA is not responding"

    # List of functions which parse the response based on what type of information is returned 
    response_func = {"project": project, "file": tcgaFile, "case": case}
    
    # If search by id is used
    if args.idSearch is not None and args.searchType is not None:
        searchType = args.searchType.lower()
        responseRAW = query_by_id(args.idSearch, searchType) # Queries GDC by id

        returnType = searchType # Will return the type matching the id search
    
    # If search by disease and/or study type is used
    elif args.disease != None or args.studyType!=None:
        if args.disease == None:
            diseases = []
        else:
            diseases = args.disease.split(",")
        if args.studyType==None:
            types = []
        else:
            types = args.studyType.split(",")
        searchDict = {"disease":diseases, "studyType":types}
        returnType = args.returnType.lower()
        responseRAW = query_by_filter(searchDict, returnType)

    else:
        return "Please enter eiter an id and search type, a disease or a study type to search"

    response = responseRAW["data"]["hits"]
    if response == []:
        return "No matches were found using the submitted search terms"

    header_row = {"project": "project_id,web_address,disease,experimental_strategy,primary_site\n",
                  "file": "file_id,case_id,project,web_address,disease,experimental_strategy\n",
                  "case": "case_id,web_address,disease,experimental_strategy,primary_site\n"}
    outStringKeys = {"project": ["project_id","project_id","disease_type","strategies_list","primary_site"],
                 "file": ["file_id","file_id","disease_type","strategies_list","primary_site"],
                 "case":["case_id","case_id","disease_type","strategies_list","primary_site"]}
    tcgaOutStr = header_row[returnType]
    diseases = []
    studyType = []
    tcga_count = 0
    for dic in response:
        tcga_count += 1
        outDict = response_func[returnType](dic) # processes output
        diseases += [outDict["disease_type"]]
        studyType += outDict["strategies_list"]
        tcgaOutStr += outDict[outStringKeys[returnType][0]]+",https://gdc-portal.nci.nih.gov/"+returnType+"s/"+outDict[outStringKeys[returnType][1]]+","\
                      +outDict[outStringKeys[returnType][2]]+","+"\\".join(outDict[outStringKeys[returnType][3]])+","+outDict[outStringKeys[returnType][4]]+"\n"
    print str(tcga_count)+ " matches found in TCGA"
    with open("tcag_output.csv", "w") as outFile:
        outFile.write(tcgaOutStr)

    query_dbGaP(args.stringencyLevel, diseases=diseases, studyTypes=list(set(studyType)))

# initialize the script
if __name__ == '__main__':
    try:
        sys.exit(main())
    except IOError, e:
        if e.errno != 32: # ignore SIGPIPE
            raise 

