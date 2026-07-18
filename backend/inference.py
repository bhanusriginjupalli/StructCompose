import cv2
import torch
import numpy as np
import torchvision.transforms as transforms

from load_model import model, device

# IMAGE PREPROCESSING TRANSFORM

transform = transforms.Compose([

    transforms.ToPILImage(),

    transforms.Resize((224, 224)),

    transforms.ToTensor(),

    transforms.Normalize(

        mean=[0.485, 0.456, 0.406],

        std=[0.229, 0.224, 0.225]
    )
])

# PREDICTION FUNCTION

def predict_composition(frame):

    # CONVERT BGR → RGB

    image = cv2.cvtColor(

        frame,

        cv2.COLOR_BGR2RGB
    )

    # APPLY TRANSFORM

    image_tensor = transform(image)

    # ADD BATCH DIMENSION

    image_tensor = image_tensor.unsqueeze(0)

    # MOVE TO DEVICE

    image_tensor = image_tensor.to(device)

    # INFERENCE

    with torch.no_grad():

        features = model.cnn(
            image_tensor
        )

    # RETURN NUMPY FEATURES

    return features.cpu().numpy()