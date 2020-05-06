from flask import Flask, Response, render_template, redirect
from flask import request, jsonify, make_response, url_for
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
from socket import gethostbyname, gethostname
from PIL import ImageFont, ImageDraw, Image
from imutils.video import VideoStream, FPS
from gevent.pywsgi import WSGIServer
from functools import partial
from utils import *
import threading, argparse, datetime
import imutils, cv2, time, config
import logging, serial, os
import numpy as np
from arduino_reader import ardThread

lock = threading.Lock()

face_detector = cv2.CascadeClassifier(config.FRONTAL_FACE_DETECTOR)

emotion_model_path = config.MODELS[config.CURR_MODEL]
emotion_classifier = load_model(emotion_model_path, 
    custom_objects={"swish_activation": swish_activation}, compile=False)
emotion_classifier._make_predict_function()

input_shape = emotion_classifier.layers[0].input_shape[0][1:3] #Getting input shape

fontpath = config.FONT_PATH
font = ImageFont.truetype(fontpath, 32) #Setting font

outputFrame = None

faces = []
emotions = []
tracker_initiated = False
tracker = None
gray = None

ard_vars = [0, 0, 0, False] #[pulse, avg_pulse, gsr, isCalibrating]

app = Flask(__name__)
PIN = generatePIN(6) #Generating PIN for auth
print(("PIN: " + PIN + "\n") * 10)

#Auth route
@app.route("/auth", methods=['GET', 'POST'])
def auth():
    if request.method == "GET":
        return render_template("auth.html")
    
    pin = request.form.get("pin")
    if PIN == pin:
        resp = make_response(redirect(url_for("detect")))
        resp.set_cookie("PIN", pin) #Setting cookie with valid PIN
        return resp
    else:
        app.logger.warning("[WARNING] Bad auth from: %s" % request.remote_addr) #Loggin bad auth
        return render_template("auth.html")

@app.route("/")
@app.route("/detect")
@auth_required(PIN)
def detect():
    return render_template("detect.html")

@app.route("/quiz")
@auth_required(PIN)
def quiz():
    return render_template("quiz.html")

#Return image list from 'static/quiz' folder
@app.route("/get_image_list")
@auth_required(PIN)
def get_image_list():
    images = os.listdir(config.QUIZ_IMAGES_PATH)

    for img in images:
        if img.startswith('.'):
            images.pop(images.index(img))

    app.logger.info("[INFO][/get_image_list] Sending image list to: %s" % request.remote_addr)
    return jsonify(images)

#Return emotion probs of current frame
@app.route("/get_emotions", methods=["GET"])
@auth_required(PIN)
def get_emotions():
    global tracker_initiated
    global emotions

    return jsonify({"emotions" : emotions, "tracker" : tracker_initiated})

@app.route('/get_vars', methods=["GET"])
@auth_required(PIN)
def get_vars():
    global ard_vars

    with lock:
        return jsonify(ard_vars)

#Starting video stream
@app.route("/video_feed")
@auth_required(PIN)
def video_feed():
    app.logger.info("[INFO][/video_feed] Starting video stream for: %s" % request.remote_addr)

    return Response(generate(request.remote_addr),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

@app.route("/choose_face", methods=["GET"])
@auth_required(PIN)
def choose_face():
    global tracker, tracker_initiated, gray, faces, lock

    if not tracker_initiated:
        try:
            mX, mY = int(request.args.get("x")), int(request.args.get("y"))
            iW, iH = int(request.args.get("w")), int(request.args.get("h"))
        except Exception:
            return "bad_arguments"

        scale_x = config.IN_WIDTH / iW        #Calculating scales for converting browser mouse XY to frame XY
        scale_y = config.IN_HEIGHT / iH

        mX *= scale_x   #Converting mouse XY to frame XY
        mY *= scale_y

        for x, y, w, h in faces:
            if (x <= mX <= x+w) and (y <= mY <= y+h):
                face_bb = (x, y, w, h)
                with lock:
                    tracker = cv2.TrackerMOSSE_create()     #Starting tracker
                    tracker.init(gray, face_bb)
                    tracker_initiated = True

                app.logger.info("[INFO] Face choosed by: %s" % request.remote_addr)
        
    return '1'

@app.route("/start_calibrate", methods=["GET"])
@auth_required(PIN)
def start_calibrating():
    global ard_vars

    with lock:
        ard_vars[3] = True
        ard_vars[1] =  0

    return '1'

@app.route("/stop_calibrate", methods=["GET"])
@auth_required(PIN)
def stop_calibrating():
    global ard_vars

    with lock:
        ard_vars[3] = False

    return '1'

@app.route("/reset_face")
@auth_required(PIN)
def reset_face():
    global tracker_initiated, emotions

    with lock:
        tracker_initiated = False
        emotions = []

    app.logger.info("[INFO] Face reseted by: %s" % request.remote_addr)

    return '1'

#Thread function for emotion detection
def detect_emotion():
    global outputFrame, tracker
    global faces, gray, tracker_initiated
    global emotions

    vs = VideoStream(src=0).start()

    fps = FPS().start()
    CURRENT_FPS = 0
    frame_ind = 0

    scale_x = config.SCALE_WIDTH
    scale_y = config.SCALE_HEIGHT

    app.logger.info("[INFO] detect_emotion thread started")

    while True:
        try:
            out_frame = vs.read()
            out_frame = cv2.resize(out_frame, (config.OUT_WIDTH, config.OUT_HEIGHT))

            with lock:
                gray = cv2.resize(out_frame, (config.IN_WIDTH, config.IN_HEIGHT))
                gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)

            if tracker_initiated:   #If tracker initiated then update tracker
                with lock:
                    success, box = tracker.update(gray)

                if success:         #If face finded then calculate emotion and draw
                    x, y, w, h = [int(i) for i in box]

                    x = 0 if x < 0 else (config.IN_WIDTH-1 if x > config.IN_WIDTH-1 else x)
                    y = 0 if y < 0 else (config.IN_HEIGHT-1 if y > config.IN_HEIGHT-1 else y)

                    with lock:
                        roi = gray[y:y+h, x:x+w]

                    roi = cv2.resize(roi, input_shape, interpolation=cv2.INTER_AREA)
                    roi = roi.astype("float") / 255.0
                    roi = img_to_array(roi)
                    roi = np.expand_dims(roi, axis=0)   #[roi,]
                    preds = emotion_classifier.predict(roi)[0]

                    with lock:
                        emotions = [int(emotion*100) for emotion in preds]

                    emotion = np.argmax(preds)

                    x, y, w, h = (x//scale_x, y//scale_y, w//scale_x, h//scale_y)
                    x, y, w, h = (int(x), int(y), int(w), int(h))

                    draw_border(out_frame, (x, y), (x+w, y+h), config.SELECTED_COLOR, 3, 5, 30)

                    out_frame = Image.fromarray(out_frame)
                    draw = ImageDraw.Draw(out_frame)

                    tW, tH = font.getsize(config.EMOTIONS_RUS[emotion])
                    draw.rectangle(((x-2, y+h+5), (x+tW+2, y+h+tH+2)), fill = config.SELECTED_COLOR)
                    draw.text((x, y+h),  config.EMOTIONS_RUS[emotion], font = font, fill = (255, 255, 255, 255))

                    out_frame = np.array(out_frame)
                else:       #Face not finded, tracker resets
                    with lock:
                        tracker_initiated = False
                        emotions = []
            else:           #Tracker not initiated, detecting faces
                with lock:
                    faces = face_detector.detectMultiScale(gray)

                    for x, y, w, h in faces:
                        x, y, w, h = (x//scale_x, y//scale_y, w//scale_x, h//scale_y)
                        x, y, w, h = (int(x), int(y), int(w), int(h))

                        draw_border(out_frame, (x, y), (x+w, y+h), config.NOT_SELECTED_COLOR, 3, 5, 30)

            #Draw fps
            draw_text_w_background(out_frame, 'FPS: %.2f' % CURRENT_FPS,
                (20, 20),
                config.font, config.fontScale,
                config.fontColor, config.bgColor, 1)

            fps.update()

            #Updating fps every 10 frames
            if (frame_ind == 10):
                fps.stop()

                CURRENT_FPS = fps.fps()
                fps = FPS().start()
                frame_ind = 0

            with lock:
                outputFrame = out_frame.copy()

            frame_ind += 1
        except Exception as e:
            app.logger.error("[ERROR] Error in detect_emotion(): \n\t%s" % e)
            continue

#Video stream generator function
def generate(addr):
    global outputFrame

    try:
        while True:
            with lock:
                if outputFrame is None:
                    continue

                (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)

            if not flag:
                continue

            yield(b'--frame\r\n' 
                b'Content-Type: image/jpeg\r\n\r\n' + bytearray(encodedImage) + b'\r\n')

    except GeneratorExit:
        app.logger.info("[INFO] Stream stopped for: %s" % addr)

    except Exception as e:
        app.logger.error(["[ERROR] Error in generate(): \n\t%s"] % e)

@app.before_first_request
def startDetectionThread():
    global ard_vars, lock

    #Starting cam thread
    cam_thread = threading.Thread(target=detect_emotion)
    cam_thread.daemon = True
    cam_thread.start()

    #Starting arduino serial thread
    # ard_thread = threading.Thread(target=partial(ardThread, 
        # '/dev/cu.usbmodem141201', 115200, ard_vars, lock))
    # ard_thread.daemon = True
    # ard_thread.start()

import logging

app.logger.setLevel(logging.DEBUG)
handler = logging.FileHandler('app.log')
handler.setLevel(logging.DEBUG)
app.logger.addHandler(handler)

if __name__ == "__main__":

    app.run('0.0.0.0', '80', debug=False, 
        threaded=True, use_reloader=False)

