#!/bin/bash
base= ./sratoolkit.2.7.0-centos_linux64 #path to the sra toolkit folder <default assumes current folder>
#path to input file with list of SRR IDs
input= ./SRRlist.txt #add the inout path here <default is the current folder>
#path to output folder
results= ./output #add the output path here <default is the current folder>

#gene region to search
#genregion=4:1723150-1810650

SRA=base + /bin

genregion=$1

while IFS= read -r sample;
do
	$SRA/sam-dump --aligned-region $genregion --output-file $results/$sample-$genregion.sam $sample
done < $input
