import os
import face_recognition
import pickle

# Define the filename to save the trained model
MODEL_FILENAME = "face_recognition_model.pkl"

# Train the face recognition model on the known faces and save it
def train_face_recognition():
    known_faces_encodings = []
    known_faces_names = []

    for folder_name in os.listdir("photos"):
        if os.path.isdir(os.path.join("photos", folder_name)):
            for file_name in os.listdir(os.path.join("photos", folder_name)):
                if file_name.endswith(".jpg"):
                    image_path = os.path.join("photos", folder_name, file_name)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)

                    if len(face_encodings) > 0:
                        face_encoding = face_encodings[0]
                        known_faces_encodings.append(face_encoding)
                        known_faces_names.append(folder_name)
                    else:
                        print("No face detected in", image_path)

    # Save the trained model
    model_data = {"encodings": known_faces_encodings, "names": known_faces_names}
    with open(MODEL_FILENAME, "wb") as model_file:
        pickle.dump(model_data, model_file)

if __name__ == "__main__":
    train_face_recognition()
    print("Face recognition model trained and saved to", MODEL_FILENAME)
