import cv2
import os
import logging
import threading
import numpy as np
import time
from flask import Flask, Response, render_template_string, jsonify

# Configuration du logging pour un suivi professionnel
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class CameraManager:
    """Gère la capture vidéo de manière sécurisée et optimisée."""
    def __init__(self, index=0):
        self.index = index
        # Utilisation de CAP_V4L2 pour une meilleure compatibilité sur Raspberry Pi/Linux
        self.cap = cv2.VideoCapture(index, cv2.CAP_V4L2)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        self.frame = None
        self.line_x = -1
        self.detected_color = "None"
        self.lock = threading.Lock()
        self.running = True

        if not self.cap.isOpened():
            logger.error(f"Impossible d'ouvrir la caméra à l'index {index}")
        else:
            # Thread de lecture pour éviter les lags de buffer
            self.thread = threading.Thread(target=self._update_loop, daemon=True)
            self.thread.start()

    def _update_loop(self):
        while self.running:
            success, frame = self.cap.read()
            if not success:
                continue

            # --- Traitement d'image pour suivi de ligne et couleurs ---
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            
            # 1. Détection de ligne (Ligne noire)
            lower_black = np.array([0, 0, 0])
            upper_black = np.array([180, 255, 60])
            mask_line = cv2.inRange(hsv, lower_black, upper_black)
            
            # Focus sur le bas de l'image (ROI)
            h, w = mask_line.shape
            roi = mask_line[int(h*0.7):h, 0:w]
            M = cv2.moments(roi)
            
            cx = -1
            if M["m00"] > 0:
                cx = int(M["m10"] / M["m00"])
                # Guide visuel vert sur le flux
                cv2.circle(frame, (cx, int(h*0.85)), 10, (0, 255, 0), -1)

            # 2. Détection de couleur dominante (Rouge / Vert)
            color_detected = "None"
            mask_red = cv2.inRange(hsv, np.array([0, 120, 70]), np.array([10, 255, 255]))
            mask_green = cv2.inRange(hsv, np.array([35, 40, 40]), np.array([85, 255, 255]))
            
            if cv2.countNonZero(mask_red) > 8000: color_detected = "Red"
            elif cv2.countNonZero(mask_green) > 8000: color_detected = "Green"

            with self.lock:
                self.frame = frame
                self.line_x = cx
                self.detected_color = color_detected

    def get_frames(self):
        """Générateur de flux MJPEG haute performance."""
        while self.running:
            with self.lock:
                if self.frame is None:
                    continue
                ret, buffer = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
                if not ret:
                    continue
                frame_bytes = buffer.tobytes()
                
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            time.sleep(0.03) # Limite à ~30 FPS pour économiser le CPU

    def __del__(self):
        self.running = False
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            logger.info("Ressources caméra libérées.")

camera = CameraManager(int(os.environ.get("CAMERA_INDEX", 0)))

@app.route('/')
def index():
    """Interface de visualisation minimaliste et moderne."""
    return render_template_string("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>SlayBot Vision</title>
            <style>
                body { margin: 0; background: #000; color: white; display: flex; flex-direction: column; justify-content: center; align-items: center; height: 100vh; font-family: sans-serif; }
                img { max-width: 90%; border: 2px solid #333; border-radius: 8px; }
                .overlay { position: absolute; top: 10px; left: 10px; background: rgba(0,0,0,0.7); padding: 15px; border-radius: 8px; border: 1px solid #0f0; }
                .val { color: #0f0; font-family: monospace; font-size: 1.2em; }
            </style>
            <script>
                setInterval(() => {
                    fetch('/status').then(r => r.json()).then(data => {
                        document.getElementById('lx').innerText = data.line_x;
                        document.getElementById('clr').innerText = data.color;
                    });
                }, 100);
            </script>
        </head>
        <body>
            <div class="overlay">
                Pos Ligne: <span id="lx" class="val">-</span><br>
                Couleur: <span id="clr" class="val">-</span>
            </div>
            <img src="{{ url_for('video_feed') }}" alt="Live Feed">
        </body>
        </html>
    """)

@app.route('/video_feed')
def video_feed():
    """Point d'entrée du flux vidéo pour le robot ou le dashboard."""
    return Response(camera.get_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/status')
def status():
    """API pour récupérer les données de suivi (ligne et couleur)."""
    return jsonify({
        "line_x": camera.line_x,
        "color": camera.detected_color
    })

if __name__ == '__main__':
    port = int(os.environ.get("CAMERA_PORT", 5001))
    app.run(host='0.0.0.0', port=port, threaded=True, debug=False)