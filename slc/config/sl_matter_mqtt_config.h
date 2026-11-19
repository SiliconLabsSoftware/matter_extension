#ifndef SL_MATTER_MQTT_CONFIG
#define SL_MATTER_MQTT_CONFIG

// <<< Use Configuration Wizard in Context Menu >>>

// <s.128 SL_MATTER_MQTT_BROKER_ENDPOINT> MQTT endpoint
// <i> DNS name or IPv4 of the MQTT broker, e.g. "192.168.1.139" or "example.com"
// <i> Default: ""
#define SL_MATTER_MQTT_BROKER_ENDPOINT ""

// <o SL_MATTER_MQTT_BROKER_PORT> MQTT broker port
// <i> Use 8883 for TLS, 1883 for plain MQTT
// <i> Default: 8883
#define SL_MATTER_MQTT_BROKER_PORT 8883

// <q SL_MATTER_MQTT_TLS_ENABLED> Enable MQTT TLS
// <i> Default: 1
#define SL_MATTER_MQTT_TLS_ENABLED 1

// <s.128 SL_MATTER_MQTT_TLS_HOSTNAME> MQTT TLS hostname
// <i> Hostname for TLS SNI / cert check. Should match broker cert CN/SAN.
// <i> Default: same as broker endpoint when left as a concrete hostname string
#define SL_MATTER_MQTT_TLS_HOSTNAME ""

// <s.64 SL_MATTER_MQTT_CLIENT_ID> MQTT client ID
// <i> Default: "matter-mqtt-client"
#define SL_MATTER_MQTT_CLIENT_ID "matter-mqtt-client"

// <o SL_MATTER_MQTT_CLIENT_PORT> MQTT client local port
// <i> Default: 5003
#define SL_MATTER_MQTT_CLIENT_PORT 5003

// <s.64 SL_MATTER_MQTT_CLIENT_USERNAME> MQTT username
// <i> Leave empty if unused
// <i> Default: ""
#define SL_MATTER_MQTT_CLIENT_USERNAME ""

// <s.64 SL_MATTER_MQTT_CLIENT_PASSWORD> MQTT password
// <i> Leave empty if unused
// <i> Default: ""
#define SL_MATTER_MQTT_CLIENT_PASSWORD ""

// <<< end of configuration section >>>

#endif // SL_MATTER_MQTT_CONFIG