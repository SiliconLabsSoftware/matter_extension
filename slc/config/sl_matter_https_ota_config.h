/*
 *
 *    Copyright (c) 2026 Project CHIP Authors
 *    All rights reserved.
 *
 *    Licensed under the Apache License, Version 2.0 (the "License");
 *    you may not use this file except in compliance with the License.
 *    You may obtain a copy of the License at
 *
 *        http://www.apache.org/licenses/LICENSE-2.0
 *
 *    Unless required by applicable law or agreed to in writing, software
 *    distributed under the License is distributed on an "AS IS" BASIS,
 *    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 *    See the License for the specific language governing permissions and
 *    limitations under the License.
 */

#pragma once

#include "sl_matter_ota_config.h"

// <<< Use Configuration Wizard in Context Menu >>>

// <o SL_MATTER_HTTPS_OTA_PERIODIC_TIMEOUT> HTTPS vendor OTA periodic check timeout
// <i> How often VendorOTARequestorDriver runs the periodic HTTPS OTA check
// <i> Default: same as OTA_PERIODIC_TIMEOUT
#ifndef SL_MATTER_HTTPS_OTA_PERIODIC_TIMEOUT
#define SL_MATTER_HTTPS_OTA_PERIODIC_TIMEOUT OTA_PERIODIC_TIMEOUT
#endif

// <s.256 SL_MATTER_HTTPS_OTA_DEFAULT_URL> Compile-time default HTTPS OTA URL
// <i> Seeds the example periodic-URL store when non-empty. The requestor does not store this URL.
// <i> Leave empty ("") so periodic checks skip until shell `https-ota default`.
// <i> Example: "https://ota.example.com/image.ota"
// <i> Host may be DNS or IPv4 (no IPv6). Format: https://host[:port]/path
#ifndef SL_MATTER_HTTPS_OTA_DEFAULT_URL
#define SL_MATTER_HTTPS_OTA_DEFAULT_URL ""
#endif

// <<< end of configuration section >>>
