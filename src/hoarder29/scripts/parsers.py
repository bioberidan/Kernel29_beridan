import re

def parse_diagnosis_text(diagnosis_text, verbose=False):
    """
    Parse diagnosis text into a list of (rank, diagnosis, reasoning) tuples.
    Handles various formats and extracts diagnosis names from complex text.
    
    Args:
        diagnosis_text: The raw diagnosis text from the LLM
        verbose: Whether to print detailed debug information
        
    Returns:
        List of tuples: [(rank_position, diagnosis_name, reasoning)]
    """
    if verbose:
        print("\n" + "="*80)
        print(f"STARTING PARSER: Received diagnosis text of length: {len(diagnosis_text) if diagnosis_text else 0}")
    
    if not diagnosis_text or not diagnosis_text.strip():
        if verbose:
            print("Empty diagnosis text, returning empty results")
        return []
    
    # Split the text into lines
    lines = diagnosis_text.strip().split('\n')
    if verbose:
        print(f"Split text into {len(lines)} lines")
    
    results = []
    current_rank = 1
    current_diagnosis = None
    current_reasoning = []
    
    if verbose:
        print("\nProcessing lines:")
    for i, line in enumerate(lines):
        line = line.strip()
        if verbose:
            print(f"\nLINE {i+1}: '{line}'")
        
        if not line:
            if verbose:
                print("  Empty line, skipping")
            continue
        
        # Check if this line starts a new diagnosis (has a number at the beginning)
        number_match = re.match(r'^\s*(\d+)[\.\)\-]?\s*(.+)', line)
        
        if number_match:
            if verbose:
                print(f"  ✓ Detected numbered diagnosis line")
                print(f"  Extracted rank: {number_match.group(1)}")
                print(f"  Extracted text: '{number_match.group(2)}'")
            
            # If we have a previous diagnosis, save it
            if current_diagnosis is not None:
                reasoning_text = "\n".join(current_reasoning) if current_reasoning else ""
                if verbose:
                    print(f"  Saving previous diagnosis: '{current_diagnosis}' with rank {current_rank}")
                    print(f"  With reasoning of length: {len(reasoning_text)}")
                results.append((current_rank, current_diagnosis, reasoning_text))
            
            # Start a new diagnosis
            rank_num = int(number_match.group(1))
            diagnosis_text = number_match.group(2).strip()
            
            # Handle the case with or without reasoning (with colon)
            colon_parts = diagnosis_text.split(':', 1)
            if len(colon_parts) > 1 and len(colon_parts[1].strip()) > 0:
                # There's a non-empty part after the colon, treat it as reasoning
                current_diagnosis = colon_parts[0].strip()
                current_reasoning = [colon_parts[1].strip()]
                if verbose:
                    print(f"  ✓ Found colon separator with content after it")
                    print(f"  Diagnosis: '{current_diagnosis}'")
                    print(f"  Initial reasoning: '{current_reasoning[0]}'")
            else:
                # No colon or empty part after colon, the whole text is the diagnosis
                current_diagnosis = diagnosis_text
                current_reasoning = []
                if verbose:
                    print(f"  No colon or empty content after colon")
                    print(f"  Full text as diagnosis: '{current_diagnosis}'")
                    print(f"  No initial reasoning")
            
            current_rank = rank_num
            if verbose:
                print(f"  Set current rank to: {current_rank}")
        else:
            if verbose:
                print(f"  Not a numbered diagnosis line")
            # This line is part of the reasoning for the current diagnosis
            if current_diagnosis is not None:
                if verbose:
                    print(f"  Adding as reasoning for current diagnosis: '{current_diagnosis}'")
                current_reasoning.append(line)
                if verbose:
                    print(f"  Current reasoning now has {len(current_reasoning)} lines")
            else:
                if verbose:
                    print(f"  No current diagnosis to associate with, treating as standalone text")
    
    # Don't forget to add the last diagnosis
    if current_diagnosis is not None:
        reasoning_text = "\n".join(current_reasoning) if current_reasoning else ""
        if verbose:
            print(f"\nSaving final diagnosis: '{current_diagnosis}' with rank {current_rank}")
            print(f"With reasoning of length: {len(reasoning_text)}")
        results.append((current_rank, current_diagnosis, reasoning_text))
    
    # In case there were no numbered items but just text
    if not results and diagnosis_text.strip():
        if verbose:
            print("\nNo numbered diagnoses found, attempting to parse as single diagnosis")
        
        # Try to parse it as a single diagnosis
        colon_parts = diagnosis_text.strip().split(':', 1)
        if len(colon_parts) > 1 and len(colon_parts[1].strip()) > 0:
            diagnosis = colon_parts[0].strip()
            reasoning = colon_parts[1].strip()
            if verbose:
                print(f"Found colon separator with content")
                print(f"Diagnosis: '{diagnosis}'")
                print(f"Reasoning: '{reasoning[:50]}...' (truncated)")
        else:
            diagnosis = diagnosis_text.strip()
            reasoning = ""
            if verbose:
                print(f"No colon separator or empty content after it")
                print(f"Using full text as diagnosis: '{diagnosis[:50]}...' (truncated)")
        
        results.append((1, diagnosis, reasoning))
        if verbose:
            print("Added as rank 1")
    
    if verbose:
        print("\nFINAL RESULTS:")
        for i, (rank, diag, reason) in enumerate(results):
            print(f"Result {i+1}:")
            print(f"  Rank: {rank}")
            print(f"  Diagnosis: '{diag}'")
            print(f"  Reasoning: {len(reason)} characters" + (f" (starts with '{reason[:50]}...')" if reason else ""))
        
        print(f"\nReturning {len(results)} parsed diagnoses")
        print("="*80 + "\n")
    
    return results
