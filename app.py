import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- CẤU HÌNH GIAO DIỆN DARK MODE ---
st.set_page_config(page_title="Hệ thống Video AI", layout="wide")

# --- QUẢN LÝ API ---
# Lấy key từ Secrets (Cloud) hoặc Input (Local)
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("Nhập Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Vui lòng cấu hình API Key để bắt đầu.")
    st.stop()

# Khởi tạo AI với model ổn định nhất
genai.configure(api_key=api_key)

@st.cache_resource
def get_model():
    try:
        # Sử dụng gemini-1.5-flash để tránh lỗi NotFound
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Lỗi khởi tạo: {e}")
        return None

model = get_model()

# --- TRẠNG THÁI (SESSION STATE) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None

# --- HÀM TRỢ GIÚP ---
def parse_json(text):
    try:
        clean = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean)
    except:
        return None

# --- LUỒNG XỬ LÝ 4 BƯỚC ---

# BƯỚC 1: TẠO Ý TƯỞNG (Giống ảnh image_231182.png)
if st.session_state.step == 1:
    st.header("Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", "Phim hoạt hình phiêu lưu về GaiO và Bibi")
        c1, c2 = st.columns(2)
        style = c1.selectbox("Phong cách", ["Hoạt hình 3D", "Anime", "Cyberpunk"])
        qty = c2.number_input("Số lượng", 1, 5, 3)
        
        if st.button("Tạo câu chuyện", type="primary"):
            with st.spinner("AI đang suy nghĩ..."):
                prompt = f"Tạo {qty} ý tưởng phim {style} về {topic}. Trả về JSON list: [{{'title': '...', 'summary': '...'}}]"
                res = model.generate_content(prompt)
                data = parse_json(res.text)
                if data:
                    st.session_state.stories = data
                    st.session_state.step = 2
                    st.rerun()

# BƯỚC 2: DANH SÁCH (Giống ảnh image_230e3c.png)
elif st.session_state.step == 2:
    st.header("Bước 2: Chọn câu chuyện")
    if st.button("← Quay lại"): 
        st.session_state.step = 1
        st.rerun()
    
    for idx, s in enumerate(st.session_state.stories):
        with st.container(border=True):
            st.subheader(f"STT: {idx+1} - {s['title']}")
            st.write(s['summary'])
            if st.button(f"Chọn câu chuyện {idx+1}", key=f"s_{idx}"):
                st.session_state.selected_story = s
                st.session_state.step = 3
                st.rerun()

# BƯỚC 3: NHÂN VẬT & KỊCH BẢN (Giống ảnh image_230a81.png & image_230a05.png)
elif st.session_state.step == 3:
    st.header("Bước 3: Chỉnh sửa nhân vật & Tạo kịch bản")
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Chỉnh sửa nhân vật")
        name = st.text_input("Tên nhân vật", "Mamala")
        char_desc = st.text_area("Prompt nhân vật", "A sleek domestic cat in 3D style...")
        st.image("https://via.placeholder.com/300?text=Preview", use_container_width=True)
        
    with col_r:
        st.subheader("Cài đặt kịch bản")
        duration = st.number_input("Thời lượng (phút)", 3)
        env = st.text_area("Bối cảnh", "Rừng rậm rực rỡ...")
        
        if st.button("Tạo kịch bản chi tiết", type="primary"):
            with st.spinner("Đang tạo 90 cảnh..."):
                prompt = f"Viết kịch bản {duration} phút cho {st.session_state.selected_story['title']}. Trả về JSON list các cảnh có STT, MO_TA, VEO_PROMPT."
                res = model.generate_content(prompt)
                st.session_state.final_script = parse_json(res.text)
                st.session_state.step = 4
                st.rerun()

# BƯỚC 4: KẾT QUẢ (Giống ảnh image_230737.png)
elif st.session_state.step == 4:
    st.header("Kịch bản đã hoàn thành!")
    df = pd.DataFrame(st.session_state.final_script)
    st.table(df)
    if st.button("Tạo kịch bản mới"):
        st.session_state.step = 1
        st.rerun()
