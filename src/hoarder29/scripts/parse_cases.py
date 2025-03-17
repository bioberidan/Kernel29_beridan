import os
import json
import datetime
import re
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy_models_working import Base, CasesBench, Models, Prompts, LlmDiagnosis, LlmDiagnosisRank

# Configuration
def get_session():
    DATABASE_URL = "postgresql://dummy_user:dummy_password_42@localhost/bench29"

    engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(engine)

    print("Tables created successfully!")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


def extract_model_prompt(dirname):
    """Extract model and prompt from directory name."""
    pattern = r"(.+)_diagnosis(?:_(.+))?"
    match = re.match(pattern, dirname)
    if match:
        model_name = match.group(1)
        prompt_name = match.group(2) if match.group(2) else "standard"
        return model_name, prompt_name
    return None, None

def get_model_id(model_name):
    """Get model ID from database."""
    model = session.query(Models).filter(Models.alias == model_name).first()
    if model:
        return model.id
    return None

def get_files(dirname):
    print("listing directories")
    dirs = [d for d in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, d))]
    
    print(f"Found {len(dirs)} directories")
    return dirs

def get_prompt_id(prompt_name):
    """Get prompt ID from database."""
    prompt = session.query(Prompts).filter(Prompts.alias == prompt_name).first()
    if prompt:
        return prompt.id
    return None

def process_patient_file(file_path, model_id, prompt_id, dir_name):
    """Process a single patient JSON file and add to database."""

    with open(file_path, 'r', encoding='utf-8-sig') as f:
        patient_data = json.load(f)
    
    # Extract patient number from filename (e.g., patient_1.json -> 1)
    patient = os.path.basename(file_path)
    print (patient)
    
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

def get_files(dirname):
    print("listing directories")
    dirs = [d for d in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, d))]
    
    print(f"Found {len(dirs)} directories")
    return dirs

def process_all_directories(dirname):
    """Process all model/prompt directories."""
    directories = []
    directories = get_files(dirname)

    
    # Process each directory
    for dir_name in directories:
        print(f"Processing directory: {dir_name}")
        
        # Extract model and prompt
        print (dir_name)
        model_name, prompt_name = extract_model_prompt(dir_name)
        if not model_name or not prompt_name:
            print(f"  Could not extract model and prompt from {dir_name}, skipping")
            continue
        
        # Get model and prompt IDs
        model_id = get_model_id(model_name)
        prompt_id = get_prompt_id(prompt_name)
        
        if not model_id:
            print(f"  Model '{model_name}' not found in database, skipping")
            continue
        
        if not prompt_id:
            print(f"  Prompt '{prompt_name}' not found in database, skipping")
            continue
        
        print(f"  Using model: {model_name} (ID: {model_id}), prompt: {prompt_name} (ID: {prompt_id})")
        
        # Process all JSON files in this directory
        dir_path = os.path.join(dirname, dir_name)
        if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
            print(f"  Directory not found: {dir_path}, skipping")
            continue
        
        files_processed = 0
        files_added = 0
        
        for filename in os.listdir(dir_path):
            if filename.endswith('.json') and filename.startswith('patient_'):
                file_path = os.path.join(dir_path, filename)
                print(f"  Processing {filename}...")
                files_processed += 1
                
                if process_patient_file(file_path, model_id, prompt_id, dir_name):
                    files_added += 1
        
        print(f"  Completed directory {dir_name}. Processed {files_processed} files, added {files_added} new records.")

def main(dirname):
    process_all_directories(dirname)
    print("All directories processed successfully!")

if __name__ == "__main__":
    dirname = "../../data/prompt_comparison_results/prompt_comparison_results"  # Change this to your directory path
    session = get_session()


    main(dirname)


