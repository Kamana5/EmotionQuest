from deepface import DeepFace



try:
    analysis = DeepFace.analyze(
        img_path='uploads/happy.jpg', 
        actions=['emotion'], 
        enforce_detection=False
    )
    print("Analysis Result:", analysis)
except Exception as e:
    print("DeepFace Error:", e)
