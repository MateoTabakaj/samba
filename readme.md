Here's your updated `README.md` file with the necessary additions:

```markdown
# Samba Web Application

A modern web interface for Samba server management, featuring secure file operations through an intuitive browser-based interface. Built with Python and secured by Nginx reverse proxy, this application provides seamless access to Samba shares whether deployed locally or on AWS EC2.

## 🚀 Features

- **Web-Based File Management**: Intuitive interface for Samba share interactions
- **Secure File Operations**: Upload and manage files through a protected web interface
- **Production-Ready**: Powered by Gunicorn application server
- **Enterprise Security**: Nginx reverse proxy configuration for enhanced security
- **Flexible Deployment**: Support for both local and AWS EC2 deployment

## 📋 Prerequisites
**⚠️ Warning: First you need to have a Samba server running. This application integrates with a Samba server to interact with shares and files.**

This is a web application that integrates with a Samba server, allowing users to interact with it through a web interface. The app uses **Gunicorn** as the application server and **Nginx** as the reverse proxy. It is designed to be deployed both locally and on AWS EC2 instances.

Before you begin, ensure you have:

- Python 3.8 or higher
- pip (Python package manager)
- Nginx web server
- Access to a Samba server
- (Optional) AWS account for EC2 deployment

## 🛠️ Installation

### Local Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/MateoTabakaj/samba-web-app.git
   cd samba-web-app
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   
   # On Linux/macOS
   source venv/bin/activate
   
   # On Windows
   .\venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Deployment

### Local Deployment

1. **Start Gunicorn Server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:8000 server:app
   ```

2. **Configure Nginx**
   ```nginx
   server {
       listen 80;
       server_name localhost;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### AWS EC2 Deployment

1. **Launch EC2 Instance**
   - Launch Ubuntu Server 20.04 LTS instance
   - Configure Security Group:
     - Allow SSH (Port 22)
     - Allow HTTP (Port 80)
     - Allow HTTPS (Port 443) if using SSL

2. **Connect to Instance**
   ```bash
   ssh -i /path/to/your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install System Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip nginx
   ```

4. **Deploy Application**
   ```bash
   # Clone and setup application
   git clone https://github.com/MateoTabakaj/samba-web-app.git
   cd samba-web-app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   
   # Start application with Gunicorn
   gunicorn -w 4 -b 0.0.0.0:8000 server:app
   ```

## 🔒 Security Configuration

1. **Configure Firewall**
   ```bash
   sudo ufw allow 'Nginx Full'
   sudo ufw allow OpenSSH
   sudo ufw enable
   ```

2. **Set Up SSL (Recommended)**
   - Install Certbot
   - Obtain SSL certificate
   - Configure Nginx for HTTPS

## 🔍 Monitoring and Maintenance

- **View Logs**
  ```bash
  # Nginx logs
  sudo tail -f /var/log/nginx/error.log
  sudo tail -f /var/log/nginx/access.log
  
  # Application logs
  tail -f logs/app.log
  ```

- **Restart Services**
  ```bash
  sudo systemctl restart nginx
  sudo systemctl restart gunicorn
  ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📮 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

Made with ❤️ by Mateo
```

This updated `README.md` includes:

- A clear **warning** about the Samba server requirement.
- Prerequisites for running the application.
- Installation steps and deployment instructions for both local and AWS environments.
- Security and monitoring instructions. 

Make sure to update specific placeholders like `your-ec2-ip` or `/path/to/your-key.pem` before using this file in your project.