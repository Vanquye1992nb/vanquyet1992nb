import streamlit as st
import google.generativeai as genai
import json
import pandas as pd
import time

# --- CẤU HÌNH HỆ THỐNG ---
st.set_page_config(page_title="Veo 3 Automation Tool", layout="wide")

# Hàm lấy API Key an toàn
def get_api_key():
    if "GEMINI_API_KEY" in st.secrets:
        return st.secrets["GEMINI_API_KEY"]
    return st.sidebar.text_input("Nhập Gemini API Key:", type="password")

api_key = get_api_key()

if api_key:
    genai.configure(api_key=api_key)
    # Sử dụng 'gemini-1.5-flash' để có tốc độ nhanh và ổn định
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.warning("⚠️ Vui lòng nhập API Key ở thanh bên để bắt đầu.")
    st.stop()

# Khởi tạo Session State để lưu dữ liệu qua các bước
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None
if 'characters' not in st.session_state: st.session_state.characters = {"name": "Mamala", "prompt": ""}

# --- HÀM TRỢ GIÚP (HELPER) ---
def parse_ai_json(text):
    """Làm sạch và parse JSON từ AI để tránh lỗi markdown"""
    try:
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except:
        return None

# --- GIAO DIỆN TỪNG BƯỚC ---

# BƯỚC 1: TẠO Ý TƯỞNG
if st.session_state.step == 1:
    st.markdown("### Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", 
                             placeholder="Ví dụ: phim hoạt hình phiêu lưu về cậu bé GaiO và robot Bibi...")
        col1, col2 = st.columns(2)
        style = col1.selectbox("Phong cách", ["Hoạt hình 3D", "Anime", "Cyberpunk", "Disney Style"])
        quantity = col2.number_input("Số lượng câu chuyện", 1, 5, 3)
        
        if st.button("Tạo câu chuyện", type="primary"):
            with st.spinner("AI đang lên ý tưởng..."):
                prompt = f"Tạo {quantity} ý tưởng phim {style} về {topic}. Trả về JSON list: [{{'title': '...', 'summary': '...'}}]"
                res = model.generate_content(prompt)
                data = parse_ai_json(res.text)
                if data:
                    st.session_state.stories = data
                    st.session_state.step = 2
                    st.rerun()
                else:
                    st.error("AI không trả về đúng định dạng. Hãy thử lại!")

# BƯỚC 2: CHỌN CÂU CHUYỆN
elif st.session_state.step == 2:
    st.markdown("### Bước 2: Chọn câu chuyện & Tạo nhân vật")
    if st.button("← Quay lại"): st.session_state.step = 1; st.rerun()
    
    for idx, s in enumerate(st.session_state.stories):
        with st.container(border=True):
            st.subheader(f"{idx+1}. {s['title']}")
            st.write(s['summary'])
            if st.button(f"Chọn câu chuyện này", key=f"btn_{idx}"):
                st.session_state.selected_story = s
                st.session_state.step = 3
                st.rerun()

# BƯỚC 3: CHI TIẾT NHÂN VẬT & KỊCH BẢN
elif st.session_state.step == 3:
    st.markdown("### Bước 3: Chỉnh sửa nhân vật & Cấu hình kịch bản")
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Nhân vật")
        st.session_state.characters["name"] = st.text_input("Tên nhân vật", st.session_state.characters["name"])
        char_desc = st.text_area("Mô tả ngoại hình (Prompt)", 
                                 "Mèo xám, mắt xanh lá, phong cách 3D, mặc áo choàng đỏ...")
        st.session_state.characters["prompt"] = char_desc
        st.image("https://via.placeholder.com/300?text=Character+Preview", use_container_width=True)

    with col_right:
        st.subheader("Cài đặt kịch bản")
        duration = st.slider("Thời lượng video (phút)", 1, 12, 3)
        env = st.text_area("Môi trường chủ đạo", "Rừng nguyên sinh sao Hỏa, ánh sáng tím...")
        
        if st.button("Tạo kịch bản chi tiết", type="primary"):
            with st.spinner("Đang xây dựng 90 cảnh phim..."):
                prompt = f"""Dựa trên chuyện '{st.session_state.selected_story['title']}', 
                nhân vật {st.session_state.characters['name']} ({char_desc}), bối cảnh {env}. 
                Hãy tạo kịch bản {duration} phút. Trả về JSON list các cảnh:
                [{{'STT': 1, 'MO_TA': '...', 'VEO_PROMPT': '...', 'NHAN_VAT': 'Có'}}]"""
                res = model.generate_content(prompt)
                st.session_state.final_script = parse_ai_json(res.text)
                st.session_state.step = 4
                st.rerun()

# BƯỚC 4: KẾT QUẢ CUỐI CÙNG
elif st.session_state.step == 4:
    st.success("✅ Kịch bản đã sẵn sàng!")
    df = pd.DataFrame(st.session_state.final_script)
    st.table(df)
    
    col1, col2 = st.columns(2)
    if col1.button("Tạo kịch bản mới"): st.session_state.step = 1; st.rerun()
    col2.download_button("Tải File Prompts (.csv)", df.to_csv(index=False), "script.csv", "text/csv")
