import cv2
import logging
import threading
import numpy as np
import time
import subprocess
from flask import Flask, Response, jsonify, render_template

# --- CONFIGURATION ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CameraManager:
    def __init__(self, index=0):
        self.index = index
        self.cap = None
        self.frame = None
        self.line_x = 0
        self.turn_hint = "STEADY"
        self.detected_color = "NONE"
        self.lock = threading.Lock()
        self.running = True

        self._force_release()
        
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()

    def _force_release(self):
        try:
            logger.info("NETTOYAGE SYSTEME CAMERA...")
            subprocess.run(["sudo", "fuser", "-k", f"/dev/video{self.index}"], capture_output=True)
            time.sleep(1)
        except: pass

    def _init_camera(self):
        logger.info(f"INITIALISATION /dev/video{self.index}...")
        # Utilisation de CAP_V4L2 pour la stabilité sur Raspberry Pi
        cap = cv2.VideoCapture(self.index, cv2.CAP_V4L2)
        
        if not cap.isOpened():
            return None

        # Optimisation du flux
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        
        time.sleep(1.5) # Temps de stabilisation
        success, _ = cap.read()
        if success:
            logger.info("✅ SIGNAL ETABLI")
            return cap
        
        cap.release()
        return None

    def _update_loop(self):
            self.cap = self._init_camera()
            
            # --- CONFIGURATION DES COULEURS (A ajuster selon tes tests) ---
            color_ranges = {
                "JAUNE": (np.array([20, 100, 100]), np.array([35, 255, 255])),
                "BLEU":  (np.array([100, 150, 50]), np.array([130, 255, 255])),
                "ROUGE": (np.array([0, 150, 50]),   np.array([10, 255, 255])),
                "VERT":  (np.array([40, 100, 50]),  np.array([80, 255, 255]))
            }

            while self.running:
                if self.cap is None:
                    time.sleep(3); self.cap = self._init_camera(); continue

                success, frame = self.cap.read()
                if not success or frame is None:
                    self.cap.release(); self.cap = None; continue

                try:
                    h, w = frame.shape[:2]
                    center_screen = w // 2
                    
                    blurred = cv2.GaussianBlur(frame, (5, 5), 0)
                    hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

                    active_mask = None
                    line_color = "NONE"
                    max_area = 0
                    
                    for name, (low, high) in color_ranges.items():
                        m = cv2.inRange(hsv, low, high)
                        area = cv2.countNonZero(m[int(h*0.5):h, :]) 
                        if area > max_area and area > 800:
                            max_area = area
                            active_mask = m
                            line_color = name

                    turn_msg = "LOST"
                    prediction_x = center_screen

                    if active_mask is not None:
                        # Bas (0.85h), Milieu (0.65h), Haut (0.45h)
                        points = []
                        for v_ratio in [0.85, 0.65, 0.45]:
                            v_pos = int(h * v_ratio)
                            roi_strip = active_mask[v_pos-10:v_pos+10, :]
                            M = cv2.moments(roi_strip)
                            if M["m00"] > 100:
                                cx_strip = int(M["m10"] / M["m00"])
                                points.append((cx_strip, v_pos))
                                # Dessiner les points de détection
                                cv2.circle(frame, (cx_strip, v_pos), 5, (0, 255, 255), -1)

                        if len(points) >= 1:
                            # La cible est la moyenne pondérée (on donne plus de poids au lointain pour anticiper)
                            # Si on a plusieurs points, on peut calculer la dérive
                            if len(points) == 3:
                                # Poids : 20% bas, 30% milieu, 50% haut (nticipation forte)
                                prediction_x = int(points[0][0]*0.2 + points[1][0]*0.3 + points[2][0]*0.5)
                                cv2.line(frame, points[0], points[2], (255, 0, 255), 3)
                            else:
                                prediction_x = points[0][0]

                            error = prediction_x - center_screen
                            
                            contours, _ = cv2.findContours(active_mask[int(h*0.7):int(h*0.9), :], 
                                                        cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                            if contours:
                                largest = max(contours, key=cv2.contourArea)
                                lx, ly, lw, lh = cv2.boundingRect(largest)
                                cv2.rectangle(frame, (lx, int(h*0.7)), (lx+lw, int(h*0.9)), (0, 0, 255), 2)

                            # Logique de virage prédictive
                            if error < -60: turn_msg = "SHARP_LEFT"
                            elif error < -20: turn_msg = "LEFT"
                            elif error > 60: turn_msg = "SHARP_RIGHT"
                            elif error > 20: turn_msg = "RIGHT"
                            else: turn_msg = "FORWARD"

                    # 4. MISE À JOUR DES DONNÉES
                    with self.lock:
                        self.frame = frame
                        self.line_x = prediction_x
                        self.turn_hint = f"{line_color}_{turn_msg}"
                        self.detected_color = line_color

                except Exception as e:
                    logger.error(f"Vision Error: {e}")

                time.sleep(0.01) 

    def get_frames(self):
        while self.running:
            with self.lock:
                if self.frame is not None:
                    ret, buffer = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
                    if ret:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            time.sleep(0.05)

camera = CameraManager(index=0)

# --- ROUTES FLASK ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(camera.get_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    return jsonify({
        "x": camera.line_x,
        "turn": camera.turn_hint,
        "color": camera.detected_color
    })

if __name__ == '__main__':
    # use_reloader=False est CRUCIAL pour ne pas instancier la caméra 2 fois
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=False, use_reloader=False)