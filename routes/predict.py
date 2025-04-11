import torch
import numpy as np
import cv2
from detectron2.engine import DefaultPredictor
from detectron2.config import get_cfg
from detectron2 import model_zoo
from services.model_service import predict_shot  # Use model loading from this service
from database import get_prediction_logs_collection
from datetime import datetime
from routes.auth import get_current_user  # You’ll need this if using user info
import os

# ---------- Config Detectron2 ----------
cfg = get_cfg()
cfg.merge_from_file(model_zoo.get_config_file("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml"))
cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = 0.5
cfg.MODEL.ROI_HEADS.NUM_CLASSES = 1
cfg.MODEL.WEIGHTS = model_zoo.get_checkpoint_url("COCO-Keypoints/keypoint_rcnn_R_50_FPN_3x.yaml")
cfg.MODEL.DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

predictor = DefaultPredictor(cfg)

# ---------- Fixed Image Dimensions Used During Training ----------
FIXED_WIDTH = 640
FIXED_HEIGHT = 480

# ---------- Extract Keypoints ----------
def extract_keypoints(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"❌ Failed to load image: {image_path}")
        return None

    outputs = predictor(image)
    instances = outputs["instances"]

    if not instances.has("pred_keypoints") or len(instances.pred_keypoints) == 0:
        print("⚠️ No keypoints detected.")
        return None

    keypoints = instances.pred_keypoints[0].cpu().numpy()
    keypoints_xy = keypoints[:, :2]

    if keypoints_xy.shape[0] != 17:
        print("⚠️ Incomplete keypoints detected.")
        return None

    # Flatten and pad if necessary
    flattened = keypoints_xy.flatten().tolist()
    while len(flattened) < 34:
        flattened.append(0.0)
    return flattened[:34]

# ---------- Predict Shot ----------
async def predict_image(image_path, request):
    keypoints = extract_keypoints(image_path)
    if not keypoints:
        return "❌ No valid keypoints found in image."

    scaled = []
    for i in range(0, len(keypoints), 2):
        x = keypoints[i] / FIXED_WIDTH
        y = keypoints[i + 1] / FIXED_HEIGHT
        scaled.extend([x, y])

    normalized = [(val - 0.5) * 2 for val in scaled]
    predicted_label = predict_shot([normalized])
    print(f"🎯 Prediction: {predicted_label}")

    # ✅ Log prediction (without confidence)
    user = await get_current_user(request)
    user_email = user["email"] if user and "email" in user else "unknown"
    logs_collection = get_prediction_logs_collection()

    await logs_collection.insert_one({
    "user_email": user_email,
    "image_name": os.path.basename(image_path),
    "predicted_shot": predicted_label,
    "timestamp": datetime.utcnow()
})


    return predicted_label
