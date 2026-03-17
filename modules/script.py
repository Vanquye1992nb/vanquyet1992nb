from utils.gemini import ask_gemini
import json

def generate_script(story, duration):
    prompt = f"""
    Tạo kịch bản video từ câu chuyện:

    {story}

    Thời lượng: {duration} phút

    Yêu cầu:
    - Chia thành các scene
    - Mỗi scene gồm:
      + desc
      + image_prompt (cinematic)
      + video_prompt (motion)

    Format JSON:
    [
      {{
        "scene": 1,
        "desc": "",
        "image_prompt": "",
        "video_prompt": ""
      }}
    ]
    """

    result = ask_gemini(prompt)

    try:
        return json.loads(result)
    except:
        return []
