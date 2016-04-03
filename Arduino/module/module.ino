#include <TimerOne.h>
#include <WiFi.h>

#include <EmonLib.h>
EnergyMonitor emon1;

int samplingPeriod = 1; // in seconds
double onesecond = 1000000;
const int numReadings = 10;
double readingBuffer[numReadings];
int index = 0;

// WiFi Parameters
char ssid[] = "BTHub5-3FJ2";
char pass[] = "";

void setup() {

	Serial.begin(115200);

	// WiFi Setup
	// Serial.print("Connection Status : ");
	// Serial.println(WiFi.begin(ssid, pass));

	// Emon Setup
	emon1.voltage(0, 334.0, 1.7);
	emon1.current(4,96.2);       // Current: input pin, calibration.

	// Timer Setup for Reading Power
	// Timer1.initialize(samplingPeriod * onesecond);
	// Timer1.attachInterrupt(readPower);
	// Timer Setup for pushReadings
}

void loop() {
	emon1.calcVI(20,2000);
	emon1.serialprint();

	delay(1000);
}

// run every X seconds
void readPower() {
	int latestReading = newPower();
	Serial.println(latestReading);

	readingBuffer[index++] = latestReading;
	index %= numReadings;
	if(index == 0) {
		pushReadings();
	}
}
double newPower(){
	// return random(1,10);
	double Irms = emon1.calcIrms(1480);
	return Irms;
}

void pushReadings() {
	Serial.print("[");
	for(int i=0; i<numReadings; i++) {
		Serial.print(readingBuffer[i]);
		if(i < numReadings-1){
			Serial.print("\t");   
		}
	}
	Serial.println("]");
}