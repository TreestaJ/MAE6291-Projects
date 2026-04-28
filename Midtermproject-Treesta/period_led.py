import RPi.GPIO as GPIO
import time
import speech_recognition as sr

# ---------------- GPIO ----------------
LED = 12

def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)
    GPIO.setup(LED, GPIO.OUT)
    GPIO.output(LED, False)

def destroy():
    GPIO.output(LED, False)
    GPIO.cleanup()

# ---------------- LED BLINK ----------------
def blink_n(n):
    for i in range(n):
        GPIO.output(LED, True)
        time.sleep(0.4)
        GPIO.output(LED, False)
        time.sleep(0.4)

# ---------------- KEYWORD DICTIONARY ----------------
PHASE_KEYWORDS = {
    "ovulation": ["swollen","happy","energized"],
    "menstruation": ["tired","cramp","hungry","irritable"],
    "luteal": ["anxious","moody","bloating"],
    "follicular": ["focused","motivated","clear"]
}

PHASE_BLINKS = {
    "ovulation": 1,
    "menstruation": 2,
    "luteal": 3,
    "follicular": 4
}

# ---------------- SPEECH ----------------
def listen_and_classify(recognizer, mic):

    with mic as source:
        print("Speak a symptom word...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source)

    try:
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        text = text.lower()

        for phase, words in PHASE_KEYWORDS.items():
            for word in words:
                if word in text:
                    return phase

    except:
        print("Could not understand speech")

    return None

# ---------------- MAIN ----------------
def main():

    setup()

    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("Press ENTER to start voice recognition.")
    print("Say a keyword when prompted.")

    while True:

        input("\nPress ENTER to speak...")

        phase = listen_and_classify(recognizer, mic)

        if phase:
            print("Detected phase:", phase)
            blink_n(PHASE_BLINKS[phase])
        else:
            print("No keyword match.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        destroy()
