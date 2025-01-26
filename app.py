from flask import Flask, request, render_template, jsonify
from deepface import DeepFace
import os
import base64  # Import the base64 module for decoding Base64 strings
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/learn-emotions')
def learn_emotions():
    return render_template('learn-emotions.html')

@app.route('/practice-emotions')
def practice_emotions():
    return render_template('practice-emotions.html')

@app.route('/happy')
def happy():
    return render_template('happy.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        try:
            # Analyze the image
            analysis = DeepFace.analyze(img_path=filepath, actions=['emotion'], enforce_detection=False)
            dominant_emotion = analysis[0]['dominant_emotion']
            return jsonify({'dominant_emotion': dominant_emotion}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    else:
        return jsonify({'error': 'Invalid file type'}), 400
    
@app.route('/live-emotion', methods=['POST'])
def live_emotion():
    try:
        # Get the Base64 image data from the request
        frame_data = request.json.get('frame')
        if not frame_data:
            return jsonify({"error": "No frame data provided"}), 400

        # Decode the Base64 image and save it
        try:
            frame_data = frame_data.split(",")[1]  # Remove "data:image/jpeg;base64," prefix
            frame_bytes = base64.b64decode(frame_data)
            frame_path = os.path.join(app.config['UPLOAD_FOLDER'], "live_frame.jpg")
            with open(frame_path, "wb") as f:
                f.write(frame_bytes)
        except Exception as e:
            return jsonify({"error": f"Base64 decoding failed: {str(e)}"}), 400

        # Confirm the file exists and is non-empty
        if os.path.exists(frame_path):
            file_size = os.path.getsize(frame_path)
            if file_size == 0:
                return jsonify({"error": "Saved image file is empty"}), 500
            print(f"File saved successfully at {frame_path}, size: {file_size} bytes")
        else:
            return jsonify({"error": "File not found after saving"}), 500

        # Analyze the saved frame with DeepFace
        try:
            analysis = DeepFace.analyze(img_path=frame_path, actions=['emotion'], enforce_detection=False)
            dominant_emotion = analysis[0]['dominant_emotion']
            return jsonify({"emotion": dominant_emotion}), 200
        except Exception as e:
            return jsonify({"error": f"DeepFace failed to process the image: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/happy.html')
def happy():
    return render_template('happy.html')

@app.route('/sad.html')
def sad():
    return render_template('sad.html')

@app.route('/surprise.html')
def surprise():
    return render_template('surprise.html')

@app.route('/angry.html')
def angry():
    return render_template('angry.html')


if __name__ == '__main__':
    app.run(debug=True)