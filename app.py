import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# Cấu hình trang
st.set_page_config(page_title="AI Video Tool", layout="wide")

# --- QUẢN LÝ API ---
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Nhập Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Vui lòng cấu hình API Key để bắt đầu.")
    st.stop()

genai.configure(api_key=api_key)

@st.cache_resource
def load_gemini():
    try:
        # Sử dụng đúng tên model chuẩn
        m = genai.GenerativeModel('gemini-1.5-flash')
        return m
    except Exception as e:
        st.error(f"Lỗi khởi tạo Model: {e}")
        return None

model = load_gemini()

# --- TRẠNG THÁI (SESSION STATE) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None
if 'final_script' not in st.session_state: st.session_state.final_script = []

# --- HÀM TRỢ GIÚP ---
def safe_parse_json(text):
    try:
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return None

# --- GIAO DIỆN CHÍNH ---

# BƯỚC 1: TẠO Ý TƯỞNG
if st.session_state.step == 1:
    st.header("Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", placeholder="Ví dụ: Phim hoạt hình về GaiO và Bibi...")
        c1, c2 = st.columns(2)
        style = c1.selectbox("Phong cách", ["Hoạt hình 3D", "Anime", "Cyberpunk"])
        qty = c2.number_input("Số lượng", 1, 5, 3)
        
        if st.button("Tạo câu chuyện", type="primary"):
            if not topic:
                st.error("Vui lòng nhập nội dung!")
            else:
                with st.spinner("Đang xử lý..."):
                    prompt = f"Tạo {qty} ý tưởng phim {style} về {topic}. Trả về JSON list: [{{'title': '...', 'summary': '...'}}]"
                    res = model.generate_content(prompt)
                    data = safe_parse_json(res.text)
                    if data:
                        st.session_state.stories = data
                        st.session_state.step = 2
                        st.rerun()

# BƯỚC 2: CHỌN CÂU CHUYỆN
elif st.session_state.step == 2:
    st.header("Bước 2: Chọn câu chuyện")
    if st.button("← Quay lại Bước 1"):
        st.session_state.step = 1
        st.rerun()
        
    for idx, s in enumerate(st.session_state.stories):
        with st.container(border=True):
            st.subheader(f"{idx+1}. {s['title']}")
            st.write(s['summary'])
            if st.button(f"Chọn câu chuyện {idx+1}", key=f"btn_{idx}"):
                st.session_state.selected_story = s
                st.session_state.step = 3
                st.rerun()

# BƯỚC 3: NHÂN VẬT & KỊCH BẢN
elif st.session_state.step == 3:
    st.header("Bước 3: Chỉnh sửa nhân vật & Tạo kịch bản")
    if st.button("← Quay lại Bước 2"):
        st.session_state.step = 2
        st.rerun()
        
    col_l, col_r = st.columns([1, 1])
    with col_l:
        st.subheader("Nhân vật")
        name = st.text_input("Tên nhân vật", "Mamala")
        desc = st.text_area("Mô tả ngoại hình", "Mèo xám phong cách hoạt hình 3D...")
        st.image("https://via.placeholder.com/300?text=Preview", use_container_width=True)
        
    with col_r:
        st.subheader("Cài đặt")
        time_vid = st.number_input("Thời lượng (phút)", 1, 12, 3)
        context = st.text_area("Bối cảnh", "Trong một khu rừng kỳ ảo...")
        
        if st.button("Tạo kịch bản chi tiết", type="primary"):
            with st.spinner("Đang tạo kịch bản..."):
                prompt = f"Viết kịch bản {time_vid} phút cho: {st.session_state.selected_story['title']}. Nhân vật {name} ({desc}). Bối cảnh {context}. Trả về JSON list các cảnh: [{{'STT': 1, 'MÔ TẢ': '...', 'VEO_PROMPT': '...', 'KIỂM TRA': 'Có'}}]"
                res = model.generate_content(prompt)
                data = safe_parse_json(res.text)
