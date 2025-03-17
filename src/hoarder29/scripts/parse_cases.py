import os
import json
import datetime
from db.utils.db_utils import get_session
from db.bench29.bench29_models import CasesBench
from db.db_queries import get_model_id, get_prompt_id
from libs.libs import get_directories, extract_model_prompt

def process_patient_file(session, file_path, model_id, prompt_id, dir_name):
    """Process a single patient JSON file and add to database."""

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        patient_data = json.load(f)
    
    # Extract patient number from filename (e.g., patient_1.json -> 1)
    patient = os.path.basename(file_path)
    print(patient)
    
    # Create source file path as directory/patient_N
    source_file_path = patient
    
    # Create or get cases_bench entry
    cases_bench = session.query(CasesBench).filter(
        CasesBench.source_file_path == source_file_path
    ).first()
    
    if not cases_bench:
        cases_bench = CasesBench(
            hospital="ramedis",
            meta_data=patient_data,
            processed_date=datetime.datetime.now(),
            source_type="jsonl",
            source_file_path=source_file_path
        )
        session.add(cases_bench)
        session.commit()
    
    return True

def process_directory(session, base_dir, dir_name):
    """Process a single model-prompt directory."""
    # Extract model and prompt
    model_name, prompt_name = extract_model_prompt(dir_name)
    if not model_name or not prompt_name:
        print(f"  Could not extract model and prompt from {dir_name}, skipping")
        return 0
    
    # Get model and prompt IDs
    model_id = get_model_id(session, model_name)
    prompt_id = get_prompt_id(session, prompt_name)
    
    if not model_id:
        print(f"  Model '{model_name}' not found in database, skipping")
        return 0
    
    if not prompt_id:
        print(f"  Prompt '{prompt_name}' not found in database, skipping")
        return 0
    
    print(f"  Using model: {model_name} (ID: {model_id}), prompt: {prompt_name} (ID: {prompt_id})")
    
    # Process all JSON files in this directory
    dir_path = os.path.join(base_dir, dir_name)
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(f"  Directory not found: {dir_path}, skipping")
        return 0
    
    files_processed = 0
    files_added = 0
    
    for filename in os.listdir(dir_path):
        if filename.endswith('.json') and filename.startswith('patient_'):
            file_path = os.path.join(dir_path, filename)
            print(f"  Processing {filename}...")
            files_processed += 1
            
            if process_patient_file(session, file_path, model_id, prompt_id, dir_name):
                files_added += 1
    
    print(f"  Completed directory {dir_name}. Processed {files_processed} files, added {files_added} new records.")
    return files_added

def process_all_directories(dirname):
    """Process all model/prompt directories."""
    session = get_session(schema="bench29")
    
    directories = get_directories(dirname, verbose=True)
    
    # Process each directory
    total_files_added = 0
    
    for dir_name in directories:
        print(f"Processing directory: {dir_name}")
        files_added = process_directory(session, dirname, dir_name)
        total_files_added += files_added
    
    print(f"All directories processed successfully! Added {total_files_added} new records.")
    session.close()

def main(dirname):
    process_all_directories(dirname)
    print("All directories processed successfully!")

if __name__ == "__main__":
    dirname = "../../data/prompt_comparison_results/prompt_comparison_results"  # Change this to your directory path
    main(dirname)