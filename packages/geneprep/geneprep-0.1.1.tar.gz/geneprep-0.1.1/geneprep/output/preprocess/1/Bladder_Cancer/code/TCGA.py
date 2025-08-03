# Path Configuration
from tools.preprocess import *

# Processing context
trait = "Bladder_Cancer"

# Input paths
tcga_root_dir = "/Users/apple/Desktop/GenePrep/TCGA"

# Output paths
out_data_file = "./output/preprocess/1/Bladder_Cancer/TCGA.csv"
out_gene_data_file = "./output/preprocess/1/Bladder_Cancer/gene_data/TCGA.csv"
out_clinical_data_file = "./output/preprocess/1/Bladder_Cancer/clinical_data/TCGA.csv"
json_path = "./output/preprocess/1/Bladder_Cancer/cohort_info.json"

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

# Target trait from the pre-configured context variable
target_trait = trait  # Use the pre-configured trait variable

# Find subdirectories that match the target trait (case-insensitive)
matching_dirs = [d for d in subdirs if target_trait.lower() in d.lower()]

if not matching_dirs:
    print(f"No suitable directory found for trait: {target_trait}. Skipping this trait.")
else:
    # If multiple directories match, select the one with the most specific match (e.g., exact match if possible)
    # Here, we prioritize directories that contain the target_trait exactly
    exact_matches = [d for d in matching_dirs if target_trait.lower() == d.lower().split('_(')[0].lower()]
    if exact_matches:
        selected_dir_name = exact_matches[0]
    else:
        # If no exact match, select the directory with the longest matching substring
        selected_dir_name = max(matching_dirs, key=lambda d: d.lower().count(target_trait.lower()))
    
    selected_dir_path = os.path.join(tcga_root_dir, selected_dir_name)
    
    # Get the paths to clinical and genetic data files
    try:
        clinical_file_path, genetic_file_path = tcga_get_relevant_filepaths(selected_dir_path)
        
        # Verify that both file paths exist
        if not os.path.isfile(clinical_file_path):
            raise FileNotFoundError(f"Clinical data file not found at: {clinical_file_path}")
        if not os.path.isfile(genetic_file_path):
            raise FileNotFoundError(f"Genetic data file not found at: {genetic_file_path}")
        
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
# Define candidate columns for age and gender
candidate_age_cols = ['age_at_initial_pathologic_diagnosis', 'age_began_smoking_in_years']
candidate_gender_cols = ['gender']

# Identify existing candidate columns in clinical data
existing_age_cols = [col for col in candidate_age_cols if col in clinical_df.columns]
existing_gender_cols = [col for col in candidate_gender_cols if col in clinical_df.columns]

# Extract candidate columns from clinical data
selected_columns = existing_age_cols + existing_gender_cols
extracted_data = clinical_df[selected_columns]

# Preview the extracted data
preview = preview_df(extracted_data, n=5, max_items=200)
print(preview)
import numpy as np

# Previous step's output
age_candidates = {
    'age_at_initial_pathologic_diagnosis': [63, 66, 69, 59, 83],
    'age_began_smoking_in_years': [20.0, 15.0, np.nan, np.nan, 30.0]
}

gender_candidates = {
    'gender': ['MALE', 'MALE', 'MALE', 'FEMALE', 'MALE']
}

def select_best_column(candidates):
    if not candidates:
        return None
    # Select the column with the least number of missing values
    best_col = None
    min_missing = float('inf')
    for col, values in candidates.items():
        missing_count = sum(pd.isna(values))
        if missing_count < min_missing:
            min_missing = missing_count
            best_col = col
    # Define a threshold for acceptable missing values (e.g., less than 20% missing)
    total = len(next(iter(candidates.values())))
    if min_missing / total < 0.2:
        return best_col
    return None

# Select age column
age_col = select_best_column(age_candidates)

# Select gender column
gender_col = select_best_column(gender_candidates)

# Print the chosen columns
print(f"Selected age column: {age_col}")
print(f"Selected gender column: {gender_col}")
import os
import pandas as pd
import json
import numpy as np

# Step 1: Extract and standardize clinical features
trait = "Bladder_Cancer"  # Pre-configured trait
selected_clinical_df = tcga_select_clinical_features(
    clinical_df=clinical_df,
    trait=trait,
    age_col=age_col,
    gender_col=gender_col
)

# Save the processed clinical data
os.makedirs(os.path.dirname(out_clinical_data_file), exist_ok=True)
selected_clinical_df.to_csv(out_clinical_data_file)
print(f"Processed clinical data saved to {out_clinical_data_file}")

# Step 2: Normalize gene symbols in gene expression data
normalized_genetic_df = normalize_gene_symbols_in_index(genetic_df)

# Save the normalized gene expression data
os.makedirs(os.path.dirname(out_gene_data_file), exist_ok=True)
normalized_genetic_df.to_csv(out_gene_data_file)
print(f"Normalized gene expression data saved to {out_gene_data_file}")

# Step 3: Link clinical and genetic data on sample IDs
# Transpose the genetic data to have samples as rows
transposed_genetic_df = normalized_genetic_df.transpose()

# Ensure that the sample IDs in clinical data match those in genetic data
common_samples = selected_clinical_df.index.intersection(transposed_genetic_df.index)
selected_clinical_df = selected_clinical_df.loc[common_samples]
transposed_genetic_df = transposed_genetic_df.loc[common_samples]

# Combine clinical and genetic data
linked_data = pd.concat([selected_clinical_df, transposed_genetic_df], axis=1)
print(f"Linked data has {linked_data.shape[0]} samples and {linked_data.shape[1]} features.")

# Step 4: Handle missing values
processed_data = handle_missing_values(linked_data, trait_col=trait)

# Step 5: Determine bias in trait and demographic features
trait_biased, processed_data = judge_and_remove_biased_features(processed_data, trait=trait)

# Step 6: Validate and save cohort information
is_final = True
cohort = "TCGA_Bladder_Cancer_(BLCA)"  # Assuming this is the cohort name
is_gene_available = True  # Since we have genetic data
is_trait_available = True  # Since we have trait data
note = "Normalization and missing value handling completed."

is_usable = validate_and_save_cohort_info(
    is_final=is_final,
    cohort=cohort,
    info_path=json_path,
    is_gene_available=is_gene_available,
    is_trait_available=is_trait_available,
    is_biased=trait_biased,
    df=processed_data,
    note=note
)

# Step 7: Save the linked data if usable
if is_usable:
    os.makedirs(os.path.dirname(out_data_file), exist_ok=True)
    processed_data.to_csv(out_data_file)
    print(f"Final linked data saved to {out_data_file}")
else:
    print("The linked data is not usable and was not saved.")