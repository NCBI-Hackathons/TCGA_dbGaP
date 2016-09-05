#!/bin/bash
input=$1 #file with list of SRR IDs
output=$2 #output path
genregion=$3 #gene region of interest in the format of chr:fromposition-toposition (e.g.  4:1723150-1810650)

while IFS= read -r sample;
do
	sam-dump --aligned-region $genregion --output-file $output/$sample-$genregion.sam $sample
done < $input
