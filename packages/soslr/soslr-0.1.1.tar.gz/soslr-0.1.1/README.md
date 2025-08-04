# SOSLR: Semi-Orchestration-Supervised Learning

A simple and effective semi-supervised learning library for image classification, built with PyTorch.

**SOSLR** implements an iterative pseudo-labeling approach. Starting with a small set of labeled images and a large pool of unlabeled images, it trains a model, uses it to predict "pseudo-labels" for chunks of the unlabeled data, and then retrains on the combined set. This process repeats, improving the model with each round.

## Table of Contents
- [Features](#features)
- [Project & Data Structure](#project--data-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
  - [1. Training](#1-training)
  - [2. Prediction](#2-prediction)
- [API Reference](#api-reference)
  - [`soslr.train(...)`](#soslrtrain)
  - [`soslr.predict(...)`](#soslrpredict)
- [Contributing](#contributing)
- [License](#license)

## Features
-   **Simple API**: A clean, function-based API with `train` and `predict`.
-   **Iterative Pseudo-Labeling**: Leverages unlabeled data to improve model accuracy.
-   **Transfer Learning**: Uses pretrained backbones from `torchvision` (e.g., DenseNet, ResNet).
-   **Automatic Artifacts**: Automatically saves the best model, class mappings, and transforms for easy prediction.
-   **Early Stopping**: Monitors validation accuracy to prevent overfitting and stops when a target is reached.

## Project & Data Structure

To use `soslr`, we recommend the following folder structure for your project:

```
your-project/
│
├── data/
│   ├── labeled/              # Your initial labeled images
│   │   ├── class_a/
│   │   │   ├── img1.jpg
│   │   │   └── img2.png
│   │   └── class_b/
│   │       └── img3.jpg
│   │
│   └── unlabeled/            # Your pool of unlabeled images
│       ├── img_x.jpg
│       └── img_y.png
│
├── images_to_predict/        # New images for prediction later
│   ├── new_img1.jpg
│   └── new_img2.png
│
└── sos_model/                # OUTPUT: Where the model will be saved
    ├── best_model.pth
    └── class_mapping.json
```

## Installation

You can install it using pip:

```bash
pip install soslr
```

## Quick Start

Here’s a complete example from training to prediction.

### 1. Training

Create a Python script (e.g., `run_training.py`) to start the training process. The library will use your labeled and unlabeled data, evaluate performance on a validation set, and save the best-performing model to the `output_dir`.

```python
# run_training.py
import soslr

# Point to your data directories
LABELED_DATA_DIR = 'data/labeled'
UNLABELED_DATA_DIR = 'data/unlabeled'
MODEL_OUTPUT_DIR = 'sos_model'

print("Starting training...")

# This will run the full training loop and save the best model
final_accuracy = soslr.train(
    labeled_dir=LABELED_DATA_DIR,
    unlabeled_dir=UNLABELED_DATA_DIR,
    output_dir=MODEL_OUTPUT_DIR,
    model_name='resnet50',  # Use a ResNet-50 backbone
    k=5,                    # Split unlabeled data into 5 chunks per round
    pseudo_epochs=1,        # Train for 1 epoch on each pseudo-labeled chunk
    target_acc=0.90         # Stop if validation accuracy reaches 90%
)

print(f"Training complete. Final test accuracy: {final_accuracy:.4f}")
```

### 2. Prediction

After training, you can use the saved model in `sos_model/` to make predictions on new, unseen images.

Create another script (e.g., `run_prediction.py`):

```python
# run_prediction.py
import soslr
import pprint

# Point to the new images and the saved model directory
IMAGES_TO_PREDICT_DIR = 'images_to_predict'
MODEL_DIR = 'sos_model'

print(f"Loading model from '{MODEL_DIR}' to predict images in '{IMAGES_TO_PREDICT_DIR}'...")

# Get predictions
predictions = soslr.predict(
    images_dir=IMAGES_TO_PREDICT_DIR,
    model_dir=MODEL_DIR,
    model_name='resnet50' # Must match the model used for training
)

print("\nPrediction Results:")
pprint.pprint(predictions)

# Example Output:
# {'new_img1.jpg': 'class_a',
#  'new_img2.png': 'class_b'}
```

## API Reference

### `soslr.train(...)`
Trains a semi-supervised model and saves the training artifacts.

| Argument | Type | Default | Description |
|---|---|---|---|
| `labeled_dir` | `str` | **Required** | Path to the directory with labeled data, organized in class subfolders. |
| `unlabeled_dir` | `str` | **Required** | Path to the directory with unlabeled images. |
| `output_dir` | `str` | `'sos_model'` | Directory to save the trained model and class mapping. |
| `model_name` | `str` | `'densenet121'` | Name of the `torchvision` model to use (e.g., 'resnet50'). |
| `k` | `int` | `5` | Number of chunks to split the unlabeled data into per round. |
| `pseudo_epochs` | `int` | `1` | Number of epochs to train on each pseudo-labeled chunk. |
| `max_rounds` | `int` | `10` | Maximum number of rounds to train over the unlabeled data. |
| `target_acc` | `float` | `0.95` | Validation accuracy threshold to trigger early stopping. |
| `batch_size` | `int` | `64` | The batch size for training and evaluation. |
| `lr` | `float` | `1e-4` | The learning rate for the Adam optimizer. |
| `val_split` | `tuple` | `(0.2, 0.2)` | Proportions of labeled data to use for validation and testing. |

**Returns**: `float` - The final test accuracy of the best model.

### `soslr.predict(...)`
Makes predictions on a directory of images using a trained model.

| Argument | Type | Default | Description |
|---|---|---|---|
| `images_dir` | `str` | **Required** | Path to the directory of images to predict. |
| `model_dir` | `str` | `'sos_model'` | Path to the directory containing the saved `best_model.pth` and `class_mapping.json`. |
| `model_name` | `str` | `'densenet121'` | The architecture name used during training. **Must be the same.** |
| `input_size` | `int` | `224` | The image input size used during training. |

**Returns**: `dict` - A dictionary mapping each image filename to its predicted class name.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request on the GitHub repository.

## License
This project is licensed under the MIT License. See the `LICENSE` file for details.
