import os, json, urllib.request, urllib.error
import streamlit as st
from datetime import date

st.set_page_config(page_title="NyayaAI | Consumer Help", page_icon="⚖️", layout="centered")
st.title("⚖️ NyayaAI")
st.caption("A practical first-step assistant for Indian online-shopping refund and defective-product disputes.")
st.warning("Not a lawyer or a substitute for legal advice. This prototype handles only ordinary consumer purchases in India. It does not file complaints or guarantee outcomes.")

LEGAL_SOURCES = [
    ("Consumer Protection Act, 2019", "https://www.indiacode.nic.in/indiacode/handle/123456789/15256"),
    ("Department of Consumer Affairs — Consumer Protection Acts and E-Commerce Rules", "https://consumeraffairs.gov.in/pages/consumer-protection-acts"),
    ("National Consumer Helpline", "https://consumerhelpline.gov.in/"),
    ("e-Jagriti consumer commission portal", "https://e-jagriti.gov.in/")
]

SYSTEM_PROMPT = """You are NyayaAI, a cautious Indian consumer-help assistant. Only help with online purchase refunds,
defective goods, wrong items, non-delivery, and e-commerce complaints in India. Ask concise factual questions.
Never invent legal sections, deadlines, case law, court fees, or outcomes. The only legal propositions you may
state are those in the supplied verified facts: the Consumer Protection Act 2019 applies to online transactions;
the National Consumer Helpline is a pre-litigation grievance channel; individual grievances can be registered
with NCH at 1915 or consumerhelpline.gov.in; consumer disputes may be filed through e-Jagriti. Clearly label
general information, distinguish facts from assumptions, and recommend a qualified lawyer for urgent,
high-value, criminal, cross-border, or complex matters. Do not claim to be a lawyer.
"""

def facts_from_text(text):
    t = text.lower()
    category = "refund"
    if any(x in t for x in ["not delivered", "not received", "delivery"]): category = "non_delivery"
    elif any(x in t for x in ["broken", "damaged", "defective", "not working"]): category = "defective"
    elif any(x in t for x in ["wrong item", "different item", "fake", "counterfeit"]): category = "wrong_item"
    elif any(x in t for x in ["refund", "money back", "cancelled", "canceled"]): category = "refund"
    amount = None
    import re
    m = re.search(r'(?:₹|rs\.?|inr)\s*([0-9,]+)', text, re.I)
    if m: amount = m.group(1).replace(",", "")
    return {"issue_type": category, "amount_inr": amount}

def build_guidance(issue, platform, order_date, complaint_date, evidence, description):
    issue_names = {"refund":"refund not received", "non_delivery":"order not delivered",
                   "defective":"defective/damaged product", "wrong_item":"wrong item received"}
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

def optional_llm_reply(user_text, facts):
    # Optional OpenAI-compatible endpoint. The app remains usable without credentials.
    endpoint = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1/chat/completions").rstrip("/")
    key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    if not key: return None
    payload = {"model": model, "temperature": 0.2, "messages":[
      {"role":"system","content":SYSTEM_PROMPT + "\nVerified links: " + json.dumps(LEGAL_SOURCES)},
      {"role":"user","content":f"User's description: {user_text}\nExtracted facts: {json.dumps(facts)}\nGive concise next-step guidance and ask at most two missing factual questions. Do not make unsupported legal claims."}
    ]}
    req = urllib.request.Request(endpoint + "/chat/completions", data=json.dumps(payload).encode(),
      headers={"Content-Type":"application/json","Authorization":"Bearer "+key}, method="POST")
    try:
      with urllib.request.urlopen(req, timeout=25) as r:
        data = json.loads(r.read().decode())
      return data["choices"][0]["message"]["content"]
    except Exception:
      return None

st.subheader("1. Tell us what happened")
description = st.text_area("Describe the purchase and problem in your own words", placeholder="Example: I ordered headphones for ₹3,499 on 2 November. The item arrived damaged. I contacted the app twice but have not received a replacement or refund.", height=130)
c1,c2 = st.columns(2)
with c1:
    consumer = st.text_input("Your name (optional)")
    city = st.text_input("City and State (optional)")
    platform = st.text_input("Shopping platform / seller")
    order_id = st.text_input("Order ID")
with c2:
    order_date = st.date_input("Order date", value=None)
    complaint_date = st.date_input("Date you first complained", value=None)
    amount = st.text_input("Amount paid (₹)")
    issue = st.selectbox("Main issue", ["refund", "non_delivery", "defective", "wrong_item"],
                         format_func=lambda x: {"refund":"Refund not received","non_delivery":"Order not delivered","defective":"Defective/damaged product","wrong_item":"Wrong item received"}[x])
evidence = st.text_input("Evidence you have (comma-separated)", placeholder="invoice, payment screenshot, chat transcript, product photos")
remedy = st.text_input("What outcome do you want?", placeholder="Full refund / replacement / delivery")
if st.button("Analyse my issue", type="primary", use_container_width=True):
    if not description.strip():
        st.error("Please describe what happened so the assistant can assess it.")
    else:
        facts = facts_from_text(description)
        result = build_guidance(issue, platform, str(order_date or ""), str(complaint_date or ""), evidence, description)
        llm = optional_llm_reply(description, facts)
        st.session_state["analysis"] = result
        st.session_state["llm"] = llm
        st.session_state["complaint"] = make_complaint(consumer, city, platform, order_id, issue, amount, str(order_date or ""), description, remedy)

if "analysis" in st.session_state:
    st.subheader("2. Suggested next steps")
    if st.session_state.get("llm"):
        st.markdown(st.session_state["llm"])
        st.caption("AI-generated explanation. Check it against the official sources below.")
    else:
        st.info("No AI API key configured. Showing the deterministic, source-grounded fallback workflow.")
    a = st.session_state["analysis"]
    st.write("**Issue identified:**", a["issue"])
    for i, step in enumerate(a["next_steps"], 1): st.write(f"{i}. {step}")
    st.write("**Evidence checklist**")
    for item in a["evidence_check"]: st.write("• " + item)
    st.write("**Legal context (limited):**")
    for item in a["legal_basis"]: st.write("• " + item)
    st.caption(a["caution"])
    st.subheader("3. Draft complaint")
    st.text_area("Editable draft — verify before sending", st.session_state["complaint"], height=300)
    st.download_button("Download complaint as .txt", st.session_state["complaint"], file_name="consumer_grievance_draft.txt")
    st.subheader("Official sources")
    for label,url in LEGAL_SOURCES: st.markdown(f"- [{label}]({url})")

with st.expander("Coverage and limitations"):
    st.markdown("""
- Covers only individual consumer purchases made online in India: refund, non-delivery, defective goods and wrong-item disputes.
- English-only in this MVP; voice input, document OCR, automatic evidence extraction and direct filing are not implemented.
- The optional language model drafts plain-language guidance only. The app's legal references and escalation links are controlled by a small verified source list.
- It does not decide jurisdiction, calculate limitation periods, assess complex liability, represent a user, or predict case outcomes.
- For urgent, high-value, complex, criminal or safety-related matters, consult a qualified lawyer.
""")
