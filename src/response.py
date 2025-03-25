"""
Module for generating structured responses from LLM.
"""
import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import GEMINI_SYSTEM_PROMPT
from logging_config import log as logger
from paths import ENV_FILE

load_dotenv(ENV_FILE)  

# input: scraped_content
# output: structured_response
# description: generate a structured response using Gemini
def gemini_llm(scraped_content):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


    user_prompt = f"""Follow the response format and simplification rules strictly.
    Extract the delivery and return policy from the following web page contents:
    {scraped_content}
    """

    # Make the API call to Gemini
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            config=types.GenerateContentConfig(
                system_instruction=GEMINI_SYSTEM_PROMPT
            ),
            contents=user_prompt
        )
    except Exception as e:
        logger.error(f"Error generating content with Gemini: {e}")
        return "Error generating content with Gemini"

    return response.text
