# lamigo-platform
LamiGo: Last-Mile Delivery Optimisation Platform for Sri Lanka (SDGP CS-155)

# 🚚 LamiGo - Last-Mile Delivery Optimization

LamiGo is a specialized platform designed to optimize last-mile delivery logistics in Sri Lanka. It connects a **Flutter** mobile frontend with a **FastAPI** backend to provide real-time delivery tracking and route management.

---

## 🛠 Tech Stack
* **Frontend:** Flutter (Mobile & macOS Desktop)
* **Backend:** Python 3.10+ / FastAPI
* **Dependencies:** `http` (Flutter), `uvicorn` (Python)

---

## 🚀 Getting Started

Follow these steps to set up the environment and run the project locally.

### 1. Backend Setup (FastAPI)
Open a new terminal and run:
```bash
cd backend
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install fastapi uvicorn

# Start the server
uvicorn main:app --reload

The backend will be running at: http://127.0.0.1:8000


### 2. Frontend Setup (Flutter)
Open a second terminal and run:

cd mobile-app
flutter pub get

# macOS specific setup
cd macos
pod install
cd ..

# Run the app
flutter run -d macos


Testing the Bridge
Once both are running:

Open the LamiGo app window.

Click the "Ping Backend" button.

If successful, the app will display a green success message, and the backend terminal will log a 200 OK response.

Note for macOS Users: If you get a "Connection Failed" error, ensure com.apple.security.network.client is set to true in your DebugProfile.entitlements file.

📂 Project Structure
/backend: Python FastAPI server and logic.

/mobile-app: Flutter source code for the driver application.


---

### How to push this to GitHub
Now that you have your README and a working project, follow these steps in your terminal to "save" everything to the cloud:

1.  **Check your status:**
    ```bash
    git status
    ```
    *This shows you all the files you've changed (like the README, entitlements, and main.dart).*

2.  **Stage the files:**
    ```bash
    git add .
    ```

3.  **Create the commit:**
    ```bash
    git commit -m "docs: add README and finalize full-stack bridge configuration"
    ```

4.  **Push the code:**
    ```bash
    git push origin main
    ```



**Once you push that, your teammates can simply run `git pull` and follow your instructions! Would you like me to help you create a 'requirements.txt' file for the backend next?** It's the final piece to ensure your team's Python setup is as easy as your Flutter setup.