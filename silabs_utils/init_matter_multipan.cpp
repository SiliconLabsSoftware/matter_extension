
#include "init_matter_multipan.h"
#include <openthread/instance.h>
#include <openthread/cli.h>

extern "C" {
#include "platform-efr32.h"
#if CHIP_DEVICE_CONFIG_THREAD_ENABLE_CLI
#include "sl_ot_custom_cli.h"
void otAppCliInit(otInstance * aInstance);
#endif // CHIP_DEVICE_CONFIG_THREAD_ENABLE_CLI  
}

// Global variable to store the OpenThread instance
static otInstance * myOtInstance = nullptr;

/**
 * @brief Initialize Matter Multi-PAN support with internal app initialization
 *
 * This file initializes a secondary OpenThread instance for Multi-PAN support
 * and initializes the OpenThread CLI to the secondary Thread instance.
 */
extern "C" void sl_internal_app_init_second_instance()
{
    myOtInstance = otInstanceInitMultiple(1);
}

extern "C" void sl_internal_app_init_cli()
{
    /* Move CLI to the secondary Thread instance */
    otAppCliInit(myOtInstance);
    sl_ot_custom_cli_init();
}