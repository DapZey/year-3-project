from PIL import Image, ImageOps
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model

# Must match the order used during training
categories = ["house", "car", "tree", "smiley face",
              "cactus", "guitar", "moon", "lightning", "star", "The Eiffel Tower"]

# Load model
model = load_model('quickdraw1.model')


def preprocess_image(img, target_size=(28, 28), show_debug=False):
    """
    Preprocess a PIL image for QuickDraw CNN:
    - Convert to grayscale
    - Invert if background is mostly white
    - Tight crop around strokes
    - Pad to square
    - Resize to target_size
    - Normalize to [0,1]
    """
    # 1. Grayscale
    if img.mode != 'L':
        img = img.convert('L')

    img_array = np.array(img, dtype=np.uint8)

    # 2. Invert if background is mostly white
    if np.mean(img_array) > 127:
        img_array = 255 - img_array

    # 3. Threshold for non-background pixels
    thresh = img_array > 20  # tweak if needed
    coords = np.argwhere(thresh)

    if coords.size > 0:
        y0, x0 = coords.min(axis=0)
        y1, x1 = coords.max(axis=0) + 1
        img_array = img_array[y0:y1, x0:x1]

    # Optional debug: show cropped
    if show_debug:
        plt.imshow(img_array, cmap="gray")
        plt.title("Cropped before padding/resizing")
        plt.axis("off")
        plt.show()

    # 4. Pad to square
    h, w = img_array.shape
    size = max(h, w)
    square = np.zeros((size, size), dtype=np.uint8)
    y_off = (size - h) // 2
    x_off = (size - w) // 2
    square[y_off:y_off+h, x_off:x_off+w] = img_array

    # 5. Resize to target_size
    img = Image.fromarray(square)
    img = img.resize(target_size, Image.Resampling.LANCZOS)

    # 6. Normalize
    img_array = np.array(img, dtype=np.float32) / 255.0

    # Optional debug: show final preprocessed
    if show_debug:
        plt.imshow(img_array, cmap="gray")
        plt.title("Final preprocessed")
        plt.axis("off")
        plt.show()

    return img_array


def predictclientimage(client_path, show_debug=False):
    """Load, preprocess, and predict the class of a client drawing"""
    img = Image.open(client_path)

    if show_debug:
        plt.imshow(img, cmap="gray")
        plt.title("Original image")
        plt.axis("off")
        plt.show()

    img_array = preprocess_image(img, target_size=(28, 28), show_debug=show_debug)
    img_array = img_array.reshape(1, 28, 28, 1).astype('float32')

    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction)
    predicted_label = categories[predicted_class_index]
    confidence = prediction[0][predicted_class_index] * 100

    print(f"Predicted label: {predicted_label}")
    print(f"Confidence: {confidence:.2f}%")

    return predicted_label, confidence


# Example usage
# predict_client_image("received_client2.png", show_debug=True)
