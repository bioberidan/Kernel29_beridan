import os
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_models_working import Base, LlmDiagnosis, LlmDiagnosisRank, Models, Prompts
from parsers import parse_diagnosis_text

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
    print("listing directories")
    dirs = [d for d in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, d))]
    
    print(f"Found {len(dirs)} directories")
    return dirs

def process_diagnosis_into_ranks(session, verbose=False):
    """
    Process all diagnosis strings in LlmDiagnosis table and parse each line
    into a separate rank in the LlmDiagnosisRank table.
    
    Args:
        session: Database session
        verbose: Whether to print detailed parsing information
    """
    # Get all LLM diagnoses
    diagnoses = session.query(LlmDiagnosis).all()
    print(f"Found {len(diagnoses)} diagnoses to process")
    
    diagnoses_processed = 0
    ranks_added = 0
    
    for diagnosis in diagnoses:
        print(f"Processing diagnosis ID: {diagnosis.id}")
        
        # Check if diagnosis has text
        if not diagnosis.diagnosis:
            print(f"  Diagnosis ID {diagnosis.id} has empty text, skipping")
            diagnoses_processed += 1
            continue
        
        # Check if any ranks already exist for this diagnosis
        existing_ranks = session.query(LlmDiagnosisRank).filter(
            LlmDiagnosisRank.llm_diagnosis_id == diagnosis.id
        ).count()
        
        if existing_ranks > 0:
            print(f"  Diagnosis ID {diagnosis.id} already has {existing_ranks} ranks, skipping")
            diagnoses_processed += 1
            continue
        
        # Parse the diagnosis text
        parsed_diagnoses = parse_diagnosis_text(diagnosis.diagnosis, verbose=verbose)
        
        if not parsed_diagnoses:
            print(f"  No valid diagnoses found in text for diagnosis ID {diagnosis.id}, skipping")
            diagnoses_processed += 1
            continue
        
        # Add each parsed diagnosis as a rank entry
        for rank_position, diagnosis_text, reasoning in parsed_diagnoses:
            diagnosis_text = diagnosis_text[:254]
            rank_entry = LlmDiagnosisRank(
                cases_bench_id=diagnosis.cases_bench_id,
                llm_diagnosis_id=diagnosis.id,
                rank_position=rank_position,
                predicted_diagnosis=diagnosis_text,
                reasoning=reasoning
            )
            
            session.add(rank_entry)
            ranks_added += 1
        
        # Commit after processing each diagnosis
        session.commit()
        print(f"  Added {len(parsed_diagnoses)} ranks for diagnosis ID {diagnosis.id}")
        
        diagnoses_processed += 1
    
    print(f"Processing completed. Processed {diagnoses_processed} diagnoses, added {ranks_added} ranks.")

def process_by_model_prompt(session, model_id=None, prompt_id=None, limit=None, verbose=False):
    """
    Process diagnoses by specific model/prompt combinations.
    
    Args:
        session: Database session
        model_id: Optional model ID to filter by
        prompt_id: Optional prompt ID to filter by
        limit: Optional limit on number of diagnoses to process
        verbose: Whether to print detailed parsing information
    """
    # Build query
    query = session.query(LlmDiagnosis)
    
    # Apply filters if provided
    if model_id is not None:
        query = query.filter(LlmDiagnosis.model_id == model_id)
    if prompt_id is not None:
        query = query.filter(LlmDiagnosis.prompt_id == prompt_id)
    if limit is not None:
        query = query.limit(limit)
    
    # Execute query
    diagnoses = query.all()
    
    # Print filter information
    filter_info = []
    if model_id is not None:
        filter_info.append(f"model_id={model_id}")
    if prompt_id is not None:
        filter_info.append(f"prompt_id={prompt_id}")
    if limit is not None:
        filter_info.append(f"limit={limit}")
    
    filter_str = ", ".join(filter_info) if filter_info else "no filters"
    print(f"Found {len(diagnoses)} diagnoses to process ({filter_str})")
    
    # Process each diagnosis
    diagnoses_processed = 0
    ranks_added = 0
    
    for diagnosis in diagnoses:
        print(f"Processing diagnosis ID: {diagnosis.id}")
        
        # Check if diagnosis has text
        if not diagnosis.diagnosis:
            print(f"  Diagnosis ID {diagnosis.id} has empty text, skipping")
            diagnoses_processed += 1
            continue
        
        # Check if any ranks already exist for this diagnosis
        existing_ranks = session.query(LlmDiagnosisRank).filter(
            LlmDiagnosisRank.llm_diagnosis_id == diagnosis.id
        ).count()
        
        if existing_ranks > 0:
            print(f"  Diagnosis ID {diagnosis.id} already has {existing_ranks} ranks, skipping")
            diagnoses_processed += 1
            continue
        
        # Parse the diagnosis text
        parsed_diagnoses = parse_diagnosis_text(diagnosis.diagnosis, verbose=verbose)
        
        if not parsed_diagnoses:
            print(f"  No valid diagnoses found in text for diagnosis ID {diagnosis.id}, skipping")
            diagnoses_processed += 1
            continue
        
        # Add each parsed diagnosis as a rank entry
        for rank_position, diagnosis_text, reasoning in parsed_diagnoses:
            rank_entry = LlmDiagnosisRank(
                cases_bench_id=diagnosis.cases_bench_id,
                llm_diagnosis_id=diagnosis.id,
                rank_position=rank_position,
                predicted_diagnosis=diagnosis_text,
                reasoning=reasoning
            )
            
            session.add(rank_entry)
            ranks_added += 1
        
        # Commit after processing each diagnosis
        session.commit()
        print(f"  Added {len(parsed_diagnoses)} ranks for diagnosis ID {diagnosis.id}")
        
        diagnoses_processed += 1
    
    print(f"Processing completed. Processed {diagnoses_processed} diagnoses, added {ranks_added} ranks.")

def main(dirname=None, verbose=False):
    """
    Process all diagnoses into ranks.
    
    Args:
        dirname: Directory path (not used in this script but kept for consistency)
        verbose: Whether to print detailed parsing information
    """
    session = get_session()
    
    # Process all diagnoses
    process_diagnosis_into_ranks(session, verbose=verbose)
    
    # Alternatively, you could process by specific model/prompt:
    # model_name = "glm4"
    # prompt_name = "few_shot"
    # model_id = get_model_id(session, model_name)
    # prompt_id = get_prompt_id(session, prompt_name)
    # if model_id and prompt_id:
    #     process_by_model_prompt(session, model_id=model_id, prompt_id=prompt_id, verbose=verbose)

if __name__ == "__main__":
    dirname = "../../data/prompt_comparison_results/prompt_comparison_results"  # Not used but kept for consistency
    verbose = True  # Set to True to see detailed parsing information
    main(dirname, verbose=verbose)
# Processing completed. Processed 2250 diagnoses, added 20879 ranks.