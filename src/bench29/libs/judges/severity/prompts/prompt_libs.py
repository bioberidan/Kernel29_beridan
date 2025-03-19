


def format_severity_prompt(
    differential_diagnosis: str,
    case_id: int,
    template: Optional[str] = None,
    verbose: bool = False
) -> str:
    """
    Format a severity prompt with the given differential diagnosis.
    
    Args:
        differential_diagnosis: The differential diagnosis text
        case_id: ID of the clinical case
        template: Optional template to use (defaults to standard template)
        verbose: Whether to print status information
        
    Returns:
        Formatted prompt text
    """
    if verbose:
        print(f"Formatting severity prompt for case {case_id}")
        
    if not template:
        template = load_severity_prompt_template(verbose=verbose)
        
    # Format the template with the differential diagnosis and case ID
    prompt = template.format(
        differential_diagnosis=differential_diagnosis,
        case_id=case_id
    )

    if verbose:
        print(f"Created prompt of length {len(prompt)}")
        
    return prompt

    
def load_severity_prompt_template(prompt_id: Optional[int] = None, verbose: bool = False) -> str:
    """
    Load a severity prompt template from the database or use default.
    
    Args:
        prompt_id: Optional ID of a specific prompt to use
        verbose: Whether to print status information
        
    Returns:
        The prompt template text
    """
    if verbose:
        print(f"Loading severity prompt template (ID: {prompt_id if prompt_id else 'default'})")
        
    if prompt_id:
        try:
            from db.utils.db_utils import get_session
            from db.prompts.prompts_models import Prompt
            
            session = get_session()
            prompt = session.query(Prompt).filter(Prompt.id == prompt_id).first()
            session.close()
            
            if prompt and prompt.content:
                if verbose:
                    print(f"Loaded prompt template with ID {prompt_id}")
                return prompt.content
        except Exception as e:
            if verbose:
                print(f"Error loading prompt template from database: {str(e)}")
    
    # Default severity prompt template
    default_template = """You are a medical expert evaluating the severity of diseases in a differential diagnosis. 
Please analyze the following differential diagnosis and evaluate the severity of each proposed disease.

Differential Diagnosis:
{differential_diagnosis}

For each disease in the differential diagnosis, evaluate its severity based on the following criteria:
1. Mild: The disease generally has minor symptoms that do not significantly affect daily activities.
2. Moderate: The disease has noticeable symptoms requiring medical intervention but is not life-threatening.
3. Severe: The disease has serious symptoms that significantly impact health and may require hospitalization.
4. Critical: The disease is life-threatening and requires immediate medical intervention.

For each disease, consider its typical presentation, potential complications, and impact on the patient's quality of life.

Please structure your response as a JSON object with the following format:
```json
{
  "case_id": {case_id},
  "severity_evaluations": [
    {
      "disease": "Disease name",
      "rank": 1,
      "severity": "mild|moderate|severe|critical",
      "reasoning": "Brief explanation for this severity assessment"
    },
    {
      "disease": "Another disease",
      "rank": 2,
      "severity": "mild|moderate|severe|critical",
      "reasoning": "Brief explanation for this severity assessment"
    }
  ],
  "overall_assessment": "Brief summary of the overall severity profile of this differential diagnosis"
}
```
Provide only the JSON response without additional text."""
    
    if verbose:
        print("Using default severity prompt template")
    
    return default_template

def format_severity_prompt(
    differential_diagnosis: str,
    case_id: int,
    template: Optional[str] = None,
    verbose: bool = False
) -> str:
    """
    Format a severity prompt with the given differential diagnosis.
    
    Args:
        differential_diagnosis: The differential diagnosis text
        case_id: ID of the clinical case
        template: Optional template to use (defaults to standard template)
        verbose: Whether to print status information
        
    Returns:
        Formatted prompt text
    """
    if verbose:
        print(f"Formatting severity prompt for case {case_id}")
        
    if not template:
        template = load_severity_prompt_template(verbose=verbose)
        
    # Format the template with the differential diagnosis and case ID
    prompt = template.format(
        differential_diagnosis=differential_diagnosis,
        case_id=case_id
    )

    if verbose:
        print(f"Created prompt of length {len(prompt)}")
        
    return prompt

def get_disease_severity_levels(session=None, verbose: bool = False) -> Dict[str, Dict[str, str]]:
    """
    Get severity level descriptions from database.
    
    Args:
        session: Optional SQLAlchemy session (will create one if not provided)
        verbose: Whether to print status information
        
    Returns:
        Dictionary mapping severity levels to their descriptions
    """
    if verbose:
        print("Loading severity levels from database")
        
    severity_levels = {}

    try:
        if not session:
            from db.utils.db_utils import get_session
            session = get_session()
            close_session = True
        else:
            close_session = False
            
        from db.registry.registry_models import SeverityLevels
        
        levels = session.query(SeverityLevels).all()
        for level in levels:
            severity_levels[level.name] = {
                "id": level.id,
                "description": level.description
            }
            
        if close_session:
            session.close()
            
        if verbose:
            print(f"Loaded {len(severity_levels)} severity levels")
    except Exception as e:
        if verbose:
            print(f"Error loading severity levels: {str(e)}")
            
    # If no levels loaded, use defaults
    if not severity_levels:
        severity_levels = {
            "mild": {
                "id": 1,
                "description": "The disease generally has minor symptoms that do not significantly affect daily activities."
            },
            "moderate": {
                "id": 2,
                "description": "The disease has noticeable symptoms requiring medical intervention but is not life-threatening."
            },
            "severe": {
                "id": 3,
                "description": "The disease has serious symptoms that significantly impact health and may require hospitalization."
            },
            "critical": {
                "id": 4,
                "description": "The disease is life-threatening and requires immediate medical intervention."
            }
        }
        
    return severity_levels



def load_severity_prompt_template(prompt_id: Optional[int] = None, verbose: bool = False) -> str:
    """
    Load a severity prompt template from the database or use default.
    
    Args:
        prompt_id: Optional ID of a specific prompt to use
        verbose: Whether to print status information
        
    Returns:
        The prompt template text
    """
    if verbose:
        print(f"Loading severity prompt template (ID: {prompt_id if prompt_id else 'default'})")
        
    if prompt_id:
        try:
            from db.utils.db_utils import get_session
            from db.prompts.prompts_models import Prompt
            
            session = get_session()
            prompt = session.query(Prompt).filter(Prompt.id == prompt_id).first()
            session.close()
            
            if prompt and prompt.content:
                if verbose:
                    print(f"Loaded prompt template with ID {prompt_id}")
                return prompt.content
        except Exception as e:
            if verbose:
                print(f"Error loading prompt template from database: {str(e)}")
    
    # Default severity prompt template
    default_template = """You are a medical expert evaluating the severity of diseases in a differential diagnosis. 
Please analyze the following differential diagnosis and evaluate the severity of each proposed disease.

Differential Diagnosis:
{differential_diagnosis}

For each disease in the differential diagnosis, evaluate its severity based on the following criteria:
1. Mild: The disease generally has minor symptoms that do not significantly affect daily activities.
2. Moderate: The disease has noticeable symptoms requiring medical intervention but is not life-threatening.
3. Severe: The disease has serious symptoms that significantly impact health and may require hospitalization.
4. Critical: The disease is life-threatening and requires immediate medical intervention.

For each disease, consider its typical presentation, potential complications, and impact on the patient's quality of life.

Please structure your response as a JSON object with the following format:
```json
{
  "case_id": {case_id},
  "severity_evaluations": [
    {
      "disease": "Disease name",
      "rank": 1,
      "severity": "mild|moderate|severe|critical",
      "reasoning": "Brief explanation for this severity assessment"
    },
    {
      "disease": "Another disease",
      "rank": 2,
      "severity": "mild|moderate|severe|critical",
      "reasoning": "Brief explanation for this severity assessment"
    }
  ],
  "overall_assessment": "Brief summary of the overall severity profile of this differential diagnosis"
}
```
Provide only the JSON response without additional text."""
    
    if verbose:
        print("Using default severity prompt template")
    
    return default_template    