from flask import Flask, render_template
from sense_hat import SenseHat
import paho.mqtt.client as mqtt
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from collections import defaultdict
import os

app = Flask(__name__)
sense = SenseHat()

EXPORT_FOLDER = "apple_health_export"
EXPORT_XML = os.path.join(EXPORT_FOLDER, "export.xml")
STEP_GOAL = 10000

def show(msg):
    print(msg)
    try:
        sense.show_message(msg, scroll_speed=0.05)
    except Exception as e:
        print("Sense HAT error:", e)

def parse_date(date_str):
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S %z")

def classify_steps(avg):
    if avg < STEP_GOAL:
   	 return "LOW"
    elif avg == STEP_GOAL:
        return "GOAL"
    else:
        return "GREAT"

def recommendation(avg):
    if avg < STEP_GOAL:
        diff = STEP_GOAL - int(avg)
        return f"You are below your 10,000-step goal. Try increasing your daily steps by about {diff:,}."
    elif avg == STEP_GOAL:
        return "You met your 10,000-step goal exactly. Keep up the consistency."
    else:
        return "You exceeded your 10,000-step goal. Great job staying active this week."

def workout_tip(status):
    if status == "LOW":
        return "Workout recommendation: Try a 30-minute walk, incline treadmill walk, or light cardio plus 10 minutes of stretching."
    elif status == "GOAL":
        return "Workout recommendation: Maintain consistency with a brisk walk, stairmaster session, or a moderate lower-body workout."
    else:
        return "Workout recommendation: You had a very active week. Focus on consistency, hydration, and one recovery-oriented workout."

def parse_health():
    steps = defaultdict(float)

    if not os.path.exists(EXPORT_XML):
        raise FileNotFoundError(f"Could not find {EXPORT_XML}")

    context = ET.iterparse(EXPORT_XML, events=("end",))
    latest = None

    for event, elem in context:
        if elem.tag == "Record":
            if elem.attrib.get("type") == "HKQuantityTypeIdentifierStepCount":
                try:
                    dt = parse_date(elem.attrib["startDate"])
                    day = dt.date()
                    val = float(elem.attrib["value"])
                    steps[day] += val
                    if latest is None or day > latest:
                        latest = day
                except Exception:
                    pass
        elem.clear()

    if latest is None:
        raise ValueError("No step data found in export.xml")

    last_week = [latest - timedelta(days=i) for i in range(6, -1, -1)]
    total = 0
    daily_data = []

    for d in last_week:
        day_steps = int(steps.get(d, 0))
        total += day_steps
        daily_data.append({"date": str(d), "steps": day_steps})

    avg = total / 7
    status = classify_steps(avg)

    return {
        "average_steps": int(avg),
        "status": status,
        "recommendation": recommendation(avg),
        "workout_tip": workout_tip(status),
        "daily_data": daily_data,
        "latest_date": str(latest)
    }
def send_mqtt(data):
    client = mqtt.Client()
    client.connect("broker.hivemq.com", 1883, 60)

    message = f"Steps: {data['average_steps']}, Status: {data['status']}"
    client.publish("treesta/pulsepilot", message)

    client.disconnect()
@app.route("/")
def dashboard():
    data = parse_health()
    show(data["status"])
    send_mqtt(data)
    return render_template("index.html", data=data)

if __name__ == "__main__":
    show("START")
    app.run(host="0.0.0.0", port=5000, debug=True)
