import os
import sys
import torch
import onnxscript

# ---------------------------------------------------
# ADD PROJECT ROOT TO PYTHON PATH
# ---------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

PROJECT_ROOT = os.path.abspath(
    os.path.join(CURRENT_DIR, "..")
)

sys.path.append(PROJECT_ROOT)

# ---------------------------------------------------
# IMPORT MODEL
# ---------------------------------------------------

from src.models.hybrid_model import HybridComposeNet

# ---------------------------------------------------
# DEVICE CONFIGURATION
# ---------------------------------------------------

device = torch.device(
    "cuda" if torch.cuda.is_available()
    else "cpu"
)

print(f"Using device: {device}")

# ---------------------------------------------------
# MODEL PATH
# ---------------------------------------------------

MODEL_PATH = os.path.join(
    PROJECT_ROOT,
    "checkpoints",
    "hybrid_compose_net.pth"
)

# ---------------------------------------------------
# LOAD MODEL
# ---------------------------------------------------

model = HybridComposeNet().to(device)

# ---------------------------------------------------
# LOAD CHECKPOINT
# ---------------------------------------------------

if not os.path.exists(MODEL_PATH):

    raise FileNotFoundError(
        f"Model checkpoint not found:\n{MODEL_PATH}"
    )

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device
)

model.load_state_dict(checkpoint)

# ---------------------------------------------------
# SET EVAL MODE
# ---------------------------------------------------

model.eval()

print("HybridComposeNet loaded successfully.")

# ---------------------------------------------------
# OPTIONAL: ENABLE CUDA OPTIMIZATION
# ---------------------------------------------------

if torch.cuda.is_available():

    torch.backends.cudnn.benchmark = True

# ---------------------------------------------------
# OPTIONAL TEST
# ---------------------------------------------------

if __name__ == "__main__":

    dummy_image = torch.randn(
        1,
        3,
        224,
        224
    ).to(device)
traced_model = torch.jit.trace(

    model.cnn,

    dummy_image
)
traced_model.save(

    r"C:\Users\bhanu\Downloads\StructCompose\checkpoints\cnn_traced.pt"
)
torch.onnx.export(

    model.cnn,

    dummy_image,

    r"C:\Users\bhanu\Downloads\StructCompose\checkpoints\cnn.onnx",

    input_names=["input"],

    output_names=["output"],

    opset_version=11
)
print("Model exported successfully")

