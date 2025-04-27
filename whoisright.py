import streamlit as st
import openai
import re
import base64
import json
from urllib.parse import urlencode
import urllib.parse
from datetime import datetime

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

# 🧠 Analyze conflict
def analyze_conflict(user1_input, user2_input, theme, user1_name, user2_name):
    system_prompt = (
        f"You are JudgeBot, an unbiased AI judge for {theme.lower()} conflicts. "
        "Analyze both sides, highlight key points, and give a fair verdict. "
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

    # Safe Base64 decoding
    def safe_base64_decode(encoded_str):
        padding_needed = 4 - (len(encoded_str) % 4)
        if padding_needed and padding_needed != 4:
            encoded_str += "=" * padding_needed
        return base64.urlsafe_b64decode(encoded_str.encode()).decode()

    try:
        user1_input_decoded = safe_base64_decode(data['user1_input'])
    except Exception as e:
        user1_input_decoded = "[Error decoding User 1 input]"
        st.error(f"❌ Error decoding input: {e}")

    st.markdown(f"**🧑 {data['user1_name']} said:**")
    st.info(user1_input_decoded)

    user2_input = st.text_area(f"👩 {data['user2_name']}, your version")

    if st.button("🧠 Get Verdict from JudgeBot"):
        with st.spinner("JudgeBot is thinking..."):
            verdict = analyze_conflict(user1_input_decoded, user2_input, data['theme'], data['user1_name'], data['user2_name'])
            save_verdict(data['theme'], data['user1_name'], data['user2_name'], user1_input_decoded, user2_input, verdict)
            st.success("✅ Verdict delivered!")
            st.markdown("### 🧑‍⚖️ JudgeBot says:")
            st.markdown(verdict)

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
