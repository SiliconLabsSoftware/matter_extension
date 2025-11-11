/*******************************************************************************
 * @file
 * @brief Core application logic.
 *******************************************************************************
 * # License
 * <b>Copyright 2024 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * SPDX-License-Identifier: Zlib
 *
 * The licensor of this software is Silicon Laboratories Inc.
 *
 * This software is provided 'as-is', without any express or implied
 * warranty. In no event will the authors be held liable for any damages
 * arising from the use of this software.
 *
 * Permission is granted to anyone to use this software for any purpose,
 * including commercial applications, and to alter it and redistribute it
 * freely, subject to the following restrictions:
 *
 * 1. The origin of this software must not be misrepresented; you must not
 *    claim that you wrote the original software. If you use this software
 *    in a product, an acknowledgment in the product documentation would be
 *    appreciated but is not required.
 * 2. Altered source versions must be plainly marked as such, and must not be
 *    misrepresented as being the original software.
 * 3. This notice may not be removed or altered from any source distribution.
 *
 ******************************************************************************/

#include "app.h"
#include <stdio.h>
#include <sl_iostream_handles.h>
#include <sl_iostream.h>
#include <sl_simple_led.h>
#include <sl_simple_led_instances.h>
#include <sl_simple_button_instances.h>

/******************************************************************************
 * SDK
 *****************************************************************************/

void sl_button_on_change(const sl_button_t *handle)
{
    bool pressed = (sl_button_get_state(handle) == SL_SIMPLE_BUTTON_PRESSED);
    if(pressed) {
        sl_led_toggle(&sl_led_led1);
    }
}

/******************************************************************************
 * Application Init.
 *****************************************************************************/

void app_init(void)
{
}

/******************************************************************************
 * Application Process Action.
 *****************************************************************************/
static size_t _count = 0;
void app_process_action(void)
{
    if(++_count > 1000000) {
        _count = 0;
        printf("Non-secure!\r\n");
        sl_led_toggle(&sl_led_led0);
    }
}

/******************************************************************************
 * Application Exit.
 *****************************************************************************/
void app_exit(void)
{
}

