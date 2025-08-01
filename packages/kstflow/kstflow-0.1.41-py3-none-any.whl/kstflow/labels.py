import csv
import matplotlib.pyplot as plt
from PIL import Image 

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
