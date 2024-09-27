from flask import Flask, render_template, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
from ultralytics import YOLO
import os
import shutil
import glob
import base64
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet', max_http_buffer_size=10 * 2000 * 1024)

model = YOLO(r"E:\\birdanddrone\\MODEL EĞİTİM\\YOLO\runs\\detect\\train\\weights\\best.pt")
os.makedirs("upload", exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/captcha')
def captcha():
    return render_template('captcha.html')



@app.route('/upload/predict/<filename>')
def serve_image(filename):
    return send_from_directory(os.path.join("upload", "predict"), filename)

@socketio.on('upload_image')
def handle_image(data):
    filename = data['filename']
    img_data = data['image'].split(",")[1]  
    img_path = os.path.join("upload", filename)

    # Decode the base64 image and save it to the server
    with open(img_path, "wb") as f:
        f.write(base64.b64decode(img_data))

    try:
        path = "upload"
        folder = glob.glob(os.path.join(path, '*predict*'))

        if folder:
            shutil.rmtree(folder[0])

        # Perform YOLO prediction
        start_time = time.time()
        results = model.predict(source=img_path, save=True, project="upload", name="predict")
        end_time = time.time()
        processing_time = end_time - start_time

        os.remove(img_path)

        if not results or len(results[0].boxes) == 0:
            socketio.emit('no_detection', {'message': 'İHA veya Kuş tespit edilemedi.'})
            return

    except Exception as e:
        socketio.emit('error', {'message': f"Error during prediction: {e}"})
        return

    # Rename the predicted image
    dir_path = "upload\\predict"
    pred_img = os.listdir(dir_path)[0]  # Get the predicted image name
    name, ext = os.path.splitext(pred_img)
    new_name = f"{name}_pred{ext}"  # Create new name with _pred suffix

    old_img_path = os.path.join(dir_path, pred_img)
    new_img_path = os.path.join(dir_path, new_name)

    # Rename the predicted image
    os.rename(old_img_path, new_img_path)

    # Emit the processed image URL back to the client
    socketio.emit('image_processed', {
        'url': f'/upload/predict/{new_name}',
        'processing_time': processing_time 
    })

    
if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1', port=5500, debug=True)  

