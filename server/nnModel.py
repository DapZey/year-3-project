import numpy as np
import tensorflow as tf
from PIL import Image
import matplotlib.pyplot as plt

# Load the saved model
model = tf.keras.models.load_model('model.h5')  # Replace with the correct model path

# Categories or class labels (replace with your actual categories)
categories = ["dog", "ant", "axe", "bird", "butterfly", "cat", "cow", "crab", "crocodile", "bus"]

# Image path (replace with your actual test image)
client_image_path = 'client0.png'  # Path to the image you want to test
image_size = (112, 112)  # Resize the image to the model input size (e.g., 56x56)

# Load and preprocess the image
client_image = Image.open(client_image_path)
client_image = client_image.convert('L')  # Convert to grayscale
client_image = client_image.resize(image_size)  # Resize to match model input
client_image_array = np.array(client_image, dtype=np.float32) / 255.0  # Normalize to [0, 1]

# Ensure the array has the correct shape (model expects a batch of images)
if len(client_image_array.shape) == 3 and client_image_array.shape[-1] in [3, 4]:
    # If the image is RGB or RGBA, convert to grayscale
    client_image_array = np.mean(client_image_array, axis=-1)

# Add a batch dimension
client_image_array = np.expand_dims(client_image_array, axis=0)

# Make a prediction
predictions = model.predict(client_image_array)

# Convert logits to probabilities using softmax
probabilities = tf.nn.softmax(predictions[0]).numpy()

# Get the predicted class
predicted_class_idx = np.argmax(probabilities)
predicted_category = categories[predicted_class_idx]

# Print the predicted category and confidence
print(f"The predicted category for the new image is: {predicted_category}")
print("Confidence in each category:")
for idx, category in enumerate(categories):
    print(f"{category}: {probabilities[idx]*100:.2f}%")

# Display the image
plt.imshow(client_image_array[0], cmap='gray')
plt.title(f"Predicted: {predicted_category}")
plt.axis('off')
plt.show()
