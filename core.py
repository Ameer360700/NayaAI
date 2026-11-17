"""Deterministic, dependency-free logic used by NyayaAI."""
import re

def facts_from_text(text):
    t = text.lower()
    category = "refund"
    if any(x in t for x in ["not delivered", "not received", "delivery"]): category = "non_delivery"
    elif any(x in t for x in ["broken", "damaged", "defective", "not working"]): category = "defective"
    elif any(x in t for x in ["wrong item", "different item", "fake", "counterfeit"]): category = "wrong_item"
    elif any(x in t for x in ["refund", "money back", "cancelled", "canceled"]): category = "refund"
    amount = None
    m = re.search(r'(?:₹|rs\.?|inr)\s*([0-9,]+)', text, re.I)
    if m: amount = m.group(1).replace(",", "")
    return {"issue_type": category, "amount_inr": amount}

def build_guidance(issue, platform, order_date, complaint_date, evidence, description):
    issue_names = {"refund":"refund not received", "non_delivery":"order not delivered", "defective":"defective/damaged product", "wrong_item":"wrong item received"}
    evidence_list = [x.strip() for x in evidence.split(",") if x.strip()]
    return {
      "issue": issue_names.get(issue, issue),
      "next_steps": [
        "Save the order confirmation, invoice, payment proof, product photos/video (if relevant), and all support chats/emails.",
        "Write to the seller and the platform's grievance officer using the contact details shown on the platform; state the remedy requested and give a clear response date.",
        "If unresolved, register a pre-litigation grievance with the National Consumer Helpline at 1915 or https://consumerhelpline.gov.in/.",
        "If still unresolved, review filing options on https://e-jagriti.gov.in/ and consider advice from a qualified consumer-law practitioner."
      ],
      "evidence_check": evidence_list if evidence_list else ["No evidence listed yet — add invoice/order ID, payment proof, and written communications."],
      "legal_basis": [
        "The Consumer Protection Act, 2019 includes online transactions within consumer protection.",
        "The Consumer Protection (E-Commerce) Rules, 2020 provide a framework for e-commerce consumer grievances."
      ],
      "caution": "This is general information, not a legal opinion. The facts, seller/platform role, transaction type and current rules may change the available remedy."
    }

def make_complaint(name, city, platform, order_id, issue, amount, order_date, description, remedy):
    return f"""To: Customer Support / Grievance Officer, {platform or '[Platform name]'}

Subject: Formal grievance regarding {issue.replace('_',' ')} — Order {order_id or '[Order ID]'}

I, {name or '[Consumer name]'}, residing in {city or '[City, State]'}, am raising a grievance regarding an online purchase.

Order details:
• Order ID: {order_id or 'Not provided'}
• Order date: {order_date or 'Not provided'}
• Amount paid: {amount or 'Not provided'}
• Issue: {issue.replace('_',' ')}
• Description: {description or 'Please insert a factual description.'}

I request that you investigate this grievance and provide the following remedy:
{remedy or 'Please provide the appropriate remedy, such as refund, replacement or delivery, as applicable.'}

Please acknowledge this grievance and respond in writing. I have retained the available order, payment and communication records and can provide copies.

Regards,
{name or '[Consumer name]'}
{city or '[City, State]'}

Before sending: verify every fact, attach supporting records, and keep proof of submission. This draft is not a court pleading or legal notice.
"""
