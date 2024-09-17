# Quran Audio Transcription API with Flask

This repository contains a Flask-based API for processing audio files, performing speech-to-text transcription, comparing it with the original text, and saving the results in a database.

## Table of Contents

- [Requirements](#requirements)
- [Setup](#setup)
  - [1. Create Virtual Environment](#1-create-virtual-environment)
  - [2. Install Dependencies](#2-install-dependencies)
  - [3. Configure Environment Variables](#3-configure-environment-variables)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Database Setup](#database-setup)

## Requirements

- Python 3.8+
- Flask
- MariaDB or MySQL
- Other dependencies are listed in `requirements.txt`

## Setup

### 1. Create Virtual Environment

Before running the application, it is recommended to create a virtual environment to isolate project dependencies.

1. **Create a virtual environment**:
    ```bash
    python -m venv venv
    ```

2. **Activate the virtual environment**:

    - On macOS/Linux:
      ```bash
      source venv/bin/activate
      ```

    - On Windows:
      ```bash
      venv\Scripts\activate
      ```

### 2. Install Dependencies

After activating the virtual environment, install all required dependencies using `requirements.txt`:

```bash
pip install -r requirements.txt
```
### 3. Configure Environment Variables
Create a `.env` file in the root of your project and define the necessary environment variables. Below is an example of the required variables:

```bash
# Database configuration
DB_HOST=localhost
DB_DATABASE=your_database
DB_USER=your_username
DB_PASSWORD=your_password

# Flask configuration
FLASK_DEBUG=True

# Audio file storage directory
AUDIO_FOLDER=./audio_files
```
### 4. Running the Application
Once all dependencies are installed and environment variables are configured, you can run the Flask application:
```bash
python app.py
```
