import os

# Create a root directory
data_root = 'student_data'
os.makedirs(data_root, exist_ok=True)

# Create course directories
courses = ['DAC', 'DBDA', 'DESD', 'D-IOT']
for course in courses:
    os.makedirs(os.path.join(data_root, course), exist_ok=True)
