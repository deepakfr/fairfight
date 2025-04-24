import streamlit as st
import openai
import re
from urllib.parse import urlencode
import base64

# Optional: Save verdict (implement if using DB)
def save_verdict(theme, user1_name, user2_name, user1_input, user2_input, verdict, user1_email=None, user2_email=None, user1_phone=None, user2_phone=None):
    # Placeholder for saving data (could be Firebase, Supabase, SQLite, etc.)
    pass

# ✅ Groq API credentials
openai.api_key = st.secrets["GROQ_API_KEY"]
openai.api_base = "https://api.groq.com/openai/v1"

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

# 📊 Extract win %
def extract_percentages(verdict_text):
    match = re.findall(r"(\b\d{1,3})%", verdict_text)
    if len(match) >= 2:
        return int(match[0]), int(match[1])
    return None, None

# 📤 WhatsApp link
def generate_whatsapp_link(phone, msg):
    phone = phone.replace("+", "").replace("-", "").replace(" ", "")
    msg = msg.replace(" ", "%20").replace("\n", "%0A")
    return f"https://wa.me/{phone}?text={msg}"

# 📧 Email link
def generate_mailto_link(email, subject, body):
    subject = subject.replace(" ", "%20")
    body = body.replace(" ", "%20").replace("\n", "%0A")
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
            "theme": theme,
            "user1_name": user1_name,
            "user2_name": user2_name,
            "user1_input": encoded_input,
            "user1_email": user1_email,
            "user2_email": user2_email,
            "user1_phone": user1_phone,
            "user2_phone": user2_phone,
        })

        share_link = f"{st.request.url_root}?{params}"
        st.success("✅ Link generated!")

        msg = f"""Hello {user2_name},

{user1_name} has submitted a conflict on FairFight AI.

Click to share your version and get JudgeBot's verdict:

🔗 {share_link}

🤖 FairFight AI"""

        st.markdown("### 🔗 Share this link:")
        st.code(share_link)

        if user2_email:
            st.markdown(f"[📧 Email to {user2_name}]({generate_mailto_link(user2_email, 'FairFight Conflict', msg)})", unsafe_allow_html=True)
        if user2_phone:
            st.markdown(f"[📲 WhatsApp to {user2_name}]({generate_whatsapp_link(user2_phone, msg)})", unsafe_allow_html=True)

# 🧾 Step 2 – User 2 responds
def step_2(data):
    st.subheader(f"2️⃣ {data['theme']} Conflict - Step 2: {data['user2_name']} Responds")

    try:
        user1_input_decoded = base64.urlsafe_b64decode(data['user1_input'].encode()).decode()
    except Exception:
        user1_input_decoded = "[Error decoding User 1 input]"

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

            p1, p2 = extract_percentages(verdict)
            if p1 and p2:
                st.markdown("### 🏆 Victory Margin")
                st.progress(p1 / 100.0, f"{data['user1_name']}: {p1}%")
                st.progress(p2 / 100.0, f"{data['user2_name']}: {p2}%")

# 🏠 Main
def main():
    st.set_page_config(page_title="FairFight AI", page_icon="⚖️")
    st.title("🤖 FairFight AI")
    st.caption("Because every conflict deserves a fair verdict.")

    query = st.experimental_get_query_params()
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
