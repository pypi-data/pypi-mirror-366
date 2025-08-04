mport os
from tensorflow.keras.models import load_model
import requests
import cv2
import numpy as np
from glob import glob
import os

def get_model(model_name: str) -> str:
    """
    Downloads the model if not present and returns its local path.
    """
    os.makedirs("models", exist_ok=True)

    if model_name == "resnetAP":
        url = "https://angsila.cs.buu.ac.th/~watcharaphong.yk/pretrained/AP_ResNet50V2.h5"
        filename = "AP_ResNet50V2.h5"
    elif model_name == "resnetLA":
        url = "https://angsila.cs.buu.ac.th/~watcharaphong.yk/pretrained/LA_ResNet50V2.h5"
        filename = "LA_ResNet50V2.h5"
    elif model_name == "resnet152":
        url = "https://angsila.cs.buu.ac.th/~watcharaphong.yk/pretrained/ResNet152V2.h5"
        filename = "ResNet152V2.h5"
    else:
        raise ValueError(f"Unknown model name: {model_name}")

    model_path = os.path.join("models", filename)

    if not os.path.exists(model_path):
        print(f"Downloading {model_name} model...")
        r = requests.get(url, stream=True)
        with open(model_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download complete.")
    
    return model_path

def load_model_from_path(model_name: str):
    """
    Returns the loaded model given a model name.
    """
    path = get_model(model_name)
    return load_model(path)




def predict_and_plot_images(model_name="resnet152", image_dir="data/BUU_LSPINE_V2_AP/test/images", limit=1):
    """
    Load the model and use it to predict on a folder of images.

    Parameters:
        model_name (str): Name of model (e.g., "resnet152")
        image_dir (str): Directory of input images (.jpg)
        limit (int): Number of images to process
    """
    from .model_loader import load_model_from_path  # if you save load_model_from_path in model_loader.py
    model = load_model_from_path(model_name)

    image_paths = sorted(glob(os.path.join(image_dir, "*.jpg")))
    if not image_paths:
        raise FileNotFoundError(f"No JPG images found in: {image_dir}")

    for i, image_path in enumerate(image_paths):
        if i < limit:
            continue

        print(f"Processing: {image_path}")
        img = cv2.imread(image_path)
        if img is None:
            print(f"Failed to read image: {image_path}")
            continue

        resized_img = cv2.resize(img, (250, 250))
        predicted_y = model.predict(np.expand_dims(resized_img / 255.0, axis=0))[0]
        predicted_points = predicted_y.reshape((20, 2))

        h, w = img.shape[:2]
        for point in predicted_points:
            x, y = tuple(np.multiply(point, [w, h]).astype(int))
            cv2.circle(img, (x, y), 15, (0, 0, 255), -1)

        save_path = f"predict_monitor_{i}.jpg"
        cv2.imwrite(save_path, img)
        print(f"Saved: {save_path}")
        break
