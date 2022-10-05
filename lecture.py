import requests
from datetime import datetime, timezone
import math as m
import smtplib

MY_LAT = 14.634915
MY_LONG = -90.506882
MY_POS = (MY_LAT, MY_LONG)
PARAMS_SUNRISE = {
    "lat": MY_LAT,
    "lng": MY_LONG,
    "formatted": 0,
}
R = 6371  # Earth Radius


def get_iss_position():
    response = requests.get(url="http://api.open-notify.org/iss-now.json")
    response.raise_for_status()
    data = response.json()["iss_position"]
    longitude = float(data["longitude"])
    latitude = float(data["latitude"])
    iss_position = (latitude, longitude)
    return iss_position


def get_sunrise_time(api_params):
    response = requests.get("https://api.sunrise-sunset.org/json", params=api_params)
    response.raise_for_status()
    data = response.json()
    sunrise = int(data["results"]["sunrise"].split("T")[1].split(":")[0])
    sunset = int(data["results"]["sunset"].split("T")[1].split(":")[0])
    return sunrise, sunset


def get_time_now():
    return datetime.now(timezone.utc).hour


def radian_converter(degrees):
    return degrees * m.pi / 180


# If the ISS is close to my current position
def calculate_distance(tuple_iss, tuple_my_pos):
    lat_1, lon_1 = tuple_my_pos
    lat_2, lon_2 = tuple_iss
    # convert all degrees to radians
    lat_1 = radian_converter(lat_1)
    lat_2 = radian_converter(lat_2)
    lon_1 = radian_converter(lon_1)
    lon_2 = radian_converter(lon_2)
    # use the haversine distance formula
    # d = 2R⋅sin⁻¹(√[sin²((θ₂ - θ₁)/2) + cosθ₁⋅cosθ₂⋅sin²((φ₂ - φ₁)/2)])
    d = 2*R*m.asin(((m.sin((lat_2 - lat_1)/2))**2 + m.cos(lat_1)*m.cos(lat_2)*(m.sin((lon_2 - lon_1)/2)**2))**(1/2))
    return d


def send_email():
    MY_EMAIL = "vicmanuelr@gmail.com"
    MY_PASSWORD = "jktkofxgfysnngyu"
    with smtplib.SMTP("smtp.gmail.com", port=587) as msg:
        msg.starttls()
        msg.login(user=MY_EMAIL, password=MY_PASSWORD)
        msg.sendmail(
            from_addr=MY_EMAIL,
            to_addrs=MY_EMAIL,
            msg=f"Subject:LOOK UP!\n\nThe Iss is currently in the sky",
        )


if calculate_distance(get_iss_position(), MY_POS) < 500:
    sunrise_hour, sunset_hour = get_sunrise_time(PARAMS_SUNRISE)
    time_now_hour = get_time_now()
    print(time_now_hour)
    print(sunrise_hour, sunset_hour)
    if time_now_hour > sunset_hour or time_now_hour < sunrise_hour:
        send_email()
        print("wrong calculation of time")

