
#include "init_matter_multipan.h"
#include <openthread/instance.h>
#include <openthread/cli.h>

extern "C" {
#include "platform-efr32.h"
#if CHIP_DEVICE_CONFIG_THREAD_ENABLE_CLI
void otAppCliInit(otInstance * aInstance);
#endif // CHIP_DEVICE_CONFIG_THREAD_ENABLE_CLI
}

// Global variable to store the OpenThread instance
static otInstance * myOtInstance = nullptr;

/**
 * @brief Initialize Matter Multi-PAN support with internal app initialization
 * 
 * This function initializes a secondary OpenThread instance for Multi-PAN support
 * and moves the CLI to the proprietary Thread instance.
 */
extern "C" void sl_internal_app_init_matter_multipan()
{
    myOtInstance = otInstanceInitMultiple(1);
    /* Move CLI to Proprietary Thread instance */
    otAppCliInit(myOtInstance);
}