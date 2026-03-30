# fairfight.py
import streamlit as st
import openai
import re
import base64
import json
import urllib.parse
from urllib.parse import urlencode
from datetime import datetime
from gtts import gTTS
import tempfile
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import uuid
import os

# ---------- Streamlit page config ----------
st.set_page_config(page_title="FairFight AI", page_icon="⚖️")

# ---------- Deterministic language detection ----------
DetectorFactory.seed = 0

# ---------- OpenAI setup ----------
openai.api_key = st.secrets["openai"]["api_key"]
openai.api_base = "https://api.openai.com/v1"

# ---------- Constants ----------
BASE_URL = "https://fairfight.streamlit.app"
PENDING_DB = "pending_cases.jsonl"   # stores step-1 payloads until step-2
VERDICTS_DB = "verdicts.jsonl"       # append-only log of delivered verdicts

# ---------- Helpers: robust Base64 (URL-safe) ----------
def b64url_encode(s: str) -> str:
    return base64.urlsafe_b64encode(s.encode("utf-8")).decode("utf-8").rstrip("=")

def b64url_decode(s: str) -> str:
    if not s:
        return ""
    s = s.replace(" ", "+")  # guard against clients turning + into space
    pad_len = (4 - len(s) % 4) % 4
    s += "=" * pad_len
    return base64.urlsafe_b64decode(s.encode("utf-8")).decode("utf-8")

# ---------- Helpers: query params (works on new/old Streamlit) ----------
def get_query_params():
    # st.query_params in newer Streamlit returns a Mapping[str, str]
    if hasattr(st, "query_params"):
        qp = st.query_params
        return {k: (v if isinstance(v, list) else [v]) for k, v in qp.items()}
    # Legacy fallback
    return st.experimental_get_query_params()

def qget(q, key, default=""):
    vals = q.get(key, [])
    if isinstance(vals, list):
        return vals[0] if vals else default
    return vals or default

# ---------- Persistence: append-only JSONL ----------
def _append_jsonl(path: str, record: dict):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        st.warning(f"⚠️ Could not write to {path}: {e}")

def _iter_jsonl(path: str):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except:
                continue

# ---------- Cases storage for Step 1 -> Step 2 handoff ----------
def save_case(payload: dict) -> str:
    token = uuid.uuid4().hex
    record = dict(payload)
    record["token"] = token
    record["created_at"] = datetime.utcnow().isoformat()
    _append_jsonl(PENDING_DB, record)
    return token

def load_case(token: str) -> dict | None:
    for rec in _iter_jsonl(PENDING_DB):
        if rec.get("token") == token:
            return rec
    return None

# ---------- Verdicts log ----------
def save_verdict(theme, user1_name, user2_name, user1_input, user2_input, verdict, **kwargs):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "theme": theme,
        "user1_name": user1_name,
        "user2_name": user2_name,
        "user1_input": user1_input,
        "user2_input": user2_input,
        "verdict": verdict,
        "meta": kwargs,
    }
    _append_jsonl(VERDICTS_DB, record)

# ---------- Link helpers ----------
def generate_mailto_link(email, subject, body):
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)
    return f"mailto:{email}?subject={subject}&body={body}"

def generate_whatsapp_link(phone, msg):
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    msg = urllib.parse.quote(msg)
    return f"https://wa.me/{phone}?text={msg}"

# ---------- JudgeBot core ----------
def analyze_conflict(user1_input, user2_input, theme, user1_name, user2_name):
    try:
        text_for_lang = (user1_input or "") + " " + (user2_input or "")
        text_for_lang = text_for_lang.strip() or "en"
        try:
            lang_code = detect(text_for_lang)
        except Exception:
            lang_code = "en"

        system_instruction = (
            "You are JudgeBot, an impartial AI judge. Analyze both sides carefully, "
            "highlight key arguments from each, and give a fair verdict. Clearly state "
            "who is more reasonable, and give a win percentage (e.g., 60% vs 40%). "
            "You should give the response in the user texted language"
        )

        try:
            system_instruction_translated = GoogleTranslator(source="en", target=lang_code).translate(system_instruction)
        except Exception:
            system_instruction_translated = system_instruction

        # Keep the user-facing message structure simple and neutral
        user_prompt = (
            f"{user1_name} says:\n{user1_input}\n\n"
            f"{user2_name} says:\n{user2_input}\n\n"
            "Who is more reasonable and why? Provide a win percentage as well."
        )

        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_instruction_translated},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content, lang_code
    except Exception as e:
        return f"❌ Error: {e}", "en"

# ---------- UI: Step 1 ----------
def step_1(theme):
    st.subheader(f"1️⃣ {theme} Conflict - Step 1: User 1")

    col1, col2 = st.columns(2)
    with col1:
        user1_name = st.text_input("🧑 User 1 Name")
        user1_email = st.text_input("📧 User 1 Email")
        user1_phone = st.text_input("📱 User 1 WhatsApp")
    with col2:
        user2_name = st.text_input("👩 User 2 Name")
        user2_email = st.text_input("📧 User 2 Email")
        user2_phone = st.text_input("📱 User 2 WhatsApp")

    user1_input = st.text_area("🧑 Describe your version")

    if st.button("📤 Generate link and send to User 2"):
        if not all([user1_name, user1_email, user2_name, user2_email, user1_input]):
            st.warning("⚠️ Please fill all required fields.")
            return

        # Save minimal payload server-side and send only a token
        token = save_case({
            "theme": theme,
            "user1_name": user1_name,
            "user1_email": user1_email,
            "user1_phone": user1_phone,
            "user2_name": user2_name,
            "user2_email": user2_email,
            "user2_phone": user2_phone,
            "user1_input": user1_input,
        })

        share_link = f"{BASE_URL}/?step=2&token={token}"
        st.success("✅ Link generated!")
        st.code(share_link, language="text")

        msg = (
            f"Hello {user2_name},\n\n"
            f"{user1_name} has submitted a conflict on FairFight AI.\n\n"
            f"Click to share your version and get JudgeBot's verdict:\n\n{share_link}\n\n"
            f"🤖 FairFight AI"
        )

        if user2_email:
            email_link = generate_mailto_link(user2_email, "FairFight Conflict", msg)
            st.markdown(f"[📧 Email to {user2_name}]({email_link})", unsafe_allow_html=True)

        if user2_phone:
            whatsapp_link = generate_whatsapp_link(user2_phone, msg)
            st.markdown(f"[📲 WhatsApp to {user2_name}]({whatsapp_link})", unsafe_allow_html=True)

        # (Optional) Also provide a base64 URL fallback for environments where writing files is blocked
        encoded_input = b64url_encode(user1_input)
        fallback_params = urlencode({
            "step": "2",
            "theme": theme,
            "user1_name": user1_name,
            "user2_name": user2_name,
            "user1_input": encoded_input,
            "user1_email": user1_email,
            "user2_email": user2_email,
            "user1_phone": user1_phone,
            "user2_phone": user2_phone,
        })
        fallback_link = f"{BASE_URL}/?{fallback_params}"
        with st.expander("Fallback link (URL-embedded data)"):
            st.code(fallback_link, language="text")
            st.caption("Use only if the main link fails. This one is longer and more fragile.")

# ---------- UI: Step 2 ----------
def step_2(data):
    st.subheader(f"2️⃣ {data.get('theme', 'Conflict')} - Step 2: {data.get('user2_name', 'User 2')} Responds")

    # Preferred: load via token
    token = data.get("token", "")
    record = load_case(token) if token else None

    if record:
        # From token record
        theme = record.get("theme", data.get("theme", "Conflict"))
        user1_name = record.get("user1_name", data.get("user1_name", "User 1"))
        user1_email = record.get("user1_email", data.get("user1_email", ""))
        user1_phone = record.get("user1_phone", data.get("user1_phone", ""))
        user2_name = record.get("user2_name", data.get("user2_name", "User 2"))
        user2_email = record.get("user2_email", data.get("user2_email", ""))
        user2_phone = record.get("user2_phone", data.get("user2_phone", ""))
        user1_input_decoded = record.get("user1_input", "")
    else:
        # Fallback: use query params (base64)
        theme = data.get("theme", "Conflict")
        user1_name = data.get("user1_name", "User 1")
        user1_email = data.get("user1_email", "")
        user1_phone = data.get("user1_phone", "")
        user2_name = data.get("user2_name", "User 2")
        user2_email = data.get("user2_email", "")
        user2_phone = data.get("user2_phone", "")
        try:
            user1_input_decoded = b64url_decode(data.get("user1_input", ""))
        except Exception:
            st.error("❌ The link appears corrupted. Ask User 1 to resend the link.")
            return

    st.markdown(f"**🧑 {user1_name} said:**")
    st.info(user1_input_decoded or "—")

    user2_input = st.text_area(f"👩 {user2_name}, your version")

    if st.button("🧠 Get Verdict from JudgeBot"):
        if not (user2_input or "").strip():
            st.warning("⚠️ Please enter your version before requesting the verdict.")
            return

        verdict, lang_code = analyze_conflict(user1_input_decoded, user2_input, theme, user1_name, user2_name)
        save_verdict(theme, user1_name, user2_name, user1_input_decoded, user2_input, verdict, token=token if record else None)

        st.success("✅ Verdict delivered!")
        st.markdown(verdict)

        # TTS (best-effort)
        try:
            tts = gTTS(text=verdict, lang=lang_code if lang_code else "en")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                tts.save(fp.name)
                st.audio(fp.name, format="audio/mp3")
        except Exception as e:
            st.warning(f"🔈 Could not generate speech: {e}")

        # Notify User 1
        msg = (
            f"Hello {user1_name},\n\n🎯 The conflict between you and {user2_name} "
            f"has been analyzed by JudgeBot.\n\nHere is the verdict:\n{verdict}\n\n"
            f"🤖 FairFight AI – Objective Conflict Resolution"
        )

        if user1_email:
            email_link = generate_mailto_link(user1_email, "FairFight AI Verdict", msg)
            st.markdown(f"[📧 Notify {user1_name} by Email]({email_link})", unsafe_allow_html=True)

        if user1_phone:
            whatsapp_link = generate_whatsapp_link(user1_phone, msg)
            st.markdown(f"[📲 Notify {user1_name} on WhatsApp]({whatsapp_link})", unsafe_allow_html=True)

# ---------- Main ----------
def main():
    st.title("🤖 FairFight AI")
    st.caption("Because every conflict deserves a fair verdict.")

    query = get_query_params()
    step = qget(query, "step", "1")

    if step == "2":
        # Collect everything we might need from query params
        keys = [
            "theme", "user1_name", "user2_name", "user1_input",
            "user1_email", "user2_email", "user1_phone", "user2_phone",
            "token"
        ]
        data = {k: qget(query, k, "") for k in keys}
        step_2(data)
    else:
        theme_choice = st.selectbox("Choose a conflict type:", ["Couple 💔", "Friends 🎭", "Pro 👨‍💼"])
        theme = theme_choice.split()[0]  # "Couple" | "Friends" | "Pro"
        step_1(theme)

if __name__ == "__main__":
    main()
