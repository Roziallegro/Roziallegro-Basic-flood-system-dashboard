// library import
#include <WiFi.h>
#include <Firebase_ESP_Client.h>
#include "addons/TokenHelper.h" // Provide the token generation process info
#include "addons/RTDBHelper.h"  // Provide the RTDB payload printing info and other helper functions

// pin declaration
const int trigPin = 5;
const int echoPin = 18;

// constants declaration
#define SOUND_SPEED 0.034
#define CM_TO_MM 10
#define WIFI_SSID "INSERT_OWN_HOTSPOT_WIFI_HERE"
#define WIFI_PASSWORD "INSERT_OWN_HOTSPOT_PASSWORD_HERE"
#define API_KEY "INSERT_API_KEY_HERE"
#define DATABASE_URL INSERT_DATABASE_URL_HERE""
#define USER_EMAIL "AUTHORISED_USER_EMAIL_HERE"
#define USER_PASSWORD "AUTHORISED_USER_PASSWORD_HERE"

// variable declaration
long duration;
float distance_cm;

FirebaseData fbdo;
FirebaseAuth auth;
FirebaseConfig config;
unsigned long sendDataPrevMillis = 0;
int initial_reading = 0;
int current_reading = 0;

// function declaration
float get_reading()
{
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
    distance_cm = duration * SOUND_SPEED / 2;
    // Convert to mm in integer
    return (int)distance_cm * CM_TO_MM;
}

void setup()
{
    Serial.begin(115200);     // Starts the serial communication
    pinMode(trigPin, OUTPUT); // Sets the trigPin as an Output
    pinMode(echoPin, INPUT);  // Sets the echoPin as an Input

    WiFi.begin(WIFI_SSID, WIFI_PASSWORD); // Sets wifi connection
    Serial.print("Connecting to Wi-Fi");
    while (WiFi.status() != WL_CONNECTED)
    {
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
    fbdo.setBSSLBufferSize(4096 /* Rx buffer size in bytes from 512 - 16384 */, 4096 /* Tx buffer size in bytes from 512 - 16384 */);

    // Assign the callback function for the long running token generation task
    config.token_status_callback = tokenStatusCallback; // see addons/TokenHelper.h
    Firebase.begin(&config, &auth);

    // Change sensor status, only once; default "offline"
    if (Firebase.RTDB.setString(&fbdo, "admin/sensor_status", "online"))
    {
        Serial.println("Status saved");
        Serial.println("PATH: " + fbdo.dataPath());
        Serial.println("TYPE: " + fbdo.dataType());
    }
    else
    {
        Serial.println("Failed" + fbdo.errorReason());
    }

    // Store first reading as treshold
    initial_reading = (int)get_reading();
    if (Firebase.RTDB.setInt(&fbdo, "initial_reading", initial_reading))
    {
        Serial.println("Data saved");
        Serial.println("PATH: " + fbdo.dataPath());
        Serial.println("TYPE: " + fbdo.dataType());
    }
    else
    {
        Serial.println("Failed" + fbdo.errorReason());
    }
}

void loop()
{
    // update readings every 5000ms(for demonstration purposes)
    if (Firebase.ready() && (millis() - sendDataPrevMillis > 3000 || sendDataPrevMillis == 0))
    { // Create a db connection everytime timer > 5000 or timer = 0 at the beginning
        // reset timer
        sendDataPrevMillis = millis();
        current_reading = (int)get_reading();

        // Save sensor reading into database
        if (Firebase.RTDB.setInt(&fbdo, "level_reading", current_reading))
        {
            Serial.println("Data saved");
            Serial.println("PATH: " + fbdo.dataPath());
            Serial.println("TYPE: " + fbdo.dataType());
        }
        else
        {
            Serial.println("Failed" + fbdo.errorReason());
        }

        // compute change in water depth
        if (Firebase.RTDB.setInt(&fbdo, "change_in_level", initial_reading - current_reading))
        {
            Serial.println("Data saved");
            Serial.println("PATH: " + fbdo.dataPath());
            Serial.println("TYPE: " + fbdo.dataType());
        }
        else
        {
            Serial.println("Failed" + fbdo.errorReason());
        }
    }
}
