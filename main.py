# from face_recognition import face_locations
from keras.models import load_model
from keras.preprocessing.image import img_to_array
from imutils.video import VideoStream, FPS
import numpy as np
import cv2, argparse

parser = argparse.ArgumentParser()
parser.add_argument('--res', metavar='N', type=int, nargs=2,
                    help='resolution w h', default=(640, 360))
parser.add_argument('--model', default="mini_x",
                    help='model name')

#y0, x0 - left_top
#y1, x1 - right_bottom

args = parser.parse_args()


OUT_WIDTH, OUT_HEIGHT = args.res
model = args.model

IN_WIDTH, IN_HEIGHT = OUT_WIDTH, OUT_HEIGHT

if (OUT_WIDTH+OUT_HEIGHT >= 1000):
	IN_WIDTH, IN_HEIGHT = OUT_WIDTH//2, OUT_HEIGHT//2

SCALE_FACTOR = OUT_WIDTH // IN_WIDTH 

NOT_SELECTED_COLOR = (0, 200, 0)[::-1] #RGB to BGR
SELECTED_COLOR = (255, 140, 0)[::-1]

font                   = cv2.FONT_HERSHEY_SIMPLEX
fontScale              = 0.5
fontColor              = (0, 255, 0)[::-1]
lineType               = 2

EMOTIONS = ["angry" ,"disgust","scared", "happy", "sad", "surprised",
 "neutral"]

MODELS = { 'tiny_x' : 'tiny_exception_0.60_48.hdf5',
 			'mini_x' : 'mini_exception_0.00_64.hdf5',
 			'big_x' : 'big_exception_0.66_48.hdf5',
 			'simpler_cnn' : 'simpler_cnn_62_48.hdf5',
 			'simple_cnn' : 'simple_cnn_0.60_48.hdf5'
 		}

emotion_model_path = "static/%s" % MODELS[model]
emotion_classifier = load_model(emotion_model_path, compile=False)
input_shape = emotion_classifier.layers[0].input_shape[1:3]

face_detector = cv2.CascadeClassifier('static/haarcascade_frontalface_default.xml')

csrt_tracker = None
tracker_initiated = False

def choose_face(event, mX, mY, flags, faces):
	global tracker_initiated, csrt_tracker, gray
	
	mX, mY = (mX//SCALE_FACTOR, mY//SCALE_FACTOR)

	if not tracker_initiated:
		if event == cv2.EVENT_LBUTTONUP and len(faces) > 0:
			for x, y, w, h in faces:
				if (x <= mX <= x+w) and (y <= mY <= y+h):
					face_bb = (x, y, w, h)
					csrt_tracker = cv2.TrackerCSRT_create()
					csrt_tracker.init(gray, face_bb)
					tracker_initiated = True

def draw_border(img, pt1, pt2, color, thickness, r, d):
    x1,y1 = pt1
    x2,y2 = pt2

    # Top left
    cv2.line(img, (x1 + r, y1), (x1 + r + d, y1), color, thickness)
    cv2.line(img, (x1, y1 + r), (x1, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x1 + r, y1 + r), (r, r), 180, 0, 90, color, thickness)

    # Top right
    cv2.line(img, (x2 - r, y1), (x2 - r - d, y1), color, thickness)
    cv2.line(img, (x2, y1 + r), (x2, y1 + r + d), color, thickness)
    cv2.ellipse(img, (x2 - r, y1 + r), (r, r), 270, 0, 90, color, thickness)

    # Bottom left
    cv2.line(img, (x1 + r, y2), (x1 + r + d, y2), color, thickness)
    cv2.line(img, (x1, y2 - r), (x1, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x1 + r, y2 - r), (r, r), 90, 0, 90, color, thickness)

    # Bottom right
    cv2.line(img, (x2 - r, y2), (x2 - r - d, y2), color, thickness)
    cv2.line(img, (x2, y2 - r), (x2, y2 - r - d), color, thickness)
    cv2.ellipse(img, (x2 - r, y2 - r), (r, r), 0, 0, 90, color, thickness)


cv2.namedWindow('cam')

cap = VideoStream(src=0, resolution=(OUT_WIDTH, OUT_HEIGHT)).start()

fps = FPS().start()
frame_ind = 0
CURRENT_FPS = 0

while True:
	out_frame = cap.read()
	out_frame = cv2.resize(out_frame, (OUT_WIDTH, OUT_HEIGHT))
	out_frame = cv2.flip(out_frame, 1)

	frame = cv2.resize(out_frame, (IN_WIDTH, IN_HEIGHT))
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

	if tracker_initiated:
		success, box = csrt_tracker.update(gray)

		if success:
			x, y, w, h = [int(i) for i in box]

			x = 0 if x < 0 else (IN_WIDTH-1 if x > IN_WIDTH-1 else x)
			y = 0 if y < 0 else (IN_HEIGHT-1 if y > IN_HEIGHT-1 else y)

			roi = gray[y:y+h, x:x+w]
			roi = cv2.resize(roi, input_shape, interpolation=cv2.INTER_AREA)
			roi = roi.astype("float") / 255.0
			roi = img_to_array(roi)
			roi = np.expand_dims(roi, axis=0)
			preds = emotion_classifier.predict(roi)[0]
			emotion = np.argmax(preds)

			x, y, w, h = (x*SCALE_FACTOR, y*SCALE_FACTOR, w*SCALE_FACTOR, h*SCALE_FACTOR)

			draw_border(out_frame, (x, y), (x+w, y+h), SELECTED_COLOR, 2, 5, 10)
			cv2.putText(out_frame, EMOTIONS[emotion] + "_%.f" % (preds[emotion]*100),
					(x+w+10, y+h+10),
					font,
					fontScale,
					fontColor,
					lineType)
			cv2.putText(out_frame, "Press <C> on your keyboard",
					(10, 15),
					font,
					fontScale,
					fontColor,
					lineType)
			cv2.putText(out_frame, "if you want to choose other face",
				(10, 30),
					font,
					fontScale,
					fontColor,
					lineType)
		else:
			tracker_initiated = False

	else:
		faces = face_detector.detectMultiScale(gray)
		for x, y, w, h in faces:
			x, y, w, h = (x*SCALE_FACTOR, y*SCALE_FACTOR, w*SCALE_FACTOR, h*SCALE_FACTOR)
			draw_border(out_frame, (x, y), (x+w, y+h), NOT_SELECTED_COLOR, 2, 5, 10)

		# faces = face_locations(gray)
		# for y0, x1, y1, x0 in faces:
		# 	draw_border(frame, (x0, y0), (x1, y1), NOT_SELECTED_COLOR, 2, 5, 10)

		cv2.setMouseCallback('cam', choose_face, faces)


		cv2.putText(out_frame, "Click on face you want to track",
					(10, 15),
					font,
					fontScale,
					fontColor,
					lineType)

	#Calculate fps
	fps.update()
	frame_ind += 1

	#Refresh CURRENT_FPS every 10 frames
	if (frame_ind == 10):
		fps.stop()
		CURRENT_FPS = fps.fps()
		fps = FPS().start()
		frame_ind = 0

	#Draw fps
	cv2.putText(out_frame, 'FPS: %.2f' % CURRENT_FPS,
					(20, IN_HEIGHT-20),
					font,
					fontScale,
					fontColor,
					lineType)

	cv2.imshow('cam', out_frame)

	k = cv2.waitKey(1)

	if k & 0xFF == ord('q'):
		break

	elif k & 0xFF == ord('c'):
		tracker_initiated = False

