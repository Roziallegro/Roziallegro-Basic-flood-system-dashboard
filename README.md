# Flood System Dashboard


## Introduction
Arduino-based project that detects changes in water level. It is connected to Google's Firebase Database. Visualisation was performed using dash and plotly Python libraries as backends.

<img src="images\System overview.png" width="50%" height="auto">
<img src="images\Dashboard UI proposed.png" width="80%" height="auto">

## Schematics

### Component required & hardware connection
1. Jumper wires
2. ESP32
3. Ultrasonic sensor
4. Google's firebase account

<img src="images\Ultrasonic sensor.jpg" width="20%" height="auto">

| Ultrasonic sensor | ESP32 pins |
| ------------------- | ------------ |
| VCC pin (for power)  | 3V3 pin |
| Trig pin (transmit ultrasound wave) | PIN 5 |
| Echo pin (listens for reflected signal) | PIN 18 |
| Gnd | GND pin |

## Code
Full code at: [Github](https://github.com/Roziallegro/Basic-flood-system-dashboard)

### Sensor
1. 1.	Create a firebase real-time database. For in depth details, head over to https://youtu.be/aO92B-K4TnQ?t=160. However, this code requires authorised email and password. The final database is as follows:
<img src="images\Database example.png" width="30%" height="auto">
2. Connected ultrasonic sensor to the ESP32. Head to the [Arduino IDE](https://www.arduino.cc/en/software) and start coding.
3.	The following libraries were downloaded for the ESP32 firebase from Mobizt: 
<img src="images\Library manager.png" width="50%" height="auto">

4. Import the libraries.
```
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h" // Provide the token generation process info
#include "addons/RTDBHelper.h" // Provide the RTDB payload printing info and other helper functions
```
5. Declare input and output pins.
```
const int trigPin = 5;
const int echoPin = 18;
```
6. Constants declaration.
**To change WiFi and Database credentials.**
```
#define SOUND_SPEED 0.034
#define CM_TO_MM 10
#define WIFI_SSID "INSERT_OWN_HOTSPOT_WIFI_HERE"
#define WIFI_PASSWORD "INSERT_OWN_HOTSPOT_PASSWORD_HERE"
#define API_KEY "INSERT_API_KEY_HERE"
#define DATABASE_URL INSERT_DATABASE_URL_HERE""
#define USER_EMAIL "AUTHORISED_USER_EMAIL_HERE"
#define USER_PASSWORD "AUTHORISED_USER_PASSWORD_HERE"
```
7. Variable declaration.
```
long duration;
float distance_cm;
int distance_mm;

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
unsigned long sendDataPrevMillis = 0;
int initial_reading = 0; 
int current_reading = 0;
```
8. Function declaration to obtain readings from the ultrasonic sensor.
Note that we have to emit an ultrasonic signal first and record the time taken for sound to be reflected back into the sensor. The distance of an object from the sensor is then calculated as **distance = time taken × (speed of sound/2)**.
```
float get_reading(){
  // Clears the trigPin
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);
  // Sets the trigPin on HIGH state for 10 micro seconds
  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  // Reads the echoPin, returns the sound wave travel time in microseconds
  duration = pulseIn(echoPin, HIGH);
  
  // Calculate the distance
  distance_cm = duration * SOUND_SPEED/2;
  // Convert to mm in integer
  return (int)distance_cm * CM_TO_MM;
}
```
9. Void setup() declaraion.
This code runs once to initialise the following variables and start with WiFi and Database connections.
```
void setup() {
  Serial.begin(115200); // Starts the serial communication
  pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echoPin, INPUT); // Sets the echoPin as an Input
  
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD); // Sets wifi connection
  Serial.print("Connecting to Wi-Fi");
  while(WiFi.status() != WL_CONNECTED) {
        Serial.print(".");
        delay(500);
    }
  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP()); 
  
  config.api_key = API_KEY;
  config.database_url = DATABASE_URL;
  auth.user.email = USER_EMAIL;
  auth.user.password = USER_PASSWORD;
  Firebase.reconnectWiFi(true);
  fbdo.setBSSLBufferSize(16384 /* Rx buffer size in bytes from 512 - 16384 */, 16384 /* Tx buffer size in bytes from 512 - 16384 */);

  // Assign the callback function for the long running token generation task
  config.token_status_callback = tokenStatusCallback; //see addons/TokenHelper.h
  Firebase.begin(&config, &auth);
```
Inside the function, wwe also initialise the database to include that our sensor is now online and store the very first reading of the sensor as we will minus it off with the current reading to find if water level increased.
<img flood level changes>
```
  // Change sensor status, only once; default "offline"
  if (Firebase.RTDB.setString(&fbdo, "admin/sensor_status", "online")){
      Serial.println("Status saved");
      Serial.println("PATH: " + fbdo.dataPath());
      Serial.println("TYPE: " + fbdo.dataType());
    }
    else{
      Serial.println("Failed" + fbdo.errorReason());
    }

   // Store first reading as treshold
   initial_reading = (int)get_reading();
    if (Firebase.RTDB.setInt(&fbdo, "initial_reading", initial_reading)){ 
      Serial.println("Data saved");
      Serial.println("PATH: " + fbdo.dataPath());
      Serial.println("TYPE: " + fbdo.dataType());
    }
    else{
      Serial.println("Failed" + fbdo.errorReason());
    }
}
```
10. Void loop() declaraion.
For every 5000 ms, collect reading from the sensor and update the database.
```
void loop() {
  // update readings every 5000ms(for demonstration purposes)
  if (Firebase.ready() && (millis() - sendDataPrevMillis > 3000 || sendDataPrevMillis == 0)){ // Create a db connection everytime timer > 5000 or timer = 0 at the beginning
    // reset timer
    sendDataPrevMillis = millis();
    current_reading = (int)get_reading();

    // Save sensor reading into database
    if (Firebase.RTDB.setInt(&fbdo, "level_reading", current_reading)){ 
      Serial.println("Data saved");
      Serial.println("PATH: " + fbdo.dataPath());
      Serial.println("TYPE: " + fbdo.dataType());
    }
    else{
      Serial.println("Failed" + fbdo.errorReason());
    }


    // compute change in water depth
    if (Firebase.RTDB.setInt(&fbdo, "change_in_level", current_reading - initial_reading)){ 
      Serial.println("Data saved");
      Serial.println("PATH: " + fbdo.dataPath());
      Serial.println("TYPE: " + fbdo.dataType());
    }
    else{
      Serial.println("Failed" + fbdo.errorReason());
    }
}}
```

### Dashboard
Full code at: 

1. Create and navigate to the folder of your choice and pip install the libraries found in requirement.txt.
`pip install -r requirements.txt`
2. Inside python IDE, import the following libraries that were pip installed from requirements.txt.
```
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc
from datetime import datetime
import firebase_admin
from firebase_admin import db, credentials
```
3. Authenticate to firebase
**To update credentials.json and database url**
Navigate to "Project Overview" -> "Project settings" -> "Service accounts" ->"Generate new private key"
<img private key>
Navigate to "Realtime Database" -> Copy database url
<img database url>
```
try:
    cred = credentials.Certificate("credentials.json")
    firebase_admin.initialize_app(cred, {"databaseURL": "DATABASE_URL_HERE"})
    main_status = "online"
except:
    # if there is error
    main_status = "offline"
  ```
  4. Initialise some helper functions that will help us (i) get today's date (ii) query from database and (iii) automatically updates the status of sensor (device), database and flood risk.
  ```
  def get_day():
    time = datetime.now()
    return(time.strftime("%A"))

def get_date():
    time = datetime.now()
    return(time.strftime("%d %B"))

def get_query(node):
    try:
        return db.reference('/'+node).get()
    except:
        # in case of no connection
        return 0 


def listen_device_status():
    admin = get_query("admin/sensor_status") 
    if admin == "online":
        return update_status("online")
    else:
        return update_status("offline")


def update_status(status):
    if status == "online":
        return html.P("Online", style={"font-family": "Calibri", "color": "#01877E", "font-size": 18, "margin": 0})
    else:
        return html.P("Offline", style={"font-family": "Calibri", "color": "#FFB0A9", "font-size": 18, "margin": 0})
    

def warning_level():
    change_in_water_level = get_query("change_in_level")

    if change_in_water_level == 0:
        return html.P("-", style={"font-family": "Calibri", "color": "#000000", "font-size": 18, "margin": 0})
    elif 0 < change_in_water_level <= 50:
        return html.P("Low flood risk", style={"font-family": "Calibri", "color": "#01877E", "font-size": 18, "margin": 0})
    elif 50 <= change_in_water_level <= 200:
        return html.P("Medium flood risk", style={"font-family": "Calibri", "color": "#F9D678", "font-size": 18, "margin": 0})
    else:
        return html.P("High flood risk", style={"font-family": "Calibri", "color": "#FFB0A9", "font-size": 18, "margin": 0})
  ```
  5. Initialise the dash application. 
  create_layout() is where our html elements will be stored, it will be defined later.
```
def main() -> None:
    app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
    app.title = "Flood System"
    app.layout = create_layout(app)
```
@app.callback() allows us to communicate with the backend via the Input() and Output() methods. Input() allows us to bring submit data, in this case it is the interval time to retrieve information in the database. Output() allows us to retrieve data from the database (in this case) and update the graph according in the webpage. 

Since we need to constantly update the graph every 1000ms, we require the `interval-component`.
```
    @app.callback([Output(component_id="water_level", component_property="figure"),
                   Output(component_id="water_status", component_property="children")], 
                  [Input('interval-component', 'n_intervals')])
    def gauge_graph(n):
        fig = go.Figure(go.Indicator(
            #mode = "gauge+number+delta",
            mode = "gauge+number",
            value = get_query("change_in_level"), # to change according to db + calibration
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Water level increase", 'font': {'size': 18}},
            #delta = {'reference': 0, 'increasing': {'color': "#FFB284"}, 'decreasing':{'color': "#849D8A"}},
            gauge = {
                'axis': {'range': [None, 1000], 'tickwidth': 1, 'tickcolor': "#13313D"},
                'bar': {'color': "#13313D"},
                'bgcolor': "#FFB0A9",
                'borderwidth': 2,
                'bordercolor': "#FFFFFF",
                'steps': [
                    {'range': [0, 50], 'color': '#01877E'},
                    {'range': [50, 200], 'color': '#F9D678'}],}
        ))

        fig.update_layout(font = {'color': "#13313D", 'family': "Calibri"})

        return fig, warning_level()
```  
This app runs on on local host: http://127.0.0.1:8051/
  ```     
    app.run_server(debug=True, port=8051)
```  
The following code is about how individual html elements are used to achieve the following layout:
<img layout>
```  
def create_layout(app: Dash) -> html.Div:
    return html.Div(
        className="app-div",
        children=[
            html.Br(),
            dbc.Row(
                [dbc.Col(left_content(app)),
                dbc.Col(right_content(app), width={"offset": 2}),]
            )
        ],
    )


def left_content(app: Dash) -> html.Div:  
    return html.Div(
        children=[
            html.P("Today", style={"font-family": "Calibri", "font-size": 16, "margin": 0}),
            html.P(get_day(), style={"font-family": "Calibri", "font-size": 25, "font-weight": "bold", "margin": 0}),
            html.P(get_date(), style={"font-family": "Calibri", "font-size": 25, "margin": 0}),
            html.Br(),
            html.P("Location:  Area 1", style={"font-family": "Calibri", "font-size": 18, "margin": 0}),
            html.Div(id="water_status", children=[]),
            html.Div([               
                dcc.Graph(id='water_level', figure={}),
                dcc.Interval(id='interval-component', interval=1000, n_intervals=0),
            ]),
        ],
    )


def right_content(app: Dash) -> html.Div:
    return html.Div(
        children = [
            html.P("Current database status", style={"font-family": "Calibri", "font-size": 18, "font-weight": "bold", "margin": 0}),
            update_status(main_status),
            html.Br(),
            html.P("Device status", style={"font-family": "Calibri", "font-size": 18, "font-weight": "bold", "margin": 0}),
            listen_device_status(),
        ],
    )
```
6. Run the whole application.
```
if __name__ == '__main__':
    main()
```
