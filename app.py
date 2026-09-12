import os
import io
import streamlit as st
from PIL import Image, ImageDraw, ImageFont
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# ==========================================
# 1. API KEY CONFIGURATION
# ==========================================
GROQ_API_KEY = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))

# ==========================================
# 2. PAGE CONFIGURATION & STYLING
# ==========================================
st.set_page_config(page_title="AI Social Media Content Suite", page_icon="🚀", layout="wide")

st.markdown("""
    <style>
    .main-title { font-size: 2.3rem; font-weight: 800; color: #0F172A; }
    .sub-title { font-size: 1rem; color: #64748B; margin-bottom: 25px; }
    .stButton>button {
        background-color: #4F46E5; color: white; font-weight: 600;
        border-radius: 8px; padding: 0.65rem 1.2rem; border: none; width: 100%;
    }
    .stButton>button:hover { background-color: #4338CA; color: white; }
    .output-card {
        padding: 1.2rem; border-radius: 12px; background-color: #F8FAFC;
        border: 1px solid #E2E8F0; margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🚀 AI Social Media Post & Banner Generator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Generate high-converting social media captions, hashtags, and visual banners in seconds.</p>', unsafe_allow_html=True)

# ==========================================
# 3. BANNER GENERATOR FUNCTION
# ==========================================
def create_banner(title, subtitle, bg_color, text_color):
    width, height = 800, 800
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Decorative Design Elements
    draw.rectangle([40, 40, width - 40, height - 40], outline=text_color, width=4)
    draw.ellipse([width - 150, -50, width + 50, 150], fill=text_color)
    
    font_title = ImageFont.load_default()
    font_sub = ImageFont.load_default()

    def draw_wrapped_text(text, font, y_start, max_width=700):
        words = text.split()
        lines, current_line = [], ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = font.getbbox(test_line)
            if bbox[2] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        lines.append(current_line)
        
        y = y_start
        for line in lines:
            bbox = font.getbbox(line)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) / 2
            draw.text((x, y), line, fill=text_color, font=font)
            y += font.size + 15
        return y

    y_after_title = draw_wrapped_text(title.upper(), font_title, 280)
    draw_wrapped_text(subtitle, font_sub, y_after_title + 30)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

# ==========================================
# 4. USER INPUT CONTROLS
# ==========================================
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.markdown("### 🎯 Post Parameters")
    topic = st.text_input("Product / Topic Name:", placeholder="e.g., Midnight Cafe Special Coffee Offer")
    details = st.text_area("Key Details / Offer:", placeholder="e.g., Get 30% off on all cold brews this weekend. Use code COFFEE30.", height=100)
    
    col_a, col_b = st.columns(2)
    with col_a:
        platform = st.selectbox("Platform:", ["Instagram", "LinkedIn", "Twitter / X", "Facebook"])
        language = st.selectbox("Language:", ["English", "Roman Urdu", "English + Urdu Mix"])
    with col_b:
        tone = st.selectbox("Tone:", ["Promotional / Sales", "Professional", "Casual & Friendly", "Humorous / Funny"])
        theme_color = st.selectbox("Banner Theme:", ["Modern Dark (#0F172A)", "Brand Blue (#1E3A8A)", "Vibrant Purple (#581C87)", "Emerald Green (#064E3B)"])

    generate_btn = st.button("✨ Generate Post & Banner")

# ==========================================
# 5. GENERATION ENGINE
# ==========================================
with col2:
    st.markdown("### 📊 AI Generated Output")
    
    if generate_btn:
        if not topic or not details:
            st.warning("⚠️ Please fill in both Topic and Key Details first.")
        elif not GROQ_API_KEY:
            st.error("🔑 API Key nahi mili! Streamlit Secrets mein 'GROQ_API_KEY' set karein.")
        else:
            with st.spinner("🤖 Writing content & designing banner..."):
                try:
                    # Model name exactly updated for Groq
                    llm = ChatGroq(
                        api_key=GROQ_API_KEY, 
                        model="openai/gpt-oss-120b"
                    )
                    
                    system_prompt = (
                        f"You are a top-tier Social Media Manager specializing in {platform}.\n"
                        f"Write a high-converting post in {language} with a {tone} tone.\n\n"
                        "Format the output strictly as:\n"
                        "### 🪝 Attention Hook\n[Catchy opening line]\n\n"
                        "### 📝 Post Caption\n[Engaging caption with line breaks & emojis]\n\n"
                        "### 🏷️ Recommended Hashtags\n[8-10 relevant hashtags]"
                    )
                    
                    prompt = ChatPromptTemplate.from_messages([
                        ("system", system_prompt),
                        ("human", f"Topic: {topic}\nDetails: {details}"),
                    ])
                    
                    chain = prompt | llm
                    ai_response = chain.invoke({})
                    
                    st.markdown('<div class="output-card">', unsafe_allow_html=True)
                    st.markdown(ai_response.content)
                    st.markdown('</div>', unsafe_allow_html=True)

                    color_map = {
                        "Modern Dark (#0F172A)": ("#0F172A", "#F8FAFC"),
                        "Brand Blue (#1E3A8A)": ("#1E3A8A", "#FFFFFF"),
                        "Vibrant Purple (#581C87)": ("#581C87", "#F3E8FF"),
                        "Emerald Green (#064E3B)": ("#064E3B", "#ECFDF5")
                    }
                    bg_hex, text_hex = color_map[theme_color]

                    banner_bytes = create_banner(topic, details[:60] + "...", bg_hex, text_hex)
                    
                    st.markdown("### 🖼️ Auto-Generated Visual Banner")
                    st.image(banner_bytes, use_container_width=True)
                    st.download_button("📥 Download Banner Image", data=banner_bytes, file_name="social_banner.png", mime="image/png")

                except Exception as e:
                    st.error(f"Error: {str(e)}")

# ==========================================
