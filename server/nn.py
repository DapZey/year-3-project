import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D, Reshape
from tensorflow.keras.utils import to_categorical
from quickdraw import QuickDrawDataGroup
from sklearn.utils import class_weight
from PIL import Image
import matplotlib.pyplot as plt

# Define categories
categories = ["dog", "ant", "axe", "bird", "butterfly", "cat", "cow", "crab", "crocodile", "bus"]
image_size = (112, 112)
X, y = [], []

# Label mapping
label_map = {category: idx for idx, category in enumerate(categories)}

# Load data
for category in categories:
    print(f"Loading {category} drawings...")
    drawings = QuickDrawDataGroup(category, max_drawings=10000)
    for drawing in list(drawings.drawings):
        img = drawing.get_image()
        img = img.convert('L')  # Convert to grayscale
        img = img.resize(image_size)  # Resize to 28x28
        img_array = np.array(img) / 255.0  # Normalize to [0, 1]
        X.append(img_array)
        y.append(label_map[category])
    print("Load complete")

# Convert to NumPy arrays
X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)

# Shuffle the dataset
shuffle_idx = np.random.permutation(len(X))
X, y = X[shuffle_idx], y[shuffle_idx]

# Split data into training and testing
split_index = int(0.8 * len(X))  # 80% training, 20% testing
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

# Compute class weights
class_weights = class_weight.compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weights_dict = dict(enumerate(class_weights))

# Convert to TensorFlow datasets
def preprocess(image, label):
    return image, tf.one_hot(label, depth=len(categories))

ds_train = tf.data.Dataset.from_tensor_slices((X_train, y_train))
ds_test = tf.data.Dataset.from_tensor_slices((X_test, y_test))

ds_train = ds_train.map(preprocess).cache().shuffle(len(X_train)).batch(128).prefetch(tf.data.AUTOTUNE)
ds_test = ds_test.map(preprocess).cache().batch(128).prefetch(tf.data.AUTOTUNE)

# Define the model
model = Sequential([
    Reshape((112, 112, 1), input_shape=(112, 112)),
    Conv2D(32, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Conv2D(64, kernel_size=(3, 3), activation='relu'),
    MaxPooling2D(pool_size=(2, 2)),
    Flatten(),
    Dense(128, activation='relu'),
    Dense(len(categories))  # Output layer
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(0.001),
    loss=tf.keras.losses.CategoricalCrossentropy(from_logits=True),
    metrics=['accuracy']
)

# Train the model
model.fit(
    ds_train,
    epochs=5,
    validation_data=ds_test,
    class_weight=class_weights_dict
)

# Save the model

# Load and preprocess the client image
client1_img_path = 'client0.png'  # Replace with the path to your new image
client1_img = Image.open(client1_img_path)  # Open the image using PIL
client1_img = client1_img.convert('L')  # Convert to grayscale
client1_img = client1_img.resize(image_size)  # Resize to match model input (28x28)
client1_img_array = np.array(client1_img) / 255.0  # Normalize the image data

# Add a batch dimension for the model (model expects a batch of images)
client1_img_array = np.expand_dims(client1_img_array, axis=0)

# Make the prediction
predictions = model.predict(client1_img_array)

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
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

# Load the client image
client_image_path = 'client0.png'  # Path to the client image
image_size = (112, 112)  # Same size as training data
client_image = Image.open(client_image_path)

# Preprocess the image (convert to grayscale, resize, normalize)
client_image = client_image.convert('L')  # Convert to grayscale
client_image = client_image.resize(image_size)  # Resize to match training data
client_image_array = np.array(client_image, dtype=np.float32) / 255.0  # Normalize to [0, 1]

# Ensure the array has the correct shape for visualization
if len(client_image_array.shape) == 3 and client_image_array.shape[-1] in [3, 4]:
    # If the image is RGB or RGBA, convert to grayscale
    client_image_array = np.mean(client_image_array, axis=-1)

# Display the image
plt.imshow(client_image_array, cmap='gray')
plt.title("Client Image (Preprocessed)")
plt.axis('off')
plt.show()
model.save('model.h5')  # Save the model as a .h5 file

