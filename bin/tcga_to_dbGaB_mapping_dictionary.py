class Mapping:
    def __init__(self):
        self.diseaseDict = {}
        self.studyDict = {"WXS":[], "miRNA-Seq":[], "RNA-Seq":[], "Genotyping Array":[]}

    def make_disease_map(self, fileName, stringency="high"):
        """ Creates a dictionary with TCGA disease name as key and
            associated dbGaP disease names as values.
            Input:
            -tsv file with dbGaP disease name mapped to TCGA disease
            -stringency requirement of returned dbGaP terms (high, medium, low)
        """

        stringencyDict = {"high": ["perfect"], "medium": ["perfect", "good", "okay"], "low": ["perfect", "good", "okay","bad"]}
        with open(fileName, 'r') as mapFile:
            for line in mapFile:
                values = line.split("\t")
                # Check if the stringency between the dbGaP and TCGA mapping is exceptible
                if values[2] in stringencyDict[stringency]:
                    self.diseaseDict[values[3].lower()] += [values[1]]
                    

    def init_diseaseDict(self, tcgaFName):
        with open(tcgaFName, 'r') as tcgaFile:
            for line in tcgaFile:
                values = line.split("\t")
                self.diseaseDict[values[0].lower()] = []

    def make_study_map(self, fileName, stringency="high"):
        stringencyDict = {"high": ["perfect"], "medium": ["perfect", "good"], "low": ["perfect", "good", "bad"]}
        with open(fileName, 'r') as mapFile:
            for line in mapFile:
                values = line.split("\t")
                if values[1] in stringencyDict[stringency] and values[2] != "NA":
                    self.studyDict[values[2].strip(" \n")] += [values[0].strip(" ")]
            

    def main(self, stringency):
        
        self.init_diseaseDict("mapping/TCGA Disease and Primary Site.tsv")
        self.make_disease_map("mapping/dbGaP to TCGA disease and primary site.tsv", stringency)
        self.make_study_map("mapping/study_type_mapping.tsv")
        return self.diseaseDict, self.studyDict


"""if __name__ == "__main__":
    mapObj = Mapping()
    mapObj.main()"""
            
    
