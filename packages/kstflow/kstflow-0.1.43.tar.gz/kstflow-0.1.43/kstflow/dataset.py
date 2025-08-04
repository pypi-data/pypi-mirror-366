import os
import zipfile
import requests
from tqdm import tqdm
import csv
import matplotlib.pyplot as plt
from PIL import Image 


def spine_dataset_small(destination_dir="spine_dataset"):
    """
    Downloads and extracts the spine dataset from BUU server into the specified directory.
    """
    dataset_url = "http://angsila.cs.buu.ac.th/~watcharaphong.yk/datasets/BUU-LSPINE_400.zip"
    zip_filename = "BUU-LSPINE_400.zip"
    extracted_dir =  destination_dir

    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)

    def download_with_progress(url, dest_path):
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        with open(dest_path, 'wb') as file, tqdm(
            desc=f"Downloading {zip_filename}",
            total=total,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)

    # Download
    if not os.path.exists(zip_path):
        print("Downloading dataset...")
        download_with_progress(dataset_url, zip_path)
    else:
        print("Dataset zip already exists.")

    # Extract
    if not os.path.exists(extracted_dir):
        print("Extracting dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        print(f"Dataset extracted to {extracted_dir}")
    else:
        print("Dataset already extracted.")

    return extracted_dir


def label_plot(view: str, image_name: str):
    """
    Plots spine label lines from CSV on top of the image.

    Parameters:
        view (str): 'AP' or 'LA'
        image_name (str): e.g., 'A0001.jpg'
    """
    if view not in ["AP", "LA"]:
        raise ValueError("view must be 'AP' or 'LA'")

    dataset_dir = os.path.join("spine_dataset", "BUU-LSPINE_400", view)
    image_path = os.path.join(dataset_dir, image_name)
    csv_path = os.path.join(dataset_dir, image_name.replace(".jpg", ".csv"))

    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found: {image_path}")
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    # Load image
    image = Image.open(image_path)
    fig, ax = plt.subplots()
    ax.imshow(image)

    # Read and draw lines
    with open(csv_path, 'r') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if len(row) < 4:
                continue
            x1, y1, x2, y2 = map(float, row[:4])
            ax.plot([x1, x2], [y1, y2], color='red', linewidth=2)

    ax.set_title(f"{view} View: {image_name}")
    plt.axis("off")
    plt.show()


def thai_handwriting_dataset(destination_dir="thai_handwriting_dataset"):
    """
    Downloads and extracts the Thai handwriting dataset from BUU server into the specified directory.
    """
    dataset_url = "https://angsila.cs.buu.ac.th/~watcharaphong.yk/datasets/20210306-all.zip"
    zip_filename = "20210306-all.zip"
    extracted_dir = destination_dir

    zip_path = os.path.join(os.path.dirname(__file__), zip_filename)

    def download_with_progress(url, dest_path):
        response = requests.get(url, stream=True)
        total = int(response.headers.get('content-length', 0))
        with open(dest_path, 'wb') as file, tqdm(
            desc=f"Downloading {zip_filename}",
            total=total,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(chunk_size=1024):
                size = file.write(data)
                bar.update(size)

    if not os.path.exists(zip_path):
        print("Downloading dataset...")
        download_with_progress(dataset_url, zip_path)
    else:
        print("Dataset zip already exists.")

    if not os.path.exists(extracted_dir):
        print("Extracting dataset...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_dir)
        print(f"Dataset extracted to {extracted_dir}")
    else:
        print("Dataset already extracted.")

    return extracted_dir






