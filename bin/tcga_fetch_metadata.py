#!/usr/bin/env python
import argparse, sys, re
import requests,time
import json

from tcga_to_dbGaB_mapping_dictionary import Mapping

from argparse import RawTextHelpFormatter

__author__ = ""
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2016-08-26$"

# --------------------------------------
# define functions
def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\
 TCGA DBGAP METADATA HARMONIZATION\n\
 author: " + __author__ + "\n\
 version: " + __version__ + "\n\
 description: Search tcga by project/study/file/samples/customSearch")
    parser.add_argument('-i', '--idSearch', type=str, default=None, help=' project/case/file id')
    parser.add_argument('-s', '--searchType', required = True, type=str, default='case', help='View results by project/file/case')
    parser.add_argument('-d', '--disease', type=str, default=None, help='disease param')
    parser.add_argument('-n', '--studyType', type=str, default=None, help='study type param wgs/wxs/rnaseq/etc')
    parser.add_argument('-l', '--stringencyLevel', type=str, default="high", help='stringency level of dbGaP term match')
    # parse the arguments
    args = parser.parse_args()
    # if no input,exit
    if len(sys.argv) <= 1:        
        parser.print_help()
        sys.exit(1)
    # send back the user input
    return args
# --------------------------------------

class Query_TCGA:
    def __init__(self):
        pass
    
    def check_tcga(self):

        status_endpt = 'https://gdc-api.nci.nih.gov/status'
        response = requests.get(status_endpt)
        response = response.json()
        status = response[u"status"]
        if status == u"OK":
            return True
        else:
            return False


    def query_by_project(self, projectName):
        url = 'https://gdc-api.nci.nih.gov/projects/'+projectName+'?expand=summary,summary.experimental_strategies,summary.data_categories&pretty=true'
    
        response = requests.get(url)
        response = response.json()
        return response

    def query_by_file(self, fileID):
        url = 'https://gdc-api.nci.nih.gov/files/'+fileID+'?pretty=true&expand=cases.project'
        response = requests.get(url)
        response = response.json()
        return response

    def query_by_sample(self, sampleID):
        url = 'https://gdc-api.nci.nih.gov/cases/'+sampleID+'?pretty=true&expand=project'
        response = requests.get(url)
        response = response.json()
        return response
    def query_by_filter(self, filtList, filtTypeList, returnType):

        fieldsDict = {"disease": {"project":"disease_type", "file":"cases.project.disease_type", "case": "project.disease_type"},
                      "studyType": {"project":"summary.experimental_strategies.experimental_strategy", "file":"experimental_strategy", "case":"files.experimental_strategy"},
                      "outputFiles": {"project":"disease_type,project_id,released,state,primary_site,dbgap_accession_number,summary.experimental_strategies.experimental_strategy,summary.data_categories.data_category", "file":"experimental_strategy,data_type,cases.summary.data_categories.data_category,cases.project.dbgap_accession_number,cases.project.disease_type,cases.project.released,cases.project.state,cases.project.primary_site,cases.project.project_id,cases.project.name", "case": "project.dbgap_accession_number,project.disease_type,project.released,project.state,project.primary_site,project.project_id,project.name,case_id,sample_ids"}}

        # Validate entry #data_type,cases.summary.data_categories.data_category
        for filt in filtTypeList:
            if filt not in ["disease", "studyType"]:
                print "Please enter a valid filter type ('disease' or 'studyType')"
                return
        if returnType not in ["project", "file", "case"]:
            print "Please enter a valid return type ('project', 'file' or 'case')"
            return
        if len(filtList) != len(filtTypeList):
            print "Please enter in the same number of filer terms and filter types"
            return

        # query the correct type
        if returnType == "project":
            url = 'https://gdc-api.nci.nih.gov/projects'
        elif returnType == "file":
            url = 'https://gdc-api.nci.nih.gov/files'
        else:
            url = 'https://gdc-api.nci.nih.gov/cases'

        if len(filtList) == 1:
            val = filtList[0]
            field = fieldsDict[filtTypeList[0]][returnType]
            filterParams = {"op": "=",
                        "content": {
                            "field": field,
                            "value": [val]
                            }
                        }
        else:
            contentList = []
            for i in range(len(filtList)):
                val = filtList[i]
                field = fieldsDict[filtTypeList[i]][returnType]
                contentList += [{ "op":"=",
                    "content": {
                    "field": field,
                    "value": [val]
                    }}]
            filterParams = {"op": "and",
                            "content": contentList}
        params = {'pretty': 'true',
                  'filters': json.dumps(filterParams),'fields': fieldsDict["outputFiles"][returnType]}
        response = requests.get(url, params=params)
        response = response.json()
        return response

            

    def query_projects_by_disease(self, diseaseName):
        url = 'https://gdc-api.nci.nih.gov/projects'
        filt ={"op": "=",
                'content':{
                    'field': 'disease_type',
                    'value': [diseaseName]}
               }
        params = {'pretty': 'true',
                  'filters': json.dumps(filt)}

        response = requests.get(url, params=params)
        response = response.json()
        return response

    def query_projects_by_type(self, studyType):
        url = 'https://gdc-api.nci.nih.gov/files'
        filt = {'op': '=',
                'content':{
                    'field': 'experimental_strategy',
                    'value': [studyType]
                    }
                }
        params = {'pretty': 'true',
                  'filters': json.dumps(filt)}

        response = requests.get(url, params=params)
        response = response.json()
        return response

class project(object):
    def __init__(self,jsonObj):
        summary = jsonObj['summary'] 
        self.strategies_list = [expt_strategy(i) for i in summary['experimental_strategies']]
        self.data_categories = [data_category(i) for i in summary['data_categories']]
        self.project_id = jsonObj['project_id']
        self.name = jsonObj['project_id']
        self.released = jsonObj['released']
        self.state = jsonObj['state']
        self.primary_site = jsonObj['primary_site']
        self.dbgap = jsonObj['dbgap_accession_number']
        self.disease_type = jsonObj['disease_type']
class strategy(object):
    def __init__(self,Dictitem):
        self.case_count= Dictitem['case_count']
        self.file_count= Dictitem['file_count']
        self.strategy= ''
        print self.file_count   
class expt_strategy(strategy):
    def __init__(self,item):
        self.strategy  = item['experimental_strategy']
class data_category(strategy):
    def __init__(self,item):
        self.strategy  = item['data_category']
class project_details(object):
    def __init__(self,item):
        self.accn = item['dbgap_accession_number']
        self.disease_type = item['disease_type']
        self.released = item['released']
        self.state = item['state']
        self.primary_site = item['primary_site']
        self.project_id = item['project_id']
        self.name = item['name']
class tcgaFile(object):
    def __init__(self,item):
        self.data_type = item['data_type']
        #self.updated_datetime = item['updated_datetime']
        #self.created_datetime = item['created_datetime']
        #self.file_name = item['file_name']
        #self.md5sum = item['md5sum']
        #self.data_format = item['data_format']
        #self.acl = item['acl']
        #self.access = item['access']
        #self.state = item['state']
        #self.file_id = item['file_id']
        #self.data_category = item['data_category']
        #self.file_size = item['file_size']
        #self.submitter_id = item['submitter_id']
        #self.type = item['type']
        #self.file_state = item['file_state']
        #self.exp_stg = item['experimental_strategy']
        #self.data_ctg = item['data_category']
        try:
            self.projects = [project_details(i['project']) for i in item['cases']]
        except KeyError:
            self.projects = None
class case(object):
    def __init__(self,jsonObj):
        self.case_id = jsonObj['case_id']
        try:
            self.sample_ids = jsonObj['sample_ids']
        except KeyError:
            self.sample_ids = None
        try:
            self.project = project_details(jsonObj['project'])
        except KeyError:
            self.project = None
def xmlParse(terms, stringency, studyType):
    mapObj = Mapping()
    diseaseDict, studyDict = mapObj.main(stringency)
    dbGaPTerms = []
    for dis in terms:
        dbGaPTerms += diseaseDict[dis.lower()]
    strTerms = "[Disease]OR".join(dbGaPTerms)+"[Disease]"
    if studyType != None:
        dbGaPType = studyDict[studyType]
        dbGaPStr = "[Molecular Data Type]OR".join(dbGaPType) 
        strTerms = "("+strTerms+")AND("+dbGaPStr+"[Molecular Data Type])"
    response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gap&term=1[s_discriminator]&' + strTerms)
    entrezIds = list()
    phsIds = list()
    harmony = dict()
    for ele in response.content.split('\n'):
        if '<Id>' in ele:
            id = ele.replace('<Id>','').replace('</Id>','')
            entrezIds.append(id)
            res = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gap&id=' + id + '&version=2.0')
            type(res.content)
            m=re.search("<d_study_id>(.{2,})</d_study_id>",res.content,re.MULTILINE)
            if m is not None:
                phsIds.append(m.group(1))
                harmony[id] = m.group(1)
    if len(phsIds)==0:
        print "dbGaP result is null"
    else:
        try:
            with open('OUTPUT.csv','wb') as f:
                f.write(','.join(['dbGaP_accession_no']) + '\n')
                for value in harmony.values():
                    f.write(','.join([value]) + '\n')
            f.close()
        except IOError:
            print "Could not open file for writing"
            sys.exit(0)
        
# main function

def main():
    # parse the command line args
    args = get_args()
    tcga = Query_TCGA()
    
    if args.searchType is not None:
        if tcga.check_tcga():
            disease = []

            if args.idSearch is not None:
                # Search by projectID
                if args.searchType.lower() == 'project':
                    response = project(tcga.query_by_project(args.idSearch)['data'])
                    disease = [response.disease_type]
                    studyType = None # Projects contain multiple study types, so will not query dbGaP with study type
                    outString = "project_id,web_address,disease,experimental_strategy\n"+response.project_id+",https://gdc-portal.nci.nih.gov/projects/"+response.project_id+","+response.disease_type+","+"\\".join([s.strategy for s in response.strategies_list])+"\n"
                    with open("tcga_results.csv", "w") as outFile:
                        outFile.write(outString)
                    
                # Search by fileID
                elif args.searchType.lower() == 'file':
                    response = tcgaFile(tcga.query_by_file(args.idSearch)['data'])
                    for p in response.projects:
                        disease += [p.disease_type]
                    studyType = response.exp_stg
                    

                # Search by CaseID
                elif args.searchType.lower() == 'case' or args.searchType.lower() == 'sample':
                    response = case(tcga.query_by_sample(args.idSearch)['data'])
                    disease = response.project.disease_type
                    studyType = response.exp_stg
            else:
                response = None
                # Search by both disease and studyType
                if args.disease != None and args.studyType!=None:
                    response = tcga.query_by_filter([args.disease, args.studyType], ["disease", "studyType"], args.searchType)['data']
                    studyType = args.studyType
                    #print response
                # Search by disease
                elif args.disease !=None:
                    response = tcga.query_by_filter([args.disease], ["disease"], args.searchType)['data']
                    studyType = None
                    #print response
                # Search by studyType
                elif args.studyType !=None:
                    response = tcga.query_by_filter([args.studyType], ["studyType"], args.searchType)['data']
                    studyType = args.studyType
                    
                else:
                    print "Enter either disease or studyType for search"
                    sys.exit(1)

                # If there is a response 
                if response != None or len(response['hits']) != 0:
                    ls = response['hits']
                    if args.searchType.lower() == 'project':
                        for item in ls:
                            res = project(item)
                            disease += [res.disease_type]
                    elif args.searchType.lower() == 'file':
                        for item in ls:
                            res = tcgaFile(item)
                            for p in res.projects:
                                                            disease += [p.disease_type]
                    elif args.searchType.lower() == 'case' or args.searchType.lower() == 'sample':
                        for item in ls:
                            res = case(item)
                            disease += [res.project.disease_type]
                else:
                    print "No Result"
                    sys.exit(1)

            xmlParse(disease, args.stringencyLevel, studyType)  
        else:
            print "TCGA is not responding"
        
# initialize the script
if __name__ == '__main__':
    try:
        sys.exit(main())
    except IOError, e:
        if e.errno != 32: # ignore SIGPIPE
            raise 
