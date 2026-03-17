def generate_script(story, duration):
    scenes = []
    total_scenes = duration * 2

    for i in range(total_scenes):
        scenes.append({
            "scene": i + 1,
            "desc": f"Cảnh {i+1}: {story}",
            "image_prompt": f"3D animation, cinematic lighting, {story}, scene {i+1}",
            "video_prompt": f"camera pan, emotional scene {i+1}"
        })

    return scenes
