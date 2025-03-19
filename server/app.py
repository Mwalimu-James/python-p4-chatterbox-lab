from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_migrate import Migrate
from sqlalchemy.orm import Session

from models import db, Message

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

# ✅ Ensure database tables exist before running the app
with app.app_context():
    db.create_all()


# ✅ GET all messages (ordered by created_at)
@app.route('/messages', methods=['GET'])
def get_messages():
    messages = Message.query.order_by(Message.created_at.asc()).all()
    return jsonify([msg.to_dict() for msg in messages]), 200


# ✅ POST a new message
@app.route('/messages', methods=['POST'])
def create_message():
    data = request.get_json()

    if not data or "body" not in data or "username" not in data:
        return jsonify({"error": "Missing required fields: 'body' and 'username'"}), 400

    new_message = Message(
        body=data["body"],
        username=data["username"]
    )

    db.session.add(new_message)
    db.session.commit()

    return jsonify(new_message.to_dict()), 201


# ✅ PATCH an existing message (update body only)
@app.route('/messages/<int:id>', methods=['PATCH'])
def update_message(id):
    message = db.session.get(Message, id)  # 🔥 Updated for SQLAlchemy 2.0+

    if not message:
        return jsonify({"error": "Message not found"}), 404

    data = request.get_json()
    
    if not data or "body" not in data:
        return jsonify({"error": "Missing required field: 'body'"}), 400

    message.body = data["body"]
    db.session.commit()

    return jsonify(message.to_dict()), 200


# ✅ DELETE a message
@app.route('/messages/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = db.session.get(Message, id)  # 🔥 Updated for SQLAlchemy 2.0+

    if not message:
        return jsonify({"error": "Message not found"}), 404

    db.session.delete(message)
    db.session.commit()

    return '', 204


# ✅ Root route for API documentation
@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to the Chatterbox API!",
        "routes": {
            "GET /messages": "Retrieve all messages",
            "POST /messages": "Create a new message",
            "PATCH /messages/<id>": "Update a message",
            "DELETE /messages/<id>": "Delete a message"
        }
    }), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
