from utils.gemini import ask_gemini

def generate_stories(topic, n):
    prompt = f"""
    Tạo {n} ý tưởng video viral về chủ đề: {topic}

    Yêu cầu:
    - Ngắn gọn
    - Gây tò mò
    - Có cảm xúc
    - Dạng list

    Trả về mỗi dòng 1 ý tưởng
    """

    result = ask_gemini(prompt)

    if result:
        stories = result.split("\n")
        return [s.strip("- ") for s in stories if s.strip() != ""]
    
    # fallback
    return [f"Câu chuyện về {topic}"]
