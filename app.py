import streamlit as st
import google.generativeai as genai
import json
import pandas as pd

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="AI Video Factory - Fixed", layout="wide")

# --- XỬ LÝ API KEY ---
# Ưu tiên lấy từ Secrets của Streamlit Cloud, nếu không có thì lấy từ Sidebar
api_key = st.secrets.get("AIzaSyDTLxNpCLC2ENeW3PjnIVEgKdnyMUYB_f8") or st.sidebar.text_input("Nhập Gemini API Key:", type="password")

if not api_key:
    st.warning("⚠️ Vui lòng cấu hình GEMINI_API_KEY trong phần Secrets hoặc nhập vào thanh bên.")
    st.stop()

# Khởi tạo AI
genai.configure(api_key=api_key)

# FIX LỖI NOTFOUND: Thử các biến thể tên model phổ biến
@st.cache_resource
def load_model():
    model_names = ['gemini-1.5-flash', 'models/gemini-1.5-flash', 'gemini-pro']
    for name in model_names:
        try:
            m = genai.GenerativeModel(name)
            # Thử gọi một câu lệnh cực ngắn để kiểm tra model có tồn tại không
            m.generate_content("ping") 
            return m, name
        except Exception:
            continue
    return None, None

model, active_model_name = load_model()

if not model:
    st.error("❌ Không thể kết nối với bất kỳ Model Gemini nào. Vui lòng kiểm tra lại API Key hoặc hạn mức tài khoản.")
    st.stop()

# Hiển thị tên model đang chạy để Minh yên tâm
st.sidebar.success(f"Đang dùng: {active_model_name}")

# --- QUẢN LÝ TRẠNG THÁI (SESSION STATE) ---
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None

# --- HÀM XỬ LÝ DỮ LIỆU ---
def parse_json_safely(text):
    try:
        # Loại bỏ các ký tự thừa nếu AI trả về kèm Markdown
        clean_text = text.replace("```json", "").replace("```", "").strip()
        return json.loads(clean_text)
    except Exception as e:
        st.error(f"Lỗi đọc dữ liệu AI: {e}")
        return None

# --- GIAO DIỆN CÁC BƯỚC (GIỐNG MẪU ẢNH CỦA MINH) ---

# BƯỚC 1
if st.session_state.step == 1:
    st.subheader("Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", "Phim hoạt hình phiêu lưu về GaiO và Bibi")
        col1, col2 = st.columns(2)
        style = col1.selectbox("Phong cách", ["Hoạt hình 3D", "Anime", "Disney"])
        qty = col2.number_input("Số lượng", 1, 5, 3)
        
        if st.button("Tạo câu chuyện", type="primary"):
            with st.spinner("Đang kết nối AI..."):
                prompt = f"Tạo {qty} ý tưởng phim {style} về {topic}. Trả về JSON list: [{{'title': '...', 'summary': '...'}}]"
                try:
                    res = model.generate_content(prompt) # Dòng này đã được fix
                    data = parse_json_safely(res.text)
                    if data:
                        st.session_state.stories = data
                        st.session_state.step = 2
                        st.rerun()
                except Exception as e:
                    st.error(f"Lỗi API: {e}")

# BƯỚC 2
elif st.session_state.step == 2:
    st.subheader("Bước 2: Chọn câu chuyện")
    if st.button("← Quay lại"): st.session_state.step = 1; st.rerun()
    
    for idx, s in enumerate(st.session_state.stories):
        with st.container(border=True):
            st.write(f"**{idx+1}. {s['title']}**")
            st.write(s['summary'])
            if st.button(f"Chọn {idx+1}", key=f"s_{idx}"):
                st.session_state.selected_story = s
                st.session_state.step = 3
                st.rerun()

# BƯỚC 3 & 4 (Rút gọn để Minh chạy thử kết nối)
elif st.session_state.step == 3:
    st.success(f"Đã chọn: {st.session_state.selected_story['title']}")
    if st.button("Tạo kịch bản chi tiết"):
        with st.spinner("Đang tạo bảng kịch bản..."):
            prompt = f"Viết kịch bản chi tiết cho: {st.session_state.selected_story['title']}. Trả về bảng JSON có cột STT, MO_TA, VEO_PROMPT."
            res = model.generate_content(prompt)
            data = parse_json_safely(res.text)
            if data:
                st.table(pd.DataFrame(data))
                if st.button("Làm lại từ đầu"): st.session_state.step = 1; st.rerun()
