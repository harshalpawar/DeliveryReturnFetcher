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
Your purpose is to extract and format the delivery and return policy of a fashion brand in India based on the provided text. Follow these steps meticulously and provide your response in TWO parts:

**Step 1: Understand the Goal and Format**
PART 1: Detailed Output with Sources
Format your findings exactly as follows:

**Delivery:**
- Delivery Charges: Rs. X; Free over Rs. Y (or "Free shipping")
  Source: [exact snippet from text]
- Estimated Delivery Time: Within B days OR A-B days
  Source: [exact snippet from text]

**Returns:**
- Return Period: Within X days (or "X days - exchanges only", "X days - exchanges only (size only)", "X days - exchanges only (defect only)")
  Source: [exact snippet from text]
- Return Method: Brand pickup / Self-ship / Return in store (mention return pickup charges if any)
  Source: [exact snippet from text]
- Refund Mode: Bank a/c / Store credit / Original mode of payment / Other (Omit if exchange only)
  Source: [exact snippet from text]

**Additional Info:**
- [Relevant details not fitting above]
  Source: [exact snippet from text]

PART 2: JSON Summary
After providing the detailed output above, provide a clean JSON object without the sources, formatted as follows:

```json
{
  "Delivery": {
    "Delivery Charges": "Rs. X; Free over Rs. Y",
    "Estimated Delivery Time": "Within B days"
  },
  "Returns": {
    "Return Period": ["Within X days", "X days - return and exchange", "X days - exchanges only", "X days - exchanges only (size only)", "X days - exchanges only (defect only)"],
    "Return Method": ["Brand pickup", "Self-ship", "Return in store"],
    "Refund Mode": ["Bank a/c", "Store credit", "Original mode of payment", "Other"]
  }
  },
  "Additional Info": [
    "Relevant detail 1",
    "Relevant detail 2"
  ]
}
```
Ensure that all time periods are in days. Convert hours to days if necessary.
You must ignore information related to international shipping, memberships, loyalty programs, or subscription services.
Omit refund mode if exchange only.
If original mode of payment is available, then don't mention other refund modes in the JSON summary.
Include return charges if any in the JSON summary. For example, "Return Method: Brand pickup (Rs. 50 pickup charge)"

**Step 2: Extract Delivery Charges**
- Find the standard delivery charge. Format as "Rs. X".
- Find the minimum order value for free shipping. Format as "; Free over Rs. Y".
- If shipping is always free, state "Free shipping".
- Combine these into the "Delivery Charges:" line.
- Include the exact text snippet from which this information was extracted, prefixed with "Source:".

**Step 3: Extract and Calculate Estimated Delivery Time**
- Locate the estimated delivery times for domestic orders within India. Ignore international delivery times.
- **Prioritize information from the main policy page** over product page examples if conflicts exist.
- If different times are given for different regions (e.g., metros vs. rest of India), find the minimum and maximum values across all domestic regions to create a single range (e.g., 3-5 days and 5-7 days becomes "3-7 days"). Note the regional differences in Step 7 (Additional Info).
- If dispatch time and delivery time are mentioned separately, add them together to get the total estimated delivery time.
- Ensure the final time is expressed in **days** (convert hours if necessary, e.g., 48 hours = 2 days).
- Format as "Within B days" or "A-B days".
- Include the exact text snippet from which this information was extracted, prefixed with "Source:".

**Step 4: Extract Return Period and Conditions**
- Find the number of days within which a customer can initiate a return or exchange.
- Ensure the final time is expressed in **days** (convert hours if necessary, e.g., 48 hours = 2 days).
- If regular returns are allowed, format as "Within X days".
- If both returns and exchanges are allowed, then mention it as "X days - return and exchange".
- Check if returns are only for exchange.
  - If yes, check if it's size-only exchange or defect-only exchange.
  - Format accordingly: "X days - exchanges only", "X days - exchanges only (size only)", or "X days - exchanges only (defect only)".
- Include the exact text snippet from which this information was extracted, prefixed with "Source:".

**Step 5: Determine Return Method(s)**
- Identify how the customer returns the item:
  - If the brand arranges pickup (e.g., "scheduled courier", "reverse logistics"), classify as **"Brand pickup"**. Note any associated pickup charges (e.g., "Brand pickup (Rs. 50 pickup charge)").
  - If the customer must ship it back themselves, classify as **"Self-ship"**.
  - If the customer can return it to a physical store, classify as **"Return in store"**.
- If there is a charge associated with returns, mention it as "Return Method: Brand pickup (Rs. X return charge)".
- List all applicable methods found.
- Include the exact text snippet from which this information was extracted, prefixed with "Source:".

**Step 6: Determine Refund Mode**
- **If Step 4 indicated "exchanges only", skip this step and omit the "Refund Mode" line in the final output.**
- Otherwise, identify how the refund is processed:
  - To a bank account: "Bank a/c"
  - As store credit: "Store credit"
  - To the original payment method: "Original mode of payment"
  - Other specified modes: Describe briefly (e.g., "Wallet transfer")
- If original mode of payment is available, then don't mention other refund modes in the JSON summary.
- If refund is exclusive to defective items, then mention it as "Refund Mode: Original mode of payment (defective items only)" in the JSON summary.
- Format as "Refund Mode: [Result]".
- Include the exact text snippet from which this information was extracted, prefixed with "Source:".

**Step 7: Collate Additional Information**
- Review the source text again.
- Identify any other relevant delivery or return details that were not captured in the structured fields above (e.g., specific conditions for returns like "only for defective items", delivery restrictions like "only in select cities", regional delivery time differences noted in Step 3).
- **Crucially, do NOT include:**
  - Information already captured in the structured fields.
  - Details about memberships, loyalty programs, international shipping.
  - Conflicting delivery times that were discarded in Step 3.
  - General marketing text or irrelevant details.
- List these points under "Additional Info:".
- For each point, include the exact text snippet from which this information was extracted, prefixed with "Source:".

**Step 8: Assemble Part 1 - Detailed Textual Response**
- Combine the results from Steps 2 through 7 into a detailed, human-readable format.
- Ensure each piece of information is followed by its source snippet.
- Organize the information under the main sections: Delivery, Returns, and Additional Info.
- Double-check that all rules have been followed and no forbidden information is included.
- Prioritize clarity, readability, and comprehensive explanation.

**Step 9: Assemble Part 2 - JSON Summary**
- Create a structured JSON representation of the extracted policy information.
- Ensure the JSON matches the format shown in the example output.
- Include only the key information from the detailed textual response.
- Validate that the JSON is concise, well-structured, and captures the essential policy details.
- Omit source snippets from the JSON to keep it clean and readable.

Example Output:
**Delivery:**
- Delivery Charges: Rs. 99; Free over Rs. 999
  Source: "Standard delivery charges of Rs. 99 apply to all orders. Orders above Rs. 999 qualify for free shipping."
- Estimated Delivery Time: 3-7 days
  Source: "For metro cities, your order will reach you within 3-5 working days. For other cities, delivery takes 5-7 working days."

**Returns:**
- Return Period: Within 7 days - exchanges only (size only)
  Source: "We accept size exchanges within 7 days of delivery. No returns or refunds are available at this time."
- Return Method: Brand pickup (Rs. 50 pickup charge)
  Source: "Once your exchange is approved, we will schedule a pickup. A convenience fee of Rs. 50 will be charged for the pickup service."
- Refund Mode: Store credit
  Source: "For any approved returns, you will receive store credit that can be used for future purchases."

**Additional Info:**
- Cash on Delivery available for orders under Rs. 10,000
  Source: "Cash on Delivery (COD) payment option is available for orders valued up to Rs. 10,000"
- Metro cities have priority delivery
  Source: "We offer priority delivery in metro cities including Delhi NCR, Mumbai, Bangalore, Chennai, and Kolkata"

```json
{
  "Delivery": {
    "Delivery Charges": "Rs. 99; Free over Rs. 999",
    "Estimated Delivery Time": "3-7 days"
  },
  "Returns": {
    "Return Period": "Within 7 days - exchanges only (size only)",
    "Return Method": "Brand pickup (Rs. 50 pickup charge)",
    "Refund Mode": "Store credit"
  },
  "Additional Info": [
    "Cash on Delivery available for orders under Rs. 10,000",
    "Metro cities have priority delivery"
  ]
}
```
"""

GEMINI_VERIFICATION_PROMPT = """
Your purpose is to verify the accuracy of scraped delivery and return policies for a fashion brand in India and assign an accuracy code (Green, Yellow, Red) based on potential customer impact. You will be given a scraped data summary and the relevant text extracted from the brand's website. Follow these steps meticulously:

**Step 1: Understand the Goal, Inputs, Outputs, and Accuracy Codes**

*   **Goal:** Verify the accuracy of the scraped policy data against the source website text and classify the accuracy level.
*   **Inputs:**
    1.  **Scraped Data Summary:** A JSON summary of the delivery and return policy extracted previously.
    2.  **Website Text:** The raw text extracted from the brand's delivery and return policy pages.
*   **Accuracy Codes:**
    *   **Green:** The scraped data is accurate or has only minor, insignificant discrepancies (e.g., wording differences like "7 days" vs. "Within 7 days") that do not change the policy's meaning or impact the customer.
    *   **Yellow:** Some details in the scraped data are incorrect or missing, but the core policy information is mostly right. These errors might cause minor confusion but are unlikely to lead to significant customer detriment (e.g., delivery estimate off by 1-2 days, a secondary return method missed, slightly inaccurate refund mode description but core type correct). Warrants review but might not require immediate action.
    *   **Red:** Significant errors or omissions in the scraped data that *will likely mislead or negatively impact the customer*. This includes incorrect return periods, wrong free shipping thresholds, missed exchange-only conditions, incorrect refund modes (e.g., showing 'Bank a/c' when it's 'Store Credit only'), missing significant fees, or completely wrong delivery times. **Requires human review and correction.**
*   **Output Format:** Your final output *must* be in one of the following forms:

    *   **If Green:**
        ```json
        {
          "Accuracy Code": "Green",
          "Assessment": "The scraped data is accurate based on the provided website text."
        }
        ```

    *   **If Yellow:**
        ```json
        {
          "Accuracy Code": "Yellow",
          "Assessment": "The scraped data has minor inaccuracies or omissions unlikely to cause significant customer issues.",
          "Corrections": {
            // Only include fields that are incorrect or missing
            "Delivery": {
              "Delivery Charges": "Corrected Value",
              // ... other corrected delivery fields
            },
            "Returns": {
              "Return Period": "Corrected Value",
              // ... other corrected return fields
            },
            "Additional Info": [
              "Corrected or missing info 1",
              // ...
            ]
          },
          "Supporting Snippets": {
            // Field name maps to the snippet supporting its correction
            "Delivery Charges": "Relevant excerpt about delivery charges",
            "Return Period": "Relevant excerpt about return period",
            "Additional Info 1": "Relevant excerpt for additional info 1"
            // ... other snippets for each correction
          }
        }
        ```

    *   **If Red:**
        ```json
        {
          "Accuracy Code": "Red",
          "Assessment": "The scraped data has significant inaccuracies or omissions likely to mislead or negatively impact the customer. Human review required.",
          "Corrections": {
             // Only include fields that are incorrect or missing
            "Delivery": {
              "Delivery Charges": "Corrected Value",
              // ... other corrected delivery fields
            },
            "Returns": {
              "Return Period": "Corrected Value",
              // ... other corrected return fields
            },
            "Additional Info": [
              "Corrected or missing info 1",
              // ...
            ]
          },
          "Supporting Snippets": {
            // Field name maps to the snippet supporting its correction
            "Delivery Charges": "Relevant excerpt about delivery charges",
            "Return Period": "Relevant excerpt about return period",
            "Additional Info 1": "Relevant excerpt for additional info 1"
            // ... other snippets for each correction
          }
        }
        ```

*   **Constraints:** Ignore information related to international shipping, memberships, loyalty programs, or subscription services. Focus solely on standard domestic delivery and return policies.

**Step 2: Analyze the Scraped Data Summary**

*   Parse the input JSON "Scraped Data Summary". Identify the values provided for each key field (Delivery Charges, Estimated Delivery Time, Return Period, Return Method, Refund Mode, Additional Info).

**Step 3: Cross-Reference with Website Text**

*   For *each* field present in the "Scraped Data Summary," meticulously search the "Website Text" for corroborating information.
*   For fields *not* present in the summary (e.g., maybe Refund Mode was omitted because it was thought to be exchange-only), check the "Website Text" to see if they *should* have been included.
*   Pay close attention to numerical values (days, amounts), conditions (exchange-only, size-only), methods (pickup, self-ship), and modes (bank, credit).

**Step 4: Identify Discrepancies and Missing Information**

*   Compare the value from the "Scraped Data Summary" with the information found in the "Website Text" for each field.
*   Note any direct contradictions (e.g., scraped says "15 days", text says "10 days").
*   Note any missing information in the scraped data that is clearly present and relevant in the text (e.g., scraped data omits a Rs. 100 pickup fee mentioned in the text).
*   Note any information present in the scraped data that *cannot* be substantiated by the website text.

**Step 5: Categorize Accuracy (Apply Green/Yellow/Red Logic)**

*   Based on the discrepancies and their potential customer impact, assign the appropriate code:
    *   **Green:** No discrepancies found, or only trivial wording differences.
    *   **Yellow:** Discrepancies exist but are minor (e.g., delivery time off by a day, missing a secondary return option, refund mode slightly mislabeled but functionally similar). Customer unlikely to be significantly harmed.
    *   **Red:** Major discrepancies exist (e.g., wrong return window, wrong free shipping threshold, missed exchange-only rule, wrong refund type like bank vs. credit, missing significant fees). High potential for customer confusion or negative experience.

**Step 6: Generate Corrections and Supporting Snippets (If Yellow or Red)**

*   If the code is Yellow or Red, construct the "Corrections" object.
    *   Include *only* the fields that were found to be inaccurate or were missing from the scraped data but present in the text.
    *   Use the correct values derived directly from the "Website Text".
    *   Format the corrected values according to the original extraction prompt's guidelines (e.g., "Rs. X; Free over Rs. Y", "A-B days", "Within X days - exchanges only").
*   Construct the "Supporting Snippets" object.
    *   For *each* field included in the "Corrections" object, provide the *exact*, concise snippet from the "Website Text" that justifies the correction.
    *   Use clear keys in the "Supporting Snippets" object that map directly to the corrected fields (e.g., "Delivery Charges", "Return Period", "Additional Info 1").

**Step 7: Assemble the Final JSON Response**

*   Combine the "Accuracy Code", "Assessment", and (if applicable) "Corrections" and "Supporting Snippets" into the final JSON output, strictly adhering to the format defined in Step 1 for the determined accuracy code.

---

Now, provide the **Scraped Data Summary** (as a JSON object) and the **Website Text**. I will follow these steps to generate the verification response.
"""
