import random

def generate_stories(topic, n):
    base = [
        f"Một hành trình kỳ lạ về {topic}",
        f"Bí ẩn đáng sợ về {topic}",
        f"Câu chuyện cảm động về {topic}",
        f"Cuộc phiêu lưu sinh tồn trong {topic}",
        f"Một sự thật chưa ai biết về {topic}"
    ]
    return random.sample(base, n)
