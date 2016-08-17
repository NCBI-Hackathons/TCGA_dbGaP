def filter_diseases(fname, cancerOutFile, notCancerOutFile, tcga_dict, site_dict):
    cancer = []
    not_cancer = []
    with open(fname, 'r') as dFile:
        for line in dFile:
            line = line.lower().strip('\n')
            if "cancer" in line or "sarcoma" in line or "carcinoma" in line\
            or "neoplasm" in line or "leukemia" in line or "lymphoma" in line\
            or "cytoma" in line or "glioma" in line or "craniopharyngioma" in\
            line or "blastoma" in line or "noma" in line or "tumor" in line\
            or "myeloma" in line or "neurofibromatoses" in line or "gioma" in\
            line or "xerostomia" in line or "hodgkin disease" in line or "myoma"\
            in line or "moma" in line:
                cancer += [line]
            else:
                not_cancer += [line]

    with open(cancerOutFile, 'w') as oFile:
        # write column headers
        oFile.write("Primary Site\tdbGaP\tMatch\tTCGA\tNotes\n")
        
        # loop through cancer-related dbGaP terms
        for dis in cancer:
            match = False
            # loop through TCGA diseases
            for key in tcga_dict:
                # loop through tcga_dict
                diseaseMatch = False
                for term in tcga_dict[key]:
                    # if one of the words in tcga disease name is in dbGaP term
                    if term in dis:
                        diseaseMatch = True

                # This prevents multiple term matches from the same disease 
                if diseaseMatch == True:
                    oFile.write(site_dict[key] + "\t"+dis+"\t\t"+ key+"\t\n")
                    match = True
            if match == False:
                oFile.write("\t"+dis+"\t\t\t\n")
                
    with open(notCancerOutFile, 'w') as oFile:
        for dis in not_cancer:
            oFile.write(dis+"\n")

def make_tcga_disease_dict(fname):
    tcga_dict = {}
    with open(fname, 'r') as tcFile:
        for line in tcFile:
            line = line.lower().strip('\n')
            names = line.split(" ")
            if "cancer" in names:
                names.remove("cancer")
            if "and" in names:
                names.remove("and")
            if "cell" in names:
                names.remove("cell")
            if "neoplasm" in names:
                names.remove("neoplasm")
            if "of" in names:
                names.remove("of")
            if "the" in names:
                names.remove("the")
            if "carcinoma" in names:
                names.remove("carcinoma")
            if "tumor" in names:
                names.remove("tumor")
            tcga_dict[line] = names
    return tcga_dict

def make_site_disease_dict(fname):
    site_dict = {}

    with open(fname, 'r') as siteFile:
        for line in siteFile:
            group = line.split("\t")
            disease = group[0].lower()
            site = group[1].lower().strip("\n")

            site_dict[disease] = site
    return site_dict
            

def main():
    tcga_dict = make_tcga_disease_dict("TCGA_List_of_diseases.txt")
    site_dict = make_site_disease_dict("TCGA Disease and Primary Site.tsv")
    filter_diseases("dbGaP_diesease.txt", "dbGaP_cancer_annotated.txt", "dbGaP_notCancer.txt", tcga_dict, site_dict)


if __name__=="__main__":
    main()
