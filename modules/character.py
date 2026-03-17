from utils.gemini import ask_gemini
import json

def generate_characters():
    prompt = """
    Tạo 3 nhân vật cho một câu chuyện.

    Format JSON:
    [
      {"name": "", "type": ""}
    ]
    """

    result = ask_gemini(prompt)

    try:
        return json.loads(result)
    except:
        return [
            {"name": "Mamela", "type": "Cat"},
            {"name": "Grizzo", "type": "Dog"}
        ]
