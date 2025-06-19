# Object Detection Dashboard

This project provides a simple, interactive dashboard for detecting objects in images using a local Ollama vision model.

The application is built with Streamlit and consists of three main modules:
- `detector.py`: Handles the interaction with the Ollama model for object detection.
- `visualize.py`: Formats and displays the detected object data.
- `app.py`: The main Streamlit application that ties everything together.

## Prerequisites

Before you begin, ensure you have the following installed:

1.  **Python 3.8+**
2.  **Ollama**: You must have Ollama installed and running on your local machine. You can find installation instructions [here](https://ollama.com/).
3.  **A vision model**: You need a vision-capable model pulled in Ollama. This project is configured to use `llama3.2-vision` by default. You can pull it by running:
    ```bash
    ollama pull llama3.2-vision
    ```

## Installation

1.  **Navigate to the `ObjectDetection` directory:**
    ```bash
    cd VisionLanguageModels/ObjectDetection
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install the required Python packages:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Ensure the Ollama application is running.**

2.  **Add a sample image** to the `VisionLanguageModels/ObjectDetection/images` directory. You can use any jpg, png, or jpeg file.

3.  **Run the Streamlit app:**
    From inside the `MultiAgentSBC4` directory, run the following command in your terminal:
    ```bash
    streamlit run VisionLanguageModels/ObjectDetection/app.py
    ```

4.  **Open the application in your browser:**
    Streamlit will provide a local URL (usually `http://localhost:8501`). Open this URL in your web browser.

## What to Expect

When you run the application, you will see a web-based dashboard with the title "🤖 Object Detection".

1.  **File Uploader**: There will be a widget allowing you to upload an image (`.jpg`, `.png`, `.jpeg`).
2.  **Image Display**: Once you upload an image, it will be displayed on the dashboard.
3.  **Analysis**: Click the "Detect Objects" button to send the image to your local Ollama model for analysis. A spinner will show that it's working.
4.  **Results**: After a few moments, a table will appear showing the detected objects, their count, and their dominant colors.

## Accessing the Dashboard from a Remote Server (HPC)

If you are running this application on a remote server or HPC cluster and want to access the web interface from your local machine, you need to use **SSH port forwarding**.

1.  **Identify the remote hostname.**
    On the remote machine where you will run the Streamlit app (e.g., a compute node), find its hostname by running:
    ```bash
    hostname
    ```
    Take note of the output (e.g., `gpu-node-123`).

2.  **Start the Streamlit app on the remote server.**
    Navigate to the project directory and run the app. It will start on a specific port, usually 8501.
    ```bash
    streamlit run VisionLanguageModels/ObjectDetection/app.py
    ```
    Leave this process running.

3.  **Set up the SSH tunnel from your local machine.**
    Open a **new terminal** on your local computer (e.g., your Mac) and run the following command. This creates a secure tunnel. Replace `YOUR_REMOTE_HOSTNAME` with the hostname you found in step 1 and `<your_username>` with your university credentials.

    ```bash
    # Command format: ssh -L <local_port>:<remote_hostname>:<remote_port> <your_ssh_login>
    ssh -L 8501:YOUR_REMOTE_HOSTNAME:8501 <your_username>@login-phoenix.pace.gatech.edu
    ```
    This new SSH session may ask for your password or other credentials. Keep it running.

4.  **Access the app in your local browser.**
    Once the SSH tunnel is active, open your web browser on your local machine and navigate to:
    ```
    http://localhost:8501
    ```
    You should now see the Streamlit application interface.

5.  **Stopping the application.**
    To stop the Streamlit server, go back to the terminal window on the remote machine where it is running and press `Ctrl+C`.

## Student Scaffolds

This project also includes student-scaffold versions of each module (`detector_student.py`, `visualize_student.py`, `app_student.py`). These files have the same structure as the complete versions but contain `# TODO` comments in place of the core logic. They are intended as a learning exercise for students to complete the implementation themselves. To use them, students should modify `app_student.py` to import the other student modules and run it with `streamlit run VisionLanguageModels/ObjectDetection/app_student.py`. 