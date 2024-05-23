def genericSoCMatterBuild(app, supportedBoards, ota_automation=false, ecosystem_automation=false)
{
    actionWithRetry {
        node(buildFarmLargeLabel)
        {
            def workspaceTmpDir = createWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                            buildOverlayDir)
            def dirPath = workspaceTmpDir + createWorkspaceOverlay.overlayMatterPath
            def saveDir = 'matter/'
            def out_dir = saved_workspace
            def transportType = "OpenThread"
            def commanderPath = dirPath + "/commander/commander"

            withDockerRegistry([url: "https://artifactory.silabs.net ", credentialsId: 'svc_gsdk']){
                sh "docker pull $chipBuildEfr32Image"
            }

            try {
                supportedBoards.families.each { family ->
                    stage(app.name + ' ' + family.name) {
                        dir(dirPath) {
                            try {
                                withDockerContainer(image: chipBuildEfr32Image, args: "-u root")
                                {
                                    // CSA Examples build
                                    withEnv(['PW_ENVIRONMENT_ROOT='+dirPath,
                                             'COMMANDER_PATH='+commanderPath,
                                             'MATTER_ROOT='+dirPath])
                                    {
                                        app.appBuildArgs.each { appBuildArg ->
                                            family.boards.each { board ->
                                                if (! app.boards.contains(board.name) ) {
                                                    // Board not targeted for the sample app
                                                    return
                                                }


                                                board.options.each {option ->
                                                    if (! app.variants.contains("all"))
                                                    {
                                                        if (! app.variants.contains(option.name) )
                                                        {
                                                            // Board variant not needed for this app
                                                            return
                                                        }
                                                    }


                                                    board.rcp.each { brcp ->
                                                        if (! app.rcp.contains(brcp) ) {
                                                            // RCP not targeted for the sample app
                                                            return
                                                        }

                                                        def rcpString = ""
                                                        if (family.isWiFi  || brcp != "") {
                                                            transportType = "WiFi"
                                                        } else {
                                                            transportType = "OpenThread"
                                                        }

                                                        def folderPath = transportType
                                                        if (brcp != "") {
                                                            rcpString = "--wifi " + brcp
                                                            folderPath += "/${brcp}"
                                                        }

                                                        sh """
                                                            echo Building ${transportType} ${board.name} ${brcp} type ${option.name}
                                                            ./scripts/examples/gn_silabs_example.sh ${app.path} ./out/${app.name}/${folderPath}/${option.name} ${board.name} ${rcpString} ${option.compilationFlags} ${appBuildArg.option}
                                                            mkdir -p ${saved_workspace}/out/${app.automation}/${option.name}/${board.name}/${folderPath}
                                                            find out/${app.name}/${folderPath}/${option.name}/${board.name} \\( -name '*.map' -o -name '*.s37' -o -name '*.rps' \\) -exec cp {} ${saved_workspace}/out/${app.automation}/${option.name}/${board.name}/${folderPath}/ \\;
                                                        """

                                                        stash name: transportType + 'Examples-'+app.name+'-'+board.name, includes: 'out/**/*.s37,out/**/*.rps '
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            } catch (e) {
                                deactivateWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                            workspaceTmpDir,
                                                            saveDir,
                                                            '-name no-files')
                                throw e
                            }
                        }
                    }
                }
            } catch (e) {
                deactivateWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                            workspaceTmpDir,
                                            "matter",
                                            '-name no-files')
                throw e
            }
            deactivateWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                            workspaceTmpDir,
                            'matter/' + saved_workspace,
                            '-name "*.s37" -o -name "*.map" -o -name "*.rps"')
        }
    }
}

return this
