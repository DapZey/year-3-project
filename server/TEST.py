from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from keras.models import load_model

# Must match the order used during training
categories = [ "house", "car", "tree", "smiley face",
               "cactus", "guitar", "moon", "lightning", "star","The Eiffel Tower"]

# Load model
model = load_model('quickdraw1.model')

def preprocess_image(img, target_size=(28, 28)):
    """Consistent preprocessing for both training and testing"""
    if img.mode != 'L':
        img = img.convert('L')
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    # Ensure consistent format - invert if background is mostly white
    if np.mean(img_array) > 0.5:
        img_array = 1.0 - img_array
    return img_array


def predictclientimage(client):
    img = Image.open(client)
    img_array = preprocess_image(img, (28, 28))  # Use same preprocessing
    img_array = img_array.reshape(1, 28, 28, 1).astype('float32')
    prediction = model.predict(img_array)
    predicted_class_index = np.argmax(prediction)
    predicted_label = categories[predicted_class_index]
    print(f"Predicted label: {predicted_label}")
    print(f"Confidence: {prediction[0][predicted_class_index] * 100:.2f}%")
    return predicted_label, prediction[0][predicted_class_index]