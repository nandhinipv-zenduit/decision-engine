from fastapi import FastAPI
import psycopg2
import os
import json
from openai import OpenAI

app = FastAPI()

# DATABASE
DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL)

# OPENAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ==============================
# PROMPT PLACEHOLDER
# ==============================

PROMPT_TEMPLATE = """
You are going to be provided information that will be helpful context in deciding values for parameters I am looking to populate. 
TICKET CONTENT:
{ticket_content}
Pick the closest match from the list of options for each of these parameters and respond in JSON. There may be instances where there is not enough information to decide in which case there are options available with Others reasons in each category. Try to avoid selecting None.


**keyword matching should be case-insensitive and across the full ticket content.

So let's say for instance if its a Medium Priority issue but none of the options apply you can select Medium :: Medium Impact Other. For nomenclature clarity `::` is a nesting of options within the first option. So from the example discussed above Medium Impact Other is a subcategory of Medium. 

Now that I have provided instructions and example for your understanding, here are the parameters and the options list to choose from. Your final response should be strictly in JSON format  :


Do not return markdown.
Do not return explanations outside JSON.
Do not invent values.
Do not modify option text.

1. Parameter name : Priority

Option list: (You can only pick one and the most relevant)
`
-None-
Critical :: Business Operations Halted
Critical :: Hardware Widespread Impact
Critical :: Software Widespread Impact
Critical :: Escalated by SLA Violation
Critical :: Enterprise Client Impact
Critical :: Critical Priority Other
High :: Business Severely Impacted
High :: Large Client Impact
High :: Software Impact Escalated
High :: Hardware Impact Escalated
High :: Feature Request Escalated
High :: High Impact Other
Medium :: Software Isolated Issue
Medium :: Hardware Isolated Issue
Medium :: Moderate Business Impact
Medium :: Medium Impact Other
Low :: General Question
Low :: Feature Request
Low :: General Feedback
Low :: General Admin Task
Low :: Low Impact Other
`


2.  Parameter name : Classification 

Option list: (You can only pick one and the most relevant)
`
-None-
Account Management :: Account Renewal
Account Management :: Contract Management
Account Management :: Device Reactivation
Account Management :: Device Reassignment/Movement
Account Management :: Device Suspension
Account Management :: Device Upgrade
Account Management :: Plan Change
Account Management :: Purchase Order to Fulfill
Billing :: Accounts Payable
Billing :: Accounts Recievable
Billing :: BIlling Accuracy
Billing :: Update Recurring Billing
Cancellations :: Cancelling 5 Plus
Cancellations :: Cancelling One HW Category
Cancellations :: Full Cancellation
Cancellations :: Less then 5
Cancellations :: Terminating Individual Device
Device Health Management :: Asset Tracker Not Communicating
Device Health Management :: Camera Not Communicating
Device Health Management :: One or More Channel Not Communicating
Device Health Management :: Camera Not Recording
Device Health Management :: Camera SD Card Issue
Device Health Management :: Geotab Device Not Communicating
Device Health Management :: Unable To Live Stream/Buffering
Device Health Management :: Video Request Unsuccessful
ELT Escalation :: Critical Failure
ELT Escalation :: Legal
ELT Escalation :: Other
Feature Request :: Asset Tracker Related
Feature Request :: General User Experience
Feature Request :: Mapping Related
Feature Request :: MyGeotab Related
Feature Request :: Performance Related
Feature Request :: Reporting Related
Feature Request :: Safety Related
Feature Request :: Security Related
Feature Request :: Work Related
Feedback :: Improvement Feedback
Feedback :: Positive Feedback for Reviews
Fulfillment :: Ordering Delay
Fulfillment :: Ordering Inquiry
Hardware Issue :: Connectivity Issue
Hardware Issue :: Data Quality Issue
Hardware Issue :: Data Storage Failure
Hardware Issue :: Device Installation
Hardware Issue :: Device Malfunction
Hardware Issue :: Existing Install Troubleshooting
Hardware Issue :: Firmware Update Failure
Hardware Issue :: Power Issue
Hardware Issue :: Recording Issue
Hardware Issue :: Signal Interference
Hardware Issue :: Transmission Delay
Hardware Setup :: Firmware Update
Hardware Setup :: HW Configuration
Hardware Setup :: Installation Request
Hardware Setup :: Installation Validation
Integration Issue :: Integration with Fiix/ZenduMA
Integration Issue :: Integration with Geotab
Integration Issue :: Integration with Zenduit
Integration Issue :: Other
Junk Notifications :: Customer Report Notifications
Junk Notifications :: Junk Mail
Junk Notifications :: Other
Managed Service :: Customer Business Review
Managed Service :: Video Review Service Request
Proactive :: Asset Tracker Not Communicating
Proactive :: Camera Not Communicating
Proactive :: Camera Not Recording
Proactive :: Geotab Not Communicating
Reseller :: Marketing Collateral Needed
Reseller :: Pricing Inquiry
Returns :: POC Return
Returns :: Warranty RMA Return
Sales :: New Product :: Asset Tracker
Sales :: New Product :: Camera
Sales :: New Product :: GPS
Security :: Documents Requested
Security :: Security Breach
Security :: Security Setup
Software Bug :: Camera Related :: No Hyperlapse
Software Bug :: Camera Related :: Video Request Failed
Software Bug :: Map UI Bug
Software Bug :: Mobile App :: Geotab Drive Add-In Module
Software Bug :: Mobile App :: Geotab Drive App
Software Bug :: Mobile App :: My Install Hub
Software Bug :: Mobile App :: ZenduONE App Login
Software Bug :: Reseller Admin :: Login
Software Bug :: Reseller Admin :: Reports
Software Bug :: Rule Trigger :: Failed to Get Notification
Software Bug :: Rule Trigger :: No Mobile Notification
Software Bug :: Rule Trigger :: Too Many Notifications
Software Bug :: ZenduONE App :: False Alerts or Notifications
Software Data Quality :: Data Usage
Software Data Quality :: Inaccurate Exception Data
Software Data Quality :: Inaccurate Measurements Data
Software Data Quality :: Inaccurate Rule Trigger
Software Data Quality :: Inaccurate Trip Report Data
Software Data Quality :: Incorrect ELD Violations :: Geotab
Software Data Quality :: Trips Inaccurate
Software Data Quality :: Video Quality Performing Poorly
Software Login :: MyGeotab Zenduit Add-In
Software Login :: Customer Login Issue
Software Login :: Geotab Drive
Software Login :: ZenduONE App
Software Performance :: Event Trigger Response Delay
Software Performance :: Map Loading Performance
Software Performance :: No Hyperlapse
Software Performance :: Reporting Slow Performance
Software Setup :: Geotab :: ELD
Software Setup :: Geotab :: General Account Setup
Software Setup :: Geotab :: Grouping Related
Software Setup :: Geotab :: HOS
Software Setup :: Geotab :: Public Works
Software Setup :: Reporting :: Custom Reporting
Software Setup :: Reporting :: Idling Report
Software Setup :: Reporting :: Safety Report
Software Setup :: Teltonika :: Wifi Update
Software Setup :: Zendu Maintenance
Software Setup :: ZenduMAP
Software Setup :: ZenduOne :: Cameras
Software Setup :: ZenduOne :: General Account Setup
Software Setup :: ZenduOne :: Grouping Related
Software Setup :: ZenduOne :: Indoor
Software Setup :: ZenduOne :: Work
Software UI :: Access Issue :: Mobile App Login
Software UI :: Reports :: Safety
Software UI :: Work :: Dispatching
Software UI :: Work :: Route Optimization
Training :: Geotab :: ELD
Training :: Geotab :: MyGeotab Platform
Training :: Geotab :: Public Works
Training :: Hardware Install and Troubleshooting
Training :: Internal Product Training
Training :: Reseller Product Training
Training :: Zendu Maintenance
Training :: ZenduOne :: General Training
Training :: ZenduOne :: Video Safety Training
Training :: ZenduOne :: Work Dispatching
`

3. Parameter name : Hardware Associated

Option list: (You can only pick one and the most relevant)
`
-None-
Cameras :: Surfsight
Cameras :: Streamax/ZenduCAM
Cameras :: Sensata / Smartwitness
Asset Trackers :: Topfly
Asset Trackers :: Globalstar
Asset Trackers :: Queclink
OBDii Trackers :: Geotab
Routers :: Teltonika
Routers :: Mokosmart
Routers :: Aruba
Beacons :: KKM
Phone :: Sold Tablets
Phone :: Employee Owned Smartphone
SIM Provider :: 1nce
SIM Provider :: Flolive


Prerequisite : The parameter `Hardware Associated` has some caveats to note. 

	1. You will only proceed to provide a selction among Option values for the parameter - "Hardware Associated" if you see any of the below selections for Option values for "Classification" parameter. If Hardware Associated not applicable, then 

"hardware_associated":"",
"reason_hardware_associated":"Not applicable based on classification.",
"hardware_confidence":0

	Here are those specific selections for Options values of "Classification" parameter that enables "Hardware Associated" to be provided with a value.

	`
	Account Management :: Device Reactivation
	Account Management :: Device Suspension
	Account Management :: Device Upgrade
	Account Management :: Plan Change
	Cancellations :: Cancelling 5 Plus
	Cancellations :: Cancelling One HW Category
	Cancellations :: Full Cancellation
	Cancellations :: Less then 5
	Cancellations :: Terminating Individual Device
	Device Health Management :: Asset Tracker Not Communicating
	Device Health Management :: Camera Not Communicating
	Device Health Management :: One or More Channel Not Communicating
	Device Health Management :: Camera Not Recording
	Device Health Management :: Camera SD Card Issue
	Device Health Management :: Geotab Device Not Communicating
	Device Health Management :: Unable To Live Stream/Buffering
	Device Health Management :: Video Request Unsuccessful
	Fulfillment :: Ordering Delay
	Fulfillment :: Ordering Inquiry
	Hardware Issue :: Connectivity Issue
	Hardware Issue :: Data Quality Issue
	Hardware Issue :: Data Storage Failure
	Hardware Issue :: Device Installation
	Hardware Issue :: Device Malfunction
	Hardware Issue :: Existing Install Troubleshooting
	Hardware Issue :: Firmware Update Failure
	Hardware Issue :: Power Issue
	Hardware Issue :: Recording Issue
	Hardware Issue :: Signal Interference
	Hardware Issue :: Transmission Delay
	Hardware Setup :: Firmware Update
	Hardware Setup :: HW Configuration
	Hardware Setup :: Installation Request
	Hardware Setup :: Installation Validation
	Proactive :: Geotab Not Communicating
	Returns :: POC Return
	Returns :: Warranty RMA Return
	Software Bug :: Rule Trigger :: Failed to Get Notification
	Software Bug :: Rule Trigger :: No Mobile Notification
	Software Bug :: Rule Trigger :: Too Many Notifications
	Software Data Quality :: Inaccurate Rule Trigger
	Training :: Hardware Install and Troubleshooting
	`


	2. There is a very small subset of Options values from "Classification" that leads to a different set of values for "Hardware Associated" parameter. Here are those scenarios

		i)If any of these values determined from Options list of "Classifications"

		`
		Proactive :: Asset Tracker Not Communicating
		`

		Then select the following from the "Hardware Associated" 

		`
		Asset Trackers :: Topfly
		Asset Trackers :: Globalstar
		Asset Trackers :: Queclink
		`

		ii)If any of these values determined from Options list of "Classifications"

		`
		Proactive :: Camera Not Communicating
		Proactive :: Camera Not Recording
		`

		Then select the following from the "Hardware Associated" 

		`
		Cameras :: Surfsight
		Cameras :: Streamax/ZenduCAM
		Cameras :: Sensata / Smartwitness
	`


4. Parameter name : Pod
Option list:
-None-
Brand and Communications
Marketplace and Integrations
Platform
Proactive Churn and Loyalty
Safety and Video
Sales and Shipping
Service Delivery
Service Reliability
Vehicles and Assets
Workforce Experience
`


5️. CONFIDENCE RULES

Return decimal values between 0 and 1:

classification_confidence
priority_confidence
hardware_confidence
pod_confidence

Confidence scores must reflect the clarity and strength of evidence in the ticket content.

Use the following guidelines:

0.90–1.00 → Explicit and clearly stated request
0.75–0.89 → Strong contextual match
0.50–0.74 → Some ambiguity
0.30–0.49 → Weak or partial evidence
0 → Not applicable

Rules:

classification_confidence must reflect how clearly the ticket matches the selected classification.

priority_confidence must reflect how clearly severity is indicated.

hardware_confidence must be 0 if hardware_associated is empty.


pod_confidence must reflect how clearly the ticket matches the selected Pod.



Do not return percentages.

Do not exceed 1.00.

Do not return null.

Confidence scores must be internally consistent. High classification_confidence requires clear ticket wording.

KNOWLEDGE BASE INPUT (DETERMINISTIC)

You will receive the following pre-selected Knowledge Base fields:

kb_title

kb_solution_id

kb_content

kb_score

These values are already the highest score match.

Do NOT compare scores.
Do NOT select from an array.
Do NOT modify these values.

Simply:

Return kb_title as provided

Return kb_solution_id as provided

Return kb_content as provided

Return kb_score as provided

Set kb_confidence equal to kb_score


Do NOT return the full object or any extra keys. Only these four fields in "knowledgebase_articles".


6. Evidence Snippets
- Include the most relevant text from the ticket that justifies your selections
- Return as a string (or array if preferred)





-----------------------------------------------------------

7. REASON FIELDS

reason_priority → simple explanation (max 25 words).
reason_classification → simple explanation (max 25 words).
reason_hardware_associated → explain hardware choice or state not applicable.






7. AI FLAG RULES

ai_priority → "True" if priority selected.
ai_classifications → "True" if classification selected.
ai_hardware_associated → "True" only if hardware_associated populated.
ai_next_steps → "True" only if summary/next steps provided in user content.

Otherwise mark as "False".


8. Triage Required
- Set triage_required = Yes if any confidence < 0.5 or kb_gap = Yes; else No


10. KB Gap
- Set kb_gap = Yes if kb_score < 0.5 or no KB article matches; else No


11. JUNK EMAIL BUSINESS RULE

If sender email ends with @gmail.com:

Evaluate content relevance.

Mark as junk ONLY if:

Promotional

Spam-like

Unrelated to fleet tracking hardware/software/billing/training/services


There are some business rules that you need to keep in mind and check if these apply to those situations. These are situations with predefined option selection and actions:

1. Determine whether or not this is a junk email. If the sender's email ends with @gmail.com, there is a high probability it is a spam email. To check whether or not it is a spam email, read through the contents and check it's relevance with the company. To provide a brief context GoFleet and Zenduit provide trackers (as seen from options under Hardware Associated list) to track fleet logistics. Now an email directed to this company specifically to this service desk department will have enquiries about hardware or processes laid in the Hardware Associated and Classification parameters. 

Additionally, It also becomes apparent from comparing the parameter options for classification and hardware associated whether the sender's email is junk or not. If determined as junk, populate the following values as shown in json. The values provided needs to be as is. For other fields leave them empty except the ones that have instructions within () on what needs to be provided as a reponse.
{{
"priority":"Low :: Low Impact Other",
"reason_priority":"Email appears promotional or unrelated to fleet tracking services and does not require operational attention.",
"classification":"Junk Notifications :: Junk Mail",
"reason_classification":"Content is unrelated to GoFleet/Zenduit services and matches spam or promotional patterns.",
"hardware_associated":"",
"reason_hardware_associated":"",
"kb_title":"",
"kb_solution_id":"",
"kb_content":"",
"kb_score":0,
"kb_confidence":0,
"pod":"",
"classification_confidence":0.95,
"priority_confidence":0.95,
"pod_confidence":0,
"hardware_confidence":0,
"evidence_snippets":"",
"kb_gap":No,
"triage_required":No,
"ai_priority":"",
"ai_classifications":"",
"ai_hardware_associated":"",
"ai_next_steps":""
}}
Stop processing.
------------------------------------------------------------

**LOW-PRIORITY KEYWORD OVERRIDE:**  
Before deciding any priority based on context, check if the ticket content contains any of the following keywords (case-insensitive):  
"general question", "inquiry", "feedback", "non-urgent", "info request", "promotion", "spam", "newsletter", "advertisement".  
If any of these keywords are present, automatically set:  


"priority":"Low :: Low Impact Other",
"reason_priority":"Ticket content matches low-priority keywords.",
"priority_confidence":0.95,
"ai_priority":"True"

If LOW-PRIORITY KEYWORD OVERRIDE applies,
ignore contextual priority logic entirely.


Finally, I need you to repond to the above questions strictly in JSON format only. Remember each of the values for should not have multiple comma separated option values, they need to be 1 value each. For example: This is not allowed

`hardware_associated: "Cameras :: Surfsight, Cameras :: Streamax/ZenduCAM, Cameras :: Sensata / Smartwitness" `

It needs to be one value only(depending on whether it's applicable) for example: `hardware_associated: "Cameras :: Surfsight"` 

Similarly for other values in JSON this needs to be followed.


Return minified JSON:

{{
"priority":"",
"reason_priority":"",
"classification":"",
"reason_classification":"",
"hardware_associated":"",
"reason_hardware_associated":"",
"pod":"",
"kb_title":"",
"kb_solution_id":"",
"kb_content":"",
"kb_score":0,
"classification_confidence":0,
"priority_confidence":0,
"pod_confidence":0,
"hardware_confidence":0,
"kb_confidence":0,
"evidence_snippets":"",
"kb_gap":No,
"triage_required":No,
"ai_priority":"True",
"ai_classifications":"True",
"ai_hardware_associated":"",
"ai_next_steps":""
}}
If uncertain, select the closest "Other" option within the correct severity or category tier.
FINAL OUTPUT RULES

Return STRICT JSON only.

Do not return markdown.
Do not return explanations.
Do not include backticks.
Do not include comments.
Do not include trailing commas.

Your response must be valid JSON parsable by a standard JSON parser.

If a value is not applicable return an empty string "" or 0 depending on the field type.

Return minified JSON in one line.

The first character must be { 
The last character must be }
"""

# ==============================
# HEALTH CHECK
# ==============================

@app.get("/")
def read_root():
    return {"status": "API running"}

# ==============================
# CLASSIFICATION ENDPOINT
# ==============================

@app.post("/enrich")
def enrich(
    ticket_id: str,
    message: str,
    kb_title: str = "",
    kb_solution_id: str = "",
    kb_content: str = "",
    kb_score: float = 0
):

    # Build prompt
prompt = PROMPT_TEMPLATE

prompt = prompt.replace("{ticket_content}", message)
prompt = prompt.replace("{kb_title}", kb_title)
prompt = prompt.replace("{kb_solution_id}", kb_solution_id)
prompt = prompt.replace("{kb_content}", kb_content)
prompt = prompt.replace("{kb_score}", str(kb_score))

    # Call OpenAI
    response = client.responses.create(
        model="gpt-4.1-mini",
        temperature=0,
        input=prompt
    )

    ai_text = response.output_text

    # Convert JSON string → dictionary
    ai_result = json.loads(ai_text)

    # Extract fields
    priority = ai_result.get("priority")
    classification = ai_result.get("classification")
    hardware_associated = ai_result.get("hardware_associated")
    pod = ai_result.get("pod")

    classification_confidence = ai_result.get("classification_confidence")
    priority_confidence = ai_result.get("priority_confidence")
    hardware_confidence = ai_result.get("hardware_confidence")
    pod_confidence = ai_result.get("pod_confidence")

    kb_confidence = ai_result.get("kb_confidence")
    kb_gap = ai_result.get("kb_gap")
    triage_required = ai_result.get("triage_required")

    evidence_snippets = ai_result.get("evidence_snippets")

    # Save to Postgres
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO decision_events
        (
            ticket_id,
            classification,
            priority,
            pod,
            classification_confidence,
            priority_confidence,
            pod_confidence,
            hardware_confidence,
            kb_confidence,
            kb_gap,
            triage_required,
            evidence_snippets
        )
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            ticket_id,
            classification,
            priority,
            pod,
            classification_confidence,
            priority_confidence,
            pod_confidence,
            hardware_confidence,
            kb_confidence,
            kb_gap,
            triage_required,
            json.dumps(evidence_snippets)
        )
    )

    conn.commit()
    cur.close()
    conn.close()

    return ai_result
