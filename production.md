# Deploying Django Application in Production with Gunicorn and Nginx on Ubuntu

This guide walks through all the steps we followed to deploy a Django application in production using **Gunicorn** as the WSGI server and **Nginx** as the reverse proxy on an Ubuntu server.

---

## 1. Prerequisites

- Ubuntu server (in our case, an EC2 instance with IP: `13.203.216.161`)
- SSH access to the server
- Django application ready and placed in `/home/ubuntu/fraud_detection`
- Python virtual environment set up inside the project directory as `.venv`

---

## 2. Install Dependencies

```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

Activate your virtual environment:
```bash
cd ~/fraud_detection
python3 -m venv .venv
source .venv/bin/activate
```

Install Gunicorn:
```bash
pip install gunicorn
```

---

## 3. Test Gunicorn manually

Inside the project directory:
```bash
gunicorn --bind 0.0.0.0:8000 fraud_detection.wsgi:application
```
Visit `http://<your-ip>:8000` to confirm your app runs.

Stop the Gunicorn server by pressing `Ctrl + C`.

---

## 4. Create a systemd Service for Gunicorn

Create the file `/etc/systemd/system/gunicorn.service`:

```ini
[Unit]
Description=gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/fraud_detection
ExecStart=/home/ubuntu/fraud_detection/.venv/bin/gunicorn \
          --access-logfile - \
          --workers 3 \
          --bind unix:/home/ubuntu/fraud_detection/gunicorn.sock \
          fraud_detection.wsgi:application

[Install]
WantedBy=multi-user.target
```

Then reload systemd and enable the service:

```bash
sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

Check status:
```bash
sudo systemctl status gunicorn
```

---

## 5. Configure Nginx

Create a config file `/etc/nginx/sites-available/fraud_detection`:

```nginx
server {
    listen 80;
    server_name 13.203.216.161;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        root /home/ubuntu/fraud_detection;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/fraud_detection/gunicorn.sock;
    }
}
```

Enable this config:
```bash
sudo ln -s /etc/nginx/sites-available/fraud_detection /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 6. Fix Permission Denied Issue for Socket

The following error in `/var/log/nginx/error.log` indicates a permissions issue:

```
connect() to unix:/home/ubuntu/fraud_detection/gunicorn.sock failed (13: Permission denied)
```

To fix it:
```bash
sudo chmod +x /home/ubuntu
sudo chmod +x /home/ubuntu/fraud_detection
```

This allows Nginx (running as `www-data`) to access the `.sock` file.

Restart services:
```bash
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```

---

## 7. Access the Application

Visit: [http://13.203.216.161/](http://13.203.216.161/)

You should now see your Django application running behind Nginx with Gunicorn as the application server.

---

## Summary

We:
- Installed Gunicorn and set it up as a systemd service
- Configured Nginx to serve as a reverse proxy
- Ensured correct directory permissions for the Unix socket
- Brought our Django app online with a production-grade deployment setup

---

This setup ensures your Django app is efficiently served with high performance and can be managed easily with systemd and Nginx.

