import requests
from bs4 import BeautifulSoup
import re
from prometheus_client import Gauge, start_http_server
import time
from dataclasses import dataclass

@dataclass
class Bike:
    model: str
    color: str
    shifting: str
    gearing: str
    link: str

WEEKS_REGEX = re.compile("Lieferzeit\s(\d*)\sWochen")
DAYS_REGEX = re.compile("Lieferzeit\s\d*\sbis\s(\d*)\sTage")
EMAIL_TEXT = "E-Mail bei Verfügbarkeit"

def delivery_text_to_days(text):
    mm = WEEKS_REGEX.match(text)
    if mm:
        weeks = int(mm.group(1))
        return weeks * 7
    mm = WEEKS_REGEX.match(text)
    if mm:
        return int(mm.group(1))
    

    return -1
        
BIKE_AVAIL = Gauge("bike_avail", "Avail of Bikes in days", ['model', 'size', 'color', 'shifting', 'gearing'])
start_http_server(3333)

models = [
        Bike("grx800", "green", "di2", "1x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-di2-1x11-2692730?product_shape=evil+pepper+green"),
        Bike("grx800", "purple", "di2", "1x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-di2-1x11-2692730?product_shape=deepest+purple"),
        Bike("grx800", "green", "mech", "1x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-1x11-2692728?product_shape=evil+pepper+green"),
        Bike("grx800", "purple", "mech", "1x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-1x11-2692728?product_shape=deepest+purple"),
        Bike("grx800", "green", "di2", "2x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-di2-2692731?product_shape=evil+pepper+green"),
        Bike("grx800", "purple", "di2", "2x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-di2-2692731?product_shape=deepest+purple"),
        Bike("grx800", "green", "mech", "2x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-2692729?product_shape=evil+pepper+green"),
        Bike("grx800", "purple", "mech", "2x11", "https://www.rosebikes.de/rose-backroad-grx-rx810-2692729?product_shape=deepest+purple")
        ]

while (1):
    for bike in models:
        print(bike.link)
        r = requests.get(bike.link)

        soup = BeautifulSoup(r.text, 'html.parser')

        size_links = soup.select(".select-size-link")
        for link in size_links:
            size = link.select(".select-size-link__key")[0].text
            if EMAIL_TEXT in str(link):
                delivery_days = -1
            else:
                delivery_text = link.select(".select-size-link__availability")[0].attrs['title']
                delivery_days = delivery_text_to_days(delivery_text)
            BIKE_AVAIL.labels(model=bike.model, size=size, color=bike.color, shifting=bike.shifting, gearing=bike.gearing).set(delivery_days)
    time.sleep(60 * 5)
