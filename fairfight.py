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

# ✅ Groq API credentials
openai.api_key = "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"
openai.api_base = "https://api.groq.com/openai/v1"

# ✅ Save verdicts to local JSON file
def save_verdict(theme, user1_name, user2_name, user1_input, user2_input, verdict, **kwargs):
    record = {
        "timestamp": datetime.utcnow().isoformat(),
        "theme": theme,
        "user1_name": user1_name,
        "user2_name": user2_name,
        "user1_input": user1_input,
        "user2_input": user2_input,
        "verdict": verdict,
        "meta": kwargs
    }
    try:
        with open("verdicts.json", "a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception as e:
        print("Error saving verdict:", e)

# 📧 Email link
def generate_mailto_link(email, subject, body):
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)
    return f"mailto:{email}?subject={subject}&body={body}"

# 📤 WhatsApp link
def generate_whatsapp_link(phone, msg):
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    msg = urllib.parse.quote(msg)
    return f"https://wa.me/{phone}?text={msg}"

# 🧠 Analyze conflict
def analyze_conflict(user1_input, user2_input, theme, user1_name, user2_name):
    system_prompt = (
        f"You are JudgeBot, an unbiased AI judge for {theme.lower()} conflicts. "
        "You must detect the language used by the participants and answer in the same language. "
        "Analyze both sides carefully, highlight key arguments from each party, and give a fair, neutral verdict. "
        "Clearly state who is more reasonable and provide a win percentage (e.g., 60% vs 40%)."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": f"{user1_name} says:\n{user1_input}\n\n"
                       f"{user2_name} says:\n{user2_input}\n\n"
                       f"Who is more reasonable and why? Show the win percentage too.",
        },
    ]

    try:
        response = openai.ChatCompletion.create(
            model="llama3-8b-8192",
            messages=messages,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"❌ Error: {e}"

# 🔁 Step 1 – User 1 inputs
def step_1(theme):
    st.subheader(f"1️⃣ {theme} Conflict - Step 1: User 1")

    user1_name = st.text_input("🧑 User 1 Name")
    user1_email = st.text_input("📧 User 1 Email")
    user1_phone = st.text_input("📱 User 1 WhatsApp")
    user2_name = st.text_input("👩 User 2 Name")
    user2_email = st.text_input("📧 User 2 Email")
    user2_phone = st.text_input("📱 User 2 WhatsApp")
    user1_input = st.text_area("🧑 Describe your version")

    if st.button("📤 Generate link and send to User 2"):
        if not all([user1_name, user1_email, user2_name, user2_email, user1_input]):
            st.warning("⚠️ Please fill all required fields.")
            return

        encoded_input = base64.urlsafe_b64encode(user1_input.encode()).decode()

        params = urlencode({
            "step": "2",
            "theme": theme.split()[0],
            "user1_name": user1_name,
            "user2_name": user2_name,
            "user1_input": encoded_input,
            "user1_email": user1_email,
            "user2_email": user2_email,
            "user1_phone": user1_phone,
            "user2_phone": user2_phone,
        })

        BASE_URL = "https://fairfight.streamlit.app"
        share_link = f"{BASE_URL}/?{params}"

        st.success("✅ Link generated!")
        msg = f"""Hello {user2_name},

{user1_name} has submitted a conflict on FairFight AI.

Click to share your version and get JudgeBot's verdict:

{share_link}

🤖 FairFight AI"""

        st.code(share_link)

        if user2_email:
            email_link = generate_mailto_link(user2_email, 'FairFight Conflict', msg)
            st.markdown(f"[📧 Email to {user2_name}]({email_link})", unsafe_allow_html=True)

        if user2_phone:
            whatsapp_link = generate_whatsapp_link(user2_phone, msg)
            st.markdown(f"[📲 WhatsApp to {user2_name}]({whatsapp_link})", unsafe_allow_html=True)

# 🧾 Step 2 – User 2 responds
def step_2(data):
    st.subheader(f"2️⃣ {data['theme']} Conflict - Step 2: {data['user2_name']} Responds")

    user1_input_decoded = base64.urlsafe_b64decode(data['user1_input']).decode()

    st.markdown(f"**🧑 {data['user1_name']} said:**")
    st.info(user1_input_decoded)

    user2_input = st.text_area(f"👩 {data['user2_name']}, your version")

    if st.button("🧠 Get Verdict from JudgeBot"):
        verdict = analyze_conflict(user1_input_decoded, user2_input, data['theme'], data['user1_name'], data['user2_name'])
        save_verdict(data['theme'], data['user1_name'], data['user2_name'], user1_input_decoded, user2_input, verdict)

        st.success("✅ Verdict delivered!")
        st.markdown(verdict)

        try:
            tts = gTTS(text=verdict)
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
                temp_audio_path = fp.name
                tts.save(temp_audio_path)
            st.audio(temp_audio_path, format="audio/mp3")
        except Exception as e:
            st.warning(f"🔈 Could not generate speech: {e}")

        msg = f"""Hello {data['user1_name']},

🎯 The conflict between you and {data['user2_name']} has been analyzed by JudgeBot.

Here is the verdict:
{verdict}

🤖 FairFight AI – Objective Conflict Resolution"""

        if data['user1_email']:
            email_link = generate_mailto_link(data['user1_email'], "FairFight AI Verdict", msg)
            st.markdown(f"[📧 Notify {data['user1_name']} by Email]({email_link})", unsafe_allow_html=True)

        if data['user1_phone']:
            whatsapp_link = generate_whatsapp_link(data['user1_phone'], msg)
            st.markdown(f"[📲 Notify {data['user1_name']} on WhatsApp]({whatsapp_link})", unsafe_allow_html=True)

# 🏠 Main entry point
def main():
    st.set_page_config(page_title="FairFight AI", page_icon="⚖️")
    st.title("🤖 FairFight AI")
    st.caption("Because every conflict deserves a fair verdict.")

    query = st.query_params
    step = query.get("step", ["1"])[0]

    if step == "2":
        keys = ["theme", "user1_name", "user2_name", "user1_input", "user1_email", "user2_email", "user1_phone", "user2_phone"]
        data = {k: query.get(k, [""])[0] for k in keys}
        step_2(data)
    else:
        theme = st.selectbox("Choose a conflict type:", ["Couple 💔", "Friends 🎭", "Pro 👨‍💼"])
        step_1(theme.split()[0])

if __name__ == "__main__":
    main()
