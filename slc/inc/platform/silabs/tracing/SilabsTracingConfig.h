#ifndef PLATFORM_SILABS_TRACING_SILABSTRACINGCONFIG_H_
#define PLATFORM_SILABS_TRACING_SILABSTRACINGCONFIG_H_

// <<< Use Configuration Wizard in Context Menu >>>

// <q TRACING_RUNTIME_STATS> Enable FreeRTOS runtime statistics collection
// <i> Default: 0
#define TRACING_RUNTIME_STATS 0

// <q TRACING_RUNTIME_STATS_MAX_TASKS> Maximum number of tasks to track for runtime statistics.
// <i> Default: 16
#define TRACING_RUNTIME_STATS_MAX_TASKS 16

// <q SILABS_TRACING_ENERGY_STATS> Enable energy mode statistics collection
// <i> Default: 0
#define SILABS_TRACING_ENERGY_STATS 1

// <q SILABS_TRACING_ENERGY_TRACES_SECONDS> Time to wait before outputting the results
// <i> Default: 600
#define SILABS_TRACING_ENERGY_TRACES_SECONDS 600

// <q SILABS_TRACING_ENERGY_TRACES_MAX> Maximum number of energy traces to store
// <i> Default: 3000
#define SILABS_TRACING_ENERGY_TRACES_MAX 3000

// <<< end of configuration section >>>

#endif // PLATFORM_SILABS_TRACING_SILABSTRACINGCONFIG_H_
