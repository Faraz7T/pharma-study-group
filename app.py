import streamlit as st
from openai import OpenAI
import os

st.set_page_config(
    page_title="اتاق مطالعه گروهی داروشناسی", 
    page_icon="💊", 
    layout="wide"
)

# بررسی و دریافت کلید امنیتی از Secrets استریم‌لیت یا متغیر محیطی
API_KEY = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("⚠️ کلید API پیدا نشد! لطفاً OPENAI_API_KEY را در بخش Secrets استریم‌لیت تنظیم کنید.")
    st.stop()

client = OpenAI(api_key=API_KEY)

# حافظه نشست پیام‌ها
if "messages" not in st.session_state:
    st.session_state.messages = []

# تنظیمات سایدبار
st.sidebar.header("⚙️ تنظیمات کاربری")
username = st.sidebar.text_input("نام شما:", value="دانشجوی داروسازی")
ask_ai = st.sidebar.checkbox("پاسخگویی هوشمند جین (AI)", value=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **اتاق مطالعه گروهی Health-Tech**\n\n"
    "این فضا برای بررسی داروهای آزمون تکنسین داروخانه، دسته‌بندی‌های دارویی و تست‌زنی طراحی شده است."
)

st.title("👥 اتاق مطالعه داروشناسی با جین")

# نمایش پیام‌های قبلی
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['user']}**: {msg['text']}")

# دریافت پیام جدید
if prompt := st.chat_input("سوال داروشناسی یا پیام خود را بنویسید..."):
    # نمایش پیام کاربر
    st.session_state.messages.append({"role": "user", "user": username, "text": prompt})
    with st.chat_message("user"):
        st.markdown(f"**{username}**: {prompt}")

    # پردازش پاسخ جین
    if ask_ai:
        with st.chat_message("assistant"):
            with st.spinner("جین در حال بررسی منابع و پاسخ‌گویی..."):
                system_prompt = {
                    "role": "system",
                    "content": (
                        "تو 'جین' هستی؛ دستیار تخصصی داروشناسی و پرستاری برای آزمون تکنسین داروخانه. "
                        "پاسخ‌هایت باید کاملاً علمی، متمرکز بر نکات امتحانی، دسته‌بندی‌ها، تداخلات و عوارض باشد. "
                        "نام تمام داروها را حتماً به صورت انگلیسی بنویس."
                    )
                }
                
                messages_to_send = [system_prompt]
                for m in st.session_state.messages[-8:]:
                    role = "assistant" if m["role"] == "assistant" else "user"
                    messages_to_send.append({"role": role, "content": f"{m['user']}: {m['text']}"})

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_to_send
                    )
                    ai_reply = response.choices[0].message.content
                    st.markdown(f"**جین (AI)**: {ai_reply}")
                    st.session_state.messages.append({"role": "assistant", "user": "جین (AI)", "text": ai_reply})
                except Exception as err:
                    st.error(f"⚠️ خطای OpenAI رخ داد: {err}")
