# Extracts train/valid/test for caldot1 and caldot2 datasets.
# This is not needed unless preparing video from scratch.

import os
import random
import subprocess
import sys


data_root = data_root = sys.argv[1]
video_path = '/data/processed/full-dataset/mini/videos/'

out_paths = [
    os.path.join(data_root, 'dataset', 'mini', 'train/video/'),
    os.path.join(data_root, 'dataset', 'mini', 'valid/video/'),
    os.path.join(data_root, 'dataset', 'mini', 'test/video/'),
    os.path.join(data_root, 'dataset', 'mini', 'tracker/video/'),
]

def get_duration(fname):
    output = subprocess.check_output(['ffprobe', '-select_streams', 'v:0', '-show_entries', 'stream=duration', '-of', 'csv=s=,:p=0', fname])
    print(f"duration is {float(output.strip())}")
    return float(output.strip())

# list of tuples (fname, seconds)
segments = []

for fname in os.listdir(video_path):
    if not fname.endswith('.mp4'):
        continue
    duration = int(get_duration(video_path+fname))
    for skip in range(0, duration, 2):
        segments.append((fname, skip))

random.shuffle(segments)
print('got {} segments'.format(len(segments)))

for out_path in out_paths:
    cur_segments = segments[0:60]
    segments = segments[60:]
    for i, (fname, skip) in enumerate(cur_segments):
        ffmpeg_args = ['ffmpeg', '-ss', str(skip), '-i', video_path+fname, '-t', '60', out_path+str(i)+'.mp4']
        subprocess.call(ffmpeg_args)
