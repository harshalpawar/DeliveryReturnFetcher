# Search keywords
SEARCH_KEYWORDS = {
    "delivery": "delivery+shipping+charges",
    "returns": "returns+refund+exchange"
}

# Jina Reader Configuration
def JINA_READER_HEADERS(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
        "X-Return-Format": "markdown"
    }

# def JINA_READER_CONFIG(api_key, brand_url):
#     return {
#         'url': 'https://r.jina.ai/',
#         'headers': {
#             'Accept': 'application/json',
#             'Authorization': f'Bearer {api_key}',
#             'X-Md-Link-Style': 'referenced',
#             'X-No-Cache': 'true',
#             'X-Retain-Images': 'none',
#             'X-With-Images-Summary': 'all',
#             'X-With-Links-Summary': 'all'
#         },
#         'data': {
#             "url": brand_url,
#             "injectPageScript": [
#             "// Remove headers, footers, navigation elements, and popups\ndocument.querySelectorAll('header, footer, nav, .navbar, .cookie-banner, .popup, .ad-banner').forEach(el => el.remove());\n\n// Ensure dynamic content is fully loaded before scraping\nconst dynamicElements = document.querySelectorAll('.dynamic-content, .ajax-loaded');\ndynamicElements.forEach(el => {\n    if (!el.innerHTML.trim()) {\n        // Wait for content to load\n        const observer = new MutationObserver((mutations, observer) => {\n            observer.disconnect(); // Stop observing once content is loaded\n        });\n        observer.observe(el, { childList: true, subtree: true });\n    }\n});"
#             ]
#         }
#     }

# Jina Search Configuration
def JINA_SEARCH_HEADERS(api_key, brand_domain):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        'X-No-Cache': 'true',
        "X-Respond-With": "no-content",
        "X-Site": brand_domain
    }

# Gemini Configuration

# Prompts
# TODO: modify the prompt
# GEMINI_SYSTEM_PROMPT = """Your purpose is to extract the delivery and return policy of a fashion brand in India.

#     📌 **RESPONSE FORMAT (Strictly follow this structure):**
#     **Delivery:**
#     - Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping" if applicable)
#     - Estimated Delivery Time: Within B days OR A-B days (if a range is specified)

#     **Returns:**
#     - Return Period: X days
#     - Return Method: Brand pickup / Self-ship **Mention the return pickup charges if any**.
#     - Refund Mode: Bank a/c / Store credit / Other

#     🔹 **Important Simplification Rules:**
#     - **Delivery Charges:** If there is a free shipping threshold, write as: "Delivery Charges: Rs. X; Free over Rs. Y".
#     - **Return Methods:**
#     - If the brand arranges a pickup, even if they use terms like **"scheduled courier pickup" or "reverse logistics service"**, treat it as **"Brand pickup"**. **Mention the return pickup charges if any**.
#     - If the customer **must ship the item themselves** using their own courier or by dropping it at a store/courier location, classify it as **"Self-ship"**.
#     - If returns are **only for exchanges**, format as: "X days - exchanges only". If exchanges are size only, then mention it as "X days - exchanges only (size only)".
#     - **Refund Mode:** If refunds are to a bank account, state "Refund in bank a/c". If store credit is used, state "Refund as store credit".
#     - **No unnecessary details** should be included. Keep only what's relevant.
#     - Do **not** make up information—return 'Not specified' for missing details.

#     Ensure **clarity and structured formatting** as per the above rules.
# """

GEMINI_SYSTEM_PROMPT = """
Your purpose is to extract the delivery and return policy of a fashion brand in India.

---

📌 RESPONSE FORMAT (Strictly follow this structure):

**Delivery:**
- Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping" if applicable)
- Estimated Delivery Time: Within B days OR A-B days (if a range is specified)

**Returns:**
- Return Period: Within X days
- Return Method: Brand pickup / Self-ship **(mention return pickup charges if any)**.
- Refund Mode: Bank a/c / Store credit / Other

**Additional Info:**
- Include any delivery or return-related information that does not fit the structured format above. For example:
  - Special conditions for returns (e.g., "Returns only for defective items").
  - Delivery restrictions (e.g., "Delivery available only in select cities").
  - Any other relevant details.

---

🔹 Important Rules:

1. **Delivery Charges:**
   - There is usually a standard delivery charge for the brand. Mention it as "Delivery Charges: Rs. Z".
   - There is usually a minimum order amount for free shipping. Mention it as "Free shipping over Rs. Z".

2. **Estimated Delivery Time:**
   - If conflicting delivery times are found (e.g., policy page vs. product pages), prioritize the **policy page** and ignore product page delivery times.
   - If there are different delivery times for different cities, then combine them into a single range. For example, "Delivery Time: 3-5 days (Metro cities) / 5-7 days (Rest of India)" should be mentioned as "Delivery Time: 3-7 days". Mention the different delivery times in the additional info section.

3. **Return Period:**
   - This is the period within which the customer can return the item. Mention it as "Return Period: within X days".

4. **Return Methods:**
   - If the brand arranges a pickup (e.g., "scheduled courier pickup" or "reverse logistics service"), classify it as **"Brand pickup"**. Mention return pickup charges if any.
   - If the customer must ship the item themselves, classify it as **"Self-ship"**.
   - If returns are only for exchanges, format as: "X days - exchanges only". If exchanges are size-only, format as: "X days - exchanges only (size only)".

5. **Refund Mode:**
   - If refunds are to a bank account, state: "Refund in bank a/c".
   - If refunds are as store credit, state: "Refund as store credit".
   - Sometimes the brand may mention that refund will be made in the original mode of payment. In that case, mention it as "Refund in original mode of payment".
   - If it exchanges only, mention it as "Refund as store credit (exchanges only)".

6. **Membership Information:**
   - Ignore any delivery or return information related to memberships, loyalty programs, or subscription services. Do not include this in the response.

7. **Additional Info:**
   - Include any delivery or return-related information that does not fit the structured format above.
   - Do not include irrelevant details or duplicate information.

8. **DO NOT mention memberships, conflicting delivery times, or any irrelevant details in the response.**

**No unnecessary details** should be included. Keep only what's relevant.
Ensure **clarity and structured formatting** as per the above rules.
---

Example Response:

**Delivery:**
- Delivery Charges: Rs. 199; Free over Rs. 999
- Estimated Delivery Time: Within 3-7 days

**Returns:**
- Return Period: 30 days
- Return Method: Brand pickup (Rs. 50 pickup charge)
- Refund Mode: Refund in bank a/c

**Additional Info:**
- Returns only for defective items.
- Delivery available only in select cities.
"""
