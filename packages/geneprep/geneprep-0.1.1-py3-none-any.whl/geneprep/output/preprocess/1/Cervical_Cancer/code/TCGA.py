# Path Configuration
from tools.preprocess import *

# Processing context
trait = "Cervical_Cancer"

# Input paths
tcga_root_dir = "/Users/apple/Desktop/GenePrep/TCGA"

# Output paths
out_data_file = "./output/preprocess/1/Cervical_Cancer/TCGA.csv"
out_gene_data_file = "./output/preprocess/1/Cervical_Cancer/gene_data/TCGA.csv"
out_clinical_data_file = "./output/preprocess/1/Cervical_Cancer/clinical_data/TCGA.csv"
json_path = "./output/preprocess/1/Cervical_Cancer/cohort_info.json"

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
# Step 1: Identify candidate age and gender columns
candidate_age_cols = ['age_at_initial_pathologic_diagnosis', 'age_began_smoking_in_years']
candidate_gender_cols = ['gender']

# Step 2: Extract candidate columns and preview data
if candidate_age_cols or candidate_gender_cols:
    selected_cols = candidate_age_cols + candidate_gender_cols
    extracted_df = clinical_df[selected_cols]
    preview_data = preview_df(extracted_df)
    print(preview_data)
# Assuming the previous step provided the following dictionaries
age_candidates = {
    'age_at_initial_pathologic_diagnosis': [51.0, 31.0, 53.0, 48.0, 49.0],
    'age_began_smoking_in_years': [float('nan'), float('nan'), 22.0, float('nan'), float('nan')]
}

gender_candidates = {
    'gender': ['FEMALE', 'FEMALE', 'FEMALE', 'FEMALE', 'FEMALE']
}

# Function to select the best column based on the number of non-missing values
def select_best_column(candidates):
    if not candidates:
        return None
    # Select the column with the highest count of non-NaN values
    best_col = max(candidates, key=lambda k: sum(pd.notna(v) for v in candidates[k]))
    # Check if the best column has a reasonable amount of non-missing data
    non_missing = sum(pd.notna(v) for v in candidates[best_col])
    total = len(candidates[best_col])
    if non_missing / total < 0.5:
        return None
    return best_col

# Select the best age column
age_col = select_best_column(age_candidates)

# Select the best gender column
gender_col = select_best_column(gender_candidates)

# Print the selected columns
print(f"Selected age column: {age_col}")
print(f"Selected gender column: {gender_col}")
