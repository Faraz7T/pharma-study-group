import streamlit as st
from groq import Groq
import os

st.set_page_config(
    page_title="اتاق مطالعه گروهی داروشناسی", 
    page_icon="💊", 
    layout="wide"
)

# دریافت کلید از Secrets
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not API_KEY:
    st.error("⚠️ کلید API پیدا نشد. لطفاً در بخش Settings -> Secrets استریم‌لیت کلید GROQ_API_KEY را وارد کنید.")
    st.stop()

client = Groq(api_key=API_KEY)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.header("⚙️ تنظیمات کاربری")
username = st.sidebar.text_input("نام شما:", value="دانشجوی داروسازی")
ask_ai = st.sidebar.checkbox("پاسخگویی هوشمند جین (AI)", value=True)

st.sidebar.markdown("---")
st.sidebar.info("💡 **اتاق مطالعه داروشناسی**")

st.title("👥 اتاق مطالعه و مباحثه داروشناسی با جین")

# نمایش پیام‌ها
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['user']}**: {msg['text']}")

# دریافت پیام جدید
if prompt := st.chat_input("سوال خود را بپرسید..."):
    st.session_state.chat_history.append({"role": "user", "user": username, "text": prompt})
    with st.chat_message("user"):
        st.markdown(f"**{username}**: {prompt}")

    if ask_ai:
        with st.chat_message("assistant"):
            with st.spinner("جین در حال تلاش برای پاسخگویی است..."):
                system_prompt = {
                    "role": "system",
                    "content": (
                        "You are 'Jean', a pharmacology expert for pharmacy students. "
                        "Always use English for drug names (Generic and Brand). "
                        "Provide concise, exam-oriented answers in Persian."
                    )
                }
                
                messages_to_send = [system_prompt]
                for m in st.session_state.chat_history[-6:]:
                    role = "assistant" if m["role"] == "assistant" else "user"
                    messages_to_send.append({"role": role, "content": f"{m['user']}: {m['text']}"})

                # لیست مدل‌های جایگزین (Fallback Mechanism)
                # اگر مدل اول خطا داد، مدل دوم را امتحان می‌کند
                models_to_try = [
                    "llama3-8b-8192", 
                    "llama3-70b-8192", 
                    "mixtral-8x7b-32768"
                ]
                
                success = False
                for model_name in models_to_try:
                    try:
                        response = client.chat.completions.create(
                            model=model_name,
                            messages=messages_to_send,
                            temperature=0.6,
                        )
                        ai_reply = response.choices[0].message.content
                        st.markdown(f"**جین (AI)**: {ai_reply}")
                        st.session_state.chat_history.append({"role": "assistant", "user": "جین (AI)", "text": ai_reply})
                        success = True
                        break # اگر موفق بود، از حلقه خارج شو
                    except Exception as e:
                        # اگر خطا داد، به مدل بعدی برو
                        continue 
                
                if not success:
                    st.error(f"❌ متاسفانه هیچ‌کدام از مدل‌ها پاسخ ندادند. خطای اصلی: \n `{st.session_state.chat_history[-1]['text']}`")
                    # نمایش خطا برای عیب‌یابی دقیق‌تر
                    st.write("تلاش برای اتصال به مدل‌ها با شکست مواجه شد. احتمالاً دسترسی به مدل‌ها محدود است.")
