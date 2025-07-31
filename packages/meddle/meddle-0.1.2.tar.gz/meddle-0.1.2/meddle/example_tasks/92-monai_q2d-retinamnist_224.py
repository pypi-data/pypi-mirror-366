import os
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from sklearn.metrics import accuracy_score, roc_auc_score
from monai.transforms import (
    Compose,
    LoadImage,
    EnsureChannelFirst,
    ScaleIntensity,
    Resize,
    RandRotate,
    RandFlip,
    RandZoom,
)
from monai.data import Dataset, DataLoader
from monai.networks.nets import DenseNet121

# Define paths
train_csv_path = "./input/train.csv"
val_csv_path = "./input/val.csv"
test_csv_path = "./input/test.csv"
train_img_dir = "./input/train_png/"
val_img_dir = "./input/val_png/"
test_img_dir = "./input/test_png/"
submission_path = "./working/submission.csv"

# Load CSV files
train_df = pd.read_csv(train_csv_path)
val_df = pd.read_csv(val_csv_path)
test_df = pd.read_csv(test_csv_path)

# Define MONAI transforms with data augmentation for training
train_transforms = Compose(
    [
        LoadImage(image_only=True),
        EnsureChannelFirst(),
        ScaleIntensity(),
        Resize((224, 224)),
        RandRotate(range_x=15, prob=0.5),
        RandFlip(spatial_axis=0, prob=0.5),
        RandFlip(spatial_axis=1, prob=0.5),
        RandZoom(min_zoom=0.9, max_zoom=1.1, prob=0.5),
    ]
)

val_transforms = Compose(
    [
        LoadImage(image_only=True),
        EnsureChannelFirst(),
        ScaleIntensity(),
        Resize((224, 224)),
    ]
)


# Define custom Dataset
class FundusDataset(Dataset):
    def __init__(self, dataframe, img_dir, transforms):
        self.dataframe = dataframe
        self.img_dir = img_dir
        self.transforms = transforms

    def __len__(self):
        return len(self.dataframe)

    def __getitem__(self, idx):
        img_path = os.path.join(
            self.img_dir, self.dataframe.iloc[idx, 2].split("/")[-1]
        )
        image = self.transforms(img_path)
        label = self.dataframe.iloc[idx, 1]
        return image, label


# Create datasets and dataloaders
train_dataset = FundusDataset(train_df, train_img_dir, train_transforms)
val_dataset = FundusDataset(val_df, val_img_dir, val_transforms)
test_dataset = FundusDataset(test_df, test_img_dir, val_transforms)

train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True)
val_loader = DataLoader(val_dataset, batch_size=32, shuffle=False)
test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

# Define model, loss, and optimizer
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = DenseNet121(spatial_dims=2, in_channels=3, out_channels=5).to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# Implement ReduceLROnPlateau scheduler
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="min", factor=0.1, patience=3
)

# Train for more epochs
num_epochs = 20
for epoch in range(num_epochs):
    model.train()
    running_loss = 0.0
    for images, labels in train_loader:
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        running_loss += loss.item()

    # Validate
    model.eval()
    val_preds, val_labels = [], []
    with torch.no_grad():
        for images, labels in val_loader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            val_preds.extend(preds.cpu().numpy())
            val_labels.extend(labels.cpu().numpy())

    # Calculate validation loss, accuracy, and AUC
    val_loss = criterion(outputs, labels).item()
    val_accuracy = accuracy_score(val_labels, val_preds)
    val_auc = roc_auc_score(val_labels, np.eye(5)[val_preds], multi_class="ovr")
    print(
        f"Epoch {epoch+1}/{num_epochs}, Loss: {running_loss/len(train_loader):.4f}, Validation Accuracy: {val_accuracy:.4f}, Validation AUC: {val_auc:.4f}"
    )

    # Step the scheduler
    scheduler.step(val_loss)

# Predict on test data
test_preds = []
model.eval()
with torch.no_grad():
    for images, _ in test_loader:
        images = images.to(device)
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        test_preds.extend(preds.cpu().numpy())

# Save predictions to submission.csv
submission_df = pd.DataFrame(
    {"Id": test_df["Id"], "class": test_preds, "path": test_df["path"]}
)
submission_df.to_csv(submission_path, index=False)
