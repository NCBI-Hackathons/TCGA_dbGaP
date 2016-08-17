import argparse, sys, re
import requests
import json
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
    parser.add_argument('-i', '--input', type=str, default=None, help=' project/case/file input (default: stdin)')
    parser.add_argument('-s', '--searchType', required = True, type=str, default=None, help='Search by project/file/case/disease/searchType')
    parser.add_argument('-d', '--disease', type=str, default=None, help='disease param')
    parser.add_argument('-n', '--studyType', type=str, default=None, help='study type param wgs/wxs/rnaseq/etc')
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
        #print status
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
        disease = response[u"data"][u"cases"][0][u"project"][u"disease_type"]
       #print disease

    def query_by_sample(self, sampleID):
        url = 'https://gdc-api.nci.nih.gov/cases/'+sampleID+'?pretty=true&expand=project'
        response = requests.get(url)
        response = response.json()
        return response
        disease = response[u"data"][u"project"][u"disease_type"]
        #print disease

    def query_by_filter(self, filtList, filtTypeList, returnType):

        fieldsDict = {"disease": "disease_type", "studyType": "experimental_strategy"}

        # Validate entry
        for filt in filtTypeList:
            if filt not in ["disease", "studyType"]:
                print "Please enter a valid filter type ('disease' or 'studyType')"
                return
        if returnType not in ["project", "files", "case"]:
            print "Please enter a valid return type ('project', 'files' or 'case')"
            return
        if len(filtList) != len(filtTypeList):
            print "Please enter in the same number of filer terms and filter types"
            return

        # query the correct type
        if returnType == "project":
            url = 'https://gdc-api.nci.nih.gov/projects'
        elif returnType == "files":
            url = 'https://gdc-api.nci.nih.gov/files'
        else:
            url = 'https://gdc-api.nci.nih.gov/cases'

        if len(filtList) == 1:
            field = fieldsDict[filtTypeList[0]]
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
                field = fieldsDict[filtTypeList[i]]
                contentList += [{ "op":"=",
                    "content": {
                    "field": field,
                    "value": [val]
                    }}]
            filterParams = {"op": "and",
                            "content": contentList}
        #print filterParams
        params = {'pretty': 'true',
                  'filters': json.dumps(filterParams)}

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
		self.updated_datetime = item['updated_datetime']
		self.created_datetime = item['created_datetime']
		self.file_name = item['file_name']
		self.md5sum = item['md5sum']
		self.data_format = item['data_format']
		self.acl = item['acl']
		self.access = item['access']
		self.state = item['state']
		self.file_id = item['file_id']
		self.data_category = item['data_category']
		self.file_size = item['file_size']
		self.submitter_id = item['submitter_id']
		self.type = item['type']
		self.file_state = item['file_state']
		self.exp_stg = item['experimental_strategy']
		self.data_ctg = item['data_category']
		try:
			self.projects = [project_details(i) for i in item['cases']]
		except KeyError:
			self.projects = None
class case(object):
	def __init__(self,jsonObj):
		self.case_id = jsonObj['case_id']
		self.sample_ids = jsonObj['sample_ids']
		self.state = jsonObj['state']
		try:
			self.project = project_details(jsonObj['project'])
		except KeyError:
			self.project = None
def xmlParse(term):
	response = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gap&term=' + term)
	print 'https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=gap&term=' + term
	entrezIds = list()
	phsIds = list()
	for ele in response.content.split('\n'):
		if '<Id>' in ele:
			id = ele.replace('<Id>','').replace('</Id>','')
			entrezIds.append(id)
			res = requests.get('https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=gap&id=' + id + '&version=2.0')
			type(res.content)
			m=re.search("<d_.*_id>(.{2,})</d_.*_id>",res.content,re.MULTILINE)
			if m is not None:
				phsIds.append(m.group(1))
				
	if len(phsIds)==0:
		print "EMPTY TERM"
	else:
		print phsIds
# main function

def main():
	# parse the command line args
	tcga = Query_TCGA()
	args = get_args()
	if args.searchType is not None:
		if tcga.check_tcga():
			if args.input is not None:
				if args.searchType.lower() == 'project':
					response = project(tcga.query_by_project(args.input)['data'])
					xmlParse(response.disease_type)
				elif args.searchType.lower() == 'file':
					response = tcgaFile(tcga.query_by_file(args.input)['data'])
					for p in response.projects:
						xmlParse(p.disease_type)
				elif args.searchType.lower() == 'case' or args.searchType.lower() == 'sample':
					response = tcga.query_by_sample(args.input)
					[xmlParse(p.disease_type) for p in response.projects]
			else:
				response = None
				if args.disease != None and args.studyType!=None:
					response = tcga.query_by_filter([args.disease, args.studyType], ["disease", "studyType"], args.searchType)['data']
					print response
				elif args.disease !=None:
					response = tcga.query_by_filter([args.disease], ["disease"], args.searchType)['data']
					print response
				elif args.studyType !=None:
					response = tcga.query_by_filter([args.studyType], ["studyType"], args.searchType)['data']
					print response
					print "Test"
				# if response != None
					# if args.searchType.lower()=='project':
						
					# if args.searchType.lower()=='file':
					# if args.searchType.lower()=='case':
				#[tcgaFile(i).file_id for i in tcga.query_projects_by_type("WXS")['data']['hits']]
		else:
			print "TCGA is not responding"
		
# initialize the script
if __name__ == '__main__':
    try:
        sys.exit(main())
    except IOError, e:
        if e.errno != 32: # ignore SIGPIPE
            raise 
