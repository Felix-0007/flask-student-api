from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# -------------------- DATABASE CONFIG (MYSQL) --------------------
# FORMAT: mysql+pymysql://username:password@host:port/database
app.config['SQLALCHEMY_DATABASE_URI'] = (
    "mysql+pymysql://flaskuser:flask123@localhost/student_db"
)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -------------------- STUDENT MODEL --------------------
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "course": self.course,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

# -------------------- CREATE TABLES --------------------
with app.app_context():
    db.create_all()

# -------------------- CREATE STUDENT --------------------
@app.route('/students', methods=['POST'])
def create_student():
    data = request.get_json()

    if not data or not data.get('name') or not data.get('email') or not data.get('course'):
        return jsonify({"error": "Name, email and course are required"}), 400

    student = Student(
        name=data['name'],
        email=data['email'],
        course=data['course']
    )

    try:
        db.session.add(student)
        db.session.commit()
        return jsonify({
            "message": "Student created successfully",
            "student": student.to_dict()
        }), 201

    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409

# -------------------- LIST STUDENTS --------------------
@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([s.to_dict() for s in students]), 200

# -------------------- UPDATE STUDENT --------------------
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    student = Student.query.get(id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    data = request.get_json()
    student.name = data.get('name', student.name)
    student.email = data.get('email', student.email)
    student.course = data.get('course', student.course)

    try:
        db.session.commit()
        return jsonify({"message": "Student updated successfully"}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email already exists"}), 409

# -------------------- DELETE STUDENT --------------------
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    student = Student.query.get(id)

    if not student:
        return jsonify({"error": "Student not found"}), 404

    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted successfully"}), 200

# -------------------- HOME --------------------
@app.route('/')
def home():
    return jsonify({"message": "Student API Running with MySQL"})

# -------------------- RUN SERVER --------------------
if __name__ == '__main__':
    app.run(debug=True)
