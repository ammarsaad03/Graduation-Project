from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
from werkzeug.utils import secure_filename
import time
from datetime import datetime

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = '/home/Ammarsaad123/flask_uploader/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'wav', 'mp3'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home page with basic info
@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Flask File Uploader</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .info { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
            code { background-color: #e0e0e0; padding: 2px 5px; border-radius: 3px; }
        </style>
    </head>
    <body>
        <h1>🚀 Flask File Uploader API</h1>
        <div class="info">
            <h2>API Endpoints:</h2>
            <ul>
                <li><code>POST /upload</code> - Upload a file</li>
                <li><code>GET /uploads/&lt;filename&gt;</code> - Retrieve uploaded file</li>
                <li><code>GET /list</code> - List all uploaded files</li>
                <li><code>GET /test</code> - Test endpoint</li>
            </ul>
            <h3>Allowed file types:</h3>
            <p>Images: PNG, JPG, JPEG, GIF</p>
            <p>Audio: WAV, MP3</p>
            <p><strong>Max file size:</strong> 16MB</p>
        </div>
    </body>
    </html>
    '''
    return render_template_string(html)

# Test endpoint
@app.route('/test')
def test():
    return jsonify({
        "status": "success",
        "message": "Flask server is running!",
        "timestamp": datetime.now().isoformat()
    })

# Upload endpoint
@app.route('/upload', methods=['POST'])
def upload():
    try:
        # Check if file is present
        if 'file' not in request.files and 'image' not in request.files:
            return jsonify({
                "error": "No file provided", 
                "expected": "file or image field in form data"
            }), 400
        
        # Get the file (support both 'file' and 'image' field names)
        file = request.files.get('file') or request.files.get('image')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": "Invalid file type",
                "allowed": list(ALLOWED_EXTENSIONS)
            }), 400
        
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        timestamp = str(int(time.time() * 1000))  # milliseconds for uniqueness
        name, ext = os.path.splitext(original_filename)
        filename = f"{name}_{timestamp}{ext}"
        
        # Save file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Generate public URL
        public_url = f"https://ammarsaad123.pythonanywhere.com/uploads/{filename}"
        
        return jsonify({
            "status": "success",
            "url": public_url,
            "filename": filename,
            "original_filename": original_filename,
            "size": os.path.getsize(filepath),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "error": "Upload failed",
            "details": str(e)
        }), 500

# Serve uploaded files
@app.route('/uploads/<filename>')
def serve_file(filename):
    try:
        # Security check - ensure filename doesn't contain path traversal
        filename = secure_filename(filename)
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except Exception as e:
        return jsonify({
            "error": "File not found",
            "details": str(e)
        }), 404

# List all uploaded files (optional - remove if you don't want this)
@app.route('/list')
def list_files():
    try:
        files = []
        for filename in os.listdir(app.config['UPLOAD_FOLDER']):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.isfile(filepath):
                files.append({
                    "filename": filename,
                    "url": f"https://ammarsaad123.pythonanywhere.com/uploads/{filename}",
                    "size": os.path.getsize(filepath),
                    "modified": datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                })
        
        return jsonify({
            "status": "success",
            "count": len(files),
            "files": files
        })
    except Exception as e:
        return jsonify({
            "error": "Failed to list files",
            "details": str(e)
        }), 500

# Error handlers
@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({
        "error": "File too large",
        "max_size": "16MB"
    }), 413

@app.errorhandler(404)
def not_found(e):
    return jsonify({
        "error": "Endpoint not found",
        "available_endpoints": ["/", "/upload", "/uploads/<filename>", "/list", "/test"]
    }), 404

@app.errorhandler(500)
def internal_error(e):
    return jsonify({
        "error": "Internal server error",
        "details": str(e)
    }), 500
