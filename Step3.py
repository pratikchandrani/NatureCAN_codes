
import json
import sys
from tqdm import tqdm
import langextract as lx
import pandas as pd

# -*- coding: utf-8 -*-


# -------- Helper function to serialize AnnotatedDocument -------- #
def doc_to_dict(doc):
    return {
        "document_id": doc.document_id,
        "text": doc.text,
        "extractions": [
            {
                "extraction_class": e.extraction_class,
                "extraction_text": e.extraction_text,
                "char_interval": (
                    {"start": e.char_interval.start_pos, "end": e.char_interval.end_pos}
                    if e.char_interval else None
                )
            }
            for e in doc.extractions
        ]
    }
#Toxicitty to Patient study only , other not available,
#Study type description -- make a new column
#Give more examples of PAtient where toxicity is present 
# -------- Load Data -------- #
dataa = pd.read_excel("Step2_Output_2.xlsx")
dataa=dataa[:]  # First Data --> 5300-5500 , Now --> 6000-6500
#dataa = pd.read_excel("Step_8_Author_&_Country_Output_115233_1_Clean_Cancer5300_5500.xlsx")
print(dataa.columns)
print(dataa.shape)

# Take a slice of the dataframe with PMID + Abstract
input_rows = dataa[["PMID", "Abstract"]].iloc[:]  #50-70,70-100,170-200
print(input_rows)

# Define extraction prompt
prompt_description = '''Extract article description to identify :
Study Type: "MUST be one of ['In vitro', 'In vivo', 'Review', 'Patient study', 'In silico']", 
Do not generate other terms like "Research Study","Laboratory Study","Experiment Study",etc.
If the study does not match these five exactly, use: Other Study (brief reason here).
The Study Type should be identified based on the oher context of the abstract text,
Model System : Identify the model, system, or organism used in the study. If not available, leave blank.,  
Experimental Techniques :List the techniques or methods applied (e.g., examination, screening, analysis, prediction) ,
Toxicity and Side effects,
Year :Include the year if explicitly mentioned, otherwise note as Not Mentioned.
Extracted_Cancer_Types : Contains Types of Cancers
The Output extracted should not contain text irrelevant or which is not in the input text. 
'''


# Example data
examples = [

#1st
    lx.data.ExampleData(
        text='''A 41-year-old woman presented with a hyphema in her right eye. Clinical examination revealed a vascular lesion of the iris that had enlarged over a 6-month period. The patient had no other evidence of ocular or cutaneous vascular malformations. Subsequently she experienced recurrent episodes of spontaneous hyphema, and there was objective evidence of growth of the lesion. Consequently, the lesion was excised by means of a sector iridectomy. Histopathological examination showed several large vascular compartments separated by thin, fibrous septa and lined by endothelium, consistent with a cavernous hemangioma. A benign iris melanocytic lesion was identified adjacent to the cavernous hemangioma. The intraocular pressure in the affected eye remained normal after the lesion was removed. After 6 months of follow-up no new hyphemas had developed. Iris cavernous hemangioma should be added to the differential diagnosis of recurrent hyphema. The woman was having vomiting and fever''',
        extractions=[
            lx.data.Extraction(
                extraction_class="Study type",
                extraction_text="Patient study",
                attributes={"sample_size": "1", "gender": "female", "age": "41", "condition": "hyphema"}
            ),
            lx.data.Extraction(
                extraction_class="Model System",
                extraction_text="Human (41-year-old woman)",
                attributes={"species": "human", "gender": "female", "age": "41", "tissue": "iris"}
            ),
            lx.data.Extraction(
                extraction_class="Experimental Techniques",
                extraction_text="Clinical examination, Histopathological examination, sector iridectomy",
                attributes={"clinical": "yes", "surgical": "iridectomy"}
            ),
            lx.data.Extraction(
                extraction_class="Toxicity and Side effects",
                extraction_text="vomiting and fever",
                attributes={"severity": "none"}
            ),
            lx.data.Extraction(
                extraction_class="Year",
                extraction_text="Not Mentioned",
                attributes={"reported": "no"}
            ),
              lx.data.Extraction(
                extraction_class="Extracted_Cancer_Type",
                extraction_text="No cancer type identified; lesion was a benign cavernous hemangioma",
                attributes={"reported": "no",
        "benign_lesion": "yes",
        "cancer_mentioned": "no"}
            ),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="No drug treatment mentioned; lesion was excised surgically by sector iridectomy",
    attributes={
        "reported": "no",
        "benign_lesion": "yes",
        "cancer_mentioned": "no"
    }
)

        ]
    ),
    
    #2nd

    lx.data.ExampleData(
        text='''Five pairs of new epimeric lanostane-type triterpenoids, abiespirones A-D (1-4) and G (7), two pairs of new epimeric cycloartane-type triterpenoids, abiespirones E and F (5, 6), and a pair of new epimeric 7(8-9)abeo-spirolanostane abiespirones H (8) with spiro-B/C and -E/F ring systems were isolated from Abies faxoniana as inseparable mixtures of C-23 epimers in a specific proportion. The HPLC plots showed that each purified isomer rapidly equilibrated with the C-23 epimer in solution. The structures of compounds 1-8 were elucidated by analysis of the NMR spectra and single-crystal X-ray diffraction. Compound 6 showed cytotoxicity against three hepatoma cell lines, namely, HepG2, Huh7, and SMMC7721, with IC50 values of 9.8, 7.5, and 10.7 uM, respectively, but exerted low cytotoxicity on normal QSG7701 hepatic cells, indicating its selective cytotoxicity for hepatoma cells. Compound 6 arrests the cell cycle at G2/M and induces cell apoptosis in Huh7 cells. In addition, the generation of reactive oxygen species (ROS) was detected in Huh7 cells when treated with compound 6, and a ROS scavenger partly blocked the effects of compound 6-induced Huh7 cell death, suggesting that compound 6-induced apoptosis is associated with elevated levels of ROS in Huh7 cells.''',
        extractions=[
            lx.data.Extraction(
                extraction_class="Study type",
                extraction_text="In vitro study",
                attributes={"environment": "cell culture", "focus": "anticancer cytotoxicity"}
            ),
            lx.data.Extraction(
                extraction_class="Model System",
                extraction_text="HepG2, Huh7, SMMC7721 (HCC cell lines); QSG7701 (normal liver cells)",
                attributes={
                    "species": "human",
                    "cancer_cells": ["HepG2", "Huh7", "SMMC7721"],
                    "normal_cells": ["QSG7701"],
                    "organ": "liver"
                }
            ),
            lx.data.Extraction(
                extraction_class="Experimental Techniques",
                extraction_text="HPLC, NMR, X-ray diffraction, Cytotoxicity assay, Cell cycle assay, Apoptosis assay, ROS assay",
                attributes={
                    "structural_methods": ["HPLC", "NMR", "X-ray diffraction"],
                    "functional_methods": ["Cytotoxicity assay", "Cell cycle assay", "Apoptosis assay", "ROS assay"]
                }
            ),
            lx.data.Extraction(
                extraction_class="Toxicity and Side effects",
                extraction_text="Selective cytotoxicity reported (low effect on normal cells)",
                attributes={
                    "toxicity_on_cancer": "high",
                    "toxicity_on_normal": "low",
                    "selectivity": "yes"
                }
            ),
            lx.data.Extraction(
                extraction_class="Year",
                extraction_text="Not Mentioned",
                attributes={"reported": "no"}
            ),
            lx.data.Extraction(
                extraction_class="Extracted_Cancer_Type",
                extraction_text="hepatocellular carcinoma (liver cancer)",
                attributes={"reported": "no",
        "cell_line_based": "yes",
        "experimental_context": "in vitro",
        "selective_toxicity": "yes",
        "compound_tested": "compound 6"}
            ),
            
            lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Compound 6 (abiespirone F)",
    attributes={
        "reported": "yes",
        "cancer_mentioned": "yes",
        "cancer_type": "hepatoma"
    }
)

        ]
    ),
    
    #3rd 
    lx.data.ExampleData(
        text='''Cancer chemoprevention, the prevention of cancer by ingestion of chemical agents that reduce the risk of carcinogenesis, is one of the potent ways to reduce morbidity and mortality. We have been searching for cancer chemopreventive agents from the leaves and barks of coniferous trees that have been treated as waste in the forestry industry. We have previously reported the isolation of spiro-biflavonoids, named as abiesinols, and a neolignan from the MeOH extract of the bark of Abies sachalinensis. These compounds were tested for their inhibitory effects on the activation of ()-(E)-methyl-2-[(E)-hydroxyimino]-5-nitro-6-methoxyhex-3-enamide (NOR 1), a nitric oxide (NO) donor, as a primary screening test for anti-tumor initiators. All compounds tested exhibited potent inhibitory effects on NOR 1 activation. Furthermore, abiesinol A, bearing a spiro-biflavonoid skeleton, showed remarkable anti-tumor-initiating activity in the in vivo two-stage mouse skin carcinogenesis test using peroxynitrite (ONOO-) as the initiator and 12-O-tetradecanoylphorbol-13-acetate (TPA) as the promoter.''',
        extractions=[
            lx.data.Extraction(
                extraction_class="Study type",
                extraction_text="In vitro and In vivo study",
                attributes={
                    "in_vitro_focus": "chemical inhibition assay",
                    "in_vivo_focus": "carcinogenesis prevention",
                    "disease_area": "cancer chemoprevention"
                }
            ),
            lx.data.Extraction(
                extraction_class="Model System",
                extraction_text="In vitro model (NOR 1 activation assay), In vivo model (Mouse skin carcinogenesis (ONOO- + TPA))",
                attributes={
                    "in_vitro": {"assay": "NOR 1 activation inhibition", "target": "nitric oxide donor"},
                    "in_vivo": {"species": "mouse", "model": "two-stage skin carcinogenesis", "initiator": "ONOO-", "promoter": "TPA"}
                }
            ),
            lx.data.Extraction(
                extraction_class="Experimental Techniques",
                extraction_text="NOR 1 inhibition assay, In vivo mouse skin carcinogenesis test",
                attributes={
                    "in_vitro_methods": ["NOR 1 inhibition assay"],
                    "in_vivo_methods": ["two-stage skin carcinogenesis test"]
                }
            ),
            lx.data.Extraction(
                extraction_class="Toxicity and Side effects",
                extraction_text="None reported",
                attributes={"reported": "no", "safety_profile": "not mentioned"}
            ),
            lx.data.Extraction(
                extraction_class="Year",
                extraction_text="Not Mentioned",
                attributes={"reported": "no"}
            ),
                lx.data.Extraction(
                extraction_class="Extracted_Cancer_Type",
                extraction_text="skin cancer",
                attributes={"reported": "no"}
            ),
            lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Abiesinol A",
    attributes={
        "reported": "yes",
        "cancer_mentioned": "yes",
        "cancer_type": "skin carcinogenesis"
    }
)

        ]
    ),


#4th
    lx.data.ExampleData(
        text='''Cellular senescence, a state of irreversible growth arrest, occurs in all somatic cells and causes the cells to exhaust replicative capacity. Recently, cellular senescence has been emerging as one of the principal mechanisms of tumor suppression, which can be induced by low doses of therapeutic drugs in cancer cells. Acetyl-11-keto-boswellic acid (AKBA), an active ingredient isolated from the plant Boswellia serrata, has been identified to induce apoptosis in hepatocellular carcinoma (HCC) cells. In this study, we found that low concentrations of AKBA treatment triggered cell growth arrest at G0/G1 phase with features of premature cellular senescence phenotype in both HCC cell lines HepG2 and SMMC7721, as observed by enlarged and flattened morphology, significant increase in cells with senescence-associated beta-galactosidase staining, and decrease in cell proliferation and DNA synthesis. Furthermore, cellular senescence induced by AKBA occurred via activation of DNA damage response and impairment of DNA repair, as evidenced by strong induction of gamma-H2AX and p53, and downregulated expressions of multiple DNA repair associated genes. Induction of p53 by AKBA caused a significant increase in p21CIP1 , which had a critical involvement in the induction of cellular senescence. Additionally, in vivo study demonstrated that induction of senescence contributed to the anticancer efficacy of AKBA. Therefore, our findings suggested that induction of premature senescence by AKBA through DNA damage response accompanied by impairment of DNA repair genes defines a novel mechanism contributing to its growth suppression in HCC cells.''',
        extractions=[
            lx.data.Extraction(
                extraction_class="Study type",
                extraction_text="In vitro and In vivo study",
                attributes={
                    "in_vitro_focus": "Cellular senescence and growth arrest in HCC cell lines",
                    "in_vivo_focus": "Efficacy of AKBA in animal model",
                    "disease_area": "Hepatocellular carcinoma",
                    "compound_tested": "AKBA"
                }
            ),
            lx.data.Extraction(
                extraction_class="Model System",
                extraction_text="In vitro (HepG2, SMMC7721 cell lines), In vivo (Animal model)",
                attributes={
                    "in_vitro": {"cell_lines": ["HepG2", "SMMC7721"], "model": "HCC cell lines"},
                    "in_vivo": {"species": "not specified", "model": "AKBA treatment in animal"}
                }
            ),
            lx.data.Extraction(
                extraction_class="Experimental Techniques",
                extraction_text="Cell cycle analysis, Senescence-associated beta-gal staining, Proliferation and DNA synthesis assays, gamma-H2AX and p53 expression analysis",
                attributes={
                    "in_vitro_methods": ["Cell cycle analysis", "Senescence-associated beta-gal staining", "Proliferation assay", "DNA synthesis assay", "gamma-H2AX expression", "p53 expression"],
                    "in_vivo_methods": ["Observation of anticancer efficacy in animal model"]
                }
            ),
            lx.data.Extraction(
                extraction_class="Toxicity and Side effects",
                extraction_text="Growth arrest and senescence induction in cancer cells",
                attributes={
                    "observed_effects": "Growth arrest, senescence",
                    "severity": "not harmful to normal cells (not reported)"
                }
            ),
            lx.data.Extraction(
                extraction_class="Year",
                extraction_text=""

  ),
  lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="hepatocellular carcinoma (HCC)",
    attributes={"reported": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Acetyl-11-keto-boswellic acid (AKBA)",
    attributes={
        "reported": "yes",
        "cancer_mentioned": "yes",
        "cancer_type": "hepatocellular carcinoma"
    }
)

        ]
    ),
    
    
    
    #5th
    lx.data.ExampleData(
        text='''Extensive research during last 2 decades has revealed that most drugs discovered today, although costs billions of dollars for discovery, and yet they are highly ineffective in their clinical response. For instance, the European Medicines Agency has approved 68 anti-cancer drugs, and out of which 39 has reached the market level with no indication of increased survival nor betterment of quality of life. Even when drugs did improve survival rate compared to available treatment strategies, most of these were found to be clinically insignificant. This is a fundamental problem with modern drug discovery which is based on thinking that most chronic diseases are caused by alteration of a single gene and thus most therapies are single gene-targeted therapies. However, extensive research has revealed that most chronic diseases are caused by multiple gene products. Although most drugs designed by man are mono-targeted therapies, however, those designed by "mother nature" and have been used for thousands of years, are "multi-targeted" therapies. In this review, we examine two agents that have been around for thousands of years, namely "guggul" from Commiphora and Boswellia. Although we are all familiar with the search engine "google," this is another type of "guggul" that has been used for centuries and being explored for its various biological activities. The current review summarizes the traditional uses, chemistry, in vitro and in vivo biological activities, molecular targets, and clinical trials performed with these agents.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="Review",
            attributes={
                "focus": "Multi-targeted therapies from traditional compounds",
                "scope": "Literature review of past studies",
                "includes": ["In vitro", "In vivo", "Clinical trials"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="In vitro, In vivo",
            attributes={
                "systems_covered": ["Cell lines", "Animal models"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Literature review and synthesis",
            attributes={
                "method_type": "Systematic review / Literature synthesis",
                "sources": "Published papers, Clinical trials, Historical uses"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="None reported",
            attributes={
                "observed_effects": "None",
                "severity": "Not applicable (review)"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="Not Mentioned",
            attributes={"reported": False}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="",
    attributes={"reported": "no", "cancer_type_found": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Guggul from Commiphora and Boswellia",
    attributes={
        "reported": "yes",
        "multi_targeted": "yes",
        "traditional_use": "yes"
    }
)


    ]
),
#6th
    lx.data.ExampleData(
        text='''Aconitum alkaloids mainly contain highly toxic aconitine (AC), mesaconitine (MA), and hypaconitine (HA) and less toxic benzoylaconine (BAC), benzoylmesaconine (BMA), benzoylhypaconine (BHA), aconine, mesaconine, and hypaconine. The efflux transporters including P-glycoprotein (P-gp), breast cancer resistance protein (BCRP) and multidrug resistance-associated protein 2 (MRP2) can efflux toxicants to prevent poisoning. Our previous publication has proved that P-gp and BCRP contributed to the efflux of AC, MA and HA, which is demonstrated in the human colonic adenocarcinoma cell lines (Caco-2 cells), Mardin-Darby canine kidney cell lines transfected with MDR1 or BCRP (MDR1-MDCKII and BCRP-MDCKII cells). However, the role of MRP2 remains uncertain. The study was completed in the year 2022 ''',
       extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In vitro Study",
            attributes={
                "focus": "Efflux transport of toxic Aconitum alkaloids",
                "scope": "Cell-based assays",
                "includes": ["Caco-2 cells", "MDR1-MDCKII", "BCRP-MDCKII cells"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Caco-2 cells, MDR1-MDCKII, BCRP-MDCKII cells",
            attributes={
                "cell_types": ["Human colonic adenocarcinoma cells", "MDCK cells transfected with MDR1/BCRP"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="In vitro cell culture (Caco-2, MDR1-MDCKII, BCRP-MDCKII), Efflux transport assay",
            attributes={
                "assays": ["Efflux transport assay for AC, MA, HA"],
                "methods": ["Cell culture", "Functional transporter assay"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Aconitum alkaloids",
            attributes={
                "observed_effects": "Toxicity due to AC, MA, HA",
                "severity": "High for AC, MA, HA; Low for BAC, BMA, BHA"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2022",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="colonic adenocarcinoma",
    attributes={"reported": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Aconitum alkaloids including aconitine (AC), mesaconitine (MA), hypaconitine (HA), benzoylaconine (BAC), benzoylmesaconine (BMA), benzoylhypaconine (BHA), aconine, mesaconine, and hypaconine",
    attributes={
        "reported": "yes",
        "toxic": "yes",
        "study_year": "2022"
    }
)

    ]
),

#7th
        lx.data.ExampleData(
        text='''The chemical composition done in 2005, including the enantiomeric excess of the main terpenes, the antimicrobial and antiradical activities, as well as the cytotoxicity of Abies alba and A. koreana seed and cone essential oils were investigated. Additionally, their seed hydrolates were characterized. In the examined oils and hydrolates, a total of 174 compounds were identified, which comprised 95.6-99.9% of the volatiles. The essential oils were mainly composed of monoterpene hydrocarbons, whereas the composition of the hydrolates, differing from the seed oils of the corresponding fir species, consisted mainly of oxygenated derivatives of sesquiterpenes. The seed and cone essential oils of both firs exhibited DPPH-radical-scavenging properties and low antibacterial activity against the bacterial strains tested. Moreover, they evoked only low cytotoxicity towards normal fibroblasts and the two cancer cell lines MCF-7 and MDA-MBA-231. At concentrations up to 50ug/ml, all essential oils were safe in relation to normal fibroblasts. Although they induced cytotoxicity towards the cancer cells at concentrations slightly lower than those required for the inhibition of fibroblast proliferation, their influence on cancer cells was weak, with IC50 values similar to those observed towards normal fibroblasts. ''',
       extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In vitro Study",
            attributes={
                "focus": "Chemical composition and bioactivity of essential oils",
                "scope": "Cellular and bacterial assays",
                "includes": ["MCF-7", "MDA-MB-231", "normal fibroblasts", "bacterial strains"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="MCF-7, MDA-MB-231 (cancer cells), normal fibroblasts, bacterial strains",
            attributes={
                "cell_types": ["MCF-7", "MDA-MB-231", "normal fibroblasts"],
                "microbial": ["Bacterial strains tested"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Chemical composition analysis, DPPH assay, Antibacterial assay, Cytotoxicity assay",
            attributes={
                "assays": ["DPPH radical scavenging", "Antibacterial", "Cytotoxicity"],
                "methods": ["Chemical composition analysis"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Low cytotoxicity toward fibroblasts; weak cytotoxicity toward cancer cells",
            attributes={
                "severity": "Low to weak",
                "target": ["Fibroblasts", "Cancer cells"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2005",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="breast cancer",
    attributes={"reported": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Essential oils from Abies alba and Abies koreana seeds and cones",
    attributes={
        "reported": "yes",
        "cytotoxicity": "low",
        "cancer_cell_lines_tested": "MCF-7, MDA-MBA-231",
        "antimicrobial_activity": "low",
        "antioxidant_activity": "DPPH-radical-scavenging"
    }
)


    ]
),

    #8th
    
    
    
            lx.data.ExampleData(
        text='''Extracts of plants have been widely tested in 2005for possible anticarcinogenic properties. In the present study a traditional remedy, consisting of an aqueous extract of mixed parts of the tree Abies alba and its mistletoe Viscum album se abies was tested on benzo(alpha)pyrene(BaP)-induced tumors in Wistar rats and on the L-1210 malignant cell line. Two main groups of male Wistar rats subcutaneously injected by 10 mg of BaP, a dose inducing 100% carcinogenesis, a control group (C-G, 15 rats) and a treatment group(TR-G, 18 rats), were used for the study. Five animals bearing BaP-induced tumors were also tested (TR-1-G). Animals of the TR-G were orally administered with the aqueous extract at doses of 50 ml/kg b.w, from the day of BaP injection and of the TR-1-G, from the 120th day of injection, till death. L-1210 malignant cells in cultivation, were administered with a powder obtained by condensation and lyophilization of the extract, at various concentrations and cytotoxicity was measured by the microculture tetrazolium assay. Autopsy of the rats, revealed metastasis in the lungs of the animals of all groups and the tumors developed were histologically identified as leiomyosarcomas. The results indicated that the extract of the above plants possess anticarcinogenic effects, documented by: a) its antiproliferative effects on L-1210 cells (IC50 = 49.6 \u00b1 1.4 micrograms/ml), b) the significant prolongation of life and reduction of tumor growth rate of the animals of the TR-G in comparison to the C-G, c) the inhibition by 16.6% of tumor induction in the TR-G and d) the prolongation of life and the necrotic effects of the extract on the tumors of the animals in the TR-1-G. The antiproliferative effects of the Abies alba and Viscum album se abies extract may be due to the lectins and thionins contained in Viscum album, as well as to the monoterpenes contained in Abies alba. Soft tissue tumors sensitive to the extract, are widespread among human organs, even in larynx, and are usually resistant to chemotherapy.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In vivo and In vitro study",
            attributes={
                "focus": "Anticarcinogenic effects of plant extracts",
                "scope": "Animal and cell line experiments",
                "includes": ["Wistar rats", "L-1210 cell line"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Wistar rats (BaP-induced leiomyosarcoma); L-1210 cancer cell line",
            attributes={
                "animal_model": "Wistar rats",
                "cancer_cell_line": "L-1210",
                "induction": "BaP-induced tumors"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="In vivo carcinogenesis, Oral extract administration, Histology, MTT assay, Autopsy",
            attributes={
                "in_vivo_methods": ["Carcinogenesis", "Oral extract administration", "Autopsy"],
                "in_vitro_methods": ["MTT assay"],
                "analysis": ["Histology"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Cytotoxicity reported (IC50 = 49.6 \u00b1 1.4 ug/ml for L-1210 cells)",
            attributes={
                "severity": "Moderate",
                "target": ["L-1210 cells"],
                "metric": "IC50 = 49.6 \u00b1 1.4 ug/ml"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2005",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="leiomyosarcoma",
    attributes={"reported": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Aqueous extract of Abies alba and Viscum album se abies",
    attributes={
        "reported": "yes",
        "anticarcinogenic_effect": "yes",
        "tested_on": "Wistar rats (BaP-induced tumors), L-1210 malignant cell line",
        "mechanism": "antiproliferative effects, tumor growth inhibition, life prolongation",
        "active_components": "lectins and thionins (Viscum album), monoterpenes (Abies alba)"
    }
)


    ]
),
#9th
  
            lx.data.ExampleData(
        text='''Viscum album is a semi-parasitic plant used for over one hundred years in complementary cancer therapy. The main commercial drugs used in cancer patients treatment are derived from the aqueous V. album extracts, whose cytotoxic potential is mostly attributed to the aqueous soluble antitumoral metabolites. On the counterpart, ethanol solvents must be used to obtain V. album mother tinctures. This methodology permits better solubilization of phenolic compounds, among others, which present antitumoral bioactivity. Recently, the metabolomics approach revealed the influence of the host tree on the V. album subspecies differentiation. To increase the scientific information about the chemical differences related to the host trees and to clarify the seasonal influences, in this study, the metabolome of 50V. album mother tinctures from three subspecies (abietis, album, austriacum) and five host trees (Malus domestica, Quercus sp., Ulmus carpinifolia, Pinus sylvestris, Abies alba) was evaluated using summer and winter plant harvests. The in vitro cytotoxic activities were investigated in breast cancer cells (MDA-MB-231) and immortalized normal human keratinocytes (HaCaT). The summer V. album mother tinctures presented higher cytotoxic activity than winter ones. Among the summer samples, those prepared with V. album subsp. album were more cytotoxic than V. album subsp. abietis and subsp. V. album subsp. austriacum. The V. album harvested from Quercus petraea and Abies alba inhibited the key-glycolytic enzymes: hexokinase (HK), phosphofructokinase (PFK), pyruvate kinase (PK). This activity was related to a reduction in glucose uptake and lactate production, which were host-tree-time-dose-dependent. The untargeted metabolomic approach was able to discriminate the mother tinctures according to respective botanical classes and harvest season. A total of 188 metabolites were annotated under positive and negative modes. Fourteen compounds were responsible for the samples differentiation, and, to the best of our knowledge, eight were described in the Viscum album species for the first time. Our study shows the interruption of the Warburg effect as a novel antitumoral mechanism triggered by V. album mother tinctures, which is related to their metabolite profile. These results bring scientific evidence that encourages the use of V. album mother tinctures as a natural product for cancer therapy.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In vitro study",
            attributes={
                "focus": "Antitumoral activity of Viscum album mother tinctures",
                "scope": "Cell line experiments",
                "includes": ["MDA-MB-231", "HaCaT"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="MDA-MB-231 (cancer cells), HaCaT (normal keratinocytes)",
            attributes={
                "cancer_cell_line": "MDA-MB-231",
                "normal_cell_line": "HaCaT",
                "comparative_analysis": True
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Cytotoxicity assay, Enzyme inhibition assays (HK, PFK, PK), Metabolomics profiling, Glucose/lactate analysis",
            attributes={
                "in_vitro_methods": ["Cytotoxicity assay", "Enzyme inhibition assays", "Glucose/lactate analysis"],
                "omics_analysis": "Metabolomics profiling",
                "mechanism_study": "Warburg effect inhibition"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Cytotoxicity reported; selective activity; inhibition of glycolytic enzymes",
            attributes={
                "severity": "Selective cytotoxicity",
                "target": ["Cancer cells", "Glycolytic enzymes"],
                "metric": "Not quantified"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2005",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="breast cancer",
    attributes={"reported": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Viscum album mother tinctures",
    attributes={
        "reported": "yes",
        "anticancer_activity": "yes",
        "variability_factors": "subspecies, host tree, harvest season"
    }
)


    ]
),



#10th
      
    
            lx.data.ExampleData(
        text='''Objectives. Helicobacter pylori infection is common and can lead to precancerous gastric lesions. Standard antibiotic therapy has a failure rate of more than 25% from antibiotic resistance. The primary aim of this observational pilot study was to test the feasibility of a large-scale clinical trial of Conifer Green Needle Complex (CGNC) to treat precancerous gastric lesions. Secondary aims were to investigate H. pylori infection, stomach function, and histopathology of the gastric mucosa. Methods. A tablet form of CGNC (extracted from Pinus sylvestris and Picea abies (L) Karst) was prescribed to 26 patients with precancerous gastric lesions (two tablets, 100umg CGNC/tablet, three times per day for six months). Another 24 patients received no treatment. Results. Compared with control patients, CGNC-treated patients showed total or partial regression (using the quantitative Rome III diagnostic criteria) of dyspeptic symptoms (92.3%, p < 0.0001), eradication of H. pylori infection (57.1%, p < 0.03), a reduction in endoscopic signs of gastritis (92.3%, p < 0.001), an increase of pepsinogen-pepsin in the gastric juice (57.7%, p < 0.05), and total regression or reduction in the degree of intestinal metaplasia (46.2%, p < 0.05) and lymphoplasmacytic infiltration (53.8%, p < 0.05). Conclusions. This study justifies a randomised-controlled trial with CGNC in patients with atrophic gastritis.The Study was completed in the year 2015''',
         extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="Patient Study",
            attributes={
                "focus": "Clinical efficacy of CGNC on precancerous gastric lesions",
                "scope": "Pilot observational study",
                "patients": 50
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Human patients with precancerous gastric lesions",
            attributes={
                "species": "Homo sapiens",
                "condition": "Precancerous gastric lesions",
                "grouping": ["CGNC-treated (26)", "Control (24)"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Symptom scoring (Rome III), Endoscopy, Histopathology, Pepsinogen analysis, H. pylori testing",
            attributes={
                "clinical_assays": ["Symptom scoring", "Endoscopy", "Histopathology"],
                "biochemical_assays": ["Pepsinogen analysis", "H. pylori detection"],
                "quantitative_metrics": True
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="No adverse effects reported",
            attributes={
                "severity": "None observed",
                "monitoring": ["Patient-reported symptoms", "Clinical follow-up"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2015",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="gastric cancer (precancerous lesions)",
    attributes={"reported": "no"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Conifer Green Needle Complex (CGNC)",
    attributes={"reported": "yes"}
)


    ]
),
    
    #11th
            lx.data.ExampleData(
        text='''Introduction: This article critically examines the systematic reviews (SR) and meta-analysis (MA) of complementary therapies for cancer patients to appraise the evidence level, and offers suggestions for future research and practice in 2018. Methods: The Cochrane Library and MEDLINE were searched from their inception to January 2018, to identify SR and MA of complementary therapies available for cancer patients in 2018. Final selected SR and MA were methodologically evaluated for their quality by applying the Assessing the Methodological Quality of Systematic Reviews 2 (AMSTAR2) instrument. Data extraction and risk of quality assessments were performed by 2 independent reviewers. Results: A total of 104 studies were included in the analysis. The majority of the individual clinical trials included in the SR and MA were performed in China (48%) and the United States (26.9%). Breast cancer was the most studied cancer type (25%), and acupuncture was the most studied intervention (21%). Side effects of cancer such as pain, depression, and fatigue were effectively managed with complementary therapies. The methodologically problematic items included not listing the excluded studies and lack of protocol or protocol registration. Conclusions: With increasing interest in research, complementary therapies appear to be beneficial in reducing side effects and raising the quality of life of cancer patients. Complementary therapies have generally been studied for all cancers, with acupuncture being the most researched, regardless of the cancer type. Since AMSTAR2 is a stricter assessment tool than before, future studies need to consider the risk of methodological bias with caution and discuss appropriate overall quality assessment tools. ''',
        
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="Review Article",
            attributes={
                "focus": "Systematic reviews and meta-analyses of complementary therapies for cancer",
                "scope": "Methodological quality assessment using AMSTAR2",
                "studies_included": 104
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Human clinical trials (via SR/MA); Breast cancer most studied",
            attributes={
                "species": "Homo sapiens",
                "cancer_types": ["Breast cancer", "Various other cancers"],
                "geography": ["China", "USA", "Other countries"],
                "trial_type": "Clinical trials included in SR/MA"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="AMSTAR2, Cochrane/MEDLINE search, dual reviewer extraction",
            attributes={
                "methodological_assessment": "AMSTAR2",
                "literature_search": ["Cochrane Library", "MEDLINE"],
                "data_extraction": "Performed by 2 independent reviewers"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Pain, fatigue, depression",
            attributes={
                "severity": "Reported in patients",
                "management": "Effectively managed by complementary therapies"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2018",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="breast cancer",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Acupuncture",
    attributes={"reported": "yes"}
)

    ]
),



#12th

            lx.data.ExampleData(
        text='''Background/aim To assess the quantity and quality of systematic reviews of in vitro cancer studies. Materials and methods PubMed, MEDLINE, Embase, Web of Knowledge and PROSPERO databases were searched. Articles described as systematic reviews of in vitro studies, focused on or relevant to cancer and published in English were selected and appraised using an adapted version of AMSTAR 2 'critical domains'. Results From 4,021 records, 41 reviews described as systematic and cancer-related were identified in 2001. Publication dates indicate increasing frequency of systematic review conduct. Mean number of databases searched was three (range=1-8). Thirty-six reviews (88%) reported search methods, 35 (85%) specified inclusion criteria, 26 (63%) reported study selection methods, and 21 (51%) used reporting guidelines. Only 13 reviews (32%) involved formal quality assessment. Conclusion Detailed investigation of reviews of cancer-relevant in vitro studies indicates need for further development and use of robust search strategies, appropriate quality assessment tools, and researchers with relevant skills done in 2001''',
       extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="Review Article",
            attributes={
                "focus": "Systematic reviews of in vitro cancer studies",
                "studies_included": 41,
                "scope": "Quality assessment and reporting methods"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="In vitro cancer models (cell culture studies)",
            attributes={
                "species": "Human or animal cell lines",
                "model_type": "Cell culture (in vitro)",
                "disease_focus": "Cancer"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Systematic literature searching, quality assessment via AMSTAR 2",
            attributes={
                "literature_search": ["PubMed", "MEDLINE", "Embase", "Web of Knowledge", "PROSPERO"],
                "quality_assessment": "AMSTAR 2 adapted for in vitro studies",
                "methodology": "Systematic review and critical appraisal"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Not Applicable",
            attributes={"relevance": "In vitro review; no direct toxicity reported"}
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2001",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="cancer",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="No specific drug mentioned",
    attributes={"reported": "no"}
)


    ]
),


#13th 

            lx.data.ExampleData(
        text='''A recent research of cancer has indicated that the mutant of isocitrate dehydrogenase 1 and 2 (IDH1 and 2) genes will induce various cancers, including chondrosarcoma, cholangiocarcinomas, and acute myelogenous leukemia due to the effect of point mutations in the active-site arginine residues of isocitrate dehydrogenase (IDH), such as IDH1/R132, IDH2/R140, and IDH2/R172. As the inhibition for those tumor-associated mutant IDH proteins may induce differentiation of those cancer cells, these tumor-associated mutant IDH proteins can be treated as a drug target proteins for a differentiation therapy against cancers in year 2024. In this study, we aim to identify the potent TCM compounds from the TCM Database@Taiwan as lead compounds of IDH2 R140Q mutant inhibitor. Comparing to the IDH2 R140Q mutant protein inhibitor, AGI-6780, the top two TCM compounds, precatorine and abrine, have higher binding affinities with target protein in docking simulation. After MD simulation, the top two TCM compounds remain as the same docking poses under dynamic conditions. In addition, precatorine is extracted from Abrus precatorius L., which represents the cytotoxic and proapoptotic effects for breast cancer and several tumor lines. Hence, we propose the TCM compounds, precatorine and abrine, as potential candidates as lead compounds for further study in drug development process with the IDH2 R140Q mutant protein against cancer in 2024.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In silico study",
            attributes={
                "focus": "Drug discovery for mutant IDH2 R140Q protein",
                "approach": "Computational screening and simulations",
                "target_disease": "Cancer (chondrosarcoma, cholangiocarcinoma, AML)"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Mutant IDH2 R140Q protein (cancer-associated target)",
            attributes={
                "species": "Human IDH2 protein",
                "model_type": "Protein target (in silico)",
                "mutation": "R140Q"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Docking simulation, MD simulation, TCM compound screening",
            attributes={
                "simulations": ["Docking", "Molecular Dynamics (MD)"],
                "compound_source": "TCM Database@Taiwan",
                "comparison": "AGI-6780 reference inhibitor"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Known cytotoxic effects of precatorine on cancer cells",
            attributes={
                "compound": "Precatorine",
                "effect": "Cytotoxic and proapoptotic",
                "target_cells": "Breast cancer and tumor lines"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2024",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="chondrosarcoma, cholangiocarcinomas, acute myelogenous leukemia, breast cancer",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="precatorine, abrine, AGI-6780",
    attributes={"reported": "yes"}
)

    ]
),



#14th
    
            lx.data.ExampleData(
        text='''Cancer is characterized by the abnormal development of cells that divide in an uncontrolled manner and further take over the body and destroy the normal cells of the body. Although several therapies are practiced, the demand and need for new therapeutic agents are ever-increasing because of issues with the safety, efficacy and efficiency of old drugs. Several plant-based therapeutics are being used for treatment, either as conjugates with existing drugs or as standalone formulations. Withania somnifera (L.) Dunal is a highly studied medicinal plant which is known to possess immunomodulatory activity as well as anticancer properties. The pivotal role of KAT6A in major cellular pathways and its oncogenic nature make it an important target in cancer treatment. Based on the literature and curated datasets, twenty-six compounds from the root of W. somnifera and a standard inhibitor were docked with the target KAT6A using Autodock vina. The compounds and the inhibitor complexes were subjected to molecular dynamics simulation (50 ns) using Desmond to understand the stability and interactions. The top compounds (based on the docking score of less than -8.5 kcal/mol) were evaluated in comparison to the inhibitor. Based on interactions at ARG655, LEU686, GLN760, ARG660, LEU689 and LYS763 amino acids with the inhibitor WM-8014, the compounds from W. somnifera were evaluated. Withanolide D, Withasomniferol C, Withanolide E, 27-Hydroxywithanone, Withanolide G, Withasomniferol B and Sitoindoside IX showed high stability with the residues of interest. The cell viability of human breast cancer MCF-7 cells was evaluated by treating them with W. Somnifera root extract using an MTT assay, which showed inhibitory activity with an IC50 value of 45 ug/mL. The data from the study support the traditional practice of W. somnifera as an anticancer herb.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In silico study",
            attributes={
                "focus": "Drug discovery and validation using W. somnifera compounds",
                "approach": "Computational docking and MD simulations; experimental validation via MTT assay",
                "target_disease": "Breast cancer"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="MCF-7 cells; KAT6A target protein (in silico)",
            attributes={
                "species": "Human",
                "model_type": "Cell line and protein target",
                "protein_target": "KAT6A",
                "cell_line": "MCF-7"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Molecular docking, molecular dynamics, MTT assay",
            attributes={
                "simulations": ["Docking", "Molecular Dynamics (50 ns)"],
                "compound_source": "W. somnifera root compounds",
                "experimental_validation": "MTT assay on MCF-7 cells"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="IC50 = 45 ug/mL (W. somnifera extract on MCF-7 cells)",
            attributes={
                "compound": "W. somnifera root extract",
                "effect": "Cytotoxicity",
                "target_cells": "MCF-7 breast cancer cells",
                "IC50": "45 ug/mL"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="Not available",
            attributes={"reported": False}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="breast cancer",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Withanolide D, Withasomniferol C, Withanolide E, 27-Hydroxywithanone, Withanolide G, Withasomniferol B, Sitoindoside IX, W. somnifera root extract, WM-8014",
    attributes={"reported": "yes"}
)

    ]
),


#15th
      
            lx.data.ExampleData(
        text='''Breast cancer is one of the most severe problems, and it is the primary cause of cancer-related death in females worldwide. The adverse effects and therapeutic resistance development are among the most potent clinical issues for potent medications for breast cancer treatment. The eugenol molecules have a significant affinity for breast cancer receptors. The aim of the study has been on the eugenol compounds, which has potent actions on Era, PR, EGFR, CDK2, mTOR, ERBB2, c-Src, HSP90, and chemokines receptors inhibition. Initially, the drug-likeness property was examined to evaluate the anti-breast cancer activity by applying Lipinski's rule of five on 120 eugenol molecules. Further, structure-based virtual screening was performed via molecular docking, as protein-like interactions play a vital role in drug development. The 3D structure of the receptors has been acquired from the protein data bank and is docked with 87 3D PubChem and ZINC structures of eugenol compounds, and five FDA-approved anti-cancer drugs using AutoDock Vina. Then, the compounds were subjected to three replica molecular dynamic simulations run of 100 ns per system. The results were evaluated using root mean square deviation (RMSD), root mean square fluctuation (RMSF), and protein-ligand interactions to indicate protein-ligand complex stability. The results confirm that Eugenol cinnamaldehyde has the best docking score for breast cancer, followed by Aspirin eugenol ester and 4-Allyl-2-methoxyphenyl cinnamate. From the results obtained from in silico studies, we propose that the selected eugenols can be further investigated and evaluated for further lead optimization and drug development.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In silico study",
            attributes={
                "focus": "Drug discovery and lead optimization for breast cancer",
                "approach": "Computational screening of eugenol compounds",
                "target_disease": "Breast cancer"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Breast cancer-related receptors (Era, PR, EGFR, CDK2, mTOR, ERBB2, c-Src, HSP90, chemokines)",
            attributes={
                "species": "Human",
                "model_type": "Protein targets (in silico)",
                "receptors": ["Era", "PR", "EGFR", "CDK2", "mTOR", "ERBB2", "c-Src", "HSP90", "chemokine receptors"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Lipinski's Rule of Five, molecular docking, molecular dynamics, RMSD, RMSF",
            attributes={
                "computational_steps": ["Drug-likeness evaluation", "Docking", "Molecular dynamics simulations (100 ns, 3 replicas)"],
                "analysis_metrics": ["RMSD", "RMSF", "Protein-ligand interactions"],
                "compound_source": "Eugenol derivatives from PubChem/ZINC"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Not reported (in silico study)",
            attributes={
                "compound": "Eugenol derivatives",
                "effect": "Predicted activity on protein targets; no experimental cytotoxicity data"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="Not available",
            attributes={"reported": False}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="breast cancer",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Eugenol cinnamaldehyde, Aspirin eugenol ester, 4-Allyl-2-methoxyphenyl cinnamate",
    attributes={"reported": "yes"}
)

    ]
),

#16th
  
            lx.data.ExampleData(
        text='''Introduction: Primary dermal melanoma (PDM) is a recently described clinical entity accounting for less than 1% of all melanomas. Histologically, it is located in the dermis or subcutaneous tissue, and it shows no connections with the overlying epidermis. The differential diagnosis is principally made along with that of metastatic cutaneous melanoma. Case report: A 72-year-old Caucasian woman with a history of multiple cancers (metachronous bilateral breast cancer, meningioma, clear cell renal cell carcinoma, uterine fibromatosis and intestinal adenomatous polyposis), came to our attention with a nodular lesion on her back. After removal of the lesion, the histology report indicated malignant PDM or metastatic malignant melanoma. The clinical and instrumental evaluation of the patient did not reveal any other primary tumour, suggesting the primitive nature of the lesion. The absence of an epithelial component argued for a histological diagnosis of PDM. Subsequently, the patient underwent a wide surgical excision with sentinel node biopsy, which was positive for metastatic melanoma. Finally, the mutational status was studied in the main genes that regulate proliferation, apoptosis and cellular senescence. No pathogenetic mutations in CDKN2A, BRAF, NRAS, KRAS, cKIT, TP53 and PTEN genes were observed. This suggests that alternative pathways and low-frequency alterations may be involved. Conclusions: The differential diagnosis between PDM and isolated metastatic melanoma depends on the negativity of imaging studies and clinical findings for other primary lesions. This distinction is important because 5-year survival rates in such cases are higher than in metastatic cases (80-100 vs. 5-20%, respectively).
        Potential toxicities observed or anticipated in this patient include cardiotoxicity, nephrotoxicity, lymphedema, immune-related adverse effects such as colitis and pneumonitis, as well as hematologic suppression.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="Patient study",
            attributes={
                "focus": "Clinical case of primary dermal melanoma",
                "approach": "Observational case report",
                "target_disease": "Primary dermal melanoma"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Human clinical case (72-year-old female)",
            attributes={
                "species": "Human",
                "age": 72,
                "sex": "Female",
                "model_type": "Single patient clinical case"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Histology, imaging, sentinel lymph node biopsy, gene mutation analysis",
            attributes={
                "techniques": ["Histology", "Imaging studies", "Sentinel lymph node biopsy", "Gene mutation analysis (CDKN2A, BRAF, NRAS, KRAS, cKIT, TP53, PTEN)"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="cardiotoxicity, nephrotoxicity, lymphedema, colitis , pneumonitis, hematologic suppression",
            attributes={"note": "No experimental drug intervention; clinical observation only"}
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="Not available",
            attributes={"reported": False}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="clear cell renal cell carcinoma, primary dermal melanoma, metastatic malignant melanoma, breast cancer",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="wide surgical excision, sentinel node biopsy",
    attributes={"reported": "yes"}
)


    ]
),

#17th

            lx.data.ExampleData(
        text='''Background Surgery is the standard care for patients with early-stage lung cancer, and stereotactic body radiation therapy is an option for those who are medically inoperable or refuse surgery. Medical developments in diagnostic and therapeutic strategies would prolong prognosis of patients with cancer. The number of patients with multiple cancers has also increased. Duplex primary malignant neoplasms are the most common, and triple or more primary malignant neoplasms were extremely rare. This is the first case of sextuple primary malignant neoplasms with lung cancer. Case presentation We report a case of two courses of stereotactic body radiation therapy for an 88-year-old Japanese male patient with six primary cancers in five organs. Cancers were detected in the thyroid, prostate, esophagus, bladder, and lungs. He also had a history of angina pectoris and had undergone percutaneous coronary intervention. Although he was capable of undergoing surgery for lung cancers, he refused it because he had experienced many invasive treatments, such as surgeries and percutaneous coronary intervention. In January 2020, the first stereotactic body radiation therapy was performed for the adenocarcinoma in the right lung. In March 2022, the second stereotactic body radiation therapy was performed for the nodule of the left lung. Although he complained of mild dyspnea after the first stereotactic body radiation therapy, we did not use steroids because his peripheral oxygen saturation was within the normal range. He had pleural effusion, cardiac dilatation, and pericardial effusion 2 months after the second stereotactic body radiation therapy, which improved with the use of compression stockings. Conclusion A total of 43 and 17 months have passed since the first and second stereotactic body radiation therapy, respectively, there is no local recurrence and the patient can walk independently. We safely performed stereotactic body radiation therapy twice for our older patient with metachronous early-stage lung cancers. If another new tumor is detected, stereotactic body radiation therapy would be a good treatment option for the functional preservation of organs.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="Patient study",
            attributes={
                "focus": "Sextuple primary cancers with early-stage lung cancer",
                "approach": "Case report",
                "target_disease": "Multiple primary malignant neoplasms"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="88-year-old Japanese male with six primary cancers",
            attributes={
                "species": "Human",
                "age": 88,
                "sex": "Male",
                "model_type": "Single patient clinical case",
                "cancer_locations": ["Thyroid", "Prostate", "Esophagus", "Bladder", "Lungs"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Intervention : Two courses of stereotactic body radiation therapy (SBRT), Outcome: No recurrence, patient ambulatory and independent",
            attributes={
                "techniques": ["Stereotactic body radiation therapy (SBRT)", "Clinical monitoring", "Functional outcome assessment"],
                "treatment_dates": ["January 2020", "March 2022"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Mild dyspnea, pleural effusion, cardiac/pericardial effusions (managed)",
            attributes={
                "severity": "Mild to moderate",
                "management": "Supportive care (compression stockings, monitoring)",
                "timeframe": "Post-SBRT"
            }
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="2020 and 2022",
            attributes={"reported": True}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="lung cancer , thyroid cancer,prostate cancer,esophageal cancer,bladder cancer",
    attributes={"reported": "yes"}
),

lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="stereotactic body radiation therapy",
    attributes={"reported": "yes"}
)


    ]
),


#18th
  
            lx.data.ExampleData(
        text='''Raman spectroscopy has proved its capability as an objective, non-invasive tool for the detection of various melanoma and non-melanoma skin cancers (NMSC) in a number of studies. Most publications are based on a Raman microspectroscopic ex vivo approach. In this in vivo clinical evaluation, we apply Raman spectroscopy using a fibre-coupled probe that allows access to a multitude of affected body sites. The probe design is optimized for epithelial sensitivity, whereby a large part of the detected signal originates from within the epidermal layer's depth down to the basal membrane where early stages of skin cancer develop. Data analysis was performed on measurements of 104 subjects scheduled for excision of lesions suspected of being malignant melanoma (MM) (n = 36), basal cell carcinoma (BCC) (n = 39) and squamous cell carcinoma (SCC) (n = 29). NMSC were discriminated from normal skin with a balanced accuracy of 73% (BCC) and 85% (SCC) using partial least squares discriminant analysis (PLS-DA). Discriminating MM and pigmented nevi (PN) resulted in a balanced accuracy of 91%. These results lie within the range of comparable in vivo studies and the accuracies achieved by trained dermatologists using dermoscopy. Discrimination proved to be unsuccessful between cancerous lesions and suspicious lesions that had been histopathologically verified as benign by dermoscopy. ''',
       extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In vivo study",
            attributes={
                "focus": "Non-invasive skin cancer detection using Raman spectroscopy",
                "approach": "Clinical evaluation",
                "target_disease": ["Melanoma", "Basal Cell Carcinoma", "Squamous Cell Carcinoma"]
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="104 human subjects with suspected skin cancer lesions",
            attributes={
                "species": "Human",
                "sample_size": 104,
                "age": "Not specified",
                "sex": "Both",
                "condition": "Suspected melanoma or NMSC lesions"
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Raman spectroscopy with fiber-coupled probe, PLS-DA for analysis",
            attributes={
                "techniques": ["Raman spectroscopy (fiber-coupled probe)", "Partial Least Squares Discriminant Analysis (PLS-DA)"],
                "data_analysis": "Discrimination between NMSC and normal skin; MM vs PN classification"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Not Available",
            attributes={"safety": "Non-invasive, no reported adverse effects"}
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="Not Available",
            attributes={"reported": False}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="malignant melanoma,basal cell carcinoma,squamous cell carcinoma",
    attributes={"reported": "yes"}
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="Raman spectroscopy",
    attributes={"reported": "yes"}
)


    ]
),

#19th
  
       lx.data.ExampleData(
        text='''Prostatic carcinoma affects 1 in 11 men and targets bone with sclerotic metastases. The study of prostate carcinoma growth in bone has been hampered by the lack of suitable animal models. We have developed an in vivo model of prostate carcinoma growth in bone by inoculating three human prostate carcinoma cell lines (PC-3, DU-145, and LNCaP) into the tibia of congenitally athymic mice. Developing tumors were analyzed by radiographic, histologic, immunohistochemical, and in situ hybridization examination. Seven of the nine PC-3 inoculated mice and all (9/9) of the DU-145 inoculated mice developed tumors in the injected limb. In contrast, inoculation with LNCaP cells failed to produce tumors (0/9). Radiologically, the tumors had a mixed sclerotic/lytic appearance with extracortical extension. All the PC-3 tumors invaded the bone marrow cavity, cortical bone, and surrounding soft tissue. The DU-145 tumors were confined to the bone marrow cavity in 7/9 animals. CK18 and Ki67 localization identified the human tumor cells and their proliferative activity, respectively. The PC-3- and DU-145-induced tibial tumors expressed alpha(1)I procollagen and osteopontin mRNA, to varying degrees. All the tumors demonstrated an up-regulation of osteoclasts at the bone/tumor interface compared with the control limbs. Thus, this is a reliable and reproducible in vivo model of prostate carcinoma growth in bone enabling the study of the interactions that occur between prostate cancer cells and bone at an important part of the metastatic cascade, namely, growth and invasion at a distant site.''',
        extractions=[
        lx.data.Extraction(
            extraction_class="Study type",
            extraction_text="In vivo study",
            attributes={
                "focus": "Prostate carcinoma growth in bone",
                "approach": "Animal model of human prostate cancer metastasis",
                "target_disease": "Prostatic carcinoma with bone metastasis"
            }
        ),
        lx.data.Extraction(
            extraction_class="Model System",
            extraction_text="Congenitally athymic mice inoculated with human prostate carcinoma cell lines (PC-3, DU-145, LNCaP) into the tibia",
            attributes={
                "species": "Mouse (athymic)",
                "sample_size": "9 mice per cell line",
                "cell_lines": ["PC-3", "DU-145", "LNCaP"],
                "tissue_targeted": "Tibia",
                "tumor_development": {"PC-3": 7/9, "DU-145": 9/9, "LNCaP": 0/9}
            }
        ),
        lx.data.Extraction(
            extraction_class="Experimental Techniques",
            extraction_text="Radiographic examination,Histologic examination,Immunohistochemical examination (CK18 and Ki67 localization),In situ hybridization examination",
            attributes={
                "techniques": ["Radiography", "Histology", "Immunohistochemistry", "In situ hybridization"],
                "markers": ["CK18", "Ki67", "alpha(1)I procollagen", "osteopontin mRNA"],
                "endpoint_analysis": "Tumor growth, invasion, osteoclast activity"
            }
        ),
        lx.data.Extraction(
            extraction_class="Toxicity and Side effects",
            extraction_text="Not Available",
            attributes={"safety": "No reported toxicity or side effects"}
        ),
        lx.data.Extraction(
            extraction_class="Year",
            extraction_text="Not Available",
            attributes={"reported": False}
        ),
        lx.data.Extraction(
    extraction_class="Extracted_Cancer_Type",
    extraction_text="prostate carcinoma",
    attributes={"reported": "yes"}
    
),
lx.data.Extraction(
    extraction_class="Drug",
    extraction_text="PC-3, DU-145, LNCaP",
    attributes={"reported": "yes"}
)


    ]
)   
              
]


# Converting our Extracted file to jsonl 
output_file = "medical_ner_extraction_20857_21000.jsonl"    #Later in Step this jsonl will be converted to Excel

# -------- Normalization dictionaries -------- #
#Some Relevant Keywords 
STUDY_TYPE_MAP = {
    "In vitro": ["cell culture", "enzyme assay", "petri dish", "test tube", "lab assay", "laboratory study"],
    "In vivo": ["mouse", "rat", "animal", "mice", "zebrafish"],
    "In silico": ["simulation", "computational", "modeling", "in silico"],
    "Review": ["review", "systematic review", "meta-analysis"],
    "Patient study": ["clinical trial", "patient study", "human subjects","Human"]
}

def normalize_study_type(text):
    text_lower = text.lower()
    normalized = []
    for key, keywords in STUDY_TYPE_MAP.items():
        if any(k in text_lower for k in keywords):
            normalized.append(key)
    return ", ".join(normalized) if normalized else text

# You can create similar maps for Model System, Experimental Techniques, Toxicity if needed
def normalize_text(text, mapping=None):
    if not mapping:
        return text
    text_lower = text.lower()
    normalized = []
    for key, keywords in mapping.items():
        if any(k in text_lower for k in keywords):
            normalized.append(key)
    return ", ".join(normalized) if normalized else text

# -------- Process rows -------- #
with open(output_file, "a", encoding="utf-8") as f_out:
    for idx, row in tqdm(input_rows.iterrows(), total=len(input_rows), desc="Processing rows"):
        pmid = row["PMID"]
        abstract = row["Abstract"]

        print(f"\n Row {idx+1}/{len(input_rows)} | PMID: {pmid}")

        try:
            # First attempt: strict parsing
            result = lx.extract(
                text_or_documents=abstract,
                prompt_description=prompt_description,
                examples=examples,
                language_model_type=lx.inference.OllamaLanguageModel,
                model_id="gemma3:27b",
                model_url="http://localhost:11434",
                fence_output=True,
                use_schema_constraints=True,
				extraction_passes=3,    # Improves recall through multiple passes
				max_workers=50     # Parallel processing for speed
				
            )
            print(result)

        except Exception as e:
            print(f" Strict parsing failed for PMID {pmid}: {str(e)}")
            try:
                # Retry with relaxed parsing
                result = lx.extract(
                    text_or_documents=abstract,
                    prompt_description=prompt_description,
                    examples=examples,
                    language_model_type=lx.inference.OllamaLanguageModel,
                    model_id="gemma3:27b",
                    model_url="http://localhost:11434",
                    fence_output=False,
                    use_schema_constraints=False,
					extraction_passes=3,    # Improves recall through multiple passes
					max_workers=50         # Parallel processing for speed
					
					)
                print(result)
            except Exception as e2:
                print(f"? Retry failed for PMID {pmid}: {str(e2)}")
                result = lx.data.AnnotatedDocument(
                    document_id=str(pmid),
                    text=abstract,
                    extractions=[
                        lx.data.Extraction(extraction_class="Error", extraction_text=str(e2))
                    ]
                )

        # ---------- MERGE & NORMALIZE MULTIPLE VALUES ---------- #
        merged_entities = {}
        for entity in result.extractions:
            class_name = entity.extraction_class
            text = entity.extraction_text

            # Normalize study type
            if class_name.lower() == "Study type":
                text = normalize_study_type(text)
            # You can normalize Model System / Experimental Techniques / Toxicity similarly if you have maps
            # elif class_name.lower() == "model system":
            #     text = normalize_text(text, MODEL_SYSTEM_MAP)
            # elif class_name.lower() == "experimental techniques":
            #     text = normalize_text(text, EXP_TECH_MAP)
            # elif class_name.lower() == "toxicity":
            #     text = normalize_text(text, TOXICITY_MAP)

            if class_name not in merged_entities:
                merged_entities[class_name] = []
            if text not in merged_entities[class_name]:
                merged_entities[class_name].append(text)

        # Replace extractions with merged values
        result.extractions = [
            lx.data.Extraction(extraction_class=k, extraction_text=", ".join(v))
            for k, v in merged_entities.items()
        ]

        # Attach metadata
        result.document_id = str(pmid)
        result.text = abstract

        # Save incrementally
        f_out.write(json.dumps(doc_to_dict(result), ensure_ascii=False) + "\n")
        f_out.flush()

        print(f"Saved summary for PMID {pmid}")
        for entity in result.extractions:
            print(f"   {entity.extraction_class}: {entity.extraction_text}")


# -------- Save visualization -------- #
#html_content = lx.visualize(output_file)
#with open("medical_ner_visualization_10K_to_50K.html", "w") as f:
#    f.write(html_content)

print("\n Output saved incrementally in JSONL generated.")   #No visualization







#Step_2  - Convert jsonl file to Excel file

# Input and output file paths
jsonl_file = "medical_ner_extraction_20857_21000.jsonl"
csv_file = "article_20857_21000.xlsx"

# Read JSONL file
df = pd.read_json(jsonl_file, lines=True)

# Save to CSV
df.to_excel(csv_file, index=False)

print(f"Converted {jsonl_file} to {csv_file}")



import ast  
#Step_3

df = pd.read_excel("article_20857_21000.xlsx")     # Step 2 Output
df = df[["text", "document_id", "extractions"]]

# Function to parse and flatten extraction list/tuple into a dict
def expand_extractions(extractions_str):
    try:
        extraction_list = ast.literal_eval(extractions_str)
        return {item["extraction_class"]: item["extraction_text"] for item in extraction_list}
    except Exception as e:
        print(f"Parse error: {e} | Value: {extractions_str[:100]}...")
        return {}

# Apply function to create new columns
expanded_df = df["extractions"].apply(expand_extractions).apply(pd.Series)

# Merge with original DataFrame (drop old "extractions" column)
final_df = pd.concat([df.drop(columns=["extractions"]), expanded_df], axis=1)

# Reorder columns (add missing ones as empty if not present)
ordered_columns = [
    "text", "document_id", "Study type",
    "Model System", "Experimental Techniques",
    "Toxicity and Side effects",  "Year","Extracted_Cancer_Type","Drug"
]
final_df = final_df.reindex(columns=ordered_columns)

# Save new CSV
output_file = "Study_Type_Extracted_23807_complete_20857_21000.xlsx"
final_df.to_excel(output_file, index=False)

print(f"Flattened file saved as {output_file}")

print(f"Done! New CSV saved as {output_file}")
print("Input on 03/10/2025-2:17")


