def add_llm_diagnosis(session, cases_bench_id, model_id, prompt_id, diagnosis_text, timestamp=None):
    """
    Add a new LLM diagnosis to the database.
    
    Args:
        session: SQLAlchemy session
        cases_bench_id: ID of the CasesBench record
        model_id: ID of the Model used
        prompt_id: ID of the Prompt used
        diagnosis_text: Text of the diagnosis
        timestamp: Optional timestamp, defaults to current time
        
    Returns:
        The created LlmDiagnosis instance with ID set
    """
    from db.bench29.bench29_models import LlmDifferentialDiagnosis
    import datetime
    
    if timestamp is None:
        timestamp = datetime.datetime.now()
    
    llm_diagnosis = LlmDifferentialDiagnosis(
        cases_bench_id=cases_bench_id,
        model_id=model_id,
        prompt_id=prompt_id,
        diagnosis=diagnosis_text,
        timestamp=timestamp
    )
    
    session.add(llm_diagnosis)
    session.commit()
    
    return llm_diagnosis

def add_diagnosis_rank(session, cases_bench_id, llm_diagnosis_id, rank_position, predicted_diagnosis, reasoning=None, verbose=False):
    """
    Add a new rank entry for a diagnosis to the database.
    Handles None values from failed parsing.
    
    Args:
        session: SQLAlchemy session
        cases_bench_id: ID of the CasesBench record
        llm_diagnosis_id: ID of the LlmDiagnosis record
        rank_position: Position in ranking (1, 2, 3, etc.) or None
        predicted_diagnosis: Text of the predicted diagnosis or None
        reasoning: Optional reasoning text
        verbose: Whether to print debug information
        
    Returns:
        The created DifferentialDiagnosis2Rank instance with ID set
    """
    from db.bench29.bench29_models import DifferentialDiagnosis2Rank
    
    # Handle None values from failed parsing
    if rank_position is None:
        # Use a large value to indicate a failed parsing
        rank_position = 9999
        if verbose:
            print("  Using default rank 9999 for failed parsing")
    
    if predicted_diagnosis is None:
        predicted_diagnosis = "PARSING_FAILED"
        if verbose:
            print("  Using 'PARSING_FAILED' as diagnosis text for failed parsing")
    else:
        # Truncate diagnosis text if too long for the field
        if len(predicted_diagnosis) > 254:
            if verbose:
                print(f"  Truncating diagnosis text from {len(predicted_diagnosis)} to 254 characters")
            predicted_diagnosis = predicted_diagnosis[:254]
    
    # Create the rank entry
    rank_entry = DifferentialDiagnosis2Rank(
        cases_bench_id=cases_bench_id,
        differential_diagnosis_id=llm_diagnosis_id,
        rank_position=rank_position,
        predicted_diagnosis=predicted_diagnosis,
        reasoning=reasoning
    )
    
    session.add(rank_entry)
    session.commit()
    
    return rank_entry

def get_diagnosis_ranks(session, llm_diagnosis_id):
    """
    Get all rank entries for a specific diagnosis.
    
    Args:
        session: SQLAlchemy session
        llm_diagnosis_id: ID of the LlmDiagnosis record
        
    Returns:
        List of DifferentialDiagnosis2Rank instances
    """
    from db.bench29.bench29_models import DifferentialDiagnosis2Rank
    
    ranks = session.query(DifferentialDiagnosis2Rank).filter(
        DifferentialDiagnosis2Rank.differential_diagnosis_id == llm_diagnosis_id
    ).order_by(DifferentialDiagnosis2Rank.rank_position).all()
    
    return ranks