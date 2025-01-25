from flask import Flask, request, render_template
from deepface import DeepFace
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "-1"
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}

# Create the upload folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part", 400
    file = request.files['file']
    if file.filename == '':
        return "No selected file", 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        # Debugging: Print the file path
        print(f"File saved at: {filepath}")

        try:
            # Analyze the image
            analysis = DeepFace.analyze(img_path=filepath, actions=['emotion'])
            print(f"DeepFace analysis: {analysis}")  # Debugging
            dominant_emotion = analysis[0]['dominant_emotion']
            return f"Dominant Emotion: {dominant_emotion}", 200
        except Exception as e:
            print(f"Error during DeepFace analysis: {e}")  # Log detailed error
            return f"Error during emotion analysis: {e}", 500
    else:
        return "Invalid file type", 400
    
if __name__ == '__main__':
    app.run(debug=True)