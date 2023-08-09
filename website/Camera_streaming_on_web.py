from flask import Flask, render_template, Response, jsonify, request
from camera import VideoCamera
import os
 
app = Flask(__name__)

video_camera = None  
global_frame = None 


"""whenever a user visits our app domain (localhost:5000 for local servers)
 at the given .route(), execute the index() function."""   
@app.route('/') 
def index():     
    return render_template('index.html')    





@app.route('/record_status', methods=['POST'])           
def record_status():
    global video_camera  
    if video_camera == None:  
        video_camera = VideoCamera()    
   
    json = request.get_json()

    status = json['status'] 
   
    if status == "true": 
        video_camera.start_record()
        return jsonify(result="started")
    else:
        video_camera.stop_record()  
        return jsonify(result="stopped")

def video_stream(): 
    global video_camera 
    global global_frame

    if video_camera == None: 
        video_camera = VideoCamera() 
        
    while True:
        frame = video_camera.get_frame()

        if frame != None:
            global_frame = frame 
            yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                            b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')

@app.route('/video_viewer')
def video_viewer():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

#To retrieve the ip address
os.system('ip addr | grep wlan0 | grep inet > ip.txt') 
file = open("ip.txt","r") 
ip = file.read() 
ip = ip[9:23] 
print(ip)
os.system('rm ip.txt')


if __name__ == "__main__":
   app.run(host=ip, port=5000,debug=True)
    

# if __name__ == "__main__":
#     app.run(host='192.168.43.161', port=5000,debug=True)
