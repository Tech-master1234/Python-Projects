import os
import numpy as np
import face_recognition
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import filedialog
import pickle

# Function to load saved encodings and labels
def load_saved_patterns(encoding_file, label_file):
    with open(encoding_file, 'rb') as f:
        known_face_encodings = pickle.load(f)
    with open(label_file, 'rb') as f:
        known_face_names = pickle.load(f)
    return known_face_encodings, known_face_names

# Load saved encodings and labels
encoding_file = "model_files/encodings.pkl"
label_file = "model_files/labels.pkl"
known_face_encodings, known_face_names = load_saved_patterns(encoding_file, label_file)

# Function to recognize faces in a new image
def recognize_faces_in_image(image_path, known_face_encodings, known_face_names):
    image = face_recognition.load_image_file(image_path)
    face_locations = face_recognition.face_locations(image)
    face_encodings = face_recognition.face_encodings(image, face_locations)

    results = []
    images_with_confidence = []

    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

        for i, distance in enumerate(face_distances):
            confidence = (1 - distance) * 100
            if matches[i] and confidence > 25.0:
                name = known_face_names[i]
                results.append((name, confidence))
                images_with_confidence.append((name, confidence))

    return results, images_with_confidence

# Function to plot images with confidence levels
def plot_images_with_confidence(images_with_confidence):
    num_images = len(images_with_confidence)
    num_rows = (num_images + 2) // 3  # Calculate the number of rows needed
    num_cols = 3

    plt.figure(figsize=(2*2*num_cols, 2*num_rows))
    for i, (name, confidence) in enumerate(images_with_confidence):
        img_path = os.path.join(known_faces_dir, name + ".jpg")
        if not os.path.exists(img_path):  # In case the extension is .png instead of .jpg
            img_path = os.path.join(known_faces_dir, name + ".png")
        img = mpimg.imread(img_path)

        plt.subplot(num_rows, num_cols, i+1)
        plt.imshow(img)
        plt.title(f"{name}\n{confidence:.2f}%")
        plt.axis('off')

    plt.tight_layout()
    plt.savefig('matches_plot.png')
    plt.show()

# Test the recognition on a new image
test_image_path = 'unknown_faces/kshmr.jpg'
recognition_results, images_with_confidence = recognize_faces_in_image(test_image_path, known_face_encodings, known_face_names)
for name, confidence in recognition_results:
    print(f'Recognized {name} with {confidence:.2f}% confidence')

# Plot the matched images with confidence levels
plot_images_with_confidence(images_with_confidence)
