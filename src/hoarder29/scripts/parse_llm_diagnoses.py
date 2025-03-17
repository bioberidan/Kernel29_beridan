import os
import json
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_models_working import Base, CasesBench, Models, Prompts, LlmDiagnosis

# Configuration
base_data_dir = "path/to/model_prompt_dirs"  # Base directory containing all model/prompt directories
db_url = "sqlite:///medical_diagnosis.db"  # Update with your database connection

# Create database connection
engine = create_engine(db_url)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()

def extract_model_prompt(dir_name):
    """Extract model and prompt from directory name."""
    parts = dir_name.split('_')
    if len(parts) >= 3 and 'diagnosis' in parts:
        idx = parts.index('diagnosis')
        model_name = '_'.join(parts[:idx])
        prompt_name = '_'.join(parts[idx+1:]) if idx+1 < len(parts) else "standard"
        return model_name, prompt_name
    return None, None

def get_or_create_model(model_name):
    """Get model ID from database or create if not exists."""
    model = session.query(Models).filter(Models.alias == model_name).first()
    if model:
        return model.id
    
    # Determine provider based on model name (simple heuristic)
    if "glm" in model_name.lower():
        provider = "Zhipu"
    elif "llama" in model_name.lower():
        provider = "Meta"
    elif "mistral" in model_name.lower():
        provider = "Mistral AI"
    elif "gemini" in model_name.lower():
        provider = "Google"
    elif "chatglm" in model_name.lower():
        provider = "Zhipu"
    else:
        provider = "Unknown"
    
    # Create new model
    new_model = Models(
        alias=model_name,
        name=model_name,
        provider=provider
    )
    session.add(new_model)
    session.commit()
    return new_model.id

def get_or_create_prompt(prompt_name):
    """Get prompt ID from database or create if not exists."""
    prompt = session.query(Prompts).filter(Prompts.alias == prompt_name).first()
    if prompt:
        return prompt.id
    
    # Create descriptions based on prompt type
    descriptions = {
        "standard": "Standard diagnosis prompt without special techniques",
        "few_shot": "Few-shot learning approach with examples",
        "dynamic_few_shot": "Dynamic few-shot learning with adaptive examples",
        "auto-cot": "Auto Chain-of-Thought prompting for reasoning",
        "medprompt": "Medical-specific prompt optimized for diagnosis"
    }
    
    description = descriptions.get(prompt_name, f"Custom prompt: {prompt_name}")
    
    # Create new prompt
    new_prompt = Prompts(
        alias=prompt_name,
        description=description
    )
    session.add(new_prompt)
    session.commit()
    return new_prompt.id

def process_directory(dir_name):
    """Process a single model-prompt directory."""
    # Extract model and prompt
    model_name, prompt_name = extract_model_prompt(dir_name)
    if not model_name or not prompt_name:
        print(f"  Could not extract model and prompt from {dir_name}, skipping")
        return 0
    
    # Get or create model and prompt
    model_id = get_or_create_model(model_name)
    prompt_id = get_or_create_prompt(prompt_name)
    
    print(f"  Using model: {model_name} (ID: {model_id}), prompt: {prompt_name} (ID: {prompt_id})")
    
    # Build directory path
    dir_path = os.path.join(base_data_dir, dir_name)
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(f"  Directory not found: {dir_path}, skipping")
        return 0
    
    # Process each JSON file
    files_processed = 0
    diagnoses_added = 0
    
    # Get all JSON files
    json_files = [f for f in os.listdir(dir_path) if f.endswith('.json') and f.startswith('patient_')]
    
    for filename in json_files:
        # Extract patient number
        patient_number = filename.split('.')[0].split('_')[-1]
        
        # Find corresponding case in database
        case_path = f"patient_{patient_number}"
        case = session.query(CasesBench).filter(
            CasesBench.source_file_path == case_path
        ).first()
        
        if not case:
            print(f"    Case not found for {filename}, skipping")
            continue
        
        # Read the prediction
        file_path = os.path.join(dir_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            predict_diagnosis = data.get("predict_diagnosis", "")
            if not predict_diagnosis:
                print(f"    No predict_diagnosis in {filename}, skipping")
                files_processed += 1
                continue
            
            # Add to database
            llm_diagnosis = LlmDiagnosis(
                cases_bench_id=case.id,
                model_id=model_id,
                prompt_id=prompt_id,
                diagnosis=predict_diagnosis,
                timestamp=datetime.datetime.now()
            )
            session.add(llm_diagnosis)
            session.commit()
            
            print(f"    Added diagnosis for {filename}")
            diagnoses_added += 1
            
        except Exception as e:
            print(f"    Error processing {filename}: {str(e)}")
        
        files_processed += 1
    
    print(f"  Completed directory {dir_name}. Processed {files_processed} files, added {diagnoses_added} diagnoses.")
    return diagnoses_added

def main():
    """Process all model-prompt directories."""
    # Get directories from dir_files.txt
    directories = []
    
    try:
        with open("dir_files.txt", "r") as f:
            for line in f:
                parts = line.strip().split()
                if parts and len(parts) > 0:
                    # Extract directory name (last part)
                    dir_name = parts[-1]
                    directories.append(dir_name)
    except Exception as e:
        print(f"Error reading dir_files.txt: {str(e)}")
        return
    
    print(f"Found {len(directories)} directories to process")
    
    # Process each directory
    total_diagnoses_added = 0
    
    for dir_name in directories:
        print(f"Processing directory: {dir_name}")
        diagnoses_added = process_directory(dir_name)
        total_diagnoses_added += diagnoses_added
    
    print(f"All directories processed. Total diagnoses added: {total_diagnoses_added}")

if __name__ == "__main__":
    main()
