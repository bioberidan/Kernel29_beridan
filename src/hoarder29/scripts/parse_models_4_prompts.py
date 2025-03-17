import os
import re
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from sqlalchemy_models_working import Base, Models, Prompts


def extract_model_prompt(dirname):
    """Extract model and prompt from directory name."""
    pattern = r"(.+)_diagnosis(?:_(.+))?"
    match = re.match(pattern, dirname)
    if match:
        model_name = match.group(1)
        prompt_name = match.group(2) if match.group(2) else "standard"
        return model_name, prompt_name
    return None, None

def add_model(model_name):
    """Add model to database if not exists, return model id."""
    # Check if model exists
    if not session.query(exists().where(Models.alias == model_name)).scalar():
        # Parse provider from model name (simple heuristic)
        if "glm" in model_name.lower():
            provider = "Zhipu"
        elif "llama" in model_name.lower():
            provider = "Meta"
        elif "mistral" in model_name.lower():
            provider = "Mistral AI"
        elif "gemini" in model_name.lower():
            provider = "Google"
        else:
            provider = "Unknown"
        
        new_model = Models(
            alias=model_name,
            name=model_name,
            provider=provider
        )
        session.add(new_model)
        session.commit()
    
    # Get model id
    return session.query(Models).filter(Models.alias == model_name).first().id

def add_prompt(prompt_name):
    """Add prompt to database if not exists, return prompt id."""
    # Check if prompt exists
    if not session.query(exists().where(Prompts.alias == prompt_name)).scalar():
        # Create descriptions based on prompt type
        descriptions = {
            "standard": "Standard diagnosis prompt without special techniques",
            "few_shot": "Few-shot learning approach with examples",
            "dynamic_few_shot": "Dynamic few-shot learning with adaptive examples",
            "auto-cot": "Auto Chain-of-Thought prompting for reasoning",
            "medprompt": "Medical-specific prompt optimized for diagnosis"
        }
        
        description = descriptions.get(prompt_name, f"Custom prompt: {prompt_name}")
        
        new_prompt = Prompts(
            alias=prompt_name,
            description=description
        )
        session.add(new_prompt)
        session.commit()
    
    # Get prompt id
    return session.query(Prompts).filter(Prompts.alias == prompt_name).first().id

def get_files(dirname):
    print("listing directories")
    dirs = [d for d in os.listdir(dirname) if os.path.isdir(os.path.join(dirname, d))]
    
    print(f"Found {len(dirs)} directories")
    return dirs


def main(dirs):
    # Get list of directories


    
    # Process each directory
    for dir_name in dirs:
        model_name, prompt_name = extract_model_prompt(dir_name)
        
        if model_name and prompt_name:
            print(f"Processing: {dir_name}")
            print(f"  Model: {model_name}")
            print(f"  Prompt: {prompt_name}")
            
            # Add to database
            model_id = add_model(model_name)
            prompt_id = add_prompt(prompt_name)
            
            print(f"  Added to database: Model ID={model_id}, Prompt ID={prompt_id}")
        else:
            print(f"Skipping {dir_name}: Could not extract model and prompt")
    
    print("Processing completed")
    return



def get_session():
    DATABASE_URL = "postgresql://dummy_user:dummy_password_42@localhost/bench29"

    engine = create_engine(DATABASE_URL)

    Base.metadata.create_all(engine)

    print("Tables created successfully!")
    Session = sessionmaker(bind=engine)
    session = Session()
    return session


if __name__ == "__main__":
# Configuration
    dirname = "../../data/prompt_comparison_results/prompt_comparison_results"  # Change this to your directory path
    session = get_session()
    dirs = get_files(dirname)

    main(dirs)
