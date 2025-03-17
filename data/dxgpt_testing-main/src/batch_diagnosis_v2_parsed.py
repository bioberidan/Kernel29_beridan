import os
import re
import json
import logging
from datasets import load_dataset
import requests
import pyhpo
import pandas as pd
import boto3
from dotenv import load_dotenv
from langchain.chat_models import AzureChatOpenAI, ChatOpenAI
from langchain_community.chat_models import BedrockChat
from langchain.prompts import PromptTemplate
from langchain.prompts.chat import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain_community.chat_models.azureml_endpoint import AzureMLChatOnlineEndpoint
from langchain_community.chat_models.azureml_endpoint import (
    AzureMLEndpointApiType,
    CustomOpenAIChatContentFormatter,
)
from langchain_core.messages import HumanMessage
from tqdm import tqdm
import anthropic
import vertexai
from vertexai.preview.generative_models import GenerativeModel
from google.oauth2 import service_account
from open_models import initialize_mistralmoe, initialize_mistral7b, initialize_mixtral_moe_big

from translate import deepl_translate

logging.basicConfig(level=logging.INFO)

# Load the environment variables from the .env file
load_dotenv()




PROMPT_TEMPLATE_RARE = "Behave like a hypotethical doctor who has to do a diagnosis for a patient. Give me a list of potential rare diseases with a short description. Shows for each potential rare diseases always with '\n\n+' and a number, starting with '\n\n+1', for example '\n\n+23.' (never return \n\n-), the name of the disease and finish with ':'. Dont return '\n\n-', return '\n\n+' instead. You have to indicate which symptoms the patient has in common with the proposed disease and which symptoms the patient does not have in common. The text is \n Symptoms:{description}"

PROMPT_TEMPLATE = "Behave like a hypotethical doctor who has to do a diagnosis for a patient. Give me a list of potential diseases with a short description. Shows for each potential diseases always with '\n\n+' and a number, starting with '\n\n+1', for example '\n\n+23.' (never return \n\n-), the name of the disease and finish with ':'. Dont return '\n\n-', return '\n\n+' instead. You have to indicate which symptoms the patient has in common with the proposed disease and which symptoms the patient does not have in common. The text is \n Symptoms:{description}"

PROMPT_TEMPLATE_MORE = "Behave like a hypotethical doctor who has to do a diagnosis for a patient. Continue the list of potential rare diseases without repeating any disease from the list I give you. If you repeat any, it is better not to return it. Shows for each potential rare diseases always with '\n\n+' and a number, starting with '\n\n+1', for example '\n\n+23.' (never return \n\n-), the name of the disease and finish with ':'. Dont return '\n\n-', return '\n\n+' instead. You have to indicate a short description and which symptoms the patient has in common with the proposed disease and which symptoms the patient does not have in common. The text is \n Symptoms: {description}. Each must have this format '\n\n+7.' for each potencial rare diseases. The list is: {initial_list} "

PROMPT_TEMPLATE_IMPROVED = """
<prompt> As an AI-assisted diagnostic tool, your task is to analyze the given patient symptoms and generate a list of the top 5 potential diagnoses. Follow these steps:
Carefully review the patient's reported symptoms.
In the <thinking></thinking> tags, provide a detailed analysis of the patient's condition: a. Highlight any key symptoms or combinations of symptoms that stand out. b. Discuss possible diagnoses and why they might or might not fit the patient's presentation. c. Suggest any additional tests or information that could help narrow down the diagnosis.
In the <top5></top5> tags, generate a list of the 5 most likely diagnoses that match the given symptoms: a. Assign each diagnosis a number, starting from 1 (e.g., "\n\n+1", "\n\n+2", etc.). b. Provide the name of the condition, followed by a colon (":"). c. Indicate which of the patient's symptoms are consistent with this diagnosis. d. Mention any key symptoms of the condition that the patient did not report, if applicable.
Remember:

Do not use "\n\n-" in your response. Only use "\n\n+" when listing the diagnoses.
The <thinking> section should come before the <top5> section.
Patient Symptoms:
<patient_description>
{description} 
</patient_description>
</prompt>
"""

PROMPT_TEMPLATE_JSON = """
Behave like a hypothetical doctor tasked with providing 5 hypothesis diagnosis for a patient based on their description. Your goal is to generate a list of 5 potential diseases, each with a short description, and indicate which symptoms the patient has in common with the proposed disease and which symptoms the patient does not have in common.

        Carefully analyze the patient description and consider various potential diseases that could match the symptoms described. For each potential disease:
        1. Provide a brief description of the disease
        2. List the symptoms that the patient has in common with the disease
        3. List the symptoms that the patient has that are not in common with the disease
        
        Present your findings in a JSON format within XML tags. The JSON should contain the following keys for each of the 5 potential disease:
        - "diagnosis": The name of the potential disease
        - "description": A brief description of the disease
        - "symptoms_in_common": An array of symptoms the patient has that match the disease
        - "symptoms_not_in_common": An array of symptoms the patient has that are not in common with the disease
        
        Here's an example of how your output should be structured:
        
        <5_diagnosis_output>
        [
        {{
            "diagnosis": "some disease 1",
            "description": "some description",
            "symptoms_in_common": ["symptom1", "symptom2", "symptomN"],
            "symptoms_not_in_common": ["symptom1", "symptom2", "symptomN"]
        }},
        ...
        {{
            "diagnosis": "some disease 5",
            "description": "some description",
            "symptoms_in_common": ["symptom1", "symptom2", "symptomN"],
            "symptoms_not_in_common": ["symptom1", "symptom2", "symptomN"]
        }}
        ]
        </5_diagnosis_output>
        
        Present your final output within <5_diagnosis_output> tags as shown in the example above.
        
        Here is the patient description:
        <patient_description>
        {description}
        </patient_description>
"""

PROMPT_TEMPLATE_JSON_RISK = """
Behave like a hypothetical doctor tasked with providing 5 hypothesis diagnosis for a patient based on their description. Your goal is to generate a list of 5 potential diseases, each with a short description, and indicate which symptoms the patient has in common with the proposed disease and which symptoms the patient does not have in common.

        Carefully analyze the patient description and consider various potential diseases that could match the symptoms described. For each potential disease:
        1. Provide a brief description of the disease
        2. List the symptoms that the patient has in common with the disease
        3. List the symptoms that the patient has that are not in common with the disease
        
        Present your findings in a JSON format within XML tags. The JSON should contain the following keys for each of the 5 potential disease:
        - "diagnosis": The name of the potential disease
        - "description": A brief description of the disease
        - "symptoms_in_common": An array of symptoms the patient has that match the disease
        - "symptoms_not_in_common": An array of symptoms the patient has that are not in common with the disease
        
        Here's an example of how your output should be structured:
        
        <5_diagnosis_output>
        [
        {{
            "diagnosis": "some disease 1",
            "description": "some description",
            "symptoms_in_common": ["symptom1", "symptom2", "symptomN"],
            "symptoms_not_in_common": ["symptom1", "symptom2", "symptomN"]
        }},
        ...
        {{
            "diagnosis": "some disease 5",
            "description": "some description",
            "symptoms_in_common": ["symptom1", "symptom2", "symptomN"],
            "symptoms_not_in_common": ["symptom1", "symptom2", "symptomN"]
        }}
        ]
        </5_diagnosis_output>
        
        Present your final output within <5_diagnosis_output> tags as shown in the example above.
        
        If there are no symptoms in the description or it is not related to a patient's clinic, return an empty list like this:

        <diagnosis_output>
        []
        </diagnosis_output>

        Here is the patient description:
        <patient_description>
        {description}
        </patient_description>
        """


def get_diagnosis(prompt, dataframe, output_file, model, num_samples=200):

    # Define the chat prompt template
    human_message_prompt = HumanMessagePromptTemplate.from_template(prompt)
    chat_prompt = ChatPromptTemplate.from_messages([human_message_prompt])

    # Iterate over the rows in the synthetic data
    for index, row in tqdm(df[:num_samples].iterrows(), total=df[:num_samples].shape[0]):
        # Get the ground truth (GT) and the description
        if HM:
            description = row[0]
        elif HF:
            description = row["Phenotype"]
            gt = row["RareDisease"]
        else:
            gt = row[0]
            description = row[1]
        # Generate a diagnosis
        diagnoses = []
        # Generate the diagnosis using the GPT-4 model
     attempts = 0
        while attempts < 2:
            try:
                if model == "c3opus":
                    diagnosis = initialize_anthropic_claude(formatted_prompt[0].content).content[0].text
                elif model == "c35sonnet":
                    diagnosis = initialize_anthropic_c35(formatted_prompt[0].content).content[0].text
                elif model == "c3sonnet":
                    diagnosis = initialize_bedrock_claude(formatted_prompt[0].content).get("content")[0].get("text")
                    # print(diagnosis)
                elif model == "mistralmoebig":
                    diagnosis = initialize_mixtral_moe_big(formatted_prompt[0].content)
                elif model == "mistralmoe":
                    diagnosis = initialize_mistralmoe(formatted_prompt[0].content)["outputs"][0]["text"]
                    # print(diagnosis)
                elif model == "mistral7b":
                    diagnosis = initialize_mistral7b(formatted_prompt[0].content)["outputs"][0]["text"]
                    print(diagnosis)
                elif model == "llama2_7b":
                    diagnosis = initialize_azure_llama2_7b(formatted_prompt[0].content)
                elif model == "llama3_8b":
                    diagnosis = initialize_azure_llama3_8b(formatted_prompt[0].content)
                elif model == "llama3_70b":
                    diagnosis = initialize_azure_llama3_70b(formatted_prompt[0].content)
                elif model == "cohere_cplus":
                    diagnosis = initialize_azure_cohere_cplus(formatted_prompt[0].content)
                elif model == "geminipro":
                    diagnosis = initialize_gcp_geminipro(formatted_prompt[0].content)
                else:
                    diagnosis = model(formatted_prompt).content  # Call the model instance directly
                break
            except Exception as e:
                attempts += 1
                print(e)
                if attempts == 2:
                    diagnosis = "ERROR"
        
        # Extract the content within the <top5> tags using regular expressions
        # print(diagnosis)

        diagnoses.append(diagnosis)
        # print(diagnosis)

        # Add the diagnoses to the new DataFrame
        if HM:
            diagnoses_df.loc[index] = [description] + diagnoses
        else:
            diagnoses_df.loc[index] = [gt] + diagnoses

        # print(diagnoses_df.loc[index])
        # break

    # Save the diagnoses to a new CSV file
    output_path = f'data/{output_file}'
    diagnoses_df.to_csv(output_path, index=False)


# datasets = ["RAMEDIS", "MME", "HMS", "LIRICAL", "PUMCH_ADM"]
data = load_dataset('chenxz/RareBench', "RAMEDIS", split='test')

mapped_data = mapping_fn_with_hpo3_plus_orpha_api(data)
# print(type(mapped_data))

# print(mapped_data[:5])

# get_diagnosis(PROMPT_TEMPLATE, 'synthetic_data_v2.csv', 'diagnoses_v2_mixtralmoe_big.csv', "mistralmoebig")

# get_diagnosis(PROMPT_TEMPLATE, mapped_data, 'diagnoses_PUMCH_ADM_mixtralmoe_big.csv', "mistralmoebig")

# get_diagnosis(PROMPT_TEMPLATE_JSON_RISK, mapped_data, 'diagnoses_RAMEDIS_gpt4o_json_risk.csv', gpt4o, 200)

# get_diagnosis(PROMPT_TEMPLATE, mapped_data, 'diagnoses_RAMEDIS_c35sonnet.csv', "c35sonnet")

# get_diagnosis(PROMPT_TEMPLATE, 'URG_Torre_Dic_2022_IA_GEN_modified_2.xlsx', 'diagnoses_URG_Torre_Dic_200_o1_mini.csv', o1_mini, 200)

# get_diagnosis(PROMPT_TEMPLATE, 'URG_Torre_Dic_2022_IA_GEN_modified_2.xlsx', 'diagnoses_URG_Torre_Dic_200_o1_preview.csv', o1_preview, 200)

get_diagnosis(PROMPT_TEMPLATE, mapped_data, 'diagnoses_RAMEDIS_o1_mini.csv', o1_mini, 200)

get_diagnosis(PROMPT_TEMPLATE, mapped_data, 'diagnoses_RAMEDIS_o1_preview.csv', o1_preview, 200)