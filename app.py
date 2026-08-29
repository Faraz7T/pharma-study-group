import streamlit as st
from openai import OpenAI
import os

st.set_page_config(
    page_title="اتاق مطالعه گروهی داروشناسی", 
    page_icon="💊", 
    layout="wide"
)

# خواندن امن کلید از Secrets استریم‌لیت
API_KEY = st.secrets.get("OPENAI_API_KEY") or os.environ.get("OPENAI_API_KEY")

if not API_KEY:
    st.error("⚠️ کلید OpenAI هنوز در بخش Secrets استریم‌لیت ست نشده است.")
    st.stop()

client = OpenAI(api_key=API_KEY)

@st.cache_resource
def get_chat_history():
    return []

chat_history = get_chat_history()

st.sidebar.header("⚙️ تنظیمات کاربری")
username = st.sidebar.text_input("نام شما:", value="دانشجوی داروسازی")
ask_ai = st.sidebar.checkbox("پاسخگویی هوشمند جین (AI)", value=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **اتاق مطالعه گروهی Health-Tech**\n\n"
    "این فضا برای بررسی داروهای آزمون تکنسین داروخانه، فرمولاسیون‌ها، دسته‌بندی‌های دارویی و تست‌زنی مشترک طراحی شده است."
)

st.title("👥 اتاق مطالعه و مباحثه داروشناسی با جین")

for msg in chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['user']}**: {msg['text']}")

if prompt := st.chat_input("سوال داروشناسی، نکته درسی یا پیام خود را بنویسید..."):
    chat_history.append({"role": "user", "user": username, "text": prompt})
    
    with st.chat_message("user"):
        st.markdown(f"**{username}**: {prompt}")

    if ask_ai:
        with st.chat_message("assistant"):
            with st.spinner("جین در حال تحلیل و پاسخ‌گویی..."):
                system_prompt = {
                    "role": "system",
                    "content": (
                        "تو 'جین' هستی؛ یک متخصص داروشناسی، فارماکولوژی، پرستاری و دستیار هوشمند مطالعه گروهی. "
                        "مخاطبان تو دانشجویان داروسازی و پرستاری هستند که برای آزمون تکنسین داروخانه و آزمون‌های بالینی آماده می‌شوند. "
                        "پاسخ‌هایت باید کاملاً علمی، متمرکز بر نکات تستی، دسته‌بندی‌های دارویی و فرم‌های دارویی باشد. "
                        "حتماً نام ژنریک و تجاری داروها را به زبان انگلیسی (English) بنویس و ساختار پاسخ‌ها را با بولت‌پوینت و خوانا ارائه بده."
                    )
                }
                
                messages_to_send = [system_prompt]
                for m in chat_history[-10:]:
                    role = "assistant" if m["role"] == "assistant" else "user"
                    messages_to_send.append({"role": role, "content": f"{m['user']}: {m['text']}"})

                try:
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=messages_to_send,
                        temperature=0.7
                    )
                    ai_reply = response.choices[0].message.content
                    st.markdown(f"**جین (AI)**: {ai_reply}")
                    chat_history.append({"role": "assistant", "user": "جین (AI)", "text": ai_reply})
                except Exception as e:
                    st.error(f"خطایی رخ داد: {e}")
    
    st.rerun()