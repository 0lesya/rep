import os
from flask import Flask, request, url_for, flash, redirect, send_from_directory
from flask_socketio import SocketIO, emit
from werkzeug.utils import secure_filename


UPLOAD_FOLDER = '/'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
socketio = SocketIO(app)

thread = None
NS ="/"
def progress_update():
    for i in range(5):
        socketio.sleep(1)
        socketio.emit('upload_file', {"text": 25*i}, namespace=NS)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config['UPLOAD_FOLDER'], name)

@socketio.on("connect", namespace=NS)
def test_connect():
    print("connect")
    socketio.start_background_task(target=progress_update())

@socketio.on("disconnect", namespace=NS)
def test_disconnect():
    print("disconnect")

# upload image
@app.route('/', methods=["POST", "GET"])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash("'Can't read the file")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            progress_update()
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('download_file', name=filename))
    return '''
        <!doctype html>
        <html>
        <head>
        <script src ="//cdnjs.cloudflare.com/ajax/libs/socket.io/1.3.5/socket.io.min.js"></script>
        <script scr="https://cdn.jsdelivr.net/npm/vue/dist/vue.js"></script>
        </head>
        <div id="">
        <div class="progress" style="width: 50%; margin: 50px;">
        <div class="progress-bar progress-bar-striped active"
        role="progressbar"
        v-bind:aria-valuenow="progress"
        aria-valuemin="0"
        aria-valuemax="100"
        v-bind:style="'width: '+progress+'%'"
        >
        <span class="progress-bar-label" v-text="progress + '%'"></span>
        </div>
        </div>
        <span v-text="message"></span>
        </div>
        
        <script>
        let app = new Vue({
        el: "#",
        data: {
        progress: 0,
        socket: null, 
        }, 
        created: function(){
        socket=io.connect("http://"+document.domain+":"+location.port+"/");
        socket.on("progress", (msg) => {
        this.progress = msg.text;
        });
        },
        })
        </script>
        
        <title>Upload new file</title>
        <h1>Upload new file</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        <html>


        '''



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


