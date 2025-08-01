import os
import cv2
import numpy as np
import requests
from tqdm import tqdm
from tensorflow.keras.models import load_model
import matplotlib.pyplot as plt

def spine_corner_point(view, image_filename):
    """
    Detects and plots corner points of vertebrae from a spine X-ray image using a pretrained ResNet50V2 model.
    
    Parameters:
        view (str): 'AP' or 'LA' view of the image.
        image_filename (str): Filename of the image to process (e.g., '0001.jpg').

    Returns:
        None
    """

    # View Validation
    if view not in ['AP', 'LA']:
        raise ValueError("View must be 'AP' or 'LA'.")

    # Dataset path
    image_path = os.path.join("spine_dataset", "BUU-LSPINE_400", view, image_filename)

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Model download URLs
    model_urls = {
        "AP": "https://angsila.cs.buu.ac.th/~watcharaphong.yk/pretrained/AP_ResNet50V2.h5",
        "LA": "https://angsila.cs.buu.ac.th/~watcharaphong.yk/pretrained/LA_ResNet50V2.h5"
    }

    model_filename = os.path.basename(model_urls[view])
    model_path = os.path.join(os.path.dirname(__file__), model_filename)

    # Download model if not exists
    def download_file(url, dest):
        if not os.path.exists(dest):
            response = requests.get(url, stream=True)
            total = int(response.headers.get('content-length', 0))
            with open(dest, 'wb') as f, tqdm(
                desc=f"Downloading {os.path.basename(dest)}",
                total=total,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in response.iter_content(chunk_size=1024):
                    size = f.write(data)
                    bar.update(size)

    download_file(model_urls[view], model_path)

    # Load model
    model = load_model(model_path)

    # Load and preprocess image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image: {image_path}")

    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img_resized = cv2.resize(img_rgb, (224, 224))  # assuming model input is 224x224
    img_input = np.expand_dims(img_resized / 255.0, axis=0)

    # Inference
    prediction = model.predict(img_input)[0]  # assuming [x, y] as output (normalized)
    x_norm, y_norm = prediction[0], prediction[1]

    # Scale to original image size
    x = int(x_norm * img.shape[1])
    y = int(y_norm * img.shape[0])

    # Plot result
    output_img = img_rgb.copy()
    cv2.circle(output_img, (x, y), 10, (255, 0, 0), -1)  # red circle in RGB

    plt.imshow(output_img)
    plt.title(f"Detected Corner Point: {image_filename} ({view})")
    plt.axis('off')
    plt.show()
