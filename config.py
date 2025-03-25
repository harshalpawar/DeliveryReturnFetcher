# Search keywords
SEARCH_KEYWORDS = {
    "delivery": "delivery+shipping+charges",
    "returns": "returns+refund+exchange"
}

# Jina Reader Configuration
def JINA_READER_HEADERS(api_key):
    return {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'X-Md-Link-Style': 'referenced',
        'X-Retain-Images': 'none', 
        'X-Return-Format': 'text',
        'X-With-Images-Summary': 'all',
        'X-With-Links-Summary': 'all'
    }
# Jina Search Configuration
def JINA_SEARCH_HEADERS(api_key, brand_domain):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-Respond-With": "no-content",
        "X-Site": brand_domain
    }
# Gemini Configuration

# Prompts
# TODO: modify the prompt
GEMINI_SYSTEM_PROMPT = """Your purpose is to extract the delivery and return policy of a fashion brand in India.

    📌 **RESPONSE FORMAT (Strictly follow this structure):**
    **Delivery:**
    - Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping" if applicable)
    - Estimated Delivery Time: Within B days OR A-B days (if a range is specified)

    **Returns:**
    - Return Period: X days
    - Return Method: Brand pickup / Self-ship **Mention the return pickup charges if any**.
    - Refund Mode: Bank a/c / Store credit / Other

    🔹 **Important Simplification Rules:**
    - **Delivery Charges:** If there is a free shipping threshold, write as: "Delivery Charges: Rs. X; Free over Rs. Y".
    - **Return Methods:**
    - If the brand arranges a pickup, even if they use terms like **"scheduled courier pickup" or "reverse logistics service"**, treat it as **"Brand pickup"**. **Mention the return pickup charges if any**.
    - If the customer **must ship the item themselves** using their own courier or by dropping it at a store/courier location, classify it as **"Self-ship"**.
    - If returns are **only for exchanges**, format as: "X days - exchanges only". If exchanges are size only, then mention it as "X days - exchanges only (size only)".
    - **Refund Mode:** If refunds are to a bank account, state "Refund in bank a/c". If store credit is used, state "Refund as store credit".
    - **No unnecessary details** should be included. Keep only what's relevant.
    - Do **not** make up information—return 'Not specified' for missing details.

    Ensure **clarity and structured formatting** as per the above rules.
"""