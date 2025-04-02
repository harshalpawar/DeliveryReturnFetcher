"""
Module for generating structured responses from LLM.
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import GEMINI_SYSTEM_PROMPT, GEMINI_CONFIG, GEMINI_VERIFICATION_PROMPT
from logging_config import log as logger
from paths import ENV_FILE
load_dotenv(ENV_FILE)  

# input: scraped_content
# output: structured_response
# description: generate a structured response using Gemini
def gemini_llm(scraped_content, brand_name=None):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    user_prompt = f"""
    Extract the delivery and return policy from the following web page contents:
    {scraped_content}
    """

    # Make the API call to Gemini
    try:
        response = client.models.generate_content(
            model=GEMINI_CONFIG["model"], 
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_PROMPT,
                temperature=GEMINI_CONFIG["temperature"]
            ),
            contents=user_prompt
        )
    except Exception as e:
        logger.error(f"Error generating content with Gemini: {e}")
        return "Error generating content with Gemini"

    return f"Final response for {brand_name}: {response.text}"

def verify_gemini(scraped_content, human_policy, brand_name=None):
    """
    Verify scraped content against human-verified policy data.
    Returns a verification result containing matches and discrepancies.
    """
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    # Create verification prompt
    verification_prompt = f"""
    Compare the following policy information against the scraped content and identify any discrepancies.
    
    Human-verified policy:
    {human_policy}
    
    Scraped content:
    {scraped_content}
    """

    try:
        response = client.models.generate_content(
            model=GEMINI_CONFIG["model"],
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_VERIFICATION_PROMPT,
                temperature=GEMINI_CONFIG["temperature"]
            ),
            contents=verification_prompt
        )
        
        return f"Final response for {brand_name}: {response.text}"
        
    except Exception as e:
        logger.error(f"Error in verification: {e}")
        return {
            "error": str(e),
            "matches": [],
            "missing": ["All - verification failed"],
            "contradictions": [],
            "confidence_score": "None - verification failed"
        }
