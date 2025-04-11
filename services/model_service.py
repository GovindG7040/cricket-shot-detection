import torch
import torch.nn as nn
import os
import numpy as np

# Define the same model structure as used during training
model = nn.Sequential(
    nn.Linear(34, 128),
    nn.ReLU(),
    nn.Linear(128, 64),
    nn.ReLU(),
    nn.Linear(64, 4)  # 4 classes
)

# Mapping from output class index to label
label_mapping = {
    0: "cover_drive",
    1: "leg_glance",
    2: "pull_shot",
    3: "sweep_shot"
}

# Load the trained model weights
model_path = os.path.join("models", "best_model.pth")
model.load_state_dict(torch.load(model_path, map_location=torch.device("cpu")))
model.eval()

# Prediction function
def predict_shot(keypoints: list) -> str:
    with torch.no_grad():
        input_tensor = torch.tensor(np.array(keypoints), dtype=torch.float32)
        output = model(input_tensor)
        predicted_class = torch.argmax(output).item()
        return label_mapping.get(predicted_class, "unknown")
