from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
import threading
import speech_recognition as sr
import pyttsx3
from datetime import datetime

predata_path = "./predata.txt"
collect_data_path = "./collect_data.txt"

class VoiceAssistantApp(App):
    def __init__(self):
        super(VoiceAssistantApp, self).__init__()
        self.responses = self.load_responses()

    def load_responses(self):
        responses = {}
        with open(predata_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                key, value = line.strip().split(" : ")
                responses[key.lower()] = value
        return responses

    def search_collect_data(self, key):
        with open(collect_data_path, "r", encoding="utf-8") as file:
            lines = file.readlines()
            for line in lines:
                try:
                    k, v = line.strip().split(" : ")
                    if k.lower() == key.lower():
                        return v
                except ValueError:
                    pass  # Handle the case where a line does not have the expected format
        return None  # Return None if the key is not found in collect_data.txt

    def build(self):
        layout = BoxLayout(orientation='vertical', spacing=10)

        self.label = Label(text="Say 'start' to begin")
        self.listening_enabled = False
        self.first_time = True

        layout.add_widget(self.label)

        return layout

    def on_start(self):
        self.start_listening_thread()

    def start_listening_thread(self):
        # Start listening thread
        listening_thread = threading.Thread(target=self.listen_continuously)
        listening_thread.start()

    def listen_continuously(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Say 'start' to begin:")
            recognizer.adjust_for_ambient_noise(source)

            while True:
                audio = recognizer.listen(source)
                try:
                    command = recognizer.recognize_google(audio).lower()
                    print("You said:", command)

                    if command == 'start':
                        self.listening_enabled = True
                        self.label.text = "Listening..."

                        # If it's the first time after 'start', wish the user
                        if self.first_time:
                            self.wish_user()
                            self.first_time = False
                    elif command == 'stop listening':
                        self.listening_enabled = False
                        self.label.text = "Listening stopped. Say 'start' to resume."

                    if self.listening_enabled:
                        response = self.responses.get(command)
                        if response is None:
                            # Key not found in predata.txt, search in collect_data.txt
                            response = self.search_collect_data(command)

                        if response:
                            self.label.text = f"You said: {command}\n{response}"
                            self.text_to_speech(response)
                        else:
                            self.label.text = f"You said: {command}"

                            # Add text-to-speech functionality using pyttsx3
                            self.text_to_speech(f"You said: {command}")

                            # You can add more logic here based on the recognized command

                except sr.UnknownValueError:
                    print("Sorry, could not understand audio.")
                    self.label.text = "Sorry, could not understand audio."

    def text_to_speech(self, text):
        engine = pyttsx3.init()
        engine.say(text)
        engine.runAndWait()

    def wish_user(self):
        current_time = datetime.now().time()
        current_date = datetime.now().date()

        if current_time < datetime.strptime('12:00:00', '%H:%M:%S').time():
            greeting = "Good Morning!"
        elif current_time < datetime.strptime('18:00:00', '%H:%M:%S').time():
            greeting = "Good Afternoon!"
        else:
            greeting = "Good Evening!"

        full_message = f"{greeting} It's {current_time.strftime('%I:%M %p')} on {current_date.strftime('%A, %B %d, %Y')}."
        self.label.text = full_message
        self.text_to_speech(full_message)

if __name__ == '__main__':
    VoiceAssistantApp().run()
