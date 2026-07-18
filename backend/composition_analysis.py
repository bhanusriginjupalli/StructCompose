import cv2
import numpy as np
from ultralytics import YOLO

# ---------------------------------------------------
# LOAD YOLO MODEL
# ---------------------------------------------------

model = YOLO("yolov8n.pt")


# ---------------------------------------------------
# RULE OF THIRDS SCORE
# ---------------------------------------------------

def compute_thirds_score(
    detections,
    width,
    height
):

    # Rule-of-thirds intersection points

    thirds_points = [

        (width / 3, height / 3),

        (2 * width / 3, height / 3),

        (width / 3, 2 * height / 3),

        (2 * width / 3, 2 * height / 3)
    ]

    scores = []

    # Compare each subject center
    # to nearest thirds intersection

    for det in detections:

        cx = det["cx"]
        cy = det["cy"]

        distances = []

        for tx, ty in thirds_points:

            d = np.sqrt(

                (cx - tx) ** 2
                +
                (cy - ty) ** 2
            )

            distances.append(d)

        min_dist = min(distances)

        # Normalize score

        score = 1 - (

            min_dist
            /
            np.sqrt(width**2 + height**2)
        )

        scores.append(score)

    if len(scores) == 0:

        return 0.0

    return float(np.mean(scores))


# ---------------------------------------------------
# MAIN COMPOSITION ANALYSIS
# ---------------------------------------------------

def analyze_composition(frame):

    # ---------------------------------------------------
    # IMAGE SIZE
    # ---------------------------------------------------

    h, w, _ = frame.shape

    # ---------------------------------------------------
    # OBJECT DETECTION
    # ---------------------------------------------------

    results = model(frame, verbose=False)

    detections = []

    # ---------------------------------------------------
    # EXTRACT DETECTIONS
    # ---------------------------------------------------

    for box in results[0].boxes:

        x1, y1, x2, y2 = (

            box.xyxy[0]
            .cpu()
            .numpy()
        )

        # Center point

        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

        # Bounding box area

        area = (

            (x2 - x1)
            *
            (y2 - y1)
        )

        # Class info

        cls_id = int(box.cls[0])

        class_name = model.names[cls_id]

        confidence = float(box.conf[0])

        # Store detection

        detections.append({

            "class": class_name,

            "confidence": confidence,

            "x1": float(x1),

            "y1": float(y1),

            "x2": float(x2),

            "y2": float(y2),

            "cx": float(cx),

            "cy": float(cy),

            "area": float(area)
        })

    # ---------------------------------------------------
    # BALANCE SCORE
    # ---------------------------------------------------

    left_weight = 0
    right_weight = 0

    for det in detections:

        if det["cx"] < w / 2:

            left_weight += det["area"]

        else:

            right_weight += det["area"]

    total = left_weight + right_weight + 1

    balance_score = (

        1 -

        abs(
            left_weight
            -
            right_weight
        ) / total
    )

    # ---------------------------------------------------
    # TENSION SCORE
    # ---------------------------------------------------

    tension_score = 0

    if len(detections) > 1:

        distances = []

        for i in range(len(detections)):

            for j in range(i + 1, len(detections)):

                dx = (
                    detections[i]["cx"]
                    -
                    detections[j]["cx"]
                )

                dy = (
                    detections[i]["cy"]
                    -
                    detections[j]["cy"]
                )

                d = np.sqrt(
                    dx**2 + dy**2
                )

                distances.append(d)

        tension_score = np.mean(
            distances
        ) / w

    # ---------------------------------------------------
    # SYMMETRY SCORE
    # ---------------------------------------------------

    gray = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2GRAY
    )

    flipped = cv2.flip(gray, 1)

    diff = cv2.absdiff(
        gray,
        flipped
    )

    symmetry_score = (

        1 -

        np.mean(diff) / 255
    )

    # ---------------------------------------------------
    # RULE OF THIRDS SCORE
    # ---------------------------------------------------

    thirds_score = compute_thirds_score(

        detections,
        w,
        h
    )

    # ---------------------------------------------------
    # FINAL COMPOSITION SCORE
    # ---------------------------------------------------

    composition_score = (

        0.3 * balance_score

        +

        0.25 * symmetry_score

        +

        0.25 * (1 - tension_score)

        +

        0.2 * thirds_score
    )

    # ---------------------------------------------------
    # REASONING ENGINE
    # ---------------------------------------------------

    feedback = []

    # Balance

    if balance_score > 0.8:

        feedback.append(
            "Frame is visually balanced."
        )

    else:

        feedback.append(
            "Composition feels asymmetric."
        )

    # Symmetry

    if symmetry_score > 0.7:

        feedback.append(
            "Strong symmetry detected."
        )

    else:

        feedback.append(
            "Frame lacks strong symmetry."
        )

    # Tension

    if tension_score > 0.4:

        feedback.append(
            "Subjects create dynamic tension."
        )

    else:

        feedback.append(
            "Composition feels visually calm."
        )

    # Rule of thirds

    if thirds_score > 0.75:

        feedback.append(
            "Subjects align well with rule-of-thirds intersections."
        )

    else:

        feedback.append(
            "Subject placement could better follow rule-of-thirds framing."
        )

    # Subject count

    if len(detections) == 0:

        feedback.append(
            "No dominant subjects detected."
        )

    elif len(detections) == 1:

        feedback.append(
            "Single-subject composition detected."
        )

    else:

        feedback.append(
            f"{len(detections)} compositional subjects detected."
        )

    # ---------------------------------------------------
    # RETURN RESULTS
    # ---------------------------------------------------

    return {

        "composition_score":
            float(composition_score),

        "balance_score":
            float(balance_score),

        "symmetry_score":
            float(symmetry_score),

        "tension_score":
            float(tension_score),

        "thirds_score":
            float(thirds_score),

        "feedback":
            feedback,

        "detections":
            detections
    }