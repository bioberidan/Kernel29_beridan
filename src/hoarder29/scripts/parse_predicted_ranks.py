import os
import json
import re
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_models_working import Base, CasesBench, Models, Prompts, LlmDiagnosis,  DiagnosisSemanticRelationship, SeverityLevels
from sqlalchemy_models_working import LlmAnalysis
# Configuration
DEFAULT_RANK = 6
RANK_THRESHOLD = 5
DEFAULT_SEMANTIC_RELATIONSHIP = 'Exact Synonym'
DEFAULT_SEVERITY = 'rare'

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

def get_model_id(session, model_name):
    """Get model ID from database."""
    model = session.query(Models).filter(Models.alias == model_name).first()
    if model:
        return model.id
    return None

def get_prompt_id(session, prompt_name):
    """Get prompt ID from database."""
    prompt = session.query(Prompts).filter(Prompts.alias == prompt_name).first()
    if prompt:
        return prompt.id
    return None

def get_files(dirname):
    """Get all directories in the specified path."""
    print("Listing directories")
    dirs = [d for d in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, d))]
    print(f"Found {len(dirs)} directories")
    return dirs

def get_semantic_relationship_id(session, relationship_name=DEFAULT_SEMANTIC_RELATIONSHIP):
    """Get the ID for a semantic relationship by name."""
    relationship = session.query(DiagnosisSemanticRelationship).filter_by(
        semantic_relationship=relationship_name
    ).first()
    
    if relationship:
        return relationship.id
    
    # If not found, return 1 (assumed to be Exact Synonym)
    print(f"Warning: Semantic relationship '{relationship_name}' not found, using default ID 1")
    return 1

def get_severity_id(session, severity_name=DEFAULT_SEVERITY):
    """Get the ID for a severity level by name."""
    severity = session.query(SeverityLevels).filter_by(name=severity_name).first()
    
    if severity:
        return severity.id
    
    # If not found, return 5 (assumed to be rare)
    print(f"Warning: Severity level '{severity_name}' not found, using default ID 5")
    return 5

def parse_rank(rank_str, default_rank=DEFAULT_RANK, threshold=RANK_THRESHOLD):
    """
    Parse the rank value from string to integer
    If the rank is a string that can't be converted or exceeds threshold, return default_rank
    """
    try:
        # Try to convert to integer
        rank = int(rank_str)
        # If rank is greater than threshold, use default
        return default_rank if rank > threshold else rank
    except (ValueError, TypeError):
        # If it's not a valid integer (including Chinese characters), return default
        return default_rank

def process_directory(session, base_dir, dir_name, semantic_id, severity_id):
    """Process a single model-prompt directory."""
    # Extract model and prompt
    model_name, prompt_name = extract_model_prompt(dir_name)
    if not model_name or not prompt_name:
        print(f"  Could not extract model and prompt from {dir_name}, skipping")
        return 0
    
    # Get or create model and prompt
    model_id = get_model_id(session, model_name)
    prompt_id = get_prompt_id(session, prompt_name)
    
    if not model_id or not prompt_id:
        print(f"  Model {model_name} or prompt {prompt_name} not found in database, skipping")
        return 0
        
    print(f"  Using model: {model_name} (ID: {model_id}), prompt: {prompt_name} (ID: {prompt_id})")
    
    # Build directory path
    dir_path = os.path.join(base_dir, dir_name)
    if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
        print(f"  Directory not found: {dir_path}, skipping")
        return 0
    
    # Process each JSON file
    files_processed = 0
    ranks_added = 0
    
    # Get all JSON files
    json_files = [f for f in os.listdir(dir_path) if f.endswith('.json') and f.startswith('patient_')]
    
    for filename in json_files:
        print(filename)
        
        # Find corresponding case in database
        case = session.query(CasesBench).filter(
            CasesBench.source_file_path == filename
        ).first()
        
        if not case:
            print(f"    Case not found for {filename}, skipping")
            continue
            
        print(f"Processing {filename}")
        
        # Read the prediction
        file_path = os.path.join(dir_path, filename)
        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)
        except Exception as e:
            print(f"    Error processing {filename}: {str(e)}")
            continue
        
        # Get predict_rank from JSON
        predict_rank_str = data.get("predict_rank", str(DEFAULT_RANK))
        predicted_rank = parse_rank(predict_rank_str)
        print(predict_rank_str,predicted_rank)
        # Find the corresponding LlmDiagnosis record
        llm_diagnosis = session.query(LlmDiagnosis).filter_by(
            cases_bench_id=case.id,
            model_id=model_id,
            prompt_id=prompt_id
        ).first()
        
        if not llm_diagnosis:
            print(f"    No LlmDiagnosis found for {filename}, model_id {model_id}, prompt_id {prompt_id}, skipping")
            continue
        
        # Check if analysis already exists for this diagnosis
        existing_analysis = session.query(LlmAnalysis).filter_by(
            llm_diagnosis_id=llm_diagnosis.id
        ).first()
        
        if existing_analysis:
            # Skip if analysis already exists
            print(f"    Analysis already exists for {filename}, skipping")
            files_processed += 1
            continue
            
        # Create a new record
        llm_analysis = LlmAnalysis(
            cases_bench_id=case.id,
            llm_diagnosis_id=llm_diagnosis.id,
            predicted_rank=predicted_rank,
            diagnosis_semantic_relationship_id=semantic_id,
            severity_levels_id=severity_id
        )
        session.add(llm_analysis)
        session.commit()
        print(f"    Added rank for {filename}: {predicted_rank}")
        ranks_added += 1
        
        files_processed += 1
    
    print(f"  Completed directory {dir_name}. Processed {files_processed} files, added/updated {ranks_added} ranks.")
    return ranks_added

def main(dirname):
    """Process all model-prompt directories."""
    session = get_session()
    
    # Get semantic relationship and severity IDs for default values
    semantic_id = get_semantic_relationship_id(session)
    severity_id = get_severity_id(session)
    
    # Get all directories
    directories = get_files(dirname)
    
    # Process each directory
    total_ranks_added = 0
    
    for dir_name in directories:
        print(f"Processing directory: {dir_name}")
        ranks_added = process_directory(session, dirname, dir_name, semantic_id, severity_id)
        total_ranks_added += ranks_added
    
    print(f"All directories processed. Total ranks added/updated: {total_ranks_added}")

if __name__ == "__main__":
    dirname = "../../data/prompt_comparison_results/prompt_comparison_results"  # Change this to your directory path
    main(dirname)
