#ifndef SL_MATTER_OTA_CONFIG_H
#define SL_MATTER_OTA_CONFIG_H

// <<< Use Configuration Wizard in Context Menu >>>

// <o OTA_PERIODIC_TIMEOUT> OTA Requestor periodic timeout
// <i> How often the device checks for available firmware updates
// <i> Default: 86400 seconds (24 hours)
#define OTA_PERIODIC_TIMEOUT 86400

// <o SL_MATTER_HTTPS_OTA_PERIODIC_TIMEOUT> HTTPS vendor OTA periodic check timeout
// <i> How often VendorOTARequestorDriver runs the periodic HTTPS OTA check
// <i> Default: same as OTA_PERIODIC_TIMEOUT
#ifndef SL_MATTER_HTTPS_OTA_PERIODIC_TIMEOUT
#define SL_MATTER_HTTPS_OTA_PERIODIC_TIMEOUT OTA_PERIODIC_TIMEOUT
#endif

// <s.64 SL_MATTER_HTTPS_OTA_ENDPOINT> Optional IPv4 connect override for HTTPS OTA
// <i> When non-empty, Range GETs connect to this IP and skip DNS.
// <i> URL hostname is still used for TLS SNI / Host (e.g. example.com).
// <i> Leave empty ("") to resolve the URL hostname via DNS.
// <i> Example: "192.168.1.50"
#ifndef SL_MATTER_HTTPS_OTA_ENDPOINT
#define SL_MATTER_HTTPS_OTA_ENDPOINT ""
#endif

// <s.256 SL_MATTER_HTTPS_OTA_DEFAULT_URL> Compile-time default HTTPS OTA URL
// <i> Seeds the example periodic-URL store when non-empty. The requestor does not store this URL.
// <i> Leave empty ("") so periodic checks skip until shell `demo https-ota default`.
// <i> Example: "https://ota.example.com/image.ota"
#ifndef SL_MATTER_HTTPS_OTA_DEFAULT_URL
#define SL_MATTER_HTTPS_OTA_DEFAULT_URL ""
#endif

// <<< end of configuration section >>>

#endif // SL_MATTER_OTA_CONFIG_H
