import firebase_admin
from firebase_admin import credentials, db as firebase_db, storage
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
# Initialize Firebase Admin
cred = credentials.Certificate('attendance-system-8e5a5-firebase-adminsdk-dlufb-f785206af3.json')
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://attendance-system-8e5a5-default-rtdb.firebaseio.com",
    'storageBucket': 'attendance-system-8e5a5.appspot.com'
})

# Get a reference to the root of the database
root_ref = firebase_db.reference('/')

def delete_student(student_id):
    try:
        # Get student data
        student_ref = firebase_db.reference('students').child(student_id)
        student_data = student_ref.get()
        if not student_data:
            return {'success': False, 'error': 'Student not found.'}

        # Retrieve the grade attribute
        grade_id = student_data.get('grade')
        class_ = student_data.get('class')

        # Delete student image from storage
        image_url = student_data.get('image_url')
        if image_url:
            image_name = image_url.split('/')[-1]  # Get the image file name
            bucket = storage.bucket()
            blob = bucket.blob('student_images/' + image_name)
            blob.delete()

        # Delete student document from students collection
        student_ref.delete()

        # Delete student ID from student_list in grades collection
        if grade_id:
            grade_ref = firebase_db.reference('grades').child(grade_id).child(class_)
            student_list_ref = grade_ref.child('student_list')
            if student_id in student_list_ref.get():
                student_list_ref.child(student_id).delete()
        return {'success': True, 'message': 'Student with ID {student_id} deleted successfully.', 'grade': grade_id}
    except Exception as e:
        return {'success': False, 'error': str(e)}

@app.route('/delete_student', methods=['DELETE'])
def delete_student_api():
    student_id = request.args.get('student_id')

    if not student_id:
        return jsonify({'error': 'Student ID is required.'}), 400

    # Call delete_student function
    result = delete_student(student_id)

    return jsonify(result)


@app.route('/', methods=['GET'])
def health_check():
    return jsonify({'status': 'UP'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8080, host='0.0.0.0')
