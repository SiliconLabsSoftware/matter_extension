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

#if defined(ENABLE_CHIP_SHELL) && defined(SL_OPENTHREAD_MULTI_INSTANCE_CLI_ENABLE)

#include "openthread_instance_handler.h"
#include <lib/shell/Engine.h>
#include <lib/shell/commands/Help.h>
#include <lib/support/CodeUtils.h>
#include <cstring>
#include <cstdlib>

// Include the OpenThread multi-instance CLI functions
extern "C" {
#include "multi_instance_cli.h"
}

using namespace chip;
using Shell::Engine;
using Shell::shell_command_t;
using Shell::streamer_get;
using Shell::streamer_printf;

#ifndef MATTER_ARRAY_SIZE
#define MATTER_ARRAY_SIZE(arr) (sizeof(arr) / sizeof(arr[0]))
#endif

Engine sShellOTSubCommands;

// Application update function - equivalent to app_process_action
void ProcessOpenThreadInstanceChange()
{
    if (sl_ot_should_change_instance())
    {
        sl_ot_switch_to_instance_index(sl_ot_get_new_instance_index());
    }
}

static CHIP_ERROR OTInstanceGetHandler(int argc, char ** argv)
{
    uint8_t currentInstance = sl_ot_get_current_instance_index();
    streamer_printf(streamer_get(), "Current instance index: %d\r\n", currentInstance);
    streamer_printf(streamer_get(), "Done\r\n");
    return CHIP_NO_ERROR;
}

static CHIP_ERROR OTInstanceSetHandler(int argc, char ** argv)
{
    if (argc != 1)
    {
        streamer_printf(streamer_get(), "Usage: otcli instance set <index>\r\n");
        return CHIP_ERROR_INVALID_ARGUMENT;
    }

    char * endptr;
    long instanceIndex = strtol(argv[0], &endptr, 10);
    
    if (*endptr != '\0' || instanceIndex < 0 || instanceIndex > 255)
    {
        streamer_printf(streamer_get(), "Error: Invalid instance index\r\n");
        return CHIP_ERROR_INVALID_ARGUMENT;
    }

    // Only store the instance index - actual switch happens in ProcessOpenThreadInstanceChange
    sl_ot_set_new_instance_index((uint8_t)instanceIndex);
    
    streamer_printf(streamer_get(), "Done\r\n");
    return CHIP_NO_ERROR;
}

static CHIP_ERROR OTInstanceCommandHandler(int argc, char ** argv)
{
    if (argc == 0)
    {
        streamer_printf(streamer_get(), "Usage: otcli instance <subcommand>\r\n");
        return CHIP_ERROR_INVALID_ARGUMENT;
    }

    if (strcmp(argv[0], "get") == 0)
    {
        return OTInstanceGetHandler(argc - 1, argv + 1);
    }
    else if (strcmp(argv[0], "set") == 0)
    {
        return OTInstanceSetHandler(argc - 1, argv + 1);
    }
    else
    {
        streamer_printf(streamer_get(), "Unknown subcommand: %s\r\n", argv[0]);
        streamer_printf(streamer_get(), "Available subcommands: get, set\r\n");
        return CHIP_ERROR_INVALID_ARGUMENT;
    }
}

static CHIP_ERROR OTCliCommandHandler(int argc, char ** argv)
{
    if (argc == 0)
    {
        streamer_printf(streamer_get(), "Usage: otcli <subcommand>\r\n");
        return CHIP_ERROR_INVALID_ARGUMENT;
    }

    return sShellOTSubCommands.ExecCommand(argc, argv);
}

static CHIP_ERROR OTCliHelpHandler(int argc, char ** argv)
{
    sShellOTSubCommands.ForEachCommand(Shell::PrintCommandHelp, nullptr);
    return CHIP_NO_ERROR;
}

// Register OpenThread CLI commands
void RegisterOpenThreadCommands()
{
    static const shell_command_t sOTSubCommands[] = {
        { &OTCliHelpHandler, "help", "Usage: otcli <subcommand>" },
        { &OTInstanceCommandHandler, "instance", "OpenThread instance commands. Usage: otcli instance <get|set>" },
    };

    static const shell_command_t sOTCommand = { &OTCliCommandHandler, "otcli",
                                               "OpenThread CLI commands. Usage: otcli <subcommand>" };
    sShellOTSubCommands.RegisterCommands(sOTSubCommands, MATTER_ARRAY_SIZE(sOTSubCommands));

    Engine::Root().RegisterCommands(&sOTCommand, 1);
}

#endif // ENABLE_CHIP_SHELL && SL_OPENTHREAD_MULTI_INSTANCE_CLI_ENABLE
