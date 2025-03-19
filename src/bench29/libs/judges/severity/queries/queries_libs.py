
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