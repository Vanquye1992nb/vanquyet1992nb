import streamlit as st
import random
import json

# =============================
# FALLBACK AI (CHỐNG SẬP API)
# =============================
def fallback_story(topic, n=3):
    base = [
        f"Một hành trình kỳ lạ về {topic}",
        f"Cuộc phiêu lưu sinh tồn trong {topic}",
        f"Một bí ẩn chưa được giải mã về {topic}"
    ]
    return random.sample(base, min(n, len(base)))

def fallback_characters():
    return [
        {"name": "Mamela", "type": "Cat"},
        {"name": "Grizzo", "type": "Dog"},
        {"name": "Pippin", "type": "Bird"}
    ]

def fallback_script(story):
    scenes = []
    for i in range(5):
        scenes.append({
            "scene": i+1,
            "desc": f"Cảnh {i+1}: {story}",
            "image_prompt": f"3D animation, cinematic, {story}, scene {i+1}",
            "video_prompt": f"cinematic motion, camera movement scene {i+1}"
        })
    return scenes

# =============================
# UI
# =============================
st.set_page_config(layout="wide")
st.title("🎬 AI VIDEO STORY TOOL (FULL PRO)")

# =============================
# STEP 1
# =============================
st.header("Bước 1: Tạo ý tưởng câu chuyện")

topic = st.text_area("Nhập ý tưởng")
style = st.selectbox("Phong cách", ["3D Animation", "Anime", "Realistic"])
num_story = st.number_input("Số lượng", 1, 10, 3)

if st.button("👉 Tạo câu chuyện"):
    stories = fallback_story(topic, num_story)
    st.session_state["stories"] = stories

# HIỂN THỊ
if "stories" in st.session_state:
    st.subheader("Danh sách story")
    selected = st.radio("Chọn story", st.session_state["stories"])
    st.session_state["selected_story"] = selected

# =============================
# STEP 2
# =============================
st.header("Bước 2: Nhân vật")

if st.button("Tạo nhân vật"):
    chars = fallback_characters()
    st.session_state["chars"] = chars

if "chars" in st.session_state:
    for i, c in enumerate(st.session_state["chars"]):
        st.session_state["chars"][i]["name"] = st.text_input(f"Tên {i}", c["name"])
        st.session_state["chars"][i]["type"] = st.text_input(f"Type {i}", c["type"])

# =============================
# STEP 3
# =============================
st.header("Bước 3: Tạo kịch bản")

duration = st.number_input("Thời lượng video (phút)", 1, 10, 3)

if st.button("🔥 Tạo kịch bản"):
    if "selected_story" in st.session_state:
        script = fallback_script(st.session_state["selected_story"])
        st.session_state["script"] = script

# =============================
# OUTPUT
# =============================
if "script" in st.session_state:
    st.success("✅ Kịch bản đã tạo")

    for s in st.session_state["script"]:
        st.markdown(f"### 🎬 Scene {s['scene']}")
        st.write("📖", s["desc"])
        st.code(s["image_prompt"])
        st.code(s["video_prompt"])

    st.download_button(
        "📥 Tải JSON",
        data=json.dumps(st.session_state["script"], indent=2),
        file_name="script.json"
    )
