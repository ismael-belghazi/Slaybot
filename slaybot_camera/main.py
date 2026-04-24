from picamera2 import Picamera2
import cv2
import numpy as np
import time

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 480)})
picam2.configure(config)
picam2.start()

time.sleep(2)

COLORS = {
    "ROUGE": [((0,120,70),(10,255,255)), ((170,120,70),(180,255,255))],
    "BLEU": [((100,150,50),(140,255,255))],
    "VERT": [((40,70,70),(80,255,255))],
    "JAUNE": [((20,100,100),(30,255,255))]
}

def get_mask(hsv, ranges):
    mask = None
    for low, high in ranges:
        m = cv2.inRange(hsv, np.array(low), np.array(high))
        mask = m if mask is None else mask + m
    return mask


# 🔥 EXTRACTION CENTRE LIGNE
def extract_center_points(mask):
    h, w = mask.shape
    pts = []

    for y in range(0, h, 3):
        xs = np.where(mask[y] > 0)[0]
        if len(xs) > 20:
            x_mean = int(np.mean(xs))
            pts.append([x_mean, y])

    return np.array(pts, dtype=np.int32)


# 🔥 SIMPLIFICATION EN VECTEURS
def simplify_line(points):
    if len(points) < 10:
        return None

    # approx polyligne
    epsilon = 10  # précision (à ajuster)
    approx = cv2.approxPolyDP(points, epsilon, False)

    return approx.reshape(-1, 2)


while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    for name, ranges in COLORS.items():

        mask = get_mask(hsv, ranges)

        kernel = np.ones((5,5), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

        # 1. extraire centre ligne
        pts = extract_center_points(mask)

        if pts is None or len(pts) < 10:
            continue

        # 2. simplifier en vecteurs
        poly = simplify_line(pts)

        if poly is None:
            continue

        color_draw = (0,0,255) if name=="ROUGE" else \
                     (255,0,0) if name=="BLEU" else \
                     (0,255,0) if name=="VERT" else \
                     (0,255,255)

        # 3. dessiner vecteurs
        for i in range(len(poly)-1):
            p1 = tuple(poly[i])
            p2 = tuple(poly[i+1])

            cv2.line(frame, p1, p2, color_draw, 4)

            # afficher vecteur
            dx = p2[0] - p1[0]
            dy = p2[1] - p1[1]
            print(name, "vecteur:", (dx, dy))

        # points clés
        for p in poly:
            cv2.circle(frame, tuple(p), 5, (255,255,255), -1)

    cv2.imshow("Vecteurs lignes", frame)

    if cv2.waitKey(1) == 27:
        break

cv2.destroyAllWindows()
picam2.stop()
