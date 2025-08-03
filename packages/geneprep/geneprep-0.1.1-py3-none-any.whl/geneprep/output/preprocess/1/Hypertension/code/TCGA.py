# Path Configuration
from tools.preprocess import *

# Processing context
trait = "Hypertension"

# Input paths
tcga_root_dir = "/Users/apple/Desktop/GenePrep/TCGA"

# Output paths
out_data_file = "./output/preprocess/1/Hypertension/TCGA.csv"
out_gene_data_file = "./output/preprocess/1/Hypertension/gene_data/TCGA.csv"
out_clinical_data_file = "./output/preprocess/1/Hypertension/clinical_data/TCGA.csv"
json_path = "./output/preprocess/1/Hypertension/cohort_info.json"

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

# Initialize variables to store the selected cohort information
selected_dir_name = None
clinical_df = None
genetic_df = None

# Iterate through each subdirectory to find a cohort with 'Hypertension' in clinical data
for d in subdirs:
    # Skip non-directory entries
    if not d.startswith("TCGA"):
        continue
    
    selected_dir_path = os.path.join(tcga_root_dir, d)
    
    # Get the paths to clinical and genetic data files using the provided function
    try:
        clinical_file_path, genetic_file_path = tcga_get_relevant_filepaths(selected_dir_path)
        
        # Verify that both file paths exist
        if not os.path.isfile(clinical_file_path):
            print(f"Clinical data file not found at: {clinical_file_path}. Skipping this cohort.")
            continue
        if not os.path.isfile(genetic_file_path):
            print(f"Genetic data file not found at: {genetic_file_path}. Skipping this cohort.")
            continue
        
        # Load the clinical data
        clinical_df_temp = pd.read_csv(
            clinical_file_path,
            index_col=0,
            sep='\t',
            low_memory=False
        )
        
        # Check if 'Hypertension' is a column in the clinical data (case-insensitive)
        hypertension_columns = [col for col in clinical_df_temp.columns if 'hypertension' in col.lower()]
        if hypertension_columns:
            selected_dir_name = d
            clinical_df = clinical_df_temp
            # Load the genetic data
            genetic_df = pd.read_csv(
                genetic_file_path,
                index_col=0,
                sep='\t',
                low_memory=False
            )
            print(f"Selected Cohort: {selected_dir_name}")
            print("Clinical Data Columns:")
            print(clinical_df.columns.tolist())
            break  # Cohort found, exit the loop
        else:
            print(f"'Hypertension' not found in clinical data of cohort: {d}. Continuing to next cohort.")
    
    except Exception as e:
        print(f"An error occurred while processing cohort '{d}': {e}. Skipping this cohort.")
        continue

# If no cohort with 'Hypertension' was found, handle gracefully
if selected_dir_name is None:
    print(f"No cohort contains the trait '{target_trait}' in their clinical data. Skipping this trait.")
# Step 1: Identify candidate age and gender columns
candidate_age_cols = ['age_at_initial_pathologic_diagnosis']
candidate_gender_cols = ['gender']

# Step 2: Extract and preview the candidate columns
selected_clinical_df = clinical_df[candidate_age_cols + candidate_gender_cols]
preview = preview_df(selected_clinical_df)
print(preview)
# Previous step's output
previous_output = {
    'age_at_initial_pathologic_diagnosis': [65, 63, 69, 68, 61],
    'gender': ['FEMALE', 'FEMALE', 'FEMALE', 'FEMALE', 'FEMALE']
}

# Define age_candidates and gender_candidates
age_candidates = {k: v for k, v in previous_output.items() if 'age' in k.lower()}
gender_candidates = {k: v for k, v in previous_output.items() if 'gender' in k.lower()}

# Function to select the best column based on non-None values
def select_best_column(candidates):
    for col, values in candidates.items():
        if values and all(v is not None for v in values):
            return col
    return None

# Select the most suitable age column
age_col = select_best_column(age_candidates) if age_candidates else None

# Select the most suitable gender column
gender_col = select_best_column(gender_candidates) if gender_candidates else None

# Print the selected columns
print(f"Selected age column: {age_col}")
print(f"Selected gender column: {gender_col}")
