# Installing Required Libraries
# If you have not installed the necessary libraries in your system, follow these steps to install 
# them automatically.

# 1. Open your terminal or command prompt in the directory where the `requirements.txt` file is located.
# 2. Run the following command to install all the required libraries:
#     pip install -r requirements.txt

# This will ensure that all necessary libraries are installed with the specified versions.



from flask import Flask, render_template, Response
import cv2
import signal
import sys
import socket
import firebase_admin
from firebase_admin import credentials, firestore




app = Flask(__name__)
camera = None  

firebase_admin_sdk = "firebase_key\sphere-6ee2b-firebase-adminsdk-pag88-6502a061c3.json"
database_parent_node = 'communicationData'
database_child_node = "credentials"




def generate_frames():
    global camera 
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            frame = cv2.flip(frame, 1)

            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')




@app.route('/')
def index():
    return render_template('index.html')




@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')




def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip




def send_ip_and_port_to_flutter_app(ip_address, port):
    try:
        # Initialize Firebase Admin SDK with your credentials
        cred = credentials.Certificate(firebase_admin_sdk)
        firebase_admin.initialize_app(cred)
        db = firestore.client()

        # Update Firestore document with IP address and port
        image_ref = db.collection(database_parent_node).document(database_child_node)
        image_ref.set({
            'ip_address': ip_address,
            'port_number': port
        })

        print('Data is successfully sent to FireBase!')

    except Exception as e:
        print(f'Failed to send data: {e}')





def cleanup_actions():
    global camera
    print('Performing memory cleanup actions...')
    if camera:
        camera.release()  # Release the camera if initialized
    cv2.destroyAllWindows()  # Close all OpenCV windows

    db = firestore.client()
    # Deletee IP address and port in Firestore document
    image_ref = db.collection(database_parent_node).document(database_child_node)
    image_ref.set({
            'ip_address': "",
            'port_number': ""
    })

    firebase_admin.delete_app(firebase_admin.get_app())  # Delete Firebase instance



def signal_handler(sig, frame):
    print(f'\nReceived signal {sig}, exiting...')
    cleanup_actions()
    sys.exit(0)



if __name__ == '__main__':

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)  # Ctrl+C
    signal.signal(signal.SIGTERM, signal_handler)  # Termination signal

    # Get local IP and port
    host_ip = get_local_ip()
    port = 5000

    # Start camera
    camera = cv2.VideoCapture(0)

    # Send IP and port information to Flutter app
    send_ip_and_port_to_flutter_app(host_ip, port)

    # Start Flask server
    print(f"Starting server at IP: {host_ip}, Port: {port}")
    app.run(host=host_ip, port=port, threaded=True)
