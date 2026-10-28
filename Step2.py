#!/usr/bin/env python
# coding: utf-8

import pandas as pd
import spacy

# Load the biomedical model
nlp = spacy.load("en_ner_bc5cdr_md")

# Load CSV
input_file_path = "Step1_Output_2.xlsx"
df = pd.read_excel(input_file_path)

df.columns = df.columns.str.strip()

print("✅ Input file loaded")
print("Total rows:", len(df))


 
 
 
 
     
# ---------------------------
# Cancer Keyword List (Your Provided List)
# ---------------------------
cancer_keywords = [
"Acute Lymphoblastic Leukemia","Acute Myeloid Leukemia","Adrenocortical Carcinoma",
"AIDS-Related Cancers","Anal Cancer","Appendix Cancer","Astrocytomas",
"Atypical Teratoid/Rhabdoid Tumor","Basal Cell Carcinoma of the Skin","Bile Duct Cancer",
"Bladder Cancer","Bone Cancer","Brain Tumors","Breast Cancer","Burkitt Lymphoma",
"Cervical Cancer","Cholangiocarcinoma","Chordoma","Chronic Lymphocytic Leukemia",
"Chronic Myelogenous Leukemia","Colorectal Cancer","Cutaneous T-Cell Lymphoma",
"Diffuse Intrinsic Pontine Glioma","Ductal Carcinoma In Situ (DCIS)",
"Endometrial Cancer (Uterine Cancer)","Ependymoma","Esophageal Cancer",
"Ewing Sarcoma","Eye Cancer","Fallopian Tube Cancer","Gallbladder Cancer",
"Gastric Cancer","Gastrointestinal Stromal Tumors","Germ Cell Tumor",
"Hairy Cell Leukemia","Head and Neck Cancer","Hepatocellular Cancer",
"Hodgkin Lymphoma","Intraocular Melanoma","Kaposi Sarcoma","Kidney Cancer",
"Laryngeal Cancer","Leukemia","Liver Cancer","Lung Cancer","Lymphoma",
"Medulloblastoma","Melanoma","Merkel Cell Carcinoma","Skin Cancer",
"Mesothelioma","Metastatic Cancer","Mouth Cancer","Multiple Myeloma",
"Myelodysplastic Syndromes","Nasopharyngeal Cancer","Neuroblastoma",
"Neuroendocrine Tumors","Non-Hodgkin Lymphoma","Non-Small Cell Lung Cancer",
"Oropharyngeal Cancer","Osteosarcoma","Ovarian Cancer","Pancreatic Cancer",
"Parathyroid Cancer","Penile Cancer","Pheochromocytoma","Pituitary Tumor",
"Prostate Cancer","Rectal Cancer","Renal Cell Cancer","Retinoblastoma",
"Rhabdomyosarcoma","Salivary Gland Cancer","Sarcoma","Sezary Syndrome",
"Small Cell Lung Cancer","Small Intestine Cancer","Soft Tissue Sarcoma",
"Squamous Cell Carcinoma of the Skin","Stomach Cancer","Testicular Cancer",
"Throat Cancer","Thymoma","Thyroid Cancer","Tracheobronchial Tumors",
"Transitional Cell Cancer","Ureter Cancer","Urethral Cancer",
"Uterine Cancer","Vaginal Cancer","Vulvar Cancer","Wilms Tumor","blastoma"
]

# Lowercase version for matching
cancer_keywords_lower = [kw.lower() for kw in cancer_keywords]

# ---------------------------
# Process each row
# ---------------------------
results = []

for idx, row in df.iterrows():
    title = str(row.get("Title", ""))
    abstract = str(row.get("Abstract", ""))
    text_combined = title + " " + abstract

    # Run NER to detect diseases
    doc = nlp(text_combined)
    detected_diseases = [ent.text for ent in doc.ents if ent.label_ == "DISEASE"]

    matched_cancer = []

    # Map detected disease → official keyword
    for disease in detected_diseases:
        disease_lower = disease.lower()

        for keyword, keyword_lower in zip(cancer_keywords, cancer_keywords_lower):
            if keyword_lower in disease_lower:
                matched_cancer.append(keyword)
                break

    # UNIQUE + SORTED
    matched_cancer = sorted(set(matched_cancer), key=lambda x: x.lower())

    # Default output
    cancer_output = ", ".join(matched_cancer) if matched_cancer else "NA"

    # ----------------------------------------------------
    # NEW CONDITION:
    # If no specific cancer detected AND the text contains "cancer",
    # then output "Cancer" instead of NA
    # ----------------------------------------------------
    if cancer_output == "NA":
        if "cancer" in text_combined.lower():
            cancer_output = "Cancer"

    # Save results
    result_row = row.to_dict()
    result_row["Cancer_Types"] = cancer_output
    results.append(result_row)

# ---------------------------
# Save Output File
# ---------------------------
results_df = pd.DataFrame(results)
results_df.to_excel("Newly_Cancer_Type_Extracted20251121.xlsx",index=False)

print(" Extraction Complete!")
print("Output file saved as: Newly_Cancer_Type_Extracted.xlsx")

if "Cancer_Types" in results_df:
    print(results_df[["Title", "Cancer_Types"]].head())
