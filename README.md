# Policy Extractor

**Description:**

This project automatically extracts delivery and return policies from fashion websites in India. It uses Jina AI for search and scraping, and Gemini (or another LLM) for information extraction. The goal is to provide structured policy data for integration into an application.

**Key Components:**

*   `mainScript.py`: Orchestrates the entire pipeline, including error handling and logging.
*   `src/`: Contains modular functions for search, scraping, cleaning, and LLM response.
*   `config.py`: Stores all configuration parameters (Jina/Gemini config, search keywords, prompts).

**Data Flow:**

1.  Reads brand information from `data/brand_input.json`.
2.  Uses Jina AI to search for relevant policy pages on the brand's website.
3.  Scrapes the content of those pages using Jina Reader.
4.  Cleans and prepares the text for the LLM.
5.  Uses Gemini (or another LLM) to extract structured policy information.
6.  Writes the final output to `data/brand_output.json`.

**Setup:**

1.  Clone the repository.
2.  Create a virtual environment: `python -m venv venv`
3.  Activate the virtual environment:
    *   On Windows: `venv\Scripts\activate`
    *   On macOS/Linux: `source venv/bin/activate`
4.  Install dependencies: `pip install -r requirements.txt`
5.  Create a `.env` file and add your API keys:

    ```
    JINA_API_KEY=your_jina_api_key
    GEMINI_API_KEY=your_gemini_api_key
    ```

**Usage:**

1.  Configure the `brand_input.json` file with the brands you want to process.
2.  Run the `mainScript.py` script: `python mainScript.py`
3.  Review the results in `data/brand_output.json`.
4.  Check logs in `/logs`

**Error Handling:**

All errors are handled and logged in `mainScript.py`.

**TODO (For Wednesday MVP):**

*   Implement `clean.py`
*   Update Gemini prompt to follow a structured output and request snippets
*   Implement `time.sleep(x)` for rate limiting (if necessary)
*   Implement simple retries

**License:**

[Add your company's license information here]
