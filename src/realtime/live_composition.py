import cv2
import numpy as np
import networkx as nx

from ultralytics import YOLO


# =========================
# LOAD YOLO MODEL
# =========================

model = YOLO("yolov8n.pt")


# =========================
# START WEBCAM
# =========================

cap = cv2.VideoCapture(0)

if not cap.isOpened():

    cap = cv2.VideoCapture(1)


# =========================
# MAIN LOOP
# =========================

while True:

    ret, frame = cap.read()

    if not ret:
        break

    # Flip for mirror view
    frame = cv2.flip(frame, 1)

    h, w, _ = frame.shape

    # =========================
    # RULE OF THIRDS GRID
    # =========================

    third_x1 = w // 3
    third_x2 = 2 * w // 3

    third_y1 = h // 3
    third_y2 = 2 * h // 3

    cv2.line(
        frame,
        (third_x1, 0),
        (third_x1, h),
        (0, 255, 0),
        1
    )

    cv2.line(
        frame,
        (third_x2, 0),
        (third_x2, h),
        (0, 255, 0),
        1
    )

    cv2.line(
        frame,
        (0, third_y1),
        (w, third_y1),
        (0, 255, 0),
        1
    )

    cv2.line(
        frame,
        (0, third_y2),
        (w, third_y2),
        (0, 255, 0),
        1
    )

    # =========================
    # OBJECT DETECTION
    # =========================

    results = model(frame, verbose=False)

    detections = []

    # =========================
    # EXTRACT DETECTIONS
    # =========================

    for box in results[0].boxes:

        cls_id = int(box.cls[0])

        class_name = model.names[cls_id]

        confidence = float(box.conf[0])

        x1, y1, x2, y2 = (
            box.xyxy[0]
            .cpu()
            .numpy()
        )

        x1 = int(x1)
        y1 = int(y1)
        x2 = int(x2)
        y2 = int(y2)

        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)

        width = x2 - x1
        height = y2 - y1

        area = width * height

        # Save detection
        detections.append({

            "class": class_name,

            "confidence": confidence,

            "x1": x1,
            "y1": y1,
            "x2": x2,
            "y2": y2,

            "center_x": center_x,
            "center_y": center_y,

            "area": area
        })

        # =========================
        # DRAW BOUNDING BOX
        # =========================

        cv2.rectangle(
            frame,
            (x1, y1),
            (x2, y2),
            (255, 0, 0),
            2
        )

        # Label
        label = f"{class_name} {confidence:.2f}"

        cv2.putText(
            frame,
            label,
            (x1, y1 - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (255, 255, 255),
            1
        )

        # Center Point
        cv2.circle(
            frame,
            (center_x, center_y),
            6,
            (0, 0, 255),
            -1
        )

    # =========================
    # BUILD LIVE SCG
    # =========================

    G = nx.Graph()

    # Add nodes
    for idx, det in enumerate(detections):

        G.add_node(

            idx,

            center_x=det["center_x"],

            center_y=det["center_y"],

            area=det["area"],

            label=det["class"]
        )

    # Add edges
    nodes = list(G.nodes())

    for i in range(len(nodes)):

        for j in range(i + 1, len(nodes)):

            n1 = G.nodes[nodes[i]]
            n2 = G.nodes[nodes[j]]

            dx = n1["center_x"] - n2["center_x"]
            dy = n1["center_y"] - n2["center_y"]

            distance = np.sqrt(dx**2 + dy**2)

            G.add_edge(

                nodes[i],
                nodes[j],

                distance=distance
            )

    # =========================
    # DRAW TENSION GRAPH
    # =========================

    for u, v, data in G.edges(data=True):

        n1 = G.nodes[u]
        n2 = G.nodes[v]

        x1g = int(n1["center_x"])
        y1g = int(n1["center_y"])

        x2g = int(n2["center_x"])
        y2g = int(n2["center_y"])

        distance = data["distance"]

        # Closer objects => thicker line
        thickness = int(
            max(1, min(6, 400 / (distance + 1)))
        )

        cv2.line(
            frame,
            (x1g, y1g),
            (x2g, y2g),
            (0, 255, 255),
            thickness
        )

    # =========================
    # BALANCE ANALYSIS
    # =========================

    left_weight = 0
    right_weight = 0

    for det in detections:

        if det["center_x"] < w // 2:

            left_weight += det["area"]

        else:

            right_weight += det["area"]

    total_weight = left_weight + right_weight + 1

    balance_score = (
        1 -
        abs(left_weight - right_weight)
        / total_weight
    )

    # =========================
    # COMPOSITION FEEDBACK
    # =========================

    feedback = ""

    if balance_score > 0.85:

        feedback = "Balanced Composition"

        feedback_color = (0, 255, 0)

    elif balance_score > 0.6:

        feedback = "Moderately Balanced"

        feedback_color = (0, 255, 255)

    else:

        feedback = "Unbalanced Framing"

        feedback_color = (0, 0, 255)

    # =========================
    # RULE OF THIRDS ANALYSIS
    # =========================

    thirds_feedback = ""

    thirds_points = [

        (w // 3, h // 3),

        (2 * w // 3, h // 3),

        (w // 3, 2 * h // 3),

        (2 * w // 3, 2 * h // 3)
    ]

    if len(detections) > 0:

        main_subject = max(
            detections,
            key=lambda x: x["area"]
        )

        cx = main_subject["center_x"]
        cy = main_subject["center_y"]

        distances = []

        for tx, ty in thirds_points:

            d = np.sqrt(
                (cx - tx) ** 2 +
                (cy - ty) ** 2
            )

            distances.append(d)

        min_distance = min(distances)

        if min_distance < 80:

            thirds_feedback = "Strong Thirds Alignment"

        elif min_distance < 160:

            thirds_feedback = "Moderate Thirds Alignment"

        else:

            thirds_feedback = "Weak Thirds Alignment"

    # =========================
    # DISPLAY TEXT
    # =========================

    cv2.putText(
        frame,
        feedback,
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        feedback_color,
        2
    )

    cv2.putText(
        frame,
        f"Balance Score: {balance_score:.2f}",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        thirds_feedback,
        (30, 120),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Subjects: {len(detections)}",
        (30, 160),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    # =========================
    # DISPLAY WINDOW
    # =========================

    cv2.imshow(
        "StructCompose Live AI Cinematography Assistant",
        frame
    )

    # =========================
    # EXIT KEY
    # =========================

    key = cv2.waitKey(1)

    if key & 0xFF == ord('q'):

        break


# =========================
# CLEANUP
# =========================

cap.release()

cv2.destroyAllWindows()