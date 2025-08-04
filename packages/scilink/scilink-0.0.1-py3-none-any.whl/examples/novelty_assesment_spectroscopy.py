#!/usr/bin/env python3

import sys
sys.path.append("../../scilink")

import os
import gdown
import zipfile

import scilink

# Configure APIs
scilink.configure('google', 'AIzaSyAFcTLu1Eme-B0LvGXr3MhVmIcFMF9HW30')
scilink.configure('futurehouse', '+MZqvbTtjHVywIJ1GWJ8Zw.platformv01.eyJqdGkiOiI1MDZiZjI2OS0wNThmLTRjNDUtYmM1OC1iMDE2NjYyYTBjMGUiLCJzdWIiOiJuaUt3MDBwVk1nUmV4MDhocUg3RTBTRFVXQ3UyIiwiaWF0IjoxNzQ0NzM4OTA5fQ.9xtT+1ZfVaKWHQurUAV69viXqaTh7YSH9nmDZ0DjnQU')


# Download and extract data files
# print("Downloading data files...")
# gdown.download("https://drive.google.com/uc?id=1E_V7elBTOPisShXHpw-skHi4fZ_GLHbU", "data.zip", quiet=False)

# print("Extracting data files...")
# with zipfile.ZipFile("data.zip", 'r') as zip_ref:
#     zip_ref.extractall(".")

# # Clean up zip file
# os.remove("data.zip")


data_path="data/tepl.npy"
system_info="data/tepl.json"
# structure_image_path="haadf_plasmon2.npy"
# structure_image_system_info="haadf_plasmon2.json"

if __name__ == "__main__":
    
    workflow = scilink.workflows.ExperimentNoveltyAssessment(
        data_type='spectroscopy',
        enable_human_feedback=True,
        measurement_recommendations=True
    )

    result_unified = workflow.run_complete_workflow(
        data_path=data_path,
        system_info=system_info,
        #structure_image_path=structure_image_path,
        #structure_system_info=structure_image_system_info
    )

    print("\n--- Workflow Summary ---")
    print(workflow.get_summary(result_unified))


    # Step 2: Extract data for DFT recommendations
    analysis_text = result_unified["claims_generation"]["detailed_analysis"]
    novel_claims = result_unified["novelty_assessment"]["potentially_novel"]
    
    print(f"\n🧬 Proceeding to DFT recommendations...")
    print(f"   Analysis text length: {len(analysis_text)} characters")
    print(f"   Novel claims found: {len(novel_claims)}")
    
    # Step 3: Generate DFT recommendations based on spectroscopic findings
    dft_workflow = scilink.DFTRecommendationsWorkflow(
        analysis_model="gemini-2.5-pro-preview-06-05",
        output_dir="spectroscopy_dft_output"
    )
    
    dft_result = dft_workflow.run_from_data(
        analysis_text=analysis_text,
        novel_claims=novel_claims
    )
