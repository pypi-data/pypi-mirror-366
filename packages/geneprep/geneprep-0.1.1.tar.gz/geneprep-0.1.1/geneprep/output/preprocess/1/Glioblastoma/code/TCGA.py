# Path Configuration
from tools.preprocess import *

# Processing context
trait = "Glioblastoma"

# Input paths
tcga_root_dir = "/Users/apple/Desktop/GenePrep/TCGA"

# Output paths
out_data_file = "./output/preprocess/1/Glioblastoma/TCGA.csv"
out_gene_data_file = "./output/preprocess/1/Glioblastoma/gene_data/TCGA.csv"
out_clinical_data_file = "./output/preprocess/1/Glioblastoma/clinical_data/TCGA.csv"
json_path = "./output/preprocess/1/Glioblastoma/cohort_info.json"

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
candidate_age_cols = [
    'age_at_initial_pathologic_diagnosis',
    'first_diagnosis_age_asth_ecz_hay_fev_mold_dust',
    'first_diagnosis_age_of_animal_insect_allergy',
    'first_diagnosis_age_of_food_allergy'
]
candidate_gender_cols = ['gender']

# Extract candidate columns from clinical data
selected_columns = candidate_age_cols + candidate_gender_cols
extracted_data = clinical_df[selected_columns]

# Preview the extracted data
preview = preview_df(extracted_data)
print(preview)
import math

# Assuming age_candidates and gender_candidates are the dictionaries from the previous step
age_candidates = {
    'age_at_initial_pathologic_diagnosis': [44.0, 50.0, 59.0, 56.0, 40.0],
    'first_diagnosis_age_asth_ecz_hay_fev_mold_dust': [math.nan, math.nan, math.nan, math.nan, math.nan],
    'first_diagnosis_age_of_animal_insect_allergy': [math.nan, math.nan, math.nan, math.nan, math.nan],
    'first_diagnosis_age_of_food_allergy': [math.nan, math.nan, math.nan, math.nan, math.nan],
}

gender_candidates = {
    'gender': ['FEMALE', 'MALE', 'MALE', 'FEMALE', 'FEMALE']
}

# Function to check if a list has significant non-NaN values
def has_valid_values(values, threshold=0.5):
    valid_count = sum(1 for v in values if not (isinstance(v, float) and math.isnan(v)))
    return valid_count / len(values) >= threshold

# Select age column
age_col = None
for col, values in age_candidates.items():
    if has_valid_values(values):
        age_col = col
        break

# Select gender column
gender_col = None
for col, values in gender_candidates.items():
    if has_valid_values(values):
        gender_col = col
        break

# Print the selected columns
print(f"Selected age column: {age_col}")
print(f"Selected gender column: {gender_col}")
import math

# Step 1: Extract and standardize clinical features
selected_clinical_df = tcga_select_clinical_features(
    clinical_df=clinical_df,
    trait=trait,
    age_col=age_col,
    gender_col=gender_col
)

# Step 2: Normalize gene symbols in the gene expression data
normalized_gene_df = normalize_gene_symbols_in_index(genetic_df)
# Save the normalized gene expression data
normalized_gene_df.to_csv(out_gene_data_file)

# Step 3: Link the clinical and genetic data on sample IDs
# Transpose the gene expression dataframe to have samples as rows
normalized_gene_df = normalized_gene_df.transpose()
# Ensure that the sample IDs match between clinical and genetic data
linked_data = selected_clinical_df.join(normalized_gene_df, how='inner')

# Step 4: Handle missing values in the linked data
processed_data = handle_missing_values(linked_data, trait_col=trait)

# Step 5: Determine and remove severely biased features
trait_biased, processed_data = judge_and_remove_biased_features(processed_data, trait)

# Step 6: Conduct final quality validation and save cohort information
is_usable = validate_and_save_cohort_info(
    is_final=True,
    cohort=selected_dir_name,
    info_path=json_path,
    is_gene_available=True,
    is_trait_available=True,
    is_biased=trait_biased,
    df=processed_data,
    note='Normalized gene symbols and handled missing values.'
)

# Step 7: Save the linked data if it is usable
if is_usable:
    processed_data.to_csv(out_data_file)
    print(f"Processed data saved to {out_data_file}")
else:
    print("Linked data is not usable. It was not saved.")