Speech Recognition Application with Tkinter
This project is a speech recognition application built in Python using the Tkinter library for the graphical user interface (GUI). It allows users to record prescriptions and patient notes through speech-to-text conversion, manage patient details, view the final record, and share the recorded data via email or SMS.

Features
Speech Recognition: Records prescriptions and patient notes using the microphone.
Patient Details: Saves and displays patient information (ID, name, age, gender, contact number).
Final Record: Provides a comprehensive view of patient details, prescriptions, and notes.
Sharing Options: Allows sharing recorded data via email (using Mailgun API) and SMS (using Twilio).
Requirements
Python 3.x
tkinter
speech_recognition
PIL (Python Imaging Library)
requests
twilio (if using SMS feature)
Installation
Clone the repository:

bash
Copy code
git clone https://github.com/priyanshuraj009/Med-Voice.git
cd speech-recognition-app
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Usage
Run the application:

bash
Copy code
python speech_recognition_app.py
Use the GUI buttons to record prescriptions and notes, manage patient details, view the final record, and share data via email or SMS.

Ensure you have valid credentials (like Mailgun API key, Twilio credentials) in the script if using email or SMS features.

Screenshots
Include screenshots of your application here to visually represent its functionality.

Contributing
Contributions are welcome! For major changes, please open an issue first to discuss what you would like to change.

Fork the repository.
Create your feature branch (git checkout -b feature/AmazingFeature).
Commit your changes (git commit -am 'Add some feature').
Push to the branch (git push origin feature/AmazingFeature).
Open a pull request.
