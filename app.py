from flask import Flask, render_template, Response
import cv2
import pygame
import time

app = Flask(__name__)

# Load Haarcascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
smile_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_smile.xml")

# Initialize pygame for sound
pygame.mixer.init()
sound = pygame.mixer.Sound("static/sound.mp3")

# Start video capture
camera = cv2.VideoCapture(0)

# Track smile detection over consecutive frames
smile_detected_frames = 0
required_consecutive_frames = 3  # Number of frames a smile must be detected

def generate_frames():
    global smile_detected_frames
    last_capture_time = 0
    cooldown = 4  # Cooldown period to prevent multiple selfies

    while True:
        success, frame = camera.read()
        if not success:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=20, minSize=(60, 60))
        for (x, y, w, h) in faces:
            roi_gray = gray[y:y+h, x:x+w]
            roi_color = frame[y:y+h, x:x+w]

            # Draw a blue box around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

            # Detect smile within the face region
            smiles = smile_cascade.detectMultiScale(roi_gray, scaleFactor=1.8, minNeighbors=27, minSize=(50, 25))

            smile_found = False  # Flag to track if a valid smile is detected

            for (sx, sy, sw, sh) in smiles:
                # Ensure the smile is in the lower half of the face and large enough
                if sy > h // 2 and sw > w * 0.4 and sh > h * 0.2:
                    smile_found = True
                    cv2.rectangle(roi_color, (sx, sy), (sx+sw, sy+sh), (0, 255, 0), 2)

            # Require a smile to be detected for consecutive frames before taking a selfie
            if smile_found:
                smile_detected_frames += 1
            else:
                smile_detected_frames = 0  # Reset counter if no smile detected

            if smile_detected_frames >= required_consecutive_frames and time.time() - last_capture_time > cooldown:
                print("😊 Smile detected consistently! Taking selfie...")

                # Save the selfie
                cv2.imwrite("static/selfie.jpg", frame)

                # Play sound when selfie is taken
                sound.play()

                last_capture_time = time.time()
                smile_detected_frames = 0  # Reset after capturing

        # Encode the frame for display
        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
