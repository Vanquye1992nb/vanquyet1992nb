import streamlit as st
import google.generativeai as genai
import os
import json
import random

# =============================
# CONFIG GEMINI
# =============================
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

# =============================
# HELPER
# =============================
def ask_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except:
        return None

def clean_json(text):
    if not text:
        return None
    text = text.replace("```json", "").replace("```", "")
    return text.strip()

# =============================
# FALLBACK
# =============================
def fallback_stories(topic, n):
    base = [
        f"Câu chuyện cảm động về {topic}",
        f"Bí ẩn đáng sợ về {topic}",
        f"Hành trình sinh tồn trong {topic}",
        f"Một sự thật chưa ai biết về {topic}",
        f"Cuộc phiêu lưu kỳ lạ về {topic}"
    ]
    return random.sample(base, n)

def fallback_characters():
    return [
        {"name": "Mamela", "type": "Cat"},
        {"name": "Grizzo", "type": "Dog"},
        {"name": "Pippin", "type": "Bird"}
    ]

def fallback_script(story, duration):
    scenes = []
    total = duration * 2
    for i in range(total):
        scenes.append({
            "scene": i+1,
            "desc": f"Cảnh {i+1}: {story}",
            "image_prompt": f"cinematic, 3D animation, {story}, scene {i+1}",
            "video_prompt": f"camera movement, emotional scene {i+1}"
        })
    return scenes

# =============================
# AI GENERATION
# =============================
def generate_stories(topic, n):
    prompt = f"""
    Tạo {n} ý tưởng video viral về chủ đề: {topic}

    Yêu cầu:
    - Hook mạnh
    - Gây tò mò
    - Ngắn gọn

    Trả mỗi dòng 1 ý tưởng.
    """

    result = ask_gemini(prompt)

    if result:
        lines = result.split("\n")
        stories = [l.strip("- ").strip() for l in lines if l.strip()]
        if len(stories) >= 1:
            return stories[:n]

    return fallback_stories(topic, n)

def generate_characters():
    prompt = """
    Tạo 3 nhân vật cho một câu chuyện.

    Trả JSON:
    [
      {"name": "", "type": ""}
    ]

    Chỉ trả JSON.
    """

    result = ask_gemini(prompt)
    result = clean_json(result)

    try:
        return json.loads(result)
    except:
        return fallback_characters()

def generate_script(story, duration):
    prompt = f"""
    Tạo kịch bản video từ câu chuyện:

    {story}

    Thời lượng: {duration} phút

    Yêu cầu:
    - Chia thành nhiều scene
    - Mỗi scene gồm:
      + scene
      + desc
      + image_prompt
      + video_prompt

    Trả JSON:
    [
      {{
        "scene": 1,
        "desc": "",
        "image_prompt": "",
        "video_prompt": ""
      }}
    ]

    Chỉ trả JSON.
    """

    result = ask_gemini(prompt)
    result = clean_json(result)

    try:
        return json.loads(result)
    except:
        return fallback_script(story, duration)

# =============================
# STREAMLIT UI
# =============================
st.set_page_config(layout="wide")
st.title("🎬 AI VIDEO TOOL - GEMINI FULL AUTO")

# SESSION INIT
if "stories" not in st.session_state:
    st.session_state.stories = []

if "selected_story" not in st.session_state:
    st.session_state.selected_story = None

if "characters" not in st.session_state:
    st.session_state.characters = []

if "script" not in st.session_state:
    st.session_state.script = []

# =============================
# STEP 1
# =============================
st.header("Bước 1: Tạo Story")

topic = st.text_area("Nhập chủ đề")
num = st.slider("Số lượng story", 1, 5, 3)

if st.button("🚀 Tạo Story"):
    with st.spinner("Đang tạo story..."):
        st.session_state.stories = generate_stories(topic, num)

if st.session_state.stories:
    st.subheader("Chọn Story")
    st.session_state.selected_story = st.radio(
        "Danh sách:",
        st.session_state.stories
    )

# =============================
# STEP 2
# =============================
st.header("Bước 2: Nhân vật")

if st.button("🎭 Tạo nhân vật"):
    with st.spinner("Đang tạo nhân vật..."):
        st.session_state.characters = generate_characters()

for i, char in enumerate(st.session_state.characters):
    col1, col2 = st.columns(2)
    with col1:
        char["name"] = st.text_input(f"Tên {i}", char["name"], key=f"name_{i}")
    with col2:
        char["type"] = st.text_input(f"Loại {i}", char["type"], key=f"type_{i}")

# =============================
# STEP 3
# =============================
st.header("Bước 3: Kịch bản")

duration = st.slider("Thời lượng (phút)", 1, 10, 3)

if st.button("🔥 Tạo kịch bản"):
    if not st.session_state.selected_story:
        st.warning("Chưa chọn story")
    else:
        with st.spinner("Đang tạo kịch bản..."):
            st.session_state.script = generate_script(
                st.session_state.selected_story,
                duration
            )

# =============================
# OUTPUT
# =============================
if st.session_state.script:
    st.success("✅ Kịch bản hoàn thành")

    for scene in st.session_state.script:
        with st.expander(f"🎬 Scene {scene['scene']}"):
            st.write("📖", scene["desc"])
            st.code(scene["image_prompt"])
            st.code(scene["video_prompt"])

    st.download_button(
        "📥 Tải JSON",
        data=json.dumps(st.session_state.script, indent=2, ensure_ascii=False),
        file_name="script.json"
    )
