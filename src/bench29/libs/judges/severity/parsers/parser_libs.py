
import os
import json
import datetime
import time
import re
from typing import Dict, List, Any, Optional, Tuple, Union

def extract_severity_from_response(response_text: str, verbose: bool = False) -> Dict[str, Any]:
    """
    Extract structured severity information from a judge response.
    
    Args:
        response_text: Response text from severity judge
        verbose: Whether to print status information
        
    Returns:
        Dictionary of structured severity data
    """
    if verbose:
        print("Extracting severity information from response")
        
    # Try to find JSON blocks in the response
    json_blocks = re.findall(r'```json\s*([\s\S]*?)\s*```', response_text)
    
    if json_blocks:
        # Use the first JSON block found
        try:
            json_str = json_blocks[0].strip()
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            if verbose:
                print(f"Error parsing JSON from response: {str(e)}")
    
    # If no JSON blocks, look for severity ratings in the text
    severity_data = {}
    
    # Look for severity ratings (e.g., "Severity: high" or "Disease X: Severe")
    severity_matches = re.findall(r'(.+?):\s*(mild|moderate|severe|critical)', response_text, re.IGNORECASE)
    
    for disease, severity in severity_matches:
        disease_name = disease.strip()
        severity_data[disease_name] = severity.lower()
    
    if not severity_data and verbose:
        print("Could not extract structured severity data from response")
        
    return severity_data

