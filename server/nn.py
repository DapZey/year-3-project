import numpy as np
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, BatchNormalization, Rescaling
from tensorflow.keras.utils import to_categorical
from PIL import Image
from quickdraw import QuickDrawData, QuickDrawDataGroup
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ReduceLROnPlateau, EarlyStopping
import matplotlib.pyplot as plt

# Define data augmentation
# Define categories for comparison
# categories = ["aircraft carrier", "airplane", "alarm clock", "ambulance", "angel", "animal migration", "ant",
#               "anvil", "apple", "arm"]
categories = [
    "aircraft carrier", "airplane", "alarm clock", "ambulance", "angel", "animal migration", "ant",
    "anvil", "apple", "arm", "asparagus", "axe", "backpack", "banana", "bandage", "barn", "baseball",
    "baseball bat", "basket", "basketball", "bat", "bathtub", "beach", "bear", "beard", "bed", "bee",
    "belt", "bench", "bicycle", "binoculars", "bird", "birthday cake", "blackberry", "blueberry", "book",
    "boomerang", "bottlecap", "bowtie", "bracelet", "brain", "bread", "bridge", "broccoli", "broom",
    "bucket", "bulldozer", "bus", "bush", "butterfly", "cactus", "cake", "calculator", "calendar", "camel",
    "camera", "camouflage", "campfire", "candle", "cannon", "canoe", "car", "carrot", "castle", "cat",
    "ceiling fan", "cello", "cell phone", "chair", "chandelier", "church", "circle", "clarinet", "clock",
    "cloud", "coffee cup", "compass", "computer", "cookie", "cooler", "couch", "cow", "crab", "crayon",
    "crocodile", "crown", "cruise ship", "cup", "diamond", "dishwasher", "diving board", "dog", "dolphin",
    "donut", "door", "dragon", "dresser", "drill", "drums", "duck", "dumbbell", "ear", "elbow", "elephant",
    "envelope", "eraser", "eye", "eyeglasses", "face", "fan", "feather", "fence", "finger", "fire hydrant",
    "fireplace", "firetruck", "fish", "flamingo", "flashlight", "flip flops", "floor lamp", "flower",
    "flying saucer", "foot", "fork", "frog", "frying pan", "garden", "garden hose", "giraffe", "goatee",
    "golf club", "grapes", "grass", "guitar", "hamburger", "hammer", "hand", "harp", "hat", "headphones",
    "hedgehog", "helicopter", "helmet", "hexagon", "hockey puck", "hockey stick", "horse", "hospital",
    "hot air balloon", "hot dog", "hot tub", "hourglass", "house", "house plant", "hurricane", "ice cream",
    "jacket", "jail", "kangaroo", "key", "keyboard", "knee", "knife", "ladder", "lantern", "laptop", "leaf",
    "leg", "light bulb", "lighter", "lighthouse", "lightning", "line", "lion", "lipstick", "lobster",
    "lollipop", "mailbox", "map", "marker", "matches", "megaphone", "mermaid", "microphone", "microwave",
    "monkey", "moon", "mosquito", "motorbike", "mountain", "mouse", "moustache", "mouth", "mug", "mushroom",
    "nail", "necklace", "nose", "ocean", "octagon", "octopus", "onion", "oven", "owl", "paintbrush",
    "paint can", "palm tree", "panda", "pants", "paper clip", "parachute", "parrot", "passport", "peanut",
    "pear", "peas", "pencil", "penguin", "piano", "pickup truck", "picture frame", "pig", "pillow",
    "pineapple", "pizza", "pliers", "police car", "pond", "pool", "popsicle", "postcard", "potato",
    "power outlet", "purse", "rabbit", "raccoon", "radio", "rain", "rainbow", "rake", "remote control",
    "rhinoceros", "rifle", "river", "roller coaster", "rollerskates", "sailboat", "sandwich", "saw",
    "saxophone", "school bus", "scissors", "scorpion", "screwdriver", "sea turtle", "see saw", "shark",
    "sheep", "shoe", "shorts", "shovel", "sink", "skateboard", "skull", "skyscraper", "sleeping bag",
    "smiley face", "snail", "snake", "snorkel", "snowflake", "snowman", "soccer ball", "sock", "speedboat",
    "spider", "spoon", "spreadsheet", "square", "squiggle", "squirrel", "stairs", "star", "steak", "stereo",
    "stethoscope", "stitches", "stop sign", "stove", "strawberry", "streetlight", "string bean", "submarine",
    "suitcase", "sun", "swan", "sweater", "swing set", "sword", "syringe", "table", "teapot", "teddy-bear",
    "telephone", "television", "tennis racquet", "tent", "The Eiffel Tower", "The Great Wall of China",
    "The Mona Lisa", "tiger", "toaster", "toe", "toilet", "tooth", "toothbrush", "toothpaste", "tornado",
    "tractor", "traffic light", "train", "tree", "triangle", "trombone", "truck", "trumpet", "t-shirt",
    "umbrella", "underwear", "van", "vase", "violin", "washing machine", "watermelon", "waterslide", "whale",
    "wheel", "windmill", "wine bottle", "wine glass", "wristwatch", "yoga", "zebra", "zigzag"
]
image_size = (28, 28)
X = []
y = []

# Mapping categories to numeric labels
label_map = {category: idx for idx, category in enumerate(categories)}

# Load QuickDraw data
qd = QuickDrawData()

# Load data for each category
for category in categories:
    drawings = QuickDrawDataGroup(category, max_drawings=3000)
    for drawing in list(drawings.drawings):
        img = drawing.get_image()
        # Convert to grayscale
        img = img.convert('L')
        # Convert to binary using a threshold
        # img = img.point(lambda x: 255 if x > 128 else 0, '1')
        img = img.resize(image_size)
        img_array = np.array(img)
        X.append(img_array)
        y.append(label_map[category])

X = np.array(X)
y = np.array(y)

# Normalize the image data (will be just 0s and 1s now)
X = X.astype('float32') / 255.0

# Convert labels to categorical
y = to_categorical(y, num_classes=len(categories))

# Split the data
train_size = int(0.8 * len(X))
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# Reshape data to include channel dimension
X_train = X_train.reshape(-1, image_size[0], image_size[1], 1)
X_test = X_test.reshape(-1, image_size[0], image_size[1], 1)

# Build a CNN model
input_shape = (28, 28, 1)
model = Sequential([
    BatchNormalization(),

    Conv2D(6, kernel_size=(3, 3), padding="same", activation="relu"),
    Conv2D(8, kernel_size=(3, 3), padding="same", activation="relu"),
    Conv2D(10, kernel_size=(3, 3), padding="same", activation="relu"),
    BatchNormalization(),
    MaxPooling2D(pool_size=(2, 2)),

    Flatten(),

    Dense(700, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),

    Dense(500, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),

    Dense(400, activation='relu'),
    Dropout(0.2),

    Dense(len(categories), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam',
              loss='categorical_crossentropy',
              metrics=['accuracy'])


# Train the model without data augmentation
history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    batch_size=32,
    epochs=14,
)

# Evaluate the model
test_loss, test_acc = model.evaluate(X_test, y_test)
print(f"Test Accuracy: {test_acc}")

# Print the number of training and testing images
print(f"Number of training images: {len(X_train)}")
print(f"Number of testing images: {len(X_test)}")

# Load and preprocess the client1 image
client1_img_path = 'client1.png'  # Replace with the path to your new image
client1_img = Image.open(client1_img_path)  # Open the image using PIL
client1_img = client1_img.convert('L')  # Convert to RGB if necessary
client1_img = client1_img.resize(image_size)  # Resize to match model input (28x28)
client1_img_array = np.array(client1_img)  # Convert to numpy array

# Normalize the image data
client1_img_array = client1_img_array.astype('float32') / 255.0

# Add a batch dimension for the model (model expects a batch of images)
client1_img_array = np.expand_dims(client1_img_array, axis=0)

# Make the prediction
predictions = model.predict(client1_img_array)

# Get the predicted class (the index of the maximum value in the prediction)
predicted_class_idx = np.argmax(predictions)

# Decode the predicted class index to the corresponding category
predicted_category = categories[predicted_class_idx]

# Print the predicted category and the confidence in each category
print(f"The predicted category for the new image is: {predicted_category}")
print("Confidence in each category:")
for idx, category in enumerate(categories):
    print(f"{category}: {predictions[0][idx]*100:.2f}%")


#checking an image:
# index_to_show = 999  # Or any valid index
# img_to_show = X[index_to_show]
# img_label = y[index_to_show]  # One-hot encoded label
#
# # Decode the one-hot encoded label to the original category
# decoded_label = categories[np.argmax(img_label)]
#
# # Rescale the image for visualization
# img_to_show = (img_to_show * 255).astype('uint8')
# img_pil = Image.fromarray(img_to_show)
#
# # Show the image
# img_pil.show()
#
# # Print the corresponding label
# print(f"Category of the displayed image: {decoded_label}")
