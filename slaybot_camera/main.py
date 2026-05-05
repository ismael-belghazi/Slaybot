import cv2
import numpy as np
import threading
import time
import json
import asyncio
import websockets
import subprocess
from flask import Flask, Response, render_template

# --- CONFIGURATION PID ---
KP = 0.32  
KI = 0.002 
KD = 0.22  
MAX_INTEGRAL = 12 

class SlayBotVision:
    def __init__(self, camera_index=0):
        self.index = camera_index
        self.cap = None
        self.running = True
        self.frame = None
        
        self.steering_angle = 0
        self.current_color = "NONE"
        self.lock = threading.Lock()
        
        self.last_error = 0
        self.integral = 0
        self.base_x = 160 
        self.line_lost_time = 0
        self.last_valid_angle = 0

        self._cleanup_v4l2()
        self.thread = threading.Thread(target=self._vision_engine, daemon=True)
        self.thread.start()

    def _cleanup_v4l2(self):
        try:
            subprocess.run(["sudo", "fuser", "-k", f"/dev/video{self.index}"], capture_output=True, check=False)
            time.sleep(0.5)
        except: pass

    def _init_cam(self):
        cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap

    def is_valid_line(self, contour, roi_w, roi_h):
        """ Filtre de rejet intelligent pour ignorer les meubles (tables) """
        area = cv2.contourArea(contour)
        
        # 1. Filtre de surface : rejette si trop petit (bruit) ou trop gros (table)
        # Une table vue de près prend énormément de place dans la ROI
        max_allowed_area = (roi_w * roi_h) * 0.25
        if area < 250 or area > max_allowed_area: 
            return False
        
        # 2. Filtre de forme (Bounding Box)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = float(w) / h
        
        # Si l'objet est massif et presque carré (0.7 à 1.4), c'est probablement un bloc/meuble
        if 0.7 < aspect_ratio < 1.4 and area > 1500:
            return False

        # 3. Solidité (Densité du contour)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        
        return solidity > 0.5 # Une ligne est un objet très "plein"

    def _vision_engine(self):
        self.cap = self._init_cam()
        
        # Ranges HSV (Stables)
        ranges = {
            "JAUNE": (np.array([18, 80, 100]), np.array([35, 255, 255])),
            "BLEU":  (np.array([100, 120, 50]), np.array([125, 255, 255])),
            "ROUGE": [(np.array([0, 120, 70]), np.array([10, 255, 255])),
                      (np.array([170, 120, 70]), np.array([180, 255, 255]))]
        }

        # Outil de nettoyage pour supprimer les reflets brillants sur la table
        kernel = np.ones((5,5), np.uint8)

        while self.running:
            if not self.cap or not self.cap.isOpened():
                self.cap = self._init_cam()
                continue

            success, frame = self.cap.read()
            if not success: continue

            h, w = frame.shape[:2]
            # ROI resserrée : On commence à 60% pour ne pas voir les bords de table au loin
            roi_y_start, roi_y_end = int(h * 0.60), int(h * 0.95)
            roi = frame[roi_y_start:roi_y_end, :]
            
            blur = cv2.GaussianBlur(roi, (7, 7), 0)
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
            
            best_mask = None
            detected_color = "NONE"

            for name, r in ranges.items():
                if name == "ROUGE":
                    m = cv2.bitwise_or(cv2.inRange(hsv, r[0][0], r[0][1]), cv2.inRange(hsv, r[1][0], r[1][1]))
                else:
                    m = cv2.inRange(hsv, r[0], r[1])
                
                # NETTOYAGE : Efface les poussières et reflets de couleur
                m = cv2.morphologyEx(m, cv2.MORPH_OPEN, kernel)
                
                cnts, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if cnts:
                    c = max(cnts, key=cv2.contourArea)
                    if self.is_valid_line(c, roi.shape[1], roi.shape[0]):
                        best_mask = m
                        detected_color = name
                        break

            target_angle = self.steering_angle

            if best_mask is not None:
                self.line_lost_time = 0 
                
                n_windows = 8
                win_h = best_mask.shape[0] // n_windows
                curr_x = self.base_x
                pts = []

                for i in range(n_windows):
                    y_low = best_mask.shape[0] - (i + 1) * win_h
                    y_high = best_mask.shape[0] - i * win_h
                    x_min, x_max = max(0, int(curr_x - 60)), min(w, int(curr_x + 60))
                    
                    win_roi = best_mask[y_low:y_high, x_min:x_max]
                    M = cv2.moments(win_roi)
                    
                    if M["m00"] > 15:
                        curr_x = int(M["m10"] / M["m00"]) + x_min
                        pts.append((curr_x, y_low + roi_y_start))

                if len(pts) >= 2:
                    self.base_x = pts[0][0]
                    target_x = pts[-1][0] 
                    error = target_x - (w // 2)
                    if abs(error) < 4: error = 0 
                    
                    self.integral = np.clip(self.integral + error, -MAX_INTEGRAL, MAX_INTEGRAL)
                    derivative = error - self.last_error
                    output = (error * KP) + (self.integral * KI) + (derivative * KD)
                    target_angle = np.clip(output, -45, 45)
                    self.last_error = error
                    self.last_valid_angle = target_angle
                    cv2.polylines(frame, [np.array(pts)], False, (0, 255, 0), 2)

            else:
                if self.line_lost_time == 0: self.line_lost_time = time.time()
                elapsed = time.time() - self.line_lost_time
                if elapsed < 0.7:
                    target_angle = self.last_valid_angle
                else:
                    target_angle *= 0.8 # Freinage progressif

            with self.lock:
                self.frame = frame
                self.steering_angle = int(target_angle)
                self.current_color = detected_color

            time.sleep(0.015)

    def get_stream(self):
        while self.running:
            with self.lock:
                if self.frame is None: continue
                _, buffer = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 50])
                data = buffer.tobytes()
            yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + data + b'\r\n')
            time.sleep(0.04)

app = Flask(__name__)
bot = SlayBotVision()

@app.route('/')
def index(): return render_template('index.html')

@app.route('/video_feed')
def video_feed(): return Response(bot.get_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

async def websocket_client(bot_v):
    uri = "ws://10.42.0.1:8765/pilote"
    while True:
        try:
            async with websockets.connect(uri) as ws:
                while True:
                    with bot_v.lock:
                        payload = json.dumps({"angle": bot_v.steering_angle, "color": bot_v.current_color})
                    await ws.send(payload)
                    await asyncio.sleep(0.02)
        except: await asyncio.sleep(1)

if __name__ == '__main__':
    threading.Thread(target=lambda: asyncio.run(websocket_client(bot)), daemon=True).start()
    app.run(host='0.0.0.0', port=5001, threaded=True, use_reloader=False)