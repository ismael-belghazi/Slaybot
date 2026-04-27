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
            
            color_ranges = {
                "JAUNE": (np.array([15, 80, 80]), np.array([40, 255, 255])),
                "BLEU":  (np.array([90, 60, 40]), np.array([140, 255, 255])), # Plus large pour le bleu
                "ROUGE": (np.array([0, 100, 40]),  np.array([10, 255, 255])),
                "VERT":  (np.array([40, 50, 40]),   np.array([90, 255, 255]))
            }

            self.last_valid_color = "NONE"

            while self.running:
                if self.cap is None:
                    time.sleep(1); self.cap = self._init_camera(); continue

                success, frame = self.cap.read()
                if not success: continue

                try:
                    h, w = frame.shape[:2]
                    overlay = frame.copy()

                    # 1. PERSPECTIVE
                    src_pts = np.float32([[20, h], [w-20, h], [int(w*0.65), int(h*0.4)], [int(w*0.35), int(h*0.4)]])
                    dst_pts = np.float32([[w//4, h], [3*w//4, h], [3*w//4, 0], [w//4, 0]])
                    M_persp = cv2.getPerspectiveTransform(src_pts, dst_pts)
                    M_inv = cv2.getPerspectiveTransform(dst_pts, src_pts)
                    
                    bird_view = cv2.warpPerspective(frame, M_persp, (w, h))
                    hsv = cv2.cvtColor(cv2.GaussianBlur(bird_view, (7, 7), 0), cv2.COLOR_BGR2HSV)

                    # 2. DÉTECTION DE COULEUR AVEC PRIORITÉ
                    active_mask = None
                    current_color = "NONE"
                    max_area = 0

                    for name, (low, high) in color_ranges.items():
                        mask = cv2.inRange(hsv, low, high)
                        # On check la zone basse pour confirmer la couleur
                        area = cv2.countNonZero(mask[int(h*0.5):, :])
                        if area > max_area and area > 400: # Seuil légèrement baissé
                            max_area = area
                            active_mask = mask
                            current_color = name
                    
                    # --- SYSTÈME DE MÉMOIRE ---
                    if current_color != "NONE":
                        self.last_valid_color = current_color
                    
                    target_x = w // 2
                    turn_hint = "LOST"

                    if active_mask is not None:
                        curve_points_bird = []
                        num_steps = 10
                        for i in range(num_steps):
                            curr_y = int(h - (i * (h / num_steps)) - 10)
                            row_pixels = np.where(active_mask[curr_y, :] > 0)[0]
                            if len(row_pixels) > 0:
                                center = (row_pixels[0] + row_pixels[-1]) // 2
                                curve_points_bird.append([center, curr_y])

                        if len(curve_points_bird) > 1:
                            pts = np.array([curve_points_bird], dtype='float32')
                            projected_pts = cv2.perspectiveTransform(pts, M_inv)[0]

                            # Dessin de la trajectoire
                            for j in range(len(projected_pts) - 1):
                                cv2.line(overlay, tuple(projected_pts[j].astype(int)), 
                                        tuple(projected_pts[j+1].astype(int)), (0, 255, 0), 3)

                            target_x = curve_points_bird[-1][0]
                            error = target_x - (w // 2)
                            
                            if abs(error) < 20: turn_hint = "FORWARD"
                            elif error > 0: turn_hint = "RIGHT"
                            else: turn_hint = "LEFT"

                    # 3. MISE À JOUR ET ENVOI
                    with self.lock:
                        self.frame = overlay 
                        self.line_x = target_x
                        # On utilise self.last_valid_color pour que l'UI ne clignote pas
                        self.turn_hint = f"{self.last_valid_color}_{turn_hint}"
                        self.detected_color = self.last_valid_color

                    # Debug dans la console pour vérifier
                    if current_color != "NONE":
                        logger.debug(f"Détection active: {current_color}")

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