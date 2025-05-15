import os
import random
from moviepy.editor import VideoFileClip, CompositeVideoClip
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from mutagen.mp4 import MP4
import numpy as np

def modify_video(filepath, output_folder, overlays_folder):
    basename = os.path.basename(filepath)
    name, ext = os.path.splitext(basename)
    random_id = random.randint(0, 1000)
    output_path = os.path.join(output_folder, f"{name}_fresh_edit_{random_id}{ext}")

    print(f"🎬 Processing: {basename}")
    clip = VideoFileClip(filepath)
    fps = clip.fps
    frames = list(clip.iter_frames())

    # 🎞️ Permute 3 à 5 paires de frames dans la zone centrale
    n_swaps = random.randint(3, 5)
    total_frames = len(frames)
    margin = int(0.1 * total_frames)
    for _ in range(n_swaps):
        i = random.randint(margin, total_frames - margin - 2)
        frames[i], frames[i+1] = frames[i+1], frames[i]

    # 🔊 Modifier légèrement le pitch audio
    pitch_factor = round(random.uniform(1.005, 1.015), 5)
    audio = clip.audio.fx(lambda a: a.set_fps(int(a.fps * pitch_factor)))

    # 🖼️ Clip vidéo à partir des frames modifiées
    new_video = ImageSequenceClip(frames, fps=fps).set_audio(audio)

    # 🌫️ Overlay transparent aléatoire
    overlay_clip = None
    if os.path.isdir(overlays_folder):
        overlays = [f for f in os.listdir(overlays_folder) if f.lower().endswith(('.mp4', '.webm'))]
        if overlays:
            chosen_overlay = random.choice(overlays)
            overlay_path = os.path.join(overlays_folder, chosen_overlay)
            print(f"📼 Overlay utilisé : {chosen_overlay}")
            overlay_clip = VideoFileClip(overlay_path).resize(new_video.size)
            if overlay_clip.duration < new_video.duration:
                overlay_clip = overlay_clip.loop(duration=new_video.duration)
            overlay_clip = overlay_clip.set_opacity(1.0)

    final_clip = CompositeVideoClip([new_video, overlay_clip]) if overlay_clip else new_video

    final_clip.write_videofile(
        output_path,
        codec="libx264",
        audio_codec="aac",
        preset="fast",
        bitrate="2000k",
        fps=fps
    )

    try:
        mp4file = MP4(output_path)
        mp4file["©nam"] = f"{name} fresh_edit_{random_id}"
        mp4file["©cmt"] = "Processed with stealth mode script"
        mp4file.save()
    except Exception as e:
        print("⚠️ Metadata update skipped:", e)

    print(f"✅ Sauvegardé sous : {output_path}")
    return output_path
