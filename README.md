# Fraud Detection In Finance

## Overview
This project focuses on detecting fraudulent transactions using machine learning techniques and Artifical Intelligence model. The goal is to build a model that can accurately classify fraudulent activities in financial transactions and signature frogery detection.

## Dataset
The dataset used for this project contains transaction details, including features such as transaction amount, transaction date, and other relevant information. The dataset is split into training and testing sets to evaluate the model's performance.

## Techstack
To run this project, you need to have Python installed along with the following libraries:
- Backend: Django, Django REST Framework
- Frontend: React (hosted on Vercel)
- Machine Learning: TensorFlow/Keras, Scikit-learn
- Database: PostgreSQL (Railway)
- Deployment: Railway (Backend), Vercel (Frontend)
- API Testing: Postman

## Frontend Repository
    ```bash
    https://github.com/sandeep9102/Fraud-Detection
    ```

## Setup and Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/Princccee/fraud_detection/tree/master
    ```
2. Navigate to the project directory:
    ```bash
    cd Fraud_detection
    ```
3. Create and activate the virtual environment:
   ```bash
    python m venv .venv
    source .venv/bin/activate
    ```
4. Install the dependencies:
   ```bash
    pip install requirements.txt
    ```
5. Build the docker container:
   ```bash
    docker-compose up --build
    ```
6. Run the container to start the server:
   ```bash
    docker run -p 8000:8000 fraud-detection-app
    ```
6. Now backend server is ready to respond

## Contributors
- Avinsh Tiwari ```https://github.com/avinash4002```
- Sandeep Kumar ```https://github.com/sandeep9102 ```
- Abhishek Jain ```https://github.com/abhishek4922 ```
- Prince Kumar  ```https://github.com/Princccee```

