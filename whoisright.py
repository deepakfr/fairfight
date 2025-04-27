import streamlit as st
import openai
import re
import base64
import json
from urllib.parse import urlencode
from datetime import datetime

# ✅ Groq API credentials
openai.api_key = "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"
openai.api_base = "https://api.groq.com/openai/v1"

# ✅ Save verdicts to local JSON file (no database needed)
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

# 📊 Extract win % with name matching
def extract_percentages(verdict_text, user1_name, user2_name):
    pattern = rf"{re.escape(user1_name)}\s*[:\-]?\s*(\d{{1,3}})%.*?{re.escape(user2_name)}\s*[:\-]?\s*(\d{{1,3}})%"
    match = re.search(pattern, verdict_text, re.IGNORECASE)
    if match:
        return int(match.group(1)), int(match.group(2))

    pattern_rev = rf"{re.escape(user2_name)}\s*[:\-]?\s*(\d{{1,3}})%.*?{re.escape(user1_name)}\s*[:\-]?\s*(\d{{1,3}})%"
    match = re.search(pattern_rev, verdict_text, re.IGNORECASE)
    if match:
        return int(match.group(2)), int(match.group(1))

    return None, None


import urllib.parse

def generate_whatsapp_link(phone, msg):
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    msg = urllib.parse.quote(msg)
    return f"https://wa.me/{phone}?text={msg}"

def generate_mailto_link(email, subject, body):
    subject = urllib.parse.quote(subject)
    body = urllib.parse.quote(body)
    return f"mailto:{email}?subject={subject}&body={body}"


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

        st.markdown("### 🔗 Share this link:")
        st.code(share_link)

        if user2_email:
            email_link = generate_mailto_link(user2_email, 'FairFight Conflict', msg)
            st.markdown(f"[📧 Email to {user2_name}]({email_link})", unsafe_allow_html=True)

        if user2_phone:
            whatsapp_link = generate_whatsapp_link(user2_phone, msg)
            st.markdown(f"[📲 WhatsApp to {user2_name}]({whatsapp_link})", unsafe_allow_html=True)

def safe_base64_decode(encoded_str):
    padding_needed = 4 - (len(encoded_str) % 4)
    if padding_needed and padding_needed != 4:
        encoded_str += "=" * padding_needed
    return base64.urlsafe_b64decode(encoded_str).decode()

# Then in step_2:

# 🧾 Step 2 – User 2 responds
# 🧾 Step 2 – User 2 responds
def step_2(data):
    st.subheader(f"2️⃣ {data['theme']} Conflict - Step 2: {data['user2_name']} Responds")

    def safe_base64_decode(encoded_str):
        padding_needed = 4 - (len(encoded_str) % 4)
        if padding_needed and padding_needed != 4:
            encoded_str += "=" * padding_needed
        return base64.urlsafe_b64decode(encoded_str).decode()

    try:
        user1_input_decoded = safe_base64_decode(data['user1_input'])
    except Exception as e:
        st.error(f"❌ Error decoding input: {e}")
        return

    st.markdown(f"**🧑 {data['user1_name']} said:**")
    st.info(user1_input_decoded)

    user2_input = st.text_area(f"👩 {data['user2_name']}, your version")

    if st.button("🧠 Get Verdict from JudgeBot"):
        with st.spinner("JudgeBot is thinking..."):
            verdict = analyze_conflict(user1_input_decoded, user2_input, data['theme'], data['user1_name'], data['user2_name'])

            save_verdict(
                data['theme'], data['user1_name'], data['user2_name'],
                user1_input_decoded, user2_input, verdict,
                user1_email=data.get('user1_email'), user2_email=data.get('user2_email'),
                user1_phone=data.get('user1_phone'), user2_phone=data.get('user2_phone')
            )

            st.success("✅ Verdict delivered!")
            st.markdown("### 🧑‍⚖️ JudgeBot says:")
            st.markdown(verdict)

            p1, p2 = extract_percentages(verdict, data['user1_name'], data['user2_name'])
            if p1 is not None and p2 is not None:
                st.markdown("### 🏆 Victory Margin")
                st.progress(p1 / 100.0, f"{data['user1_name']}: {p1}%")
                st.progress(p2 / 100.0, f"{data['user2_name']}: {p2}%")



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
