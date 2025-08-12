import numpy as np
from sklearn.utils import shuffle as sk_shuffle
from sklearn.model_selection import train_test_split
from quickdraw import QuickDrawDataGroup
from keras.utils import to_categorical
from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Flatten, BatchNormalization
from keras.layers import Conv2D, MaxPooling2D
from keras.callbacks import EarlyStopping, ReduceLROnPlateau
import matplotlib.pyplot as plt

# Configuration - Updated to 10 categories
categories = [ "house", "car", "tree", "smiley face",
               "cactus", "guitar", "moon", "lightning", "star","The Eiffel Tower"]

image_size = (28, 28)
num_of_classes = len(categories)


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


X, y = [], []
label_map = {category: idx for idx, category in enumerate(categories)}

for category in categories:
    print(f"Loading {category} drawings...")
    drawings = QuickDrawDataGroup(category, max_drawings=8000)
    for drawing in drawings.drawings:
        try:
            img = drawing.get_image()
            img_array = preprocess_image(img, image_size)
            X.append(img_array)
            y.append(label_map[category])
        except:
            continue
    print("Load complete")

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.int32)

# Shuffle and split
X, y = sk_shuffle(X, y, random_state=0)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

y_train_cnn = to_categorical(y_train)
y_test_cnn = to_categorical(y_test)
num_classes = y_test_cnn.shape[1]

# reshape to be [samples][pixels][width][height]
X_train_cnn = X_train.reshape(X_train.shape[0], 28, 28, 1).astype('float32')
X_test_cnn = X_test.reshape(X_test.shape[0], 28, 28, 1).astype('float32')

s = X_train_cnn.shape
print(s, num_classes)


def cnn_model28():
    # create model - improved architecture
    model = Sequential()

    model.add(Conv2D(32, (3, 3), input_shape=(28, 28, 1), activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(32, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(BatchNormalization())
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.25))

    model.add(Conv2D(128, (3, 3), activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.25))

    model.add(Flatten())
    model.add(Dense(512, activation='relu'))
    model.add(BatchNormalization())
    model.add(Dropout(0.5))
    model.add(Dense(256, activation='relu'))
    model.add(Dropout(0.5))
    model.add(Dense(num_classes, activation='softmax'))

    # Compile model
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


model = cnn_model28()

# Fit the model with early stopping
early_stop = EarlyStopping(monitor='val_accuracy', patience=8, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=5, min_lr=1e-7)

history = model.fit(X_train_cnn, y_train_cnn,
                    validation_data=(X_test_cnn, y_test_cnn),
                    epochs=50, batch_size=32,
                    callbacks=[early_stop, reduce_lr])

# Final evaluation of the model
scores = model.evaluate(X_test_cnn, y_test_cnn, verbose=0)
print('Final CNN accuracy: ', scores[1] * 100, "%")

# Save weights
model.save_weights('quickdraw_neuralnet1.h5')
model.save('quickdraw1.model')
print("Model is saved")