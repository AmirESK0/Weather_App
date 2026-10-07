import sys
import os
from dotenv import load_dotenv
import requests
from PyQt5.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout)
from PyQt5.QtCore import Qt
from requests import HTTPError
from PyQt5.QtGui import QIcon
load_dotenv()


class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.name = QLabel("❤️AMIR❤️", self)
        self.city_label = QLabel("Stadt eingeben: ", self)
        self.city_input = QLineEdit(self)
        self.f_Button = QPushButton("F°", self)
        self.c_Button = QPushButton("C°", self)
        self.get_weather_button = QPushButton("Wetter anzeigen", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.current_temp_k = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Wetter App")
        self.setGeometry(1150, 100, 500, 600)
        self.resize(650, 900)
        self.setWindowIcon(QIcon("logo.ico"))

        vbox = QVBoxLayout()
        hbox = QHBoxLayout()

        vbox.addWidget(self.name)
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)

        hbox.addWidget(self.c_Button)
        hbox.addWidget(self.f_Button)

        vbox.addLayout(hbox)

        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)

        self.setLayout(vbox)

        self.name.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.name.setObjectName("name")
        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.f_Button.setObjectName("F")
        self.c_Button.setObjectName("C")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
            QLabel, QPushButton{
                font-family: calibri;
            }
            QLabel#name{
                font-size: 35px;
                font-weight: bold;
                font-family: Segoe UI Emoji;
            }
            QLabel#city_label{
                font-size: 45px;
                font-style: italic;
            }
            QLineEdit#city_input{
                font-size: 35px;
            }
            QPushButton#F{
                font-size: 25px;
            }
            QPushButton#C{
                font-size: 25px;
            }
            QPushButton#get_weather_button{
                font-size: 30px;
                font-weight: bold;
            }
            QLabel#temperature_label{
                font-size: 75px;
            }
            QLabel#emoji_label{
                font-size: 90px;
                font-family: Segoe UI Emoji;
            }
            QLabel#description_label{
                font-size: 45px;
            }
        """)

        self.get_weather_button.clicked.connect(self.get_weather)
        self.c_Button.clicked.connect(self.show_celsius)
        self.f_Button.clicked.connect(self.show_fahrenheit)

    def get_weather(self):

        api_key = os.getenv("OPENWEATHER_API_KEY")
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            match response.status_code:
                case 400:
                    self.display_error("Schlechte Anfrage\nBitte überprüfe deine Eingabe.")
                case 401:
                    self.display_error("Nicht autorisiert\nAuthentifizierung erforderlich oder fehlgeschlagen.")
                case 403:
                    self.display_error("Verboten\nDu hast keine Berechtigung, auf diese Ressource zuzugreifen.")
                case 404:
                    self.display_error("Nicht gefunden\nDie angeforderte Ressource konnte nicht gefunden werden.")
                case 500:
                    self.display_error("Interner Serverfehler\nEtwas ist auf dem Server schiefgelaufen.")
                case 502:
                    self.display_error("Bad Gateway\nEs wurde eine ungültige Antwort vom Upstream-Server empfangen.")
                case 503:
                    self.display_error(
                        "Service nicht verfügbar\nDer Server ist momentan nicht verfügbar.\nVersuche es später noch einmal.")
                case 504:
                    self.display_error(
                        "Gateway Timeout\nDer Server hat keine Antwort in der vorgegebenen Zeit erhalten.")
                case _:
                    self.display_error(f"Unbehandelter HTTP-Fehler: {http_error}")

        except requests.exceptions.ConnectionError:
            self.display_error("Verbindungsfehler\nÜberprüfe deine Internetverbindung oder den Serverstatus.")
        except requests.exceptions.Timeout:
            self.display_error("Zeitüberschreitung\nDie Anfrage hat zu lange gedauert. Versuche es später noch einmal.")
        except requests.exceptions.TooManyRedirects:
            self.display_error("Zu viele Weiterleitungen\nDie URL führt zu einer Endlosschleife von Weiterleitungen.")
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Fehler bei der Anfrage\n{req_error}")

    def display_error(self, massage):
        self.temperature_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        self.temperature_label.setText(massage)
        self.emoji_label.clear()
        self.description_label.clear()

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px; ")
        temperature_k = data["main"]["temp"]
        temperature_c = temperature_k - 273.15
        temperature_f = (temperature_k * 9 / 5) - 459.67
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["id"]
        self.current_temp_k = temperature_k

        self.temperature_label.setText(f"{temperature_c:.0f}°C")
        self.c_Button.setStyleSheet("font-weight: bold;")
        self.emoji_label.setText(self.get_weather_emoji(weather_id))
        self.description_label.setText(self.get_weather_description(weather_description))

    def show_celsius(self):
        if self.current_temp_k is not None:
            temp_c = self.current_temp_k - 273.15
            self.temperature_label.setText(f"{temp_c:.0f}°C")
            self.c_Button.setStyleSheet("font-weight: bold;")
            self.f_Button.setStyleSheet("font-weight: normal;")

    def show_fahrenheit(self):
        if self.current_temp_k is not None:
            temp_f = (self.current_temp_k * 9 / 5) - 459.67
            self.temperature_label.setText(f"{temp_f:.0f}°F")
            self.f_Button.setStyleSheet("font-weight: bold;")
            self.c_Button.setStyleSheet("font-weight: normal;")

    @staticmethod
    def get_weather_emoji(weather_id):

        if 200 <= weather_id <= 202:
            return "⛈️"  # Thunderstorm with rain
        elif 210 <= weather_id <= 221:
            return "🌩️"  # Light to severe thunderstorm
        elif 230 <= weather_id <= 232:
            return "⛈️"  # Thunderstorm with drizzle
        elif 300 <= weather_id <= 321:
            return "🌦️"  # Drizzle
        elif 500 <= weather_id <= 504:
            return "🌧️"  # Light to heavy rain
        elif weather_id == 511:
            return "🌨️"  # Freezing rain
        elif 520 <= weather_id <= 531:
            return "🌧️"  # Shower rain
        elif 600 <= weather_id <= 602:
            return "❄️"  # Light to heavy snow
        elif 611 <= weather_id <= 622:
            return "🌨️"  # Sleet or snow showers
        elif 701 <= weather_id <= 711:
            return "🌫️"  # Mist, smoke
        elif weather_id == 721:
            return "🌁"  # Haze
        elif weather_id == 731 or weather_id == 761:
            return "🌬️"  # Dust/sand
        elif weather_id == 741:
            return "🌫️"  # Fog
        elif weather_id == 751:
            return "🌬️"  # Sand
        elif weather_id == 762:
            return "🌋"  # Volcanic ash
        elif weather_id == 771:
            return "💨"  # Squalls
        elif weather_id == 781:
            return "🌪️"  # Tornado
        elif weather_id == 800:
            return "☀️"  # Clear
        elif weather_id == 801:
            return "🌤️"  # Few clouds
        elif weather_id == 802:
            return "⛅"  # Scattered clouds
        elif weather_id == 803:
            return "🌥️"  # Broken clouds
        elif weather_id == 804:
            return "☁️"  # Overcast clouds
        else:
            return "❔"  # Unknown weather

    @staticmethod
    def get_weather_description(weather_description):

        if weather_description == 200:
            return "Gewitter mit leichtem Regen"
        elif weather_description == 201:
            return "Gewitter mit Regen"
        elif weather_description == 202:
            return "Starkes Gewitter mit Regen"
        elif weather_description == 210:
            return "Leichtes Gewitter"
        elif weather_description == 211:
            return "Gewitter"
        elif weather_description == 212:
            return "Starkes Gewitter"
        elif weather_description == 221:
            return "Unregelmässiges Gewitter"
        elif weather_description == 230:
            return "Gewitter mit leichtem Nieselregen"
        elif weather_description == 231:
            return "Gewitter mit Nieselregen"
        elif weather_description == 232:
            return "Gewitter mit starkem Nieselregen"
        elif weather_description == 300:
            return "Leichter Nieselregen"
        elif weather_description == 301:
            return "Nieselregen"
        elif weather_description == 302:
            return "Starker Nieselregen"
        elif weather_description == 310:
            return "Leichter Nieselregen mit Regen"
        elif weather_description == 311:
            return "Nieselregen mit Regen"
        elif weather_description == 312:
            return "Starker Nieselregen mit Regen"
        elif weather_description == 313:
            return "Schauer mit Nieselregen"
        elif weather_description == 314:
            return "Starke Schauer mit Nieselregen"
        elif weather_description == 321:
            return "Nieselschauer"
        elif weather_description == 500:
            return "Leichter Regen"
        elif weather_description == 501:
            return "Mäßiger Regen"
        elif weather_description == 502:
            return "Starker Regen"
        elif weather_description == 503:
            return "Sehr starker Regen"
        elif weather_description == 504:
            return "Extrem starker Regen"
        elif weather_description == 511:
            return "Gefrierender Regen"
        elif weather_description == 520:
            return "Leichter Regenschauer"
        elif weather_description == 521:
            return "Regenschauer"
        elif weather_description == 522:
            return "Starker Regenschauer"
        elif weather_description == 531:
            return "Unregelmässiger Regenschauer"
        elif weather_description == 600:
            return "Leichter Schneefall"
        elif weather_description == 601:
            return "Schneefall"
        elif weather_description == 602:
            return "Starker Schneefall"
        elif weather_description == 611:
            return "Schneeregen"
        elif weather_description == 612:
            return "Leichter Schneeregenschauer"
        elif weather_description == 613:
            return "Schneeregenschauer"
        elif weather_description == 615:
            return "Leichter Regen mit Schnee"
        elif weather_description == 616:
            return "Regen mit Schnee"
        elif weather_description == 620:
            return "Leichter Schneeschauer"
        elif weather_description == 621:
            return "Schneeschauer"
        elif weather_description == 622:
            return "Starker Schneeschauer"
        elif weather_description == 701:
            return "Dunst"
        elif weather_description == 711:
            return "Rauch"
        elif weather_description == 721:
            return "Dunstschleier"
        elif weather_description == 731:
            return ("Staubwirbel")
        elif weather_description == 741:
            return "Nebel"
        elif weather_description == 751:
            return "Sand"
        elif weather_description == 761:
            return "Staub"
        elif weather_description == 762:
            return "Vulkanasche"
        elif weather_description == 771:
            return "Böen"
        elif weather_description == 781:
            return "Tornado"
        elif weather_description == 800:
            return "Klarer Himmel"
        elif weather_description == 801:
            return "Wenige Wolken"
        elif weather_description == 802:
            return "Vereinzelte Wolken"
        elif weather_description == 803:
            return "Aufgelockerte Bewölkung"
        elif weather_description == 804:
            return "Bedeckt"
        else:
            return "❔"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    weather_app = WeatherApp()
    weather_app.show()
    sys.exit(app.exec_())
