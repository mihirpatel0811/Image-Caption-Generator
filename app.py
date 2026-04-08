# AutoCaption AI - Main Application File
# This file runs the web application

import os
import uuid
import sys
from flask import Flask, render_template, request, jsonify, session
from werkzeug.utils import secure_filename
from models import db, ImageCaption, SavedCaption
from vision_engine import generate_captions, generate_captions_from_text, PLATFORM_CONFIGS
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create Flask application
app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///captions.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["UPLOAD_FOLDER"] = os.path.join("static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB limit

# Allowed file extensions for image uploads
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

# Create upload folder if it doesn't exist
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# Initialize database
db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()


# Function to check if file extension is allowed
def allowed_file(filename):
    # Check if filename has a dot and extension is allowed
    if "." in filename:
        ext = filename.rsplit(".", 1)[1].lower()
        return ext in ALLOWED_EXTENSIONS
    return False


# Home page - Main caption generator
@app.route("/")
def index():
    # Create list of platforms for the dropdown
    platforms = []
    for pid, cfg in PLATFORM_CONFIGS.items():
        platforms.append({
            "id": pid,
            "name": cfg["name"],
            "style": cfg["style"]
        })
    return render_template("index.html", platforms=platforms)


# About page - Information about the app
@app.route("/about")
def about():
    return render_template("about.html")


# Gallery page - View previously generated captions
@app.route("/gallery")
def gallery():
    # Get all images from database, newest first
    images = ImageCaption.query.order_by(ImageCaption.timestamp.desc()).all()
    return render_template("gallery.html", images=images)


# Upload endpoint - Handle image upload and caption generation
@app.route("/upload", methods=["POST"])
def upload_file():
    # Check if image file was included in request
    if "image" not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files["image"]
    
    # Check if a file was actually selected
    if file.filename == "":
        return jsonify({"error": "No file selected for uploading"}), 400

    # Get form data
    platform = request.form.get("platform", "general")
    caption_hint = request.form.get("caption_hint", "")
    caption_type = request.form.get("caption_type", "all")

    # Process file if valid
    if file and allowed_file(file.filename):
        # Secure the filename and create unique name
        filename = secure_filename(file.filename)
        unique_filename = str(uuid.uuid4().hex) + "_" + filename
        
        # Save file to uploads folder
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], unique_filename)
        file.save(filepath)

        # Generate captions using AI
        captions = generate_captions(filepath, platform=platform, caption_hint=caption_hint, caption_type=caption_type)

        # Check for errors
        if "error" in captions:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"error": captions["error"]}), 500

        # Save to database
        new_image = ImageCaption(
            filename=unique_filename,
            descriptive_caption=captions.get("descriptive"),
            social_caption=captions.get("social"),
            alt_text=captions.get("accessibility"),
            platform=platform,
        )
        db.session.add(new_image)
        db.session.commit()

        # Return success response
        return jsonify(
            {
                "success": True,
                "filename": unique_filename,
                "captions": captions,
                "platform": platform,
                "platform_name": captions.get("platform_name", "General"),
            }
        )
    else:
        return (
            jsonify({"error": "Allowed file types are png, jpg, jpeg, gif, webp"}),
            400,
        )


# Regenerate endpoint - Create new captions for existing image
@app.route("/regenerate", methods=["POST"])
def regenerate_caption():
    # Get request data
    data = request.get_json()
    if not data or "filename" not in data:
        return jsonify({"error": "No filename provided"}), 400

    filename = data["filename"]
    platform = data.get("platform", "general")
    caption_hint = data.get("caption_hint", "")
    caption_type = data.get("caption_type", "all")

    # Check if file exists
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404

    # Generate new captions
    captions = generate_captions(filepath, platform=platform, caption_hint=caption_hint, caption_type=caption_type)

    if "error" in captions:
        return jsonify({"error": captions["error"]}), 500

    # Update database record
    record = ImageCaption.query.filter_by(filename=filename).first()
    if record:
        record.descriptive_caption = captions.get("descriptive")
        record.social_caption = captions.get("social")
        record.alt_text = captions.get("accessibility")
        record.platform = platform
        db.session.commit()

    return jsonify(
        {
            "success": True,
            "captions": captions,
            "platform": platform,
            "platform_name": captions.get("platform_name", "General"),
        }
    )


# Generate from text endpoint - Create captions without image
@app.route("/generate-from-text", methods=["POST"])
def generate_from_text():
    data = request.get_json()
    if not data or "description" not in data or not data["description"].strip():
        return jsonify({"error": "Description is required"}), 400

    description = data["description"].strip()
    platform = data.get("platform", "general")
    caption_type = data.get("caption_type", "promotional")
    tone = data.get("tone", "casual")
    count = min(max(int(data.get("count", 3)), 1), 10)

    result = generate_captions_from_text(
        description=description,
        platform=platform,
        caption_type=caption_type,
        tone=tone,
        count=count,
    )

    if "error" in result:
        return jsonify({"error": result["error"]}), 500

    return jsonify(result)


# Save caption endpoint - Save a caption to favorites
@app.route("/save-caption", methods=["POST"])
def save_caption():
    data = request.get_json()
    if not data or "caption_text" not in data or not data["caption_text"].strip():
        return jsonify({"error": "Caption text is required"}), 400

    saved = SavedCaption(
        caption_text=data["caption_text"].strip(),
        platform=data.get("platform", "general"),
        caption_type=data.get("caption_type", "promotional"),
        tone=data.get("tone", "casual"),
        description=data.get("description", ""),
        is_favorite=data.get("is_favorite", False),
    )
    db.session.add(saved)
    db.session.commit()

    return jsonify({"success": True, "caption": saved.to_dict()})


# Get saved captions endpoint
@app.route("/saved-captions", methods=["GET"])
def get_saved_captions():
    favorites_only = request.args.get("favorites", "false").lower() == "true"
    query = SavedCaption.query.order_by(SavedCaption.timestamp.desc())
    if favorites_only:
        query = query.filter_by(is_favorite=True)
    captions = query.all()
    return jsonify({"captions": [c.to_dict() for c in captions]})


# Update saved caption endpoint
@app.route("/saved-captions/<int:caption_id>", methods=["PATCH"])
def update_saved_caption(caption_id):
    saved = SavedCaption.query.get_or_404(caption_id)
    data = request.get_json()
    if "is_favorite" in data:
        saved.is_favorite = bool(data["is_favorite"])
    if "caption_text" in data:
        saved.caption_text = data["caption_text"]
    db.session.commit()
    return jsonify({"success": True, "caption": saved.to_dict()})


# Delete saved caption endpoint
@app.route("/saved-captions/<int:caption_id>", methods=["DELETE"])
def delete_saved_caption(caption_id):
    saved = SavedCaption.query.get_or_404(caption_id)
    db.session.delete(saved)
    db.session.commit()
    return jsonify({"success": True})


# Reset endpoint - Clear all data
@app.route("/reset", methods=["POST"])
def reset_data():
    # Delete all database records
    ImageCaption.query.delete()
    SavedCaption.query.delete()
    db.session.commit()

    # Delete all uploaded files
    upload_folder = app.config["UPLOAD_FOLDER"]
    if os.path.exists(upload_folder):
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception:
                pass

    return jsonify({"success": True, "message": "All data has been cleared."})


# Logout endpoint - Exit the application
@app.route("/logout", methods=["GET", "POST"])
def logout():
    import os, signal, threading
    
    # Function to shut down the server
    def shutdown_server():
        # A short delay to allow the response to be sent before killing
        os.kill(os.getpid(), signal.SIGINT)
        
    threading.Timer(0.5, shutdown_server).start()
    return jsonify({"success": True, "message": "Application closed"})


# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5000)