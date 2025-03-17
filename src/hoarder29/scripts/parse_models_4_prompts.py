import os
from db.utils.db_utils import get_session
from db.db_queries import add_model, get_model_id, add_prompt, get_prompt_id
from libs.libs import get_directories, extract_model_prompt

def main(dirname):
    # Get database session
    session = get_session(schema="llm")
    
    # Get list of directories
    dirs = get_directories(dirname, verbose=True)
    
    # Process each directory
    for dir_name in dirs:
        model_name, prompt_name = extract_model_prompt(dir_name)
        
        if model_name and prompt_name:
            print(f"Processing: {dir_name}")
            print(f"  Model: {model_name}")
            print(f"  Prompt: {prompt_name}")
            
            # Add to database
            model_id = add_model(session, model_name)
            prompt_id = add_prompt(session, prompt_name)
            
            print(f"  Added to database: Model ID={model_id}, Prompt ID={prompt_id}")
        else:
            print(f"Skipping {dir_name}: Could not extract model and prompt")
    
    print("Processing completed")
    session.close()
    return


if __name__ == "__main__":
    # Configuration
    dirname = "../../data/prompt_comparison_results/prompt_comparison_results"  # Change this to your directory path
    main(dirname)