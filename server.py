import os
from flask import Flask, request, redirect, url_for, render_template, flash, send_file
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import smbclient
from io import BytesIO
from config import Config
import zipfile


app = Flask(__name__)
app.config.from_object(Config)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Mock user database
users = {
    'user': generate_password_hash('password')
}

# Configure your Samba credentials and share
samba_server = 'your_samba_ip'
samba_share = 'your_samba_folder'
samba_username = 'samba_username'
samba_password = 'samba_password'
samba_path = f'\\\\{samba_server}\\{samba_share}'

# Initialize SMB client with the credentials
smbclient.ClientConfig(username=samba_username, password=samba_password)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

@app.context_processor
def utility_functions():
    def is_folder(file_name):
        file_path = os.path.join(samba_path, file_name)
        try:
            smbclient.listdir(file_path)
            return True  # It's a folder if we can list the directory
        except Exception:
            return False  # Not a folder if an exception occurs
    return dict(is_folder=is_folder)

@app.route('/')
@login_required
def index():
    files = []
    try:
        for file in smbclient.listdir(samba_path):
            files.append(file)
    except Exception as e:
        flash(f"Error accessing files: {str(e)}")
    return render_template('index.html', files=files)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and check_password_hash(users[username], password):
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)

        files = request.files.getlist('file')
        if not files:
            flash('No selected files', 'danger')
            return redirect(request.url)

        for file in files:
            if file:
                # Preserve the relative path
                filename = secure_filename(file.filename)
                file_path = os.path.join(samba_path, filename)

                # Create the directory if it doesn't exist
                try:
                    with smbclient.open_file(file_path, mode='wb') as f:
                        f.write(file.read())
                    flash(f'File {filename} successfully uploaded', 'success')
                except Exception as e:
                    flash(f"Error uploading file {filename}: {str(e)}", 'danger')

        return redirect(url_for('index'))
    return render_template('upload.html')



@app.route('/download/<filename>')
@login_required
def download_file(filename):
    file_path = os.path.join(samba_path, filename)
    
    # Check if it's a file or a directory
    if os.path.isdir(file_path):  # Directory case
        try:
            # Create a BytesIO buffer to hold the zip file
            zip_buffer = BytesIO()
            
            # Create a ZipFile object in memory
            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                for root, dirs, files in os.walk(file_path):
                    for file in files:
                        full_path = os.path.join(root, file)
                        zip_file.write(full_path, os.path.relpath(full_path, file_path))  # Add to zip file
            
            zip_buffer.seek(0)  # Rewind the buffer to the beginning
            return send_file(zip_buffer, download_name=f"{filename}.zip", as_attachment=True)
        
        except Exception as e:
            flash(f"Error downloading directory: {str(e)}")
            return redirect(url_for('index'))
    
    else:  # File case
        try:
            with smbclient.open_file(file_path, mode='rb') as f:
                file_data = BytesIO(f.read())
            return send_file(file_data, download_name=filename, as_attachment=True)
        except Exception as e:
            flash(f"Error downloading file: {str(e)}")
            return redirect(url_for('index'))


@app.route('/delete/<filename>', methods=['POST'])
@login_required
def delete_file(filename):
    file_path = os.path.join(samba_path, filename)
    try:
        smbclient.remove(file_path)
        flash('File successfully deleted')
    except Exception as e:
        flash(f"Error deleting file: {str(e)}")
    return redirect(url_for('index'))

@app.route('/rename/<filename>', methods=['POST'])
@login_required
def rename_file(filename):
    old_name = request.form['old_name']
    new_name = request.form['new_name']
    old_file_path = os.path.join(samba_path, old_name)
    new_file_path = os.path.join(samba_path, new_name)

    try:
        smbclient.rename(old_file_path, new_file_path)
        flash(f'File "{old_name}" successfully renamed to "{new_name}"')
    except Exception as e:
        flash(f"Error renaming file: {str(e)}", 'danger')
    
    return redirect(url_for('index'))

# @app.route('/register', methods=['GET', 'POST'])
# def register():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         if username not in users:
#             users[username] = generate_password_hash(password)
#             flash('User successfully registered')
#             return redirect(url_for('login'))
#         else:
#             flash('User already exists')
#     return render_template('register.html')

@app.route('/open_folder/<foldername>')
@login_required
def open_folder(foldername):
    folder_path = os.path.join(samba_path, foldername)
    try:
        files = smbclient.listdir(folder_path)
        return render_template('index.html', files=files, foldername=foldername)
    except Exception as e:
        flash(f"Error opening folder: {str(e)}")
        return redirect(url_for('index'))

@app.route('/download_folder/<foldername>')
@login_required
def download_folder(foldername):
    folder_path = os.path.join(samba_path, foldername)
    try:
        # Create an in-memory zip file
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    zip_file.write(full_path, os.path.relpath(full_path, folder_path))  # Add file to zip

        zip_buffer.seek(0)  # Rewind the buffer
        return send_file(zip_buffer, download_name=f'{foldername}.zip', as_attachment=True)
    except Exception as e:
        flash(f"Error downloading folder: {str(e)}", 'danger')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
