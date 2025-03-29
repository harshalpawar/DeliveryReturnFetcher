SEARCH_KEYWORDS = {
    "delivery": "delivery+shipping+charges",
    "returns": "returns+refund+exchange"
}

def JINA_READER_HEADERS(api_key):
    return {
        'Authorization': f'Bearer {api_key}',
        "X-Return-Format": "markdown"
    }

def JINA_SEARCH_HEADERS(api_key, brand_domain):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        'X-No-Cache': 'true',
        "X-Respond-With": "no-content",
        "X-Site": brand_domain
    }

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
