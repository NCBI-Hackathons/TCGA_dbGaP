import requests
#import demjson
import json


class Query_TCGA:
    def __init__(self):
        pass
    
    def check_tcga(self):

        status_endpt = 'https://gdc-api.nci.nih.gov/status'
        response = requests.get(status_endpt)
        response = response.json()
        status = response[u"status"]
        print status
        if status == u"OK":
            return True
        else:
            return False


    def query_by_project(self, projectName):
        url = 'https://gdc-api.nci.nih.gov/projects/'+projectName+'?expand=summary,summary.experimental_strategies,summary.data_categories&pretty=true'
    
        response = requests.get(url)
        response = response.json()
        disease = response[u"data"][u"disease_type"]
        print disease

    def query_by_file(self, fileID):
        url = 'https://gdc-api.nci.nih.gov/files/'+fileID+'?pretty=true&expand=cases.project'
        response = requests.get(url)
        response = response.json()
        disease = response[u"data"][u"cases"][0][u"project"][u"disease_type"]
        print disease

    def query_by_sample(self, sampleID):
        url = 'https://gdc-api.nci.nih.gov/cases/'+sampleID+'?pretty=true&expand=project'
        response = requests.get(url)
        response = response.json()
        disease = response[u"data"][u"project"][u"disease_type"]
        print disease

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

        
        print filterParams
        params = {'pretty': 'true',
                  'filters': json.dumps(filterParams)}

        response = requests.get(url, params=params)
        response = response.json()
        print response

            

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
        print response

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
        print response

def main():
    tcga = Query_TCGA()
    if tcga.check_tcga():
        tcga.query_by_project('TCGA-LUAD')
        tcga.query_by_file('000225ad-497b-4a8c-967e-a72159c9b3c9')
        tcga.query_by_sample('1f601832-eee3-48fb-acf5-80c4a454f26e')
        tcga.query_by_filter(["Lung Adenocarcinoma", "WXS"], ["disease", "studyType"], "case")
        #tcga.query_projects_by_disease("Breast Invasive Carcinoma")
        #tcga.query_projects_by_type("WXS")
        
    else:
        print "TCGA is not responding"

if __name__ == "__main__":
    main()
