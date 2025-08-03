# Path Configuration
from tools.preprocess import *

# Processing context
trait = "Acute_Myeloid_Leukemia"

# Input paths
tcga_root_dir = "/Users/apple/Desktop/GenePrep/TCGA"

# Output paths
out_data_file = "./output/preprocess/1/Acute_Myeloid_Leukemia/TCGA.csv"
out_gene_data_file = "./output/preprocess/1/Acute_Myeloid_Leukemia/gene_data/TCGA.csv"
out_clinical_data_file = "./output/preprocess/1/Acute_Myeloid_Leukemia/clinical_data/TCGA.csv"
json_path = "./output/preprocess/1/Acute_Myeloid_Leukemia/cohort_info.json"

import os
import pandas as pd

# List of subdirectories provided
subdirs = [
    'TCGA_Colon_and_Rectal_Cancer_(COADREAD)', 'TCGA_Ocular_melanomas_(UVM)',
    'TCGA_Lower_Grade_Glioma_(LGG)', 'CrawlData.ipynb',
    'TCGA_Mesothelioma_(MESO)', 'TCGA_Pancreatic_Cancer_(PAAD)',
    'TCGA_Bladder_Cancer_(BLCA)', '.DS_Store',
    'TCGA_Kidney_Clear_Cell_Carcinoma_(KIRC)', 'TCGA_Head_and_Neck_Cancer_(HNSC)',
    'TCGA_Lung_Cancer_(LUNG)', 'TCGA_Ovarian_Cancer_(OV)',
    'TCGA_Testicular_Cancer_(TGCT)', 'TCGA_lower_grade_glioma_and_glioblastoma_(GBMLGG)',
    'TCGA_Liver_Cancer_(LIHC)', 'TCGA_Uterine_Carcinosarcoma_(UCS)',
    'TCGA_Cervical_Cancer_(CESC)', 'TCGA_Colon_Cancer_(COAD)',
    'TCGA_Acute_Myeloid_Leukemia_(LAML)', 'TCGA_Kidney_Papillary_Cell_Carcinoma_(KIRP)',
    'TCGA_Endometrioid_Cancer_(UCEC)', 'TCGA_Rectal_Cancer_(READ)',
    'TCGA_Melanoma_(SKCM)', 'TCGA_Breast_Cancer_(BRCA)',
    'TCGA_Prostate_Cancer_(PRAD)', 'TCGA_Lung_Squamous_Cell_Carcinoma_(LUSC)',
    'TCGA_Stomach_Cancer_(STAD)', 'TCGA_Large_Bcell_Lymphoma_(DLBC)',
    'TCGA_Thyroid_Cancer_(THCA)', 'TCGA_Glioblastoma_(GBM)',
    'TCGA_Kidney_Chromophobe_(KICH)', 'TCGA_Sarcoma_(SARC)',
    'TCGA_Lung_Adenocarcinoma_(LUAD)', 'TCGA_Esophageal_Cancer_(ESCA)',
    'TCGA_Bile_Duct_Cancer_(CHOL)', 'TCGA_Thymoma_(THYM)',
    'TCGA_Pheochromocytoma_Paraganglioma_(PCPG)', 'TCGA_Adrenocortical_Cancer_(ACC)'
]

# Target trait
target_trait = "Acute_Myeloid_Leukemia"

# Find subdirectories that match the target trait
matching_dirs = [d for d in subdirs if target_trait in d]

if not matching_dirs:
    print(f"No suitable directory found for trait: {target_trait}. Skipping this trait.")
else:
    # Select the most specific match (assuming the first match is the most specific)
    selected_dir_name = matching_dirs[0]
    selected_dir_path = os.path.join(tcga_root_dir, selected_dir_name)
    
    # Get the paths to clinical and genetic data files
    try:
        clinical_file_path, genetic_file_path = tcga_get_relevant_filepaths(selected_dir_path)
        
        # Load the clinical data
        clinical_df = pd.read_csv(
            clinical_file_path,
            index_col=0,
            sep='\t',
            low_memory=False
        )
        
        # Load the genetic data
        genetic_df = pd.read_csv(
            genetic_file_path,
            index_col=0,
            sep='\t',
            low_memory=False
        )
        
        # Print the column names of the clinical data
        print("Clinical Data Columns:")
        print(clinical_df.columns.tolist())
        
    except Exception as e:
        print(f"An error occurred while loading data: {e}")
candidate_age_cols = ['age_at_initial_pathologic_diagnosis']
candidate_gender_cols = ['gender']

# Extract the candidate columns
selected_columns = candidate_age_cols + candidate_gender_cols
extracted_data = clinical_df[selected_columns]

# Preview the extracted data
preview = preview_df(extracted_data, n=5, max_items=200)
print(preview)
# Define the candidate dictionaries based on the previous step's output
age_candidates = {'age_at_initial_pathologic_diagnosis': [50, 61, 30, 77, 46]}
gender_candidates = {'gender': ['MALE', 'FEMALE', 'MALE', 'MALE', 'MALE']}

# Select the age column
age_col = list(age_candidates.keys())[0] if age_candidates else None

# Select the gender column
gender_col = list(gender_candidates.keys())[0] if gender_candidates else None

# Print the selected columns
print(f"Selected age column: {age_col}")
print(f"Selected gender column: {gender_col}")
# Step 4: Feature Engineering and Validation

# 1. Extract and standardize clinical features
selected_clinical_df = tcga_select_clinical_features(
    clinical_df=clinical_df,
    trait=trait,
    age_col=age_col,
    gender_col=gender_col
)

# 2. Normalize gene symbols in the genetic data
normalized_gene_df = normalize_gene_symbols_in_index(genetic_df)
normalized_gene_df.to_csv(out_gene_data_file)
print(f"Normalized gene expression data saved to {out_gene_data_file}")

# 3. Link clinical and genetic data on sample IDs
# Assuming that normalized_gene_df's columns correspond to sample IDs
# and selected_clinical_df's index corresponds to sample IDs
# We need to ensure that the sample IDs match and are aligned

# Transpose gene data to have samples as rows
normalized_gene_df_transposed = normalized_gene_df.T

# Merge clinical and genetic data on sample IDs (index)
linked_data = selected_clinical_df.join(normalized_gene_df_transposed, how='inner')
print("Clinical and genetic data linked successfully.")

# 4. Handle missing values
linked_data = handle_missing_values(linked_data, trait_col=trait)
print("Missing values handled successfully.")

# 5. Determine bias in trait and demographic features
is_biased, processed_data = judge_and_remove_biased_features(linked_data, trait=trait)

# 6. Final quality validation and save cohort information
is_usable = validate_and_save_cohort_info(
    is_final=True,
    cohort=trait,
    info_path=json_path,
    is_gene_available=True,  # Assuming gene data is available after normalization
    is_trait_available=True,  # Assuming trait data is available after extraction
    is_biased=is_biased,
    df=processed_data,
    note="Processed Acute Myeloid Leukemia cohort data."
)

# 7. Save linked data if usable
if is_usable:
    processed_data.to_csv(out_data_file)
    print(f"Processed linked data saved to {out_data_file}")
else:
    print("Linked data is not usable. Data not saved.")