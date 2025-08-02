import os
from pathlib import Path

def get_desktop_path():
    return str(Path.home() / "Desktop")

def get_video_root_dir():
    video_root = os.path.join(get_desktop_path(), "video")
    if not os.path.exists(video_root):
        os.makedirs(video_root)
    return video_root

def get_task_dir(task_id):
    task_dir = os.path.join(get_video_root_dir(), f"task_{task_id}")
    if not os.path.exists(task_dir):
        os.makedirs(task_dir)
    return task_dir

def get_task_image_dir(task_id):
    task_dir = get_task_dir(task_id)
    image_dir = os.path.join(task_dir, "images")
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    return image_dir

def get_task_video_dir(task_id):
    task_dir = get_task_dir(task_id)
    video_dir = os.path.join(task_dir, "videos")
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)
    return video_dir

def get_task_no_music_dir(task_id):
    task_dir = get_task_dir(task_id)
    no_music_dir = os.path.join(task_dir, "no_music_vides")
    if not os.path.exists(no_music_dir):
        os.makedirs(no_music_dir)
    return no_music_dir
