import streamlit as st
import google.generativeai as genai
import pandas as pd
import json

# Cấu hình API Gemini
genai.configure(api_key="AIzaSyDTLxNpCLC2ENeW3PjnIVEgKdnyMUYB_f8") # Thay bằng Key của bạn
model = genai.GenerativeModel('gemini-1.5-flash')

# Cấu hình giao diện Dark Mode & Rộng
st.set_page_config(page_title="AI Video Factory", layout="wide")

# Khởi tạo Session State để lưu dữ liệu qua các bước
if 'step' not in st.session_state: st.session_state.step = 1
if 'stories' not in st.session_state: st.session_state.stories = []
if 'selected_story' not in st.session_state: st.session_state.selected_story = None

# --- FUNCTIONS XỬ LÝ ---
def generate_stories(topic, style, quantity):
    prompt = f"""Hãy tạo {quantity} ý tưởng câu chuyện cho thể loại {topic} với phong cách {style}.
    Trả về định dạng JSON list gồm: "title" (tiêu đề) và "summary" (tóm tắt ngắn gọn)."""
    response = model.generate_content(prompt)
    try:
        # Làm sạch chuỗi JSON từ AI
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except:
        return [{"title": "Lỗi", "summary": "AI không trả về đúng định dạng JSON"}]

def generate_full_script(story, env, duration):
    # Tạo kịch bản chi tiết 12 phút (khoảng 20-30 cảnh)
    prompt = f"""Dựa trên câu chuyện: {story['title']}. Bối cảnh: {env}. Thời lượng: {duration} phút.
    Hãy tạo kịch bản chi tiết từng cảnh. Mỗi cảnh gồm:
    1. Mô tả (tiếng Việt)
    2. VEO PROMPT (tiếng Anh để chạy AI Video)
    3. Kiểm tra nhân vật (đánh dấu 'Có')
    Trả về định dạng JSON list."""
    response = model.generate_content(prompt)
    return response.text # Tương tự xử lý JSON như trên

# --- GIAO DIỆN TỪNG BƯỚC ---

# BƯỚC 1: TẠO Ý TƯỞNG
if st.session_state.step == 1:
    st.header("Bước 1: Tạo ý tưởng câu chuyện")
    with st.container(border=True):
        topic = st.text_area("Nhập thể loại hoặc ý tưởng câu chuyện", placeholder="Ví dụ: phim hoạt hình phiêu lưu về động vật...")
        col1, col2 = st.columns(2)
        style = col1.selectbox("Phong cách", ["Hoạt hình 3D", "Anime", "Thực tế", "Điện ảnh"])
        quantity = col2.number_input("Số lượng câu chuyện", min_value=1, max_value=10, value=3)
        
        st.write("--- HOẶC ---")
        uploaded_file = st.file_uploader("Tải file lên (.csv)", type="csv")
        
        if st.button("Tạo câu chuyện", type="primary"):
            with st.spinner("Đang sáng tạo ý tưởng..."):
                st.session_state.stories = generate_stories(topic, style, quantity)
                st.session_state.step = 2
                st.rerun()

# BƯỚC 2: CHỌN CÂU CHUYỆN & TẠO NHÂN VẬT
elif st.session_state.step == 2:
    st.header("Bước 2: Chọn câu chuyện & Tạo nhân vật")
    if st.button("← Quay lại Bước 1"): st.session_state.step = 1; st.rerun()
    
    # Hiển thị danh sách câu chuyện đã tạo
    for idx, story in enumerate(st.session_state.stories):
        with st.container(border=True):
            col_a, col_b = st.columns([1, 4])
            col_a.write(f"STT: {idx+1}")
            col_b.subheader(story['title'])
            col_b.write(story['summary'])
            if col_b.button(f"Chọn câu chuyện {idx+1}"):
                st.session_state.selected_story = story
                st.session_state.step = 3
                st.rerun()

# BƯỚC 3: CHỈNH SỬA NHÂN VẬT & TẠO KỊCH BẢN
elif st.session_state.step == 3:
    st.header("Bước 3: Chỉnh sửa nhân vật & Tạo kịch bản")
    if st.button("← Quay lại Bước 2"): st.session_state.step = 2; st.rerun()
    
    col_left, col_right = st.columns([1, 2])
    
    with col_left:
        st.subheader("Chỉnh sửa & Xác nhận nhân vật")
        st.image("https://via.placeholder.com/300", caption="Ảnh nhân vật AI") # Thay bằng link API ảnh thực tế
        char_name = st.text_input("Tên nhân vật 1", value="Mamala")
        char_prompt = st.text_area("Prompt nhân vật 1", value="A single full-body portrait of Mamala, a sleek domestic cat in a 3D cartoon style...")
        st.button("Tạo lại ảnh")
    
    with col_right:
        st.subheader("Cài đặt kịch bản")
        duration = st.number_input("Thời lượng video (phút)", value=3)
        env = st.text_area("Mô tả môi trường & bối cảnh", placeholder="Ví dụ: Rừng rậm Amazon vào buổi bình minh...")
        
        if st.button("Tạo kịch bản", type="primary"):
            st.session_state.step = 4
            st.rerun()

# BƯỚC CUỐI: KẾT QUẢ
elif st.session_state.step == 4:
    st.header("Kịch bản đã hoàn thành!")
    st.info(f"Tóm tắt: {st.session_state.selected_story['summary']}")
    
    # Bảng kết quả giả lập theo đúng mẫu ảnh
    data = [
        {
            "STT": 1, 
            "MÔ TẢ": "MỞ ĐẦU: Cảnh quay toàn cảnh từ trên cao một ngọn đồi khô cằn...", 
            "VEO PROMPT": "3D Animation, cinematic crane shot descending slowly, revealing a desolate hill...", 
            "KIỂM TRA": "✅ Có"
        },
        {
            "STT": 2, 
            "MÔ TẢ": "Nhân vật Mamala xuất hiện bên giếng nước...", 
            "VEO PROMPT": "3D cartoon style, Mamala cat sitting by an empty stone well...", 
            "KIỂM TRA": "✅ Có"
        }
    ]
    st.table(data)
    
    col1, col2, col3 = st.columns(3)
    if col1.button("Tạo kịch bản mới"): st.session_state.step = 1; st.rerun()
    col2.button("Tải Prompts (.txt)")
    col3.button("Tạo lại prompt lỗi")
