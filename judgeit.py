import streamlit as st
from openai import OpenAI
import re
import base64
import json
import urllib.parse
from datetime import datetime
from gtts import gTTS
import tempfile
from langdetect import detect, DetectorFactory
from deep_translator import GoogleTranslator
import uuid
import os

# ---------- Streamlit page config ----------
st.set_page_config(page_title="FairFight AI", page_icon="⚖️", layout="centered")

# ---------- Deterministic language detection ----------
DetectorFactory.seed = 0

# ---------- DeepSeek Setup (Modern OpenAI v1.x Syntax) ----------
# ---------- API Setup ----------
DEEPSEEK_API_KEY = st.secrets.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY")

if not DEEPSEEK_API_KEY:
    st.error("❌ API key missing (Streamlit secrets or environment variable)")
    st.stop()

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

# ---------- Constants ----------
BASE_URL = "https://fairfight.streamlit.app"
PENDING_DB = "pending_cases.jsonl"   
VERDICTS_DB = "verdicts.jsonl"       

# ---------- Helpers: robust Base64 (URL-safe) ----------
def b64url_decode(s: str) -> str:
    if not s:
        return ""
    s = s.replace(" ", "+") 
    pad_len = (4 - len(s) % 4) % 4
    s += "=" * pad_len
    try:
        return base64.urlsafe_b64decode(s.encode("utf-8")).decode("utf-8")
    except:
        return ""

# ---------- Persistence: append-only JSONL ----------
def _append_jsonl(path: str, record: dict):
    try:
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception as e:
        st.warning(f"⚠️ Persistence error: {e}")

def _iter_jsonl(path: str):
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line: continue
            try:
                yield json.loads(line)
            except: continue

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

def save_verdict(theme, u1n, u2n, u1i, u2i, verdict, token):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "token": token,
        "theme": theme,
        "user1_name": u1n,
        "user2_name": u2n,
        "user1_input": u1i,
        "user2_input": u2i,
        "verdict": verdict,
    }
    _append_jsonl(VERDICTS_DB, record)

# ---------- Link helpers ----------
def generate_mailto_link(email, subject, body):
    return f"mailto:{email}?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"

def generate_whatsapp_link(phone, msg):
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    return f"https://wa.me/{phone}?text={urllib.parse.quote(msg)}"

# ---------- JudgeBot core (DeepSeek) ----------
def analyze_conflict(user1_input, user2_input, theme, user1_name, user2_name):
    try:
        text_for_lang = (user1_input or "") + " " + (user2_input or "")
        try:
            lang_code = detect(text_for_lang.strip() or "en")
        except:
            lang_code = "en"

        system_instruction = (
            "You are JudgeBot, an impartial AI judge. Analyze both sides carefully, "
            "highlight key arguments from each, and give a fair verdict. Clearly state "
            "who is more reasonable, and give a win percentage (e.g., 60% vs 40%). "
            "Respond in the same language as the users."
        )

        try:
            # Translating instructions to match user language for better prompt adherence
            system_instruction = GoogleTranslator(source="en", target=lang_code).translate(system_instruction)
        except: pass

        user_prompt = (
            f"Context: {theme} conflict.\n"
            f"{user1_name} says: {user1_input}\n\n"
            f"{user2_name} says: {user2_input}\n\n"
            "Provide a final verdict and the win percentage."
        )

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
        )
        return response.choices[0].message.content, lang_code
    except Exception as e:
        return f"❌ AI Error: {e}", "en"

# ---------- UI Sections ----------
def step_1(theme):
    st.subheader(f"⚖️ {theme} Dispute - Step 1")
    col1, col2 = st.columns(2)
    with col1:
        u1n = st.text_input("🧑 Your Name", placeholder="e.g. Alex")
        u1e = st.text_input("📧 Your Email")
        u1p = st.text_input("📱 Your WhatsApp (with country code)")
    with col2:
        u2n = st.text_input("👩 Opponent Name", placeholder="e.g. Sam")
        u2e = st.text_input("📧 Opponent Email")
        u2p = st.text_input("📱 Opponent WhatsApp")

    u1i = st.text_area("📝 Your side of the story", height=150)

    if st.button("🚀 Generate Case & Link"):
        if not all([u1n, u2n, u1i]):
            st.error("⚠️ Please provide names and your version of the story.")
            return

        token = save_case({
            "theme": theme, "user1_name": u1n, "user1_email": u1e, "user1_phone": u1p,
            "user2_name": u2n, "user2_email": u2e, "user2_phone": u2p, "user1_input": u1i,
        })

        share_link = f"{BASE_URL}/?step=2&token={token}"
        st.success("✅ Case Created! Send this link to your opponent:")
        st.code(share_link)

        msg = f"Hello {u2n}, {u1n} wants to resolve a {theme} conflict via AI Judge. Give your version here: {share_link}"
        
        c1, c2 = st.columns(2)
        if u2e: c1.markdown(f"[✉️ Email Opponent]({generate_mailto_link(u2e, 'FairFight Arbitration', msg)})", unsafe_allow_html=True)
        if u2p: c2.markdown(f"[💬 WhatsApp Opponent]({generate_whatsapp_link(u2p, msg)})", unsafe_allow_html=True)

def step_2(token):
    record = load_case(token)
    if not record:
        st.error("❌ Case not found or link expired.")
        return

    u1n, u2n, theme = record["user1_name"], record["user2_name"], record["theme"]
    u1i = record["user1_input"]

    st.subheader(f"⚖️ {theme} Dispute - Step 2")
    st.markdown(f"### 🧑 **{u1n}'s Version:**")
    st.info(u1i)

    st.markdown(f"### 👩 **{u2n}, it's your turn:**")
    u2i = st.text_area("📝 Describe your version of events", height=150)

    if st.button("⚖️ Get Final Verdict"):
        if not u2i.strip():
            st.warning("⚠️ You must enter your version to receive a verdict.")
            return

        with st.spinner("JudgeBot is deliberating..."):
            verdict, lang = analyze_conflict(u1i, u2i, theme, u1n, u2n)
            save_verdict(theme, u1n, u2n, u1i, u2i, verdict, token)

            st.divider()
            st.markdown("## 📜 The Verdict")
            st.write(verdict)

            # Text to Speech
            try:
                tts = gTTS(text=verdict, lang=lang)
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                    tts.save(fp.name)
                    st.audio(fp.name, format="audio/mp3")
            except Exception:
                pass

def main():
    st.title("🤖 FairFight AI")
    st.caption("Impartial, AI-powered conflict resolution.")

    # Handle query parameters
    params = st.query_params
    step = params.get("step")
    token = params.get("token")

    if step == "2" and token:
        step_2(token)
    else:
        choice = st.selectbox("What kind of conflict is this?", ["Couple 💔", "Friends 🎭", "Professional 👨‍💼"])
        step_1(choice.split()[0])

if __name__ == "__main__":
    main()