#include <Bridge.h>
#include <HttpClient.h>
#include <YunClient.h>

#define onesecond 1000
#define output_period 3

HttpClient httpClient;
YunClient yunClient;

void setup() {
	Bridge.begin();

	Serial.begin(9600);
	while(!Serial);
	Serial.println("Serial Begin!");
}

void loop() {
	sendPower();

	// while (httpClient.available()) {
	// 	char c = httpClient.read();
	// 	Serial.print(c);
	// }
	// Serial.flush();

	delay(output_period*onesecond);
}

void sendPower() {
	if(yunClient.connect("192.168.1.66",8080)){
		float realPower = 0.0;
		int min = 1000;
		int max = 1500;
		realPower = random(min, max);

		// Post Request
		String to_send = "{\"appliance_id\": \"5629499534213120\",\"real\" : ";
		to_send += realPower;
		to_send += "}";
		Serial.println(to_send);

		yunClient.println("POST /_ah/api/ems/v1/writePower HTTP/1.1");
		yunClient.print("Content-length:");
		yunClient.println(to_send.length());
		Serial.println(to_send.length());
		Serial.println(to_send);
		yunClient.println("Connection: Close");
		yunClient.println("Host:192.168.1.66:8080");
		yunClient.println("Content-Type: application/json");
		yunClient.println();
		yunClient.println(to_send);
	};
}
