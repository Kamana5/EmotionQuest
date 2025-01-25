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
        data = request.get_json()
        if not data or 'frame' not in data:
            return jsonify({'error': 'No frame provided'}), 400

        # Decode the Base64 image
        frame_data = data['frame'].split(",")[1]
        frame_bytes = base64.b64decode(frame_data)
        frame_path = os.path.join(app.config['UPLOAD_FOLDER'], 'live_frame.jpg')

        # Save the frame
        with open(frame_path, 'wb') as f:
            f.write(frame_bytes)

        # Analyze the frame
        analysis = DeepFace.analyze(img_path=frame_path, actions=['emotion'], enforce_detection=False)
        dominant_emotion = analysis[0]['dominant_emotion']
        return jsonify({'emotion': dominant_emotion}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
