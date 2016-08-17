#!/bin/bash

SRA=~/ewagner/sratoolkit.2.7.0-centos_linux64/bin
results=~/ewagner/sratoolkit.2.7.0-centos_linux64/HACKATHON2016

#input file with list of SRR IDs
input=~/ewagner/sratoolkit.2.7.0-centos_linux64/HACKATHON2016/SRRlist.txt

#gene region to search
#genregion=4:1723150-1810650

#can input multiple regions in the regionlist.txt file to query mutiple regions
#region=~/ewagner/sratoolkit.2.7.0-centos_linux64/HACKATHON2016/regionlist.txt

#alternative gene region to search
#genregion=7:55086678-55279262

genregion=$1

while IFS= read -r sample;
do
	$SRA/sam-dump --aligned-region $genregion --output-file $results/$sample-$genregion.sam $sample
done < $input

