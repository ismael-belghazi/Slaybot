import cv2
import logging
import threading
import numpy as np
import time
import subprocess
import json
import asyncio
import websockets
from flask import Flask, Response, jsonify, render_template

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CameraManager:
    def __init__(self, index=0):
        self.index = index
        self.cap = None
        self.frame = None
        self.steering_angle = 0  
        self.turn_hint = "STEADY"
        self.detected_color = "NONE"
        
        # --- LOGIQUE DE VERROUILLAGE ---
        self.current_track_color = "NONE" 
        
        self.lock = threading.Lock()
        self.running = True
        self.ws_url = "ws://10.42.0.1:8765/pilote"

        self._force_release()
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        self.ws_thread = threading.Thread(target=self._start_ws_client, daemon=True)
        self.ws_thread.start()

    def _force_release(self):
        try:
            subprocess.run(["sudo", "fuser", "-k", f"/dev/video{self.index}"], capture_output=True, check=False)
            time.sleep(0.5)
        except: pass

    def _init_camera(self):
        cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)
        if not cap.isOpened(): return None
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        return cap

    def _start_ws_client(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._ws_loop())

    async def _ws_loop(self):
        while self.running:
            try:
                async with websockets.connect(self.ws_url, ping_interval=5, ping_timeout=2) as ws:
                    while self.running:
                        with self.lock:
                            payload = {"angle": self.steering_angle, "color": self.detected_color, "hint": self.turn_hint}
                        await ws.send(json.dumps(payload))
                        await asyncio.sleep(0.05)
            except: await asyncio.sleep(2)

    def _update_loop(self):
        self.cap = self._init_camera()
        
        color_ranges = {
            "JAUNE": (np.array([18, 80, 80]), np.array([38, 255, 255])),
            "BLEU":  (np.array([90, 100, 50]), np.array([130, 255, 255])),
            "ROUGE": [(np.array([0, 120, 70]), np.array([10, 255, 255])), (np.array([170, 120, 70]), np.array([180, 255, 255]))],
            "VERT":  (np.array([45, 70, 50]), np.array([85, 255, 255]))
        }

        kernel = np.ones((5,5), np.uint8)

        while self.running:
            if self.cap is None:
                self.cap = self._init_camera(); continue

            success, frame = self.cap.read()
            if not success: continue

            try:
                h, w = frame.shape[:2]
                
                # 1. PERSPECTIVE (Bird's Eye)
                src_pts = np.float32([[15, h], [w-15, h], [int(w*0.65), int(h*0.4)], [int(w*0.35), int(h*0.4)]])
                dst_pts = np.float32([[w//4, h], [3*w//4, h], [3*w//4, 0], [w//4, 0]])
                M_persp = cv2.getPerspectiveTransform(src_pts, dst_pts)
                M_inv = cv2.getPerspectiveTransform(dst_pts, src_pts)
                
                bird_view = cv2.warpPerspective(frame, M_persp, (w, h))
                hsv = cv2.cvtColor(cv2.GaussianBlur(bird_view, (5, 5), 0), cv2.COLOR_BGR2HSV)

                # 2. TRAITEMENT MULTI-MASQUES
                masks = {}
                visibility = {}
                
                for name, r in color_ranges.items():
                    if name == "ROUGE":
                        mask = cv2.bitwise_or(cv2.inRange(hsv, r[0][0], r[0][1]), cv2.inRange(hsv, r[1][0], r[1][1]))
                    else:
                        mask = cv2.inRange(hsv, r[0], r[1])
                    
                    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
                    masks[name] = mask
                    # On mesure la présence de chaque couleur en bas de l'image (proche du robot)
                    visibility[name] = cv2.countNonZero(mask[int(h*0.7):, :])

                # 3. LOGIQUE DE SELECTION DE CIBLE
                if self.current_track_color == "NONE" or visibility.get(self.current_track_color, 0) < 100:
                    best_c = max(visibility, key=visibility.get)
                    if visibility[best_c] > 400:
                        self.current_track_color = best_c
                    else:
                        self.current_track_color = "NONE"

                # 4. CALCUL DE L'ANGLE (Uniquement sur la couleur verrouillée)
                new_angle = 0
                hint = "SEARCHING"
                
                target_mask = masks.get(self.current_track_color)
                if target_mask is not None and self.current_track_color != "NONE":
                    points = []
                    last_x = w // 2
                    
                    for i in range(10):
                        y = int(h - (i * (h / 12)) - 10)
                        row = target_mask[y, :]
                        pixels = np.where(row > 0)[0]
                        
                        if len(pixels) > 0:
                            # Gestion des bifurcations de même couleur : on prend le cluster le plus proche
                            diff = np.diff(pixels)
                            split_indices = np.where(diff > 15)[0] + 1
                            clusters = np.split(pixels, split_indices)
                            best_cluster = min(clusters, key=lambda c: abs(np.mean(c) - last_x))
                            
                            mid = int(np.mean(best_cluster))
                            points.append((mid, y, i + 1))
                            last_x = mid

                    if len(points) >= 2:
                        total_weight = sum(p[2] for p in points)
                        avg_x = sum(p[0] * p[2] for p in points) / total_weight
                        
                        dx = avg_x - (w // 2)
                        dy = h * 0.6
                        new_angle = int(np.clip(np.degrees(np.arctan2(dx, dy)) * 1.3, -45, 45))
                        hint = "FORWARD" if abs(new_angle) < 7 else ("RIGHT" if new_angle > 0 else "LEFT")

                        # --- DESSIN DEBUG ---
                        # On dessine UNIQUEMENT la trajectoire de la couleur suivie
                        pts_draw = np.array([[p[0], p[1]] for p in points], dtype='float32')
                        projected = cv2.perspectiveTransform(np.array([pts_draw]), M_inv)[0]
                        for j in range(len(projected)-1):
                            cv2.line(frame, tuple(projected[j].astype(int)), tuple(projected[j+1].astype(int)), (0, 255, 0), 3)

                with self.lock:
                    self.frame = frame
                    self.steering_angle = new_angle
                    self.detected_color = self.current_track_color
                    self.turn_hint = f"{self.current_track_color}_{hint}"

            except Exception as e:
                logger.error(f"Vision Error: {e}")
            time.sleep(0.01)

    def get_frames(self):
        while self.running:
            with self.lock:
                if self.frame is not None:
                    ret, buffer = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
                    if ret: yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.04)

camera = CameraManager(index=0)

@app.route('/')
def index(): return render_template('index.html')

@app.route('/video_feed')
def video_feed(): return Response(camera.get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    with camera.lock:
        return jsonify({"angle": camera.steering_angle, "turn": camera.turn_hint, "color": camera.detected_color})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=False, use_reloader=False)