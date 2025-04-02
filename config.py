SEARCH_KEYWORDS = {
    "delivery": "delivery+shipping",
    "returns": "returns+refund+exchange"
}

def JINA_READER_HEADERS(api_key):
    return {
        "Authorization": f"Bearer {api_key}",
        "X-Base": "final",
        "X-No-Cache": "true",
        "X-Proxy": "auto",
        "X-Retain-Images": "none"
    }

def JINA_SEARCH_HEADERS(api_key, brand_domain):
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {api_key}",
        "X-No-Cache": "true",
        "X-Respond-With": "no-content",
        "X-Site": brand_domain
    }

GEMINI_CONFIG = {
    "model": "gemini-2.0-flash-thinking-exp-01-21",
    "temperature": 0.1,
}
GEMINI_SYSTEM_PROMPT = """
Your purpose is to extract and format the delivery and return policy of a fashion brand in India based on the provided text. Follow these steps meticulously:

**Step 1: Understand the Goal and Format**
- Your final output must strictly adhere to the following structure:
  **Delivery:**
  - Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping")
  - Estimated Delivery Time: Within B days OR A-B days
  **Returns:**
  - Return Period: Within X days (or "X days - exchanges only", "X days - exchanges only (size only)", "X days - exchanges only (defect only)")
  - Return Method: Brand pickup / Self-ship / Return in store (mention return pickup charges if any)
  - Refund Mode: Bank a/c / Store credit / Original mode of payment / Other (Omit if exchange only)
  **Additional Info:**
  - [Relevant details not fitting above]
- You must ignore information related to international shipping, memberships, loyalty programs, or subscription services.

**Step 2: Extract Delivery Charges**
- Find the standard delivery charge. Format as "Rs. X".
- Find the minimum order value for free shipping. Format as "; Free over Rs. Y".
- If shipping is always free, state "Free shipping".
- Combine these into the "Delivery Charges:" line.

**Step 3: Extract and Calculate Estimated Delivery Time**
- Locate the estimated delivery times for domestic orders within India.
- **Prioritize information from the main policy page** over product page examples if conflicts exist.
- If different times are given for different regions (e.g., metros vs. rest of India), find the minimum and maximum values across all domestic regions to create a single range (e.g., 3-5 days and 5-7 days becomes "3-7 days"). Note the regional differences in Step 7 (Additional Info).
- If dispatch time and delivery time are mentioned separately, add them together to get the total estimated delivery time.
- Ensure the final time is expressed in **days** (convert hours if necessary, e.g., 48 hours = 2 days).
- Format as "Within B days" or "A-B days".

**Step 4: Extract Return Period and Conditions**
- Find the number of days within which a customer can initiate a return or exchange.
- Check if returns are only for exchange.
  - If yes, check if it's size-only exchange or defect-only exchange.
  - Format accordingly: "X days - exchanges only", "X days - exchanges only (size only)", or "X days - exchanges only (defect only)".
- If regular returns are allowed, format as "Within X days".

**Step 5: Determine Return Method(s)**
- Identify how the customer returns the item:
  - If the brand arranges pickup (e.g., "scheduled courier", "reverse logistics"), classify as **"Brand pickup"**. Note any associated pickup charges (e.g., "Brand pickup (Rs. 50 pickup charge)").
  - If the customer must ship it back themselves, classify as **"Self-ship"**.
  - If the customer can return it to a physical store, classify as **"Return in store"**.
- List all applicable methods found.

**Step 6: Determine Refund Mode**
- **If Step 4 indicated "exchanges only", skip this step and omit the "Refund Mode" line in the final output.**
- Otherwise, identify how the refund is processed:
  - To a bank account: "Bank a/c"
  - As store credit: "Store credit"
  - To the original payment method: "Original mode of payment"
  - Other specified modes: Describe briefly (e.g., "Wallet transfer")
- Format as "Refund Mode: [Result]".

**Step 7: Collate Additional Information**
- Review the source text again.
- Identify any other relevant delivery or return details that were not captured in the structured fields above (e.g., specific conditions for returns like "only for defective items", delivery restrictions like "only in select cities", regional delivery time differences noted in Step 3).
- **Crucially, do NOT include:**
  - Information already captured in the structured fields.
  - Details about memberships, loyalty programs, international shipping.
  - Conflicting delivery times that were discarded in Step 3.
  - General marketing text or irrelevant details.
- List these points under "Additional Info:".

**Step 8: Assemble the Final Response**
- Combine the results from Steps 2 through 7 into the final, structured format defined in Step 1.
- Double-check that all rules have been followed and no forbidden information is included.
- Ensure clarity and conciseness.

---

Example of applying the steps (mental walkthrough):

1.  *Goal understood, format noted.*
2.  *Found 'Rs. 199 shipping', 'free shipping on orders over Rs. 999'. Result: "Rs. 199; Free over Rs. 999"*
3.  *Policy page says '3-7 days'. Product page says '2 days'. Prioritize policy. Result: "Within 3-7 days"*
4.  *Found '30 days return window'. No mention of exchange-only. Result: "30 days"*
5.  *Found 'reverse pickup arranged', 'Rs. 50 charge applies'. Result: "Brand pickup (Rs. 50 pickup charge)"*
6.  *Not exchange-only. Found 'refund processed to original bank account'. Result: "Refund in bank a/c"*
7.  *Found 'returns only for defective items', 'delivery only in select cities'. Result: "- Returns only for defective items.\n- Delivery available only in select cities."*
8.  *Assemble all results into the final format.*

---

Now, provide the text containing the delivery and return policy for the brand. I will follow these steps to generate the response.
"""

GEMINI_VERIFICATION_PROMPT = """
Your purpose is to verify the accuracy of scraped delivery and return policies for a fashion brand in India. You will be given a scraped data summary and the relevant text extracted from the brand's website. Your task is to assess the accuracy of the scraped data based on the website text, following these steps meticulously:

**Step 1: Understand the Goal, Format, and Inputs**

- You are given two inputs:
    1.  **Scraped Data Summary:** A summary of the delivery and return policy extracted from the brand's website, formatted according to the structure defined below.
    2.  **Website Text:** The raw text extracted from the brand's delivery and return policy pages.

- Your final output must indicate whether the scraped data is accurate and, if not, provide corrections *and* the relevant snippets from the website text that support those corrections. It *must* be in one of the following forms:

    *   **If accurate:** "The scraped data is accurate based on the provided website text."
    *   **If inaccurate:**
        ```
        The scraped data is inaccurate. Corrections:
        **Delivery:**
        - Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping")
          > Website Snippet: "Relevant excerpt about delivery charges"
        - Estimated Delivery Time: Within B days OR A-B days
          > Website Snippet: "Relevant excerpt about delivery time"
        **Returns:**
        - Return Period: Within X days (or "X days - exchanges only", "X days - exchanges only (size only)", "X days - exchanges only (defect only)")
          > Website Snippet: "Relevant excerpt about return period"
        - Return Method: Brand pickup / Self-ship / Return in store (mention return pickup charges if any)
          > Website Snippet: "Relevant excerpt about return method"
        - Refund Mode: Bank a/c / Store credit / Original mode of payment / Other (Omit if exchange only)
          > Website Snippet: "Relevant excerpt about refund mode"
        **Additional Info:**
        - [Relevant details not fitting above]
          > Website Snippet: "Relevant excerpt providing additional info"
        ```

- You must ignore information related to international shipping, memberships, loyalty programs, or subscription services.

**Step 2: Analyze the Scraped Data**

- Deconstruct the "Scraped Data Summary" into its individual components: delivery charges, estimated delivery time, return period, return method, refund mode, and additional info.

**Step 3: Cross-Reference with Website Text**

- For *each* component of the "Scraped Data Summary," search for supporting evidence (or lack thereof) within the "Website Text."
- Pay close attention to:
    -   **Delivery Charges:** Confirm the standard charge and free shipping threshold.
    -   **Estimated Delivery Time:**  Prioritize information from the main policy page. Check if the scraped range matches what's on the website. If regional differences exist, ensure the scraped range accounts for them.
    -   **Return Period:** Verify the return window duration and any exchange-only conditions (size, defect, etc.).
    -   **Return Method:**  Confirm whether the return is brand pickup, self-ship, or return in store. Verify pickup charges, if any.
    -   **Refund Mode:** If returns are allowed (not just exchanges), check if the scraped refund mode matches the website's description.
    -   **Additional Info:**  Ensure the scraped "Additional Info" isn't already covered in other sections and doesn't contain forbidden information (memberships, international shipping, etc.).

**Step 4: Identify Discrepancies**

- If *any* of the following conditions are met, the scraped data is inaccurate:
    -   A component in the "Scraped Data Summary" *cannot* be found or reasonably inferred from the "Website Text."
    -   The value or description of a component in the "Scraped Data Summary" *contradicts* the information in the "Website Text."

**Step 5: Provide Corrections AND Snippets (If Necessary)**

- If the scraped data is inaccurate, create a "Corrections" section formatted exactly as described in Step 1.
- For *each* inaccurate component, provide the *correct* information as found in the "Website Text." Use the formatting guidelines from the original prompt (Rs. X, Within B days, etc.).
- **Immediately following the corrected information, include a "> Website Snippet: " line followed by the exact text excerpt from the "Website Text" that supports the correction.  Keep the snippet concise and directly relevant.**
- If information is missing in the scraped data, add it to the "Corrections" section *with* the supporting snippet.
- Retain any accurate information that can still be extracted despite an inaccurate extraction.
- Only include truly relevant delivery/return information. Exclude marketing text and irrelevant details.
- Do not add information already contained in the "Scraped Data Summary."

**Step 6: Assemble the Final Response**

- Based on your analysis, provide *one* of the two final responses defined in Step 1:
    -   "The scraped data is accurate based on the provided website text."
    -   Or the detailed "Corrections" section if discrepancies were found, *including the website snippets.*

---

Example of applying the steps (mental walkthrough):

1. *Inputs received and format understood.*
2. *Scraped data: Delivery Charges: Rs. 99, Return Period: 14 days, Refund Mode: Store Credit, etc.*
3. *Website text: "Free shipping on orders over Rs. 50. Returns accepted within 30 days for a full refund."*
4. *Discrepancies found: Delivery charges are wrong, return period is wrong, refund mode is wrong.*
5. *Corrections generated:*
   * *Delivery Charges: Free over Rs. 50*
     *> Website Snippet: "Free shipping on orders over Rs. 50"*
   * *Return Period: Within 30 days*
     *> Website Snippet: "Returns accepted within 30 days"*
   * *Refund Mode: Bank a/c*
     *> Website Snippet: "for a full refund"*
6. *Final response assembled with the identified corrections and snippets.*

---

Now, provide the **Scraped Data Summary** and the **Website Text**. I will follow these steps to generate the response.
"""



# GEMINI_SYSTEM_PROMPT = """
# Your purpose is to extract the delivery and return policy of a fashion brand in India.

# ---

# 📌 RESPONSE FORMAT (Strictly follow this structure):

# **Delivery:**
# - Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping" if applicable)
# - Estimated Delivery Time: Within B days OR A-B days (if a range is specified)

# **Returns:**
# - Return Period: Within X days
# - Return Method: Brand pickup / Self-ship **(mention return pickup charges if any)**.
# - Refund Mode: Bank a/c / Store credit / Other

# **Additional Info:**
# - Include any delivery or return-related information that does not fit the structured format above. For example:
#   - Special conditions for returns (e.g., "Returns only for defective items").
#   - Delivery restrictions (e.g., "Delivery available only in select cities").
#   - Any other relevant details.

# ---

# 🔹 Important Rules:

# 1. **Delivery Charges:**
#    - There is usually a standard delivery charge for the brand. Mention it as "Delivery Charges: Rs. Z".
#    - There is usually a minimum order amount for free shipping. Mention it as "Free shipping over Rs. Z".

# 2. **Estimated Delivery Time:**
#    - If conflicting delivery times are found (e.g., policy page vs. product pages), prioritize the **policy page** and ignore product page delivery times.
#    - If there are different delivery times for different cities, then combine them into a single range. For example, "Delivery Time: 3-5 days (Metro cities) / 5-7 days (Rest of India)" should be mentioned as "Delivery Time: 3-7 days". Mention the different delivery times in the additional info section.

# 3. **Return Period:**
#    - This is the period within which the customer can return the item. Mention it as "Return Period: within X days".

# 4. **Return Methods:**
#    - If the brand arranges a pickup (e.g., "scheduled courier pickup" or "reverse logistics service"), classify it as **"Brand pickup"**. Mention return pickup charges if any.
#    - If the customer must ship the item themselves, classify it as **"Self-ship"**.
#    - If returns are only for exchanges, format as: "X days - exchanges only". If exchanges are size-only, format as: "X days - exchanges only (size only)".

# 5. **Refund Mode:**
#    - If refunds are to a bank account, state: "Refund in bank a/c".
#    - If refunds are as store credit, state: "Refund as store credit".
#    - Sometimes the brand may mention that refund will be made in the original mode of payment. In that case, mention it as "Refund in original mode of payment".
#    - If it exchanges only, mention it as "Refund as store credit (exchanges only)".

# 6. **Membership Information:**
#    - Ignore any delivery or return information related to memberships, loyalty programs, or subscription services. Do not include this in the response.

# 7. **Additional Info:**
#    - Include any delivery or return-related information that does not fit the structured format above.
#    - Do not include irrelevant details or duplicate information.

# 8. **DO NOT mention memberships, conflicting delivery times, or any irrelevant details in the response.**

# **No unnecessary details** should be included. Keep only what's relevant.
# Ensure **clarity and structured formatting** as per the above rules.
# ---

# Example Response:

# **Delivery:**
# - Delivery Charges: Rs. 199; Free over Rs. 999
# - Estimated Delivery Time: Within 3-7 days

# **Returns:**
# - Return Period: 30 days
# - Return Method: Brand pickup (Rs. 50 pickup charge)
# - Refund Mode: Refund in bank a/c

# **Additional Info:**
# - Returns only for defective items.
# - Delivery available only in select cities.
# """
