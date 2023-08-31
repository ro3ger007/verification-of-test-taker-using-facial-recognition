import os
import cv2
import numpy as np
import face_recognition
import pickle
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Define the filename to save the trained model
MODEL_FILENAME = "face_recognition_model.pkl"

# Load the trained model
def load_trained_model():
    with open(MODEL_FILENAME, "rb") as model_file:
        model_data = pickle.load(model_file)
    return model_data["encodings"], model_data["names"]

# Verify the captured face against the trained face recognition model
def verify_user(username, password, captured_image_data):
    # Verify username and password
    if username != "PRN" or password != "Welcome@123":
        return False, None

    # Load the trained model
    known_faces_encodings, known_faces_names = load_trained_model()
    for encoding in known_faces_encodings:
        print("Known face encoding shape:", encoding.shape)

    # Load the captured image and its face encoding
    captured_image_data = base64_to_opencv(captured_image_data)
    captured_face_encodings = face_recognition.face_encodings(captured_image_data)
    print("Number of detected faces:", len(captured_face_encodings))


    if not captured_face_encodings:
        print("No face found in the captured image.")
        return False, None

    captured_face_encoding = captured_face_encodings[0]
    print("Captured face encoding shape:", captured_face_encoding.shape)

    # Calculate face distances and compare with a threshold
    threshold = 0.7  # Adjust this value as needed
    face_distances = face_recognition.face_distance(known_faces_encodings, captured_face_encoding)
    matches = face_distances <= threshold

    if any(matches):
        match_index = np.argmin(face_distances)
        matched_name = known_faces_names[match_index]
        print("Matched face:", matched_name)
        return True, matched_name
    else:
        print("No match found in known faces.")
        return False, None


# Convert base64 image data to OpenCV format



def base64_to_opencv(data):
    nparr = np.frombuffer(data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

# Serve the verification page
@app.route("/verification", methods=["GET", "POST"])
def verification():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        captured_image_data = request.files["capturedImage"].read()

        # Verify user using face recognition
        is_authenticated, matched_name = verify_user(username, password, captured_image_data)

        if is_authenticated:
            return redirect(url_for("test_page"))  # Redirect to the test page on successful verification
        else:
            return render_template("Unauthorized.html", matched_name=matched_name)  # Render the unauthenticated template on failed verification

    return render_template("verification.html")  # Render the verification template

@app.route("/verification", methods=["POST"])
def verify():
    username = request.form["username"]
    password = request.form["password"]
    captured_image_data = request.files["capturedImage"].read()

    # Verify user's identity using the face recognition model
    is_authenticated, user_name = verify_user(username, password, captured_image_data)

    if is_authenticated:
        return redirect(url_for("test_page"))  # Redirect to the test page on successful verification
    else:
        return render_template("Unauthorized.html")  # Render the unauthenticated template on failed verification



if __name__ == "__main__":
    app.run(debug=False)
