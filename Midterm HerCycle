import time
import RPi.GPIO as GPIO
import speech_recognition as sr

# ---------- Pin setup (BOARD numbering) ----------
LED_PIN = 12     # physical pin 12
TRIG = 16    # physical pin 16
ECHO = 15    # physical pin 15

# ---------- Behavior settings ----------
DIST_THRESHOLD_CM = 25.0     # only listen if something is closer than this
COOLDOWN_SEC = 1.0           # pause after a successful detection to avoid repeats

# Menstrual phase keyword map
PHASE_KEYWORDS = {
    "ovulation": ["swollen", "happy", "energized"],
    "menstruation": ["tired", "cramp", "hungry", "irritable"],
    "luteal": ["anxious", "moody", "bloating"],
    "follicular": ["focused", "motivated", "clear"],
}

PHASE_TO_BLINKS = {
    "ovulation": 1,
    "menstruation": 2,
    "luteal": 3,
    "follicular": 4,
}

# ---------- GPIO helpers ----------
def setup_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setwarnings(False)

    GPIO.setup(LED_PIN, GPIO.OUT)
    GPIO.output(LED_PIN, GPIO.LOW)

    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)

    # Ensure trig is low initially
    GPIO.output(TRIG, GPIO.LOW)
    time.sleep(0.2)

def cleanup_gpio():
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()

def blink_n_times(n: int, on_time=0.25, off_time=0.25):
    for _ in range(n):
        GPIO.output(LED_PIN, GPIO.HIGH)
        time.sleep(on_time)
        GPIO.output(LED_PIN, GPIO.LOW)
        time.sleep(off_time)

# ---------- Ultrasonic distance ----------
def distance():
    GPIO.output(TRIG, 0)
    time.sleep(0.000002)
    GPIO.output(TRIG, 1)
    time.sleep(0.00001)
    GPIO.output(TRIG, 0)

    time1=0
    time2=0
    
    while GPIO.input(ECHO) == 0:
        time1 = time.time()
        
    while GPIO.input(ECHO) == 1:
        time2 = time.time()

    during = time2
    dist = during * 34000 / 2 #Returns distance in cm
    return dist

# ---------- Speech + classification ----------
def classify_phase():
    t = text.lower()
    for phase, words in PHASE_KEYWORDS.items():
        for w in words:
            if w in t:
                return phase
    return None

def listen_for_keywords():
    """
    Captures speech and returns recognized text, or None if recognition failed.
    Requires internet for Google recognition.
    """
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        r.adjust_for_ambient_noise(source, duration=0.6)

        print("Listening (say your symptom keywords)...")
        # phrase_time_limit prevents it from listening forever
        audio = r.listen(source, timeout=4, phrase_time_limit=4)

    print("Recognizing (Google Speech)...")
    try:
        return r.recognize_google(audio)
    except sr.UnknownValueError:
        print("Could not understand audio.")
        return None
    except sr.RequestError as e:
        print(f"Google Speech request failed: {e}")
        return None

# ---------- Main loop ----------
def main():
    setup_gpio()
    r = sr.Recognizer()

    print("Running: ultrasonic-gated speech recognition + LED patterns")
    print(f"Distance threshold: {DIST_THRESHOLD_CM} cm")

    while True:
        dist = distance()
        if dist is None:
            # Sensor timed out; just continue
            time.sleep(0.1)
            continue

        # Print distance occasionally (optional)
        # print(f"Distance: {dist:.1f} cm")

        if dist <= DIST_THRESHOLD_CM:
            print(f"Object detected at {dist:.1f} cm -> start voice capture")

            text = listen_for_keywords()
            if text:
                print(f"You said: {text}")
                phase = classify_phase(text)

                if phase:
                    blinks = PHASE_TO_BLINKS[phase]
                    print(f"Matched phase: {phase} -> blink {blinks} time(s)")
                    blink_n_times(blinks)
                    time.sleep(COOLDOWN_SEC)
                else:
                    print("No keyword match found. Try again.")
            else:
                print("No valid text recognized. Try again.")

        time.sleep(0.1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting...")
    finally:
        cleanup_gpio()
