/**
 * @file
 * @brief OpenThread Multi-Instance Handler for Matter Shell
 *******************************************************************************
 * # License
 * <b>Copyright 2025 Silicon Laboratories Inc. www.silabs.com</b>
 *******************************************************************************
 *
 * The licensor of this software is Silicon Laboratories Inc. Your use of this
 * software is governed by the terms of Silicon Labs Master Software License
 * Agreement (MSLA) available at
 *
 * https://www.silabs.com/about-us/legal/master-software-license-agreement
 *
 * This software is distributed to you in Source Code format and is governed by
 * the sections of the MSLA applicable to Source Code.
 */

#pragma once

/**
 * @brief Process OpenThread instance changes (equivalent to app_process_action)
 * 
 * This function implements the same logic as app_process_action in bare-metal apps:
 * if (sl_ot_should_change_instance()) {
 *     sl_ot_switch_to_instance_index(sl_ot_get_new_instance_index());
 * }
 */
void ProcessOpenThreadInstanceChange();

/**
 * @brief Register OpenThread CLI commands
 * 
 * This function registers OpenThread CLI commands (like otcli instance set/get)
 * with the CHIP shell system. Similar to how performance test commands are registered.
 */
void RegisterOpenThreadCommands();
