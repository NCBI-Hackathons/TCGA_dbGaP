#!/usr/bin/env python
"""
Created on Wed Aug 17 10:03:52 2016

@author: satya_000
"""
__author__ = "Satyajeet"
__version__ = "$Revision: 0.0.1 $"
__date__ = "$Date: 2016-08-17$"
import requests
import argparse, sys
from argparse import RawTextHelpFormatter
import pandas as pd
from io import StringIO

#SRPS = []
#SRRS = []

# --------------------------------------
# define functions
def get_args():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter, description="\SRR Fetcher from Gap Idsn\
 author: " + __author__ + "\n\
 version: " + __version__ + "\n\
 description: Search for genomic data from SRA using dbGap Ids")
    parser.add_argument('-f', '--file', type=str, default=None, help=' <path to file containing dbGap Ids>')
    parser.add_argument('-id', '--dbGapIds', type=str, default=None, help=' <path to file containing dbGap Ids>')
    # parse the arguments
    args = parser.parse_args()
    # if no input,exit
    if len(sys.argv) <= 1:        
        parser.print_help()
        sys.exit(1)
    # send back the user input
    return args
            

def main():
    # parse the command line args
    args = get_args()
    if args.file is not None:
        try:
            csvdata  = pd.read_csv(args.file, sep = ",")
        except:
            print('File not found at the path entered.')
            sys.exit()
        gapIDs = csvdata['dbGaP_accession_number']
    elif args.dbGapIds is not None:
        gapIDs = args.dbGapIds.split(',')
    file = open('SRRlist.txt', "w")        
    for gapID in gapIDs:  
        try:
           response = requests.get('http://trace.ncbi.nlm.nih.gov/Traces/sra/?sp=runinfo&acc=' + gapID)
           rawdata = StringIO(response.text)
           df = pd.read_csv(rawdata, sep=",") 
           s = df['Run']
           file = open('SRRlist.txt', "w")
           for item in s:        
            file.write(item + '\n')
        except:
              continue
        file.close()
    
if __name__ == "__main__":
    main()
