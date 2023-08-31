import os
import csv
from flask import Flask, render_template, request, redirect, url_for, Response, send_from_directory
from pymongo import MongoClient
from verification import verify_user
import base64
import io



app = Flask(__name__)

# MongoDB configuration
client = MongoClient("mongodb://localhost:27017/")
db = client["examregistration"]

# Serve your HTML page
@app.route("/", methods=["GET"])
def index():
    return render_template("exam_form1.html")

# Handle form submission
@app.route("/", methods=["POST"])
def register():
    try:
        name = request.form["name"]
        course = request.form["course"]
        roll_number = request.form["rollNumber"]
        email = request.form["email"]
        photo = request.files["photo"].read()

        collection = db[course]

        # Check if the record already exists
        existing_record = collection.find_one({"roll_number": roll_number})
        if existing_record:
            return redirect(url_for("already_registered"))

        data = {
            "name": name,
            "roll_number": roll_number,
            "email": email,
            "photo": base64.b64encode(photo).decode("utf-8")
        }
        collection.insert_one(data)

        # Save the student photo
        photo_filename = roll_number + ".jpg"
        photo_path = os.path.join("photos", course, photo_filename)
        os.makedirs(os.path.dirname(photo_path), exist_ok=True)
        with open(photo_path, "wb") as photo_file:
            photo_file.write(photo)

        return redirect(url_for("success"))
    except Exception as e:
        print(e)
        return "An error occurred."

# Handle downloading tabular data as CSV
@app.route("/download_data", methods=["GET"])
def download_data():
    csv_data = []
    for course in db.list_collection_names():
        data = db[course].find()
        for entry in data:
            csv_data.append([entry["name"], course, entry["roll_number"], entry["email"]])

    # Create a CSV file in-memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "Course", "Roll Number", "Email"])
    writer.writerows(csv_data)

    # Set up the response for downloading the CSV file
    response = Response(output.getvalue(), content_type="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=registration_data.csv"

    return response


# Route to download student photos
@app.route("/download_photos/<course>/<roll_number>")
def download_photo(course, roll_number):
    photo_path = os.path.join("photos", course, roll_number + ".jpg")
    if os.path.exists(photo_path):
        return send_from_directory(os.path.dirname(photo_path), os.path.basename(photo_path))
    else:
        return "Photo not found."

# Handle re-registrations or duplicates
@app.route("/already_registered.html", methods=["GET"])
def already_registered():
    return render_template("already_registered.html")

# Handle successful registration
@app.route("/success.html", methods=["GET"])
def success():
    return render_template("success.html")

# Serve the test taker verification page
@app.route("/verification", methods=["GET"])
def verification():
    return render_template("verification.html")

# Handle verification form submission
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
    app.run(debug=True)


