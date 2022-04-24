# extract 2000 uniform random frames
# ../blazeit does binary label, 0 no detections 1 has detections
# here we do count label (label is # detections in the frame)

# Note: this is similar to ../pipeline/16_blazeit_frames.py
# It used to be in ../pipeline but now we need access to queries.py in the blazeit2 folder.

import json
import numpy
import os
import random
import skimage.io
import subprocess
import sys

import queries

data_root = sys.argv[1]
label = sys.argv[2]
best_detector = sys.argv[3]

with open(os.path.join(data_root, 'dataset', label, 'cfg.json'), 'r') as f:
	cfg = json.load(f)
	orig_dims = cfg['OrigDims']

detection_path = os.path.join(data_root, 'dataset', label, 'train', best_detector)
out_path = os.path.join(data_root, 'dataset', label, 'train/blazeit2-train/images/')
os.makedirs(out_path, exist_ok=True)

video_path = os.path.join(data_root, 'dataset', label, 'train/video/')
all_frames = []
for fname in os.listdir(video_path):
	id = int(fname.split('.mp4')[0])
	with open(os.path.join(detection_path, str(id)+'.json'), 'r') as f:
		nframes = len(json.load(f))
	for frame_idx in range(nframes):
		all_frames.append((id, frame_idx))
good_frames = random.sample(all_frames, 2000)

# read all the videos and save the good frames, along with corresponding detections
print('extracting {} frames'.format(len(good_frames)))
counter = 0
for fname in os.listdir(video_path):
	id = int(fname.split('.mp4')[0])
	with open(os.path.join(detection_path, str(id)+'.json'), 'r') as f:
		detections = json.load(f)
	FNULL = open(os.devnull, 'w')
	pipe = subprocess.Popen([
		'ffmpeg', '-threads', '2', '-nostdin',
		'-i', os.path.join(video_path, str(id)+'.mp4'),
		'-vf', 'scale={}x{}'.format(orig_dims[0], orig_dims[1]),
		'-c:v', 'rawvideo', '-pix_fmt', 'rgb24', '-f', 'rawvideo',
		'-',
	], stdout=subprocess.PIPE, stderr=FNULL)
	for frame_idx in range(len(detections)):
		buf = pipe.stdout.read(orig_dims[0]*orig_dims[1]*3)
		if not buf:
			break
		if (id, frame_idx) not in good_frames:
			continue
		im = numpy.frombuffer(buf, dtype='uint8').reshape((orig_dims[1], orig_dims[0], 3))
		skimage.io.imsave(os.path.join(out_path, str(counter)+'.jpg'), im)
		_, _, train_count = queries.get_score(label, detections[frame_idx])
		with open(os.path.join(out_path, str(counter)+'.txt'), 'w') as f:
			f.write(str(train_count)+"\n")
		counter += 1
	pipe.wait()
	FNULL.close()
