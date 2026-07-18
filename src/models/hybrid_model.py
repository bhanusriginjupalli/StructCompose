import torch
import torch.nn.functional as F

import torchvision.models as models

from torch.nn import Linear

from torch_geometric.nn import (
    GCNConv,
    global_mean_pool
)


# -----------------------------
# CNN BACKBONE
# -----------------------------

cnn_backbone = models.resnet18(
    weights="DEFAULT"
)

# Remove classification layer
cnn_backbone.fc = torch.nn.Identity()


# -----------------------------
# HYBRID CNN + GNN MODEL
# -----------------------------

class HybridComposeNet(torch.nn.Module):

    def __init__(self):

        super().__init__()

        # CNN branch
        self.cnn = cnn_backbone

        # GNN branch
        self.conv1 = GCNConv(4, 32)

        self.conv2 = GCNConv(32, 64)

        # Fusion layers
        self.fc1 = Linear(512 + 64, 128)

        self.fc2 = Linear(128, 64)

        self.fc3 = Linear(64, 1)

    def forward(self, data):

        # -----------------------------
        # IMAGE FEATURES
        # -----------------------------

        images = data.image

        cnn_features = self.cnn(images)

        # -----------------------------
        # GRAPH FEATURES
        # -----------------------------

        x = data.x

        edge_index = data.edge_index

        batch = data.batch

        x = self.conv1(x, edge_index)

        x = F.relu(x)

        x = self.conv2(x, edge_index)

        x = F.relu(x)

        graph_features = global_mean_pool(
            x,
            batch
        )

        # -----------------------------
        # FEATURE FUSION
        # -----------------------------

        combined = torch.cat(
            [cnn_features, graph_features],
            dim=1
        )

        x = self.fc1(combined)

        x = F.relu(x)

        x = self.fc2(x)

        x = F.relu(x)

        output = self.fc3(x)

        return output

    # ---------------------------------
    # EMBEDDING EXTRACTION
    # ---------------------------------

    def extract_embedding(self, data):

        # IMAGE FEATURES

        
        images = data.image.view(-1, 3, 224, 224)

        cnn_features = self.cnn(images)

        # GRAPH FEATURES

        x = data.x

        edge_index = data.edge_index

        batch = data.batch

        x = self.conv1(x, edge_index)

        x = F.relu(x)

        x = self.conv2(x, edge_index)

        x = F.relu(x)

        graph_features = global_mean_pool(
            x,
            batch
        )

        # FUSION

        combined = torch.cat(
            [cnn_features, graph_features],
            dim=1
        )

        embedding = self.fc1(combined)

        return embedding