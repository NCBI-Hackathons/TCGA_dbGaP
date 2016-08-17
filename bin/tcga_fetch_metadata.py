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
TCGA ID SEARCH\n\
author: " + __author__ + "\n\
version: " + __version__ + "\n\
description: Find a tcga id and search")
    parser.add_argument('-i', '--input', type=str, default=None, help='projectID input (default: stdin)')
    parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout, help='Output to write (default: stdout)')
    # parse the arguments
    args = parser.parse_args()

    # if no input, check if part of pipe and if so, read stdin.
    if args.input == None:
        if sys.stdin.isatty():
            parser.print_help()
            exit(1)
        else:
            args.input = sys.stdin

    # send back the user input
    return args

# --------------------------------------
class project(object):
	def __init__(self,jsonObj):
		self.summary = jsonObj['data']['summary'] 
		self.strategies_list = [expt_strategy(i) for i in self.summary['experimental_strategies']]
		self.data_categories = [data_category(i) for i in self.summary['data_categories']]
		self.project_id = jsonObj['data']['project_id']
		self.name = jsonObj['data']['project_id']
		self.released = jsonObj['data']['released']
		self.state = jsonObj['data']['state']
		self.primary_site = jsonObj['data']['primary_site']
		self.dbgap = jsonObj['data']['dbgap_accession_number']
		self.disease_type = jsonObj['data']['disease_type']
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
# main function
def main():
	# parse the command line args
	args = get_args()
	status_endpt ='https://gdc-api.nci.nih.gov/projects/' + args.input + '?expand=summary,summary.experimental_strategies,summary.data_categories&pretty=false'
	response = requests.get(status_endpt)
	if response.status_code == 200:
		p = project(response.json())
		print p
	else:
		print "FAILURE"
	
# initialize the script
if __name__ == '__main__':
    try:
        sys.exit(main())
    except IOError, e:
        if e.errno != 32: # ignore SIGPIPE
            raise 
