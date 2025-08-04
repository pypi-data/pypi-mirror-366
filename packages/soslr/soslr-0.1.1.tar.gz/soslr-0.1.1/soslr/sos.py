import os
import random
import json
from pathlib import Path
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
import torchvision.transforms as T
import torchvision.models as models
from torch.utils.data import Dataset, Subset, DataLoader, ConcatDataset
from torchvision.datasets import ImageFolder

# ======================================================================================
# 1. DATASET HELPERS
# ======================================================================================

class UnlabeledImageFolder(Dataset):
    """Loads images from a folder without requiring subfolders (class labels)."""
    def __init__(self, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.paths = [p for p in self.root_dir.iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')]

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        img_path = self.paths[idx]
        img = Image.open(img_path).convert('RGB')
        if self.transform:
            img = self.transform(img)
        # Return a dummy label for compatibility with existing loaders
        return img, -1

class PseudoDataset(Dataset):
    """A dataset that wraps original images and pairs them with pseudo-labels."""
    def __init__(self, original_subset, pseudo_labels):
        self.original_subset = original_subset
        self.pseudo_labels = pseudo_labels

    def __len__(self):
        return len(self.original_subset)

    def __getitem__(self, i):
        # The original subset returns (img, -1), we replace -1 with the pseudo-label
        img, _ = self.original_subset[i]
        return img, self.pseudo_labels[i]

# ======================================================================================
# 2. CORE TRAINING CLASS (Internal)
# ======================================================================================

class _Trainer:
    """Internal class to handle the training loop logic."""
    def __init__(self, labeled_dir, unlabeled_dir, output_dir, model_fn, pretrained,
                 input_size, batch_size, lr, k, pseudo_epochs, max_rounds,
                 target_acc, val_split, seed, device):

        # Set seeds for reproducibility
        random.seed(seed)
        np.random.seed(seed)
        torch.manual_seed(seed)

        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Using device: {self.device}")

        self.batch_size = batch_size
        self.lr = lr
        self.k = k
        self.pseudo_epochs = pseudo_epochs
        self.max_rounds = max_rounds
        self.target_acc = target_acc
        self.output_dir = Path(output_dir)

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Define image transforms
        self.transform = T.Compose([
            T.Resize((input_size, input_size)),
            T.ToTensor(),
            T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        self._prepare_data(labeled_dir, unlabeled_dir, val_split)

        # Build model
        self.model = model_fn(pretrained=pretrained)
        num_classes = len(self.labeled_train.dataset.classes)

        # *** CORRECTED LOGIC HERE ***
        # This now correctly handles different model architectures
        if hasattr(self.model, 'classifier') and isinstance(self.model.classifier, nn.Linear):
            num_ftrs = self.model.classifier.in_features
            self.model.classifier = nn.Linear(num_ftrs, num_classes)
        elif hasattr(self.model, 'fc') and isinstance(self.model.fc, nn.Linear):
            num_ftrs = self.model.fc.in_features
            self.model.fc = nn.Linear(num_ftrs, num_classes)
        else:
            raise TypeError("Unsupported model architecture. Could not find 'classifier' or 'fc' layer.")

        self.model = self.model.to(self.device)

        # Loss and optimizer
        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr)

    def _prepare_data(self, labeled_dir, unlabeled_dir, val_split):
        """Loads and splits the data into training, validation, and test sets."""
        full_labeled_dataset = ImageFolder(labeled_dir, transform=self.transform)
        self.class_to_idx = full_labeled_dataset.class_to_idx
        self.idx_to_class = {v: k for k, v in self.class_to_idx.items()}

        n = len(full_labeled_dataset)
        indices = list(range(n))
        random.shuffle(indices)

        n_val = int(val_split[0] * n)
        n_test = int(val_split[1] * n)
        n_train = n - n_val - n_test

        train_indices = indices[:n_train]
        val_indices = indices[n_train : n_train + n_val]
        test_indices = indices[n_train + n_val :]

        self.labeled_train = Subset(full_labeled_dataset, train_indices)
        self.labeled_val = Subset(full_labeled_dataset, val_indices)
        self.labeled_test = Subset(full_labeled_dataset, test_indices)
        self.unlabeled_all = UnlabeledImageFolder(unlabeled_dir, transform=self.transform)

        print(f"Labeled data: {n_train} train, {n_val} val, {n_test} test")
        print(f"Unlabeled data: {len(self.unlabeled_all)} images")
        print(f"Classes: {self.class_to_idx}")


        self.train_loader = DataLoader(self.labeled_train, batch_size=self.batch_size, shuffle=True, num_workers=2)
        self.val_loader = DataLoader(self.labeled_val, batch_size=self.batch_size, shuffle=False, num_workers=2)
        self.test_loader = DataLoader(self.labeled_test, batch_size=self.batch_size, shuffle=False, num_workers=2)


    def evaluate(self, loader):
        """Evaluates the model on a given data loader."""
        self.model.eval()
        correct, total = 0, 0
        with torch.no_grad():
            for imgs, labels in loader:
                imgs, labels = imgs.to(self.device), labels.to(self.device)
                outputs = self.model(imgs)
                _, preds = torch.max(outputs, 1)
                correct += (preds == labels).sum().item()
                total += labels.size(0)
        return correct / total if total > 0 else 0

    def _pseudo_label_chunk(self, indices):
        """Generates pseudo-labels for a chunk of the unlabeled dataset."""
        chunk_subset = Subset(self.unlabeled_all, indices)
        loader = DataLoader(chunk_subset, batch_size=self.batch_size, shuffle=False, num_workers=2)
        pseudo_labels = []
        self.model.eval()
        with torch.no_grad():
            for imgs, _ in loader:
                imgs = imgs.to(self.device)
                outputs = self.model(imgs)
                _, preds = torch.max(outputs, 1)
                pseudo_labels.extend(preds.cpu().tolist())
        return PseudoDataset(chunk_subset, pseudo_labels)

    def _train_on_dataset(self, dataset, epochs):
        """Trains the model on a given dataset for a number of epochs."""
        loader = DataLoader(dataset, batch_size=self.batch_size, shuffle=True, num_workers=2)
        self.model.train()
        for epoch in range(epochs):
            for imgs, labels in loader:
                imgs, labels = imgs.to(self.device), labels.to(self.device)
                self.optimizer.zero_grad()
                outputs = self.model(imgs)
                loss = self.criterion(outputs, labels)
                loss.backward()
                self.optimizer.step()

    def fit(self):
        """The main training loop."""
        best_val_acc = 0.0
        # Initial training on labeled data only
        print("--- Initial training on labeled data ---")
        self._train_on_dataset(self.labeled_train, epochs=max(1, self.pseudo_epochs * self.k // 2))
        best_val_acc = self.evaluate(self.val_loader)
        print(f"Initial validation accuracy: {best_val_acc:.4f}")

        unlabeled_indices = list(range(len(self.unlabeled_all)))

        for rnd in range(1, self.max_rounds + 1):
            print(f"\n=== Round {rnd}/{self.max_rounds} ===")
            random.shuffle(unlabeled_indices)
            chunks = np.array_split(unlabeled_indices, self.k)

            for i, chunk_indices in enumerate(chunks, 1):
                pseudo_labeled_dataset = self._pseudo_label_chunk(chunk_indices)
                combined_dataset = ConcatDataset([self.labeled_train, pseudo_labeled_dataset])
                self._train_on_dataset(combined_dataset, epochs=self.pseudo_epochs)

                val_acc = self.evaluate(self.val_loader)
                print(f"  Round {rnd}, chunk {i}/{self.k} — Val acc: {val_acc:.4f}")

                if val_acc > best_val_acc:
                    print(f"  New best validation accuracy! Saving model to {self.output_dir}")
                    best_val_acc = val_acc
                    torch.save(self.model.state_dict(), self.output_dir / 'best_model.pth')
                    with open(self.output_dir / 'class_mapping.json', 'w') as f:
                        json.dump(self.class_to_idx, f)


            if best_val_acc >= self.target_acc:
                print(f"\nReached target validation accuracy ({best_val_acc:.4f}). Stopping early.")
                break

        print("\n--- Training Finished ---")
        if (self.output_dir / 'best_model.pth').exists():
            print("Loading best model for final test evaluation...")
            self.model.load_state_dict(torch.load(self.output_dir / 'best_model.pth'))
        else:
            print("No best model was saved. Using the final model for test evaluation.")
        
        test_acc = self.evaluate(self.test_loader)
        print(f"*** Final Test Accuracy on best model = {test_acc:.4f} ***")
        return test_acc

# ======================================================================================
# 3. PUBLIC API FUNCTIONS
# ======================================================================================

def train(labeled_dir, unlabeled_dir, output_dir='sos_model', model_name='densenet121',
          pretrained=True, input_size=224, batch_size=64, lr=1e-4, k=5,
          pseudo_epochs=1, max_rounds=10, target_acc=0.95, val_split=(0.2, 0.2),
          seed=42):
    """
    Trains a semi-supervised model and saves the artifacts.
    """
    model_fn = getattr(models, model_name, None)
    if not callable(model_fn):
        raise ValueError(f"Model '{model_name}' not found in torchvision.models")

    trainer = _Trainer(
        labeled_dir=labeled_dir,
        unlabeled_dir=unlabeled_dir,
        output_dir=output_dir,
        model_fn=model_fn,
        pretrained=pretrained,
        input_size=input_size,
        batch_size=batch_size,
        lr=lr,
        k=k,
        pseudo_epochs=pseudo_epochs,
        max_rounds=max_rounds,
        target_acc=target_acc,
        val_split=val_split,
        seed=seed,
        device=None
    )
    return trainer.fit()


def predict(images_dir, model_dir='sos_model', model_name='densenet121', input_size=224):
    """
    Makes predictions on a directory of images using a trained model.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_dir = Path(model_dir)
    model_path = model_dir / 'best_model.pth'
    class_map_path = model_dir / 'class_mapping.json'

    if not all([model_path.exists(), class_map_path.exists()]):
        raise FileNotFoundError(f"Model artifacts not found in '{model_dir}'. Did you train a model first?")

    # Load class mapping
    with open(class_map_path, 'r') as f:
        class_to_idx = json.load(f)
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    num_classes = len(idx_to_class)

    # Load model
    model_fn = getattr(models, model_name, None)
    if not callable(model_fn):
        raise ValueError(f"Model '{model_name}' not found in torchvision.models")

    model = model_fn(pretrained=False)

    # *** CORRECTED LOGIC HERE ***
    # Rebuild the final layer EXACTLY as it was during training
    if hasattr(model, 'classifier') and isinstance(model.classifier, nn.Linear):
        num_ftrs = model.classifier.in_features
        model.classifier = nn.Linear(num_ftrs, num_classes)
    elif hasattr(model, 'fc') and isinstance(model.fc, nn.Linear):
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, num_classes)
    else:
        raise TypeError("Unsupported model architecture. Could not find 'classifier' or 'fc' layer.")

    model.load_state_dict(torch.load(model_path, map_location=device))
    model = model.to(device)
    model.eval()

    # Define transforms
    transform = T.Compose([
        T.Resize((input_size, input_size)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    # Predict
    results = {}
    image_paths = [p for p in Path(images_dir).iterdir() if p.suffix.lower() in ('.png', '.jpg', '.jpeg')]

    with torch.no_grad():
        for img_path in image_paths:
            img = Image.open(img_path).convert('RGB')
            img_tensor = transform(img).unsqueeze(0).to(device)
            output = model(img_tensor)
            _, pred_idx = torch.max(output, 1)
            pred_class = idx_to_class[pred_idx.item()]
            results[img_path.name] = pred_class

    return results
