#ifndef SL_MATTER_ICD_CONFIG_H
#define SL_MATTER_ICD_CONFIG_H

// Default ICD implementation for Short Idle Time (SIT) devices

// <<< Use Configuration Wizard in Context Menu >>>

// <o SL_IDLE_MODE_DURATION_S>  Idle Mode Duration
// <i> 10 minute Idle Mode Duration
// <i> Default: 600
#define SL_IDLE_MODE_DURATION_S 600

// <o SL_ACTIVE_MODE_DURATION_MS>  Active Mode Duration
// <i> 1 second Active Mode Duration
// <i> Default: 1000
#define SL_ACTIVE_MODE_DURATION_MS 1000

// <o SL_ACTIVE_MODE_THRESHOLD>  Active Mode Thresholed
// <i> 500ms Active Mode Threshold
// <i> Default: 500
#define SL_ACTIVE_MODE_THRESHOLD 500

// <o SL_ICD_SUPPORTED_CLIENTS_PER_FABRIC>  ICD Supported Clients
// <i> Default: 2
#define SL_ICD_SUPPORTED_CLIENTS_PER_FABRIC 2

// <o SL_TRANSPORT_IDLE_INTERVAL>   15s Idle Intervals
// <i> Default: 15000
#define SL_TRANSPORT_IDLE_INTERVAL 15000

// <o SL_TRANSPORT_ACTIVE_INTERVAL> 200ms Active Intervals
// <i> Default: 200
#define SL_TRANSPORT_ACTIVE_INTERVAL 200

// <o SL_CSL_TIMEOUT>
// <i> Default: 30
// <i> Feature requires matter_synchronized_sed component
#define SL_CSL_TIMEOUT 30

// <o CHIP_CONFIG_ENABLE_ICD_DSLS>
// <i> Default: 0
// <i> Set to true if device supports dynamic switching from SIT to LIT operating modes (DSLS)
#define CHIP_CONFIG_ENABLE_ICD_DSLS 0

// <<< end of configuration section >>>

#endif // SL_MATTER_ICD_CONFIG_H