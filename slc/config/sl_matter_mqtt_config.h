#ifndef SL_MATTER_MQTT_CONFIG
#define SL_MATTER_MQTT_CONFIG

// <<< Use Configuration Wizard in Context Menu >>>
// <q SL_MATTER_MQTT_BROKER_ENDPOINT > MQTT endpoint
// <i> MQTT endpoint, e.g. "192.168.1.139" "example.com"
#define SL_MATTER_MQTT_BROKER_ENDPOINT ""

// <q SL_MATTER_MQTT_BROKER_PORT > MQTT port
// <i> MQTT port, e.g. 1883 8883 (use for TLS)
// <i> Default: 8883
#define SL_MATTER_MQTT_BROKER_PORT 8883

// <q SL_MATTER_MQTT_TLS_ENABLED > MQTT TLS enabled
// <i> MQTT TLS enabled, e.g. 1
// <i> Default: 1
#define SL_MATTER_MQTT_TLS_ENABLED 1

// <q SL_MATTER_MQTT_TLS_HOSTNAME > MQTT TLS hostname
// <i> MQTT TLS hostname, e.g. "example.com"
// <i> Default: SL_MATTER_MQTT_BROKER_ENDPOINT
#define SL_MATTER_MQTT_TLS_HOSTNAME SL_MATTER_MQTT_BROKER_ENDPOINT

// <q SL_MATTER_MQTT_CLIENT_ID > MQTT client ID
// <i> MQTT client ID, e.g. "mqtt-client-id"
// <i> Default: "matter-mqtt-client"
#define SL_MATTER_MQTT_CLIENT_ID "matter-mqtt-client"

// <q SL_MATTER_MQTT_CLIENT_PORT > MQTT client port
// <i> Local source port of the MQTT client
// <i> Default: 5003
#define SL_MATTER_MQTT_CLIENT_PORT 5003

// <q SL_MATTER_MQTT_CLIENT_USERNAME > MQTT username
// <i> MQTT username, e.g. "admin"
// <i> Default: ""
#define SL_MATTER_MQTT_CLIENT_USERNAME ""

// <q SL_MATTER_MQTT_CLIENT_PASSWORD > MQTT password
// <i> MQTT password, e.g. "password"
// <i> Default: ""
#define SL_MATTER_MQTT_CLIENT_PASSWORD ""

// <<< end of configuration section >>>

#endif // SL_MATTER_MQTT_CONFIG
