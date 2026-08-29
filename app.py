import streamlit as st
from groq import Groq
import os

st.set_page_config(
    page_title="اتاق مطالعه گروهی داروشناسی", 
    page_icon="💊", 
    layout="wide"
)

# خواندن امن کلید از Secrets استریم‌لیت
API_KEY = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")

if not API_KEY:
    st.error("⚠️ کلید API پیدا نشد. لطفاً در بخش Settings -> Secrets استریم‌لیت کلید GROQ_API_KEY را وارد کنید.")
    st.stop()

# اتصال به موتور هوش مصنوعی پرسرعت
client = Groq(api_key=API_KEY)

# حافظه چت در طول نشست
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.sidebar.header("⚙️ تنظیمات کاربری")
username = st.sidebar.text_input("نام شما:", value="دانشجوی داروسازی")
ask_ai = st.sidebar.checkbox("پاسخگویی هوشمند جین (AI)", value=True)

st.sidebar.markdown("---")
st.sidebar.info(
    "💡 **اتاق مطالعه داروشناسی و آمادگی آزمون**\n\n"
    "سوالات داروشناسی، طبقه‌بندی داروها و نکات آزمون تکنسین داروخانه را اینجا بنویسید."
)

st.title("👥 اتاق مطالعه و مباحثه داروشناسی با جین")

# نمایش تاریخچه پیام‌ها
for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(f"**{msg['user']}**: {msg['text']}")

# دریافت پیام جدید کاربر
if prompt := st.chat_input("سوال داروشناسی، نکته درسی یا پیام خود را بنویسید..."):
    # ثبت پیام کاربر
    st.session_state.chat_history.append({"role": "user", "user": username, "text": prompt})
    with st.chat_message("user"):
        st.markdown(f"**{username}**: {prompt}")

    # پردازش توسط جین
    if ask_ai:
        with st.chat_message("assistant"):
            with st.spinner("جین در حال تحلیل علمی و آماده‌سازی پاسخ..."):
                system_prompt = {
                    "role": "system",
                    "content": (
                        "تو 'جین' هستی؛ یک متخصص برجسته داروشناسی، فارماکولوژی، پرستاری و راهنمای ارشد آزمون تکنسین داروخانه. "
                        "پاسخ‌هایت باید فوق‌العاده علمی، دقیق، ساختاریافته با بولت‌پوینت و متمرکز بر نکات تستی آزمون تکنسین داروخانه باشد. "
                        "قانون مهم: تمام نام‌های ژنریک و تجاری داروها، دسته‌بندی‌ها و اصطلاحات دارویی حتماً باید به زبان انگلیسی (English) نوشته شوند "
                        "(مثلاً Diphenhydramine، Loratadine، Drowsiness). "
                        "لحن شما مشوق، دانشگاهی و متمرکز بر آمادگی آزمون باشد."
                    )
                }
                
                messages_to_send = [system_prompt]
                for m in st.session_state.chat_history[-8:]:
                    role = "assistant" if m["role"] == "assistant" else "user"
                    messages_to_send.append({"role": role, "content": f"{m['user']}: {m['text']}"})

                try:
                    # استفاده از مدلی که قطعاً در دسترس است
                    response = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=messages_to_send,
                        temperature=0.6,
                    )
                    ai_reply = response.choices[0].message.content
                    st.markdown(f"**جین (AI)**: {ai_reply}")
                    st.session_state.chat_history.append({"role": "assistant", "user": "جین (AI)", "text": ai_reply})
                except Exception as e:
                    st.error(f"❌ خطای دریافت پاسخ:\n\n`{e}`")
