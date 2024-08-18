import tkinter as tk
from tkinter import simpledialog, ttk
import threading
import time
import speech_recognition as sr
from PIL import Image, ImageTk
import requests
#from twilio.rest import Client
import queue
import json


# Use a dedicated email account instead of a personal account
sender_email = "visiontech@candle.engineer"
sender_password = "*****"
mailgun_api_key = "**************"  # ]Mailgun API key
mailgun_domain = "candle.engineer"  # ]Mailgun domain


#uncomment and replace it with ur credentials
'''# Twilio credentials
account_sid = '**************'
auth_token = '*********'
twilio_phone_number = '*******' '''

# Define patient information variables in the global scope
patient_id = ""
patient_name = ""
patient_age = ""
patient_gender = ""
patient_contact = ""

# Create a queue for communication between threads
transcript_queue = queue.Queue()
prescriptions_list = []  # To store all recorded prescriptions
notes_list = []  # To store all recorded notes

def listen_thread(mode):
    global listening
    r = sr.Recognizer()
    with sr.Microphone() as source:
        while listening:
            audio_text = r.listen(source)
            try:
                transcript = r.recognize_google(audio_text)
                transcript_queue.put((mode, transcript))
            except Exception as e:
                transcript_queue.put((mode, "Sorry, I didn't get that"))

            # Add a delay to prevent the thread from consuming too much CPU
            time.sleep(1)

def update_transcript():
    while not transcript_queue.empty():
        mode, transcript = transcript_queue.get()
        if transcript != "Stopped listening":
            if "Sorry, I didn't get that" not in transcript:
                transcript_display.insert(tk.END, f"[{mode.capitalize()}]: {transcript}\n")
                if mode.lower() == "prescription":
                    prescriptions_list.append(transcript + "\n")
                elif mode.lower() == "note":
                    notes_list.append(transcript + "\n")

    # Schedule the next update
    root.after(100, update_transcript)

def start_listen(mode):
    global listening, progress_thread
    listening = True

    # Start a new thread to handle speech recognition
    progress_thread = threading.Thread(target=listen_thread, args=(mode,))
    progress_thread.start()

    # Update the GUI to show the progress bar
    progress_bar.start()

def stop_listen():
    global listening, progress_thread
    listening = False

    # Give some time for the listen_thread to finish
    time.sleep(1)

    # Wait for the progress thread to finish
    if progress_thread:
        progress_thread.join()

    progress_bar.stop()

def open_patient_detail():
    # Your existing code for opening the patient details menu
    global patient_id, patient_name, patient_age, patient_gender, patient_contact
    transcript_window = tk.Toplevel(root)
    transcript_window.geometry('400x300')
    transcript_window.title('Patient Details')

    patient_id_var = tk.StringVar()
    patient_name_var = tk.StringVar()
    patient_age_var = tk.StringVar()
    patient_gender_var = tk.StringVar()
    patient_contact_var = tk.StringVar()

    tk.Label(transcript_window, text='Patient ID:').grid(row=0, column=0)
    id_entry = tk.Entry(transcript_window, textvariable=patient_id_var)
    id_entry.grid(row=0, column=1)

    tk.Label(transcript_window, text='Name:').grid(row=1, column=0)
    name_entry = tk.Entry(transcript_window, textvariable=patient_name_var)
    name_entry.grid(row=1, column=1)

    tk.Label(transcript_window, text='Age:').grid(row=2, column=0)
    age_entry = tk.Entry(transcript_window, textvariable=patient_age_var)
    age_entry.grid(row=2, column=1)

    tk.Label(transcript_window, text='Gender:').grid(row=3, column=0)
    gender_entry = tk.Entry(transcript_window, textvariable=patient_gender_var)
    gender_entry.grid(row=3, column=1)

    tk.Label(transcript_window, text='Contact Number:').grid(row=4, column=0)
    contact_entry = tk.Entry(transcript_window, textvariable=patient_contact_var)
    contact_entry.grid(row=4, column=1)

    tk.Button(transcript_window, text='Save', command=lambda: [save_patient_info(
        patient_id_var, patient_name_var, patient_age_var, patient_gender_var, patient_contact_var), transcript_window.destroy()]).grid(
        row=5, column=0, columnspan=2)

def save_patient_info(id_var, name_var, age_var, gender_var, contact_var):
    global patient_id, patient_name, patient_age, patient_gender, patient_contact
    patient_id = id_var.get()
    patient_name = name_var.get()
    patient_age = age_var.get()
    patient_gender = gender_var.get()
    patient_contact = contact_var.get()

def view_transcript():
    # Your existing code for viewing the transcript
    transcript_window = tk.Toplevel(root)
    transcript_window.geometry('600x400')  # Increased column width
    transcript_window.title('Final Record')

    tk.Label(transcript_window, text='Patient ID:').grid(row=0, column=0)
    tk.Label(transcript_window, text=patient_id).grid(row=0, column=1)

    tk.Label(transcript_window, text='Patient Name:').grid(row=1, column=0)
    tk.Label(transcript_window, text=patient_name).grid(row=1, column=1)

    tk.Label(transcript_window, text='Patient Age:').grid(row=2, column=0)
    tk.Label(transcript_window, text=patient_age).grid(row=2, column=1)

    tk.Label(transcript_window, text='Patient Gender:').grid(row=3, column=0)
    tk.Label(transcript_window, text=patient_gender).grid(row=3, column=1)

    tk.Label(transcript_window, text='Patient Contact Number:').grid(
        row=4, column=0)
    tk.Label(transcript_window, text=patient_contact).grid(
        row=4, column=1)

    # Separate blocks for prescription and notes
    tk.Label(transcript_window, text='Prescription:').grid(row=5, column=0)
    tk.Label(transcript_window, text=''.join(prescriptions_list)).grid(row=5, column=1)

    tk.Label(transcript_window, text='Notes:').grid(row=6, column=0)
    tk.Label(transcript_window, text=''.join(notes_list)).grid(row=6, column=1)
###To Store data
def save_data_to_json():
    global patient_id, patient_name, patient_age, patient_gender, patient_contact
    global prescriptions_list, notes_list

    try:
        # Try to read existing data from the file
        with open("medical_record.json", "r") as json_file:
            existing_data = json.load(json_file)
    except FileNotFoundError:
        # If the file doesn't exist, create an empty dictionary
        existing_data = {}

    # Use patient_id as the primary key
    existing_data[patient_id] = {
        "patient_name": patient_name,
        "patient_age": patient_age,
        "patient_gender": patient_gender,
        "patient_contact": patient_contact,
        "prescriptions": prescriptions_list,
        "notes": notes_list
    }

    try:
        # Write the updated data back to the file
        with open("medical_record.json", "w") as json_file:
            json.dump(existing_data, json_file, indent=4)
        result.set("Data Saved")
    except Exception as e:
        result.set(f"Failed to save data. Error: {e}")
##
def send_email():
    subject = "Speech Recognition Transcript"
    body = f"Patient ID: {patient_id}\n" \
           f"Patient Name: {patient_name}\n" \
           f"Patient Age: {patient_age}\n" \
           f"Patient Gender: {patient_gender}\n" \
           f"Patient Contact Number: {patient_contact}\n" \
           f"Prescription: {''.join(prescriptions_list)}\n" \
           f"Notes: {''.join(notes_list)}"

    recipient_email = simpledialog.askstring(
        "Email", "Enter recipient's email address:")
    if recipient_email:
        # Mailgun API URL
        mailgun_url = f"https://api.mailgun.net/v3/{mailgun_domain}/messages"

        # Data for the Mailgun API call
        data = {
            "from": sender_email,
            "to": recipient_email,
            "subject": subject,
            "text": body
        }

        # Authentication for the Mailgun API call
        auth = ("api", mailgun_api_key)

        try:
            # Make the Mailgun API call
            response = requests.post(mailgun_url, auth=auth, data=data)
            response.raise_for_status()  # Raise an error for HTTP errors

            result.set("Email sent successfully!")
        except requests.exceptions.RequestException as e:
            print(f"Error sending email: {e}")
            result.set("Failed to send email. Check console for details.")

def send_sms():
    phone_number = simpledialog.askstring("Phone Number", "Enter recipient's phone number:")
    if phone_number:
        client = Client(account_sid, auth_token)
        message_body = f"Patient ID: {patient_id}\n" \
                       f"Patient Name: {patient_name}\n" \
                       f"Patient Age: {patient_age}\n" \
                       f"Patient Gender: {patient_gender}\n" \
                       f"Patient Contact Number: {patient_contact}\n" \
                       f"Prescription: {''.join(prescriptions_list)}\n" \
                       f"Notes: {''.join(notes_list)}"

        try:
            message = client.messages.create(
                from_=twilio_phone_number,
                body=message_body,
                to=phone_number
            )
            result.set(f"SMS sent successfully! SID: {message.sid}")
        except Exception as e:
            result.set(f"Failed to send SMS. Error: {e}")
    else:
        result.set("Invalid phone number.")

def share():
    save_data_to_json()
    share_window = tk.Toplevel(root)
    share_window.geometry('200x100')
    share_window.title('Share Options')

    mail_button = tk.Button(
        share_window, text="Mail", fg="white",
        bg="#3498DB", command=send_email)
    mail_button.pack(pady=10)

    sms_button = tk.Button(
        share_window, text="SMS", fg="white",
        bg="#E74C3C", command=send_sms)
    sms_button.pack(pady=10)

# Create the main GUI window
root = tk.Tk()
root.geometry('1300x800')
root.title('Speech Recognition')
root.configure(bg='#FDFEFE')  # Light Grey background color

# Create labels and buttons
listening = False
progress_thread = None
custom_font = ("Helvetica", 14)

# Place all the buttons at the top horizontally with a 50px margin
button_frame = tk.Frame(root, bg='#FDFEFE')  # Light Grey background color
button_frame.pack(pady=20)

# Use a consistent width for the buttons
button_width = 18

start_prescription_button = tk.Button(
    button_frame, text="Record Prescription", fg="white",
    bg="#28B463", command=lambda: start_listen("prescription"), font=custom_font, width=button_width)
start_prescription_button.pack(side=tk.LEFT, padx=10)

start_notes_button = tk.Button(
    button_frame, text="Record Patient Note", fg="white",
    bg="#3498DB", command=lambda: start_listen("note"), font=custom_font, width=button_width)
start_notes_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(
    button_frame, text="Stop Listening", fg="white",
    bg="#E74C3C", command=stop_listen, font=custom_font, width=button_width)
stop_button.pack(side=tk.LEFT, padx=10)

patient_detail_button = tk.Button(
    button_frame, text="Patient Detail", fg="white",
    bg="#3498DB", command=open_patient_detail, font=custom_font, width=button_width)
patient_detail_button.pack(side=tk.LEFT, padx=10)

final_record_button = tk.Button(
    button_frame, text="Final Record", fg="white",
    bg="#8E44AD", command=view_transcript, font=custom_font, width=button_width)
final_record_button.pack(side=tk.LEFT, padx=10)

share_button = tk.Button(
    button_frame, text="Share", fg="white",
    bg="#F39C12", command=share, font=custom_font, width=button_width)
share_button.pack(side=tk.LEFT, padx=10)

# Create a text box for live speech-to-text output
transcript_display = tk.Text(
    root, height=10, width=50, font=custom_font, bg='#ECF0F1')  # Light Grey background color
transcript_display.pack(pady=20)



# Progress bar for indicating speech recognition progress
progress_bar = ttk.Progressbar(root, orient='horizontal', length=300, mode='indeterminate')
progress_bar.pack(pady=20)

# Result label
result = tk.StringVar()
label_result = tk.Label(root, textvariable=result, bg='#ECF0F1', fg='#2C3E50', font=custom_font)  # Dark Grey text color
label_result.pack(pady=20)

# Start updating the transcript when the GUI starts
root.after(100, update_transcript)

root.mainloop()