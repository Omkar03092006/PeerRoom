from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import os
import subprocess
import json
import time
import uuid
import shutil
import atexit
from PIL import Image

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Generate a random secret key for better security

# Dummy database for users - will be cleared on restart
users = []
active_sessions = {}  # Track active sessions and their associated users

def cleanup_all_data():
    """Clean up all data when server starts/stops"""
    try:
        users.clear()
        active_sessions.clear()
        session.clear()
        
        # Clear users.json if it exists
        if os.path.exists('users.json'):
            try:
                with open('users.json', 'w') as f:
                    json.dump([], f)
            except Exception as e:
                print(f"Error clearing users.json: {str(e)}")
        
        # Remove uploads directory and all its contents
        uploads_dir = os.path.join(os.getcwd(), 'uploads')
        if os.path.exists(uploads_dir):
            shutil.rmtree(uploads_dir)
            
        print("All data cleaned up successfully")
    except Exception as e:
        print(f"Cleanup error: {str(e)}")

# Register cleanup function to run when server starts and stops
atexit.register(cleanup_all_data)
cleanup_all_data()  # Clean up on start

def ensure_directory(path):
    """Create directory if it doesn't exist and return the absolute path"""
    abs_path = os.path.abspath(path)
    os.makedirs(abs_path, exist_ok=True)
    return abs_path

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        year = request.form.get("year")
        subjects = request.form.get("subjects")
        specialization = request.form.get("specialization")
        group_size = request.form.get("group-size")
        whatsapp = request.form.get("whatsapp")

        # Generate a unique session ID
        session_id = str(uuid.uuid4())
        tab_id = str(uuid.uuid4())
        
        # Create user data
        user_data = {
            "name": name,
            "email": email,
            "year": year,
            "subjects": subjects,
            "specialization": specialization,
            "group_size": group_size,
            "whatsapp": whatsapp,
            "is_verified": False,
            "session_id": session_id,
            "tab_id": tab_id
        }
        
        # Store user data
        users.append(user_data)
        
        # Store session information
        session['current_user'] = name
        session['session_id'] = session_id
        session['tab_id'] = tab_id
        active_sessions[session_id] = user_data
        
        print(f"New registration - Name: {name}, Session ID: {session_id}, Tab ID: {tab_id}")
        return render_template("thankyou.html", name=name, tab_id=tab_id, redirect_url=url_for('room', name=name, tab_id=tab_id))

@app.route('/verify-id', methods=['POST'])
def verify_id():
    print("\n=== Starting ID Verification Process ===")
    
    if 'id_card' not in request.files:
        print("Error: No file part in request")
        return jsonify({'status': 'error', 'message': 'No file uploaded'})
    
    id_card = request.files['id_card']
    if id_card.filename == '':
        print("Error: No selected file")
        return jsonify({'status': 'error', 'message': 'No file selected'})
    
    # Get session information
    session_id = session.get('session_id')
    tab_id = session.get('tab_id')
    current_user_name = session.get('current_user')
    
    print(f"\nVerification request details:")
    print(f"User Name: {current_user_name}")
    print(f"Session ID: {session_id}")
    print(f"Tab ID: {tab_id}")
    
    if not all([session_id, current_user_name, tab_id]):
        print("Error: Missing session information")
        return jsonify({
            'status': 'error',
            'message': 'Session expired. Please refresh the page and try again.'
        })
    
    # Find current user
    current_user = next((user for user in users 
                        if user["name"] == current_user_name 
                        and user.get("session_id") == session_id 
                        and user.get("tab_id") == tab_id), None)
    
    if not current_user:
        print("Error: User not found in active sessions")
        return jsonify({
            'status': 'error',
            'message': 'User not found. Please refresh the page and try again.'
        })
    
    try:
        # Ensure directories exist
        uploads_dir = ensure_directory('uploads')
        tessdata_dir = ensure_directory('tessdata')
        
        # Check if tessdata is properly set up
        if not os.path.exists(os.path.join(tessdata_dir, 'eng.traineddata')):
            print("Error: Tesseract language data file missing")
            return jsonify({
                'status': 'error',
                'message': 'OCR system not properly configured. Please contact administrator.'
            })
        
        # Save the uploaded file with unique name
        filename = f"{session_id}_{id_card.filename}"
        file_path = os.path.join(uploads_dir, filename)
        
        # Ensure the file is a valid image before saving
        try:
            # First save the uploaded file temporarily
            temp_path = os.path.join(uploads_dir, f"temp_{filename}")
            id_card.save(temp_path)
            
            # Open and convert to PNG
            with Image.open(temp_path) as img:
                # Convert to RGB if needed (handles RGBA images)
                if img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[-1])
                    img = background
                elif img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Save as PNG with high quality
                png_path = os.path.splitext(file_path)[0] + '.png'
                img.save(png_path, 'PNG', quality=95)
                file_path = png_path
            
            # Clean up temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
                
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': 'Could not process the image. Please try uploading a different image file.'
            })
        
        print(f"\nFile details:")
        print(f"Saved to: {file_path}")
        print(f"File exists: {os.path.exists(file_path)}")
        print(f"File size: {os.path.getsize(file_path)} bytes")
        
        # Get absolute paths
        jar_path = os.path.join(os.getcwd(), 'target', 'frontend-1.0-SNAPSHOT-jar-with-dependencies.jar')
        
        print(f"\nVerification paths:")
        print(f"JAR path: {jar_path}")
        print(f"Tessdata path: {tessdata_dir}")
        print(f"JAR exists: {os.path.exists(jar_path)}")
        
        if not os.path.exists(jar_path):
            print("Error: JAR file not found")
            return jsonify({
                'status': 'error',
                'message': 'Verification system not properly configured. Please contact administrator.'
            })
        
        # Run Java verifier with explicit tessdata path
        print("\nRunning Java verifier:")
        cmd = ['java', '-jar', jar_path, file_path, current_user_name]
        print(f"Command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env={**os.environ, 'TESSDATA_PREFIX': tessdata_dir}
        )
        
        print(f"\nJava process results:")
        print(f"Exit code: {result.returncode}")
        print(f"Stdout: {result.stdout}")
        print(f"Stderr: {result.stderr}")
        
        if result.returncode != 0:
            print("Error: Java process returned non-zero exit code")
            return jsonify({
                'status': 'error',
                'message': 'Verification process failed. Please try again.'
            })
        
        try:
            verification_result = json.loads(result.stdout)
            print(f"\nParsed verification result: {verification_result}")
            
            if verification_result.get('success'):
                current_user['is_verified'] = True
                print(f"Verification successful for user: {current_user_name}")
                return jsonify({
                    'status': 'success',
                    'message': 'ID card verified successfully'
                })
            else:
                error_msg = verification_result.get('message', 'Verification failed')
                print(f"Verification failed: {error_msg}")
                return jsonify({
                    'status': 'error',
                    'message': error_msg
                })
                
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {result.stdout}")
            return jsonify({
                'status': 'error',
                'message': 'Invalid verification response. Please try again.'
            })
            
    except Exception as e:
        print(f"\nError during verification: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': 'An error occurred during verification. Please try again.'
        })
    finally:
        # Clean up uploaded file
        try:
            if os.path.exists(file_path):
                print(f"\nCleaning up file: {file_path}")
                os.remove(file_path)
        except Exception as e:
            print(f"Error cleaning up file: {str(e)}")

@app.route("/room/<name>/<tab_id>")
def room(name, tab_id):
    current_user = next((user for user in users 
                        if user["name"] == name 
                        and user.get("tab_id") == tab_id), None)
    
    if not current_user:
        return redirect(url_for('home'))

    matched_users = [
        user for user in users
        if user["tab_id"] != tab_id
        and user["year"] == current_user["year"]
        and user["group_size"] == current_user["group_size"]
        and (
            (current_user["year"] == "1" and user["subjects"] == current_user["subjects"]) or
            (current_user["year"] != "1" and user["specialization"] == current_user["specialization"])
        )
    ]

    return render_template("room.html", 
                         name=name,
                         current_user=current_user,
                         matched_users=matched_users,
                         is_verified=current_user.get("is_verified", False))

@app.route('/room-status')
def room_status():
    session_id = session.get('session_id')
    tab_id = session.get('tab_id')
    current_user_name = session.get('current_user')
    
    if not all([session_id, tab_id, current_user_name]):
        return jsonify({
            'status': 'error',
            'message': 'Session information not found'
        })
    
    current_user = next((user for user in users 
                        if user["name"] == current_user_name 
                        and user.get("session_id") == session_id
                        and user.get("tab_id") == tab_id), None)
    
    if not current_user:
        return jsonify({
            'status': 'error',
            'message': 'User not found'
        })
    
    matched_users = [user for user in users 
                    if user["tab_id"] != tab_id
                    and ((current_user["year"] == "1" and user["subjects"] == current_user["subjects"])
                    or (current_user["year"] != "1" and user["specialization"] == current_user["specialization"]))
                    and user["year"] == current_user["year"]
                    and user["group_size"] == current_user["group_size"]]
    
    return jsonify({
        'all_verified': all(user["is_verified"] for user in matched_users) and current_user["is_verified"],
        'user_count': len(matched_users)
    })

if __name__ == "__main__":
    print("\n=== Starting PeerRoom Application ===")
    print("Checking environment:")
    
    # Check Java
    try:
        java_version = subprocess.run(['java', '-version'], capture_output=True, text=True)
        print(f"Java version found: {java_version.stderr}")
    except Exception as e:
        print(f"Warning: Java check failed: {e}")
    
    # Check JAR file
    jar_path = os.path.join(os.getcwd(), 'target', 'frontend-1.0-SNAPSHOT-jar-with-dependencies.jar')
    print(f"JAR file exists: {os.path.exists(jar_path)}")
    
    # Check tessdata
    tessdata_path = os.path.join(os.getcwd(), 'tessdata')
    print(f"Tessdata exists: {os.path.exists(tessdata_path)}")
    
    print("\nStarting server with fresh data...")
    app.run(debug=True)
