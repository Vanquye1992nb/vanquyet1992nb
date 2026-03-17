import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- CẤU HÌNH GIAO DIỆN DARK MODE ---
st.set_page_config(page_title="Hệ thống sản xuất Video AI", layout="wide")

# --- QUẢN LÝ API ---
st.sidebar.title("Cấu hình hệ thống")
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Nhập Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Vui lòng nhập API Key để bắt đầu.")
    st.stop()

# Khởi tạo AI với cơ chế bắt lỗi chi tiết
genai.configure(api_key=api_key)

@st.cache_resource
def init_model():
    # Thử model 1.5 Flash vì nó nhanh và hỗ trợ tốt nhất hiện nay
    model_name = 'gemini-1.5-flash'
    try:
        m = genai.GenerativeModel(model_name)
        # Thử một lệnh siêu nhỏ để check quyền
        m.generate_content("Hi") 
        return m, model_name, None
    except Exception as e:
        return None, None, str(e)

model, active_model, error_msg = init_model()

if not model:
    st.error(f"❌ Lỗi kết nối API: {error_msg}")
    st.info("Mẹo: Hãy kiểm tra xem API Key của bạn có bị giới hạn vùng (Region) không, hoặc thử tạo Key mới tại Google AI Studio.")
    st.stop()

# --- TRẠNG THÁI ỨNG DỤNG ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None
if 'char_prompt' not in st.session_state: st.session_state.char_prompt = ""

# --- BƯỚC 1: TẠO Ý TƯỞNG ---
if st.session_state.step == 1:
    st.header("Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", 
                             placeholder="Ví dụ: phim hoạt hình phiêu lưu về GaiO và Bibi...")
        c1, c2 = st.columns(2)
        style = c1.selectbox("Phong cách", ["Hoạt hình 3D", "Anime", "Cyberpunk"])
        qty = c2.number_input("Số lượng câu chuyện", 1, 10, 3)
        
        st.write("--- HOẶC ---")
        st.file_uploader("Tải file lên (.csv)", type="csv")
        
        if st.button("Tạo câu chuyện", type="primary"):
            with st.spinner("Đang lên ý tưởng..."):
                prompt = f"Tạo {qty} ý tưởng phim {style} về {topic}. Trả về JSON list: [{{'title': '...', 'summary': '...'}}]"
                res = model.generate_content(prompt)
                try:
                    # Làm sạch text để lấy JSON
                    clean_res = res.text.replace("```json", "").replace("```", "").strip()
                    st.session_state.stories = json.loads(clean_res)
                    st.session_state.step = 2
                    st.rerun()
                except:
                    st.error("AI trả về định dạng không đúng. Hãy thử nhấn nút lại.")

# --- BƯỚC 2: CHỌN CÂU CHUYỆN ---
elif st.session_state.step == 2:
    st.header("Bước 2: Chọn câu chuyện & Tạo nhân vật")
    if st.button("← Quay lại"): st.session_state.step = 1; st.rerun()
    
    # Hiển thị bảng danh sách như trong ảnh của Minh
    for idx, s in enumerate(st.session_state.stories):
        with st.container(border=True):
            col_idx, col_content = st.columns([0.5, 4.5])
            col_idx.write(f"**STT: {idx+1}**")
            col_content.write(f"**Tên câu chuyện:** {s['title']}")
            col_content.write(f"**Tóm tắt:** {s['summary']}")
            if st.button(f"Chọn câu chuyện {idx+1}", key=f"sel_{idx}"):
                st.session_state.selected_story = s
                st.session_state.step = 3
                st.rerun()

# --- BƯỚC 3: CHỈNH SỬA NHÂN VẬT & TẠO KỊCH BẢN ---
elif st.session_state.step == 3:
    st.header("Bước 3: Chỉnh sửa nhân vật & Tạo kịch bản")
    if st.button("← Quay lại"): st.session_state.step = 2; st.rerun()
    
    col_char, col_config = st.columns([1, 1])
    
    with col_char:
        st.subheader("Chỉnh sửa & Xác nhận nhân vật")
        st.image("https://via.placeholder.com/400x400.png?text=AI+Character+Preview", use_container_width=True)
        char_name = st.text_input("Tên nhân vật", value="Mamala")
        st.session_state.char_prompt = st.text_area("Prompt nhân vật", 
                                                   value="A single full-body portrait of Mamala, a sleek domestic cat in a 3D cartoon style...")
        st.button("Tạo lại ảnh (Leonardo)")

    with col_config:
        st.subheader("Cài đặt kịch bản")
        duration = st.number_input("Thời lượng video (phút)", value=3)
        env = st.text_area("Mô tả môi trường & bối cảnh", "Rừng rậm rực rỡ dưới ánh hoàng hôn...")
        
        if st
