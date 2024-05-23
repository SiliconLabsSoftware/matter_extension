#!groovy

def buildUnifyApp(arch, app, env_exports, buildDir, out_path)
{
    echo "Build Unify Matter " + app
    sh 'rm -rf ./.environment'
    sh 'git config --global --add safe.directory $(pwd)'
    sh 'git config --global --add safe.directory $(pwd)/third_party/pigweed/repo'

    // Compile the Unify app
    dir (buildDir)
    {
        def archname = arch - 'hf'
        sh "../../../scripts/run_in_build_env.sh \"${env_exports}; gn gen ${out_path} --args='target_cpu=\\\"" + archname + "\\\"'\""
        sh "../../../scripts/run_in_build_env.sh \"${env_exports}; ninja -C ${out_path}\""
    }
}

def buildUnifyARM(arch, triples, app)
{
    actionWithRetry {
        node(buildFarmLargeLabel)
        {
            def workspaceTmpDir = createWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                            buildOverlayDir)
            def dirPath = workspaceTmpDir + createWorkspaceOverlay.overlayMatterPath
            def unifyCheckoutDir = workspaceTmpDir + "/overlay/unify"
            def saveDir = 'matter/out/'
            try {

                withDockerRegistry([url: "https://artifactory.silabs.net ", credentialsId: 'svc_gsdk']) {

                    def unify_matter_docker = docker.image('artifactory.silabs.net/gsdk-docker-production/unify-cache/unify-matter:1.1.4-' + arch)
                    stage('unify ' + arch) {
                        dir(dirPath) {
                            unify_matter_docker.inside("-u root -v${unifyCheckoutDir}:/unify")
                            {
                                withEnv(['PW_ENVIRONMENT_ROOT=' + dirPath])
                                {
                                    // Build libunify
                                    echo "Build libunify for " + arch
                                    sh 'cd /unify && cmake -DCMAKE_INSTALL_PREFIX=$PWD/stage_' + arch + ' -GNinja -DCMAKE_TOOLCHAIN_FILE=../cmake/' + arch + '_debian.cmake  -B build_unify_' + arch + '/ -S components -DBUILD_TESTING=OFF'
                                    sh 'cd /unify && cmake --build build_unify_' + arch
                                    sh 'cd /unify && cmake --install build_unify_' + arch + ' --prefix $PWD/stage_' + arch
                                }
                            }
                        }
                    }
                    stage('Unify Matter ' + app + ' ' + arch) {

                            dir(dirPath)
                            {
                                unify_matter_docker.inside("-u root -v${unifyCheckoutDir}:/unify")
                                {
                                    withEnv(['PW_ENVIRONMENT_ROOT=' + dirPath])
                                    {
                                        def pkg_config_export = "export PKG_CONFIG_PATH=:/unify/stage_" + arch + "/share/pkgconfig:/usr/lib/" + triples + "/pkgconfig"
                                        buildUnifyApp(arch, app, pkg_config_export, "silabs_examples/unify-matter-" + app + "/linux", "../../../out/silabs_examples/unify-matter-" + app + "/" + arch + "_debian_bullseye")
                                    }
                                }

                                // Move binaries to standardized output
                                sh """  mkdir -p ${saved_workspace}/out/""" + app + """/""" + arch + """_debian_bullseye

                                        cp ./out/silabs_examples/unify-matter-""" + app + """/""" + arch + """_debian_bullseye/obj/bin/unify-matter-""" + app + """ ${saved_workspace}/out/""" + app + """/""" + arch + """_debian_bullseye/
                                """
                                if (fileExists("""./out/silabs_examples/unify-matter-""" + app + """/""" + arch + """_debian_bullseye/packages""")) {
                                    sh """  cp ./out/silabs_examples/unify-matter-""" + app + """/""" + arch + """_debian_bullseye/packages/* ${saved_workspace}/out/""" + app + """/""" + arch + """_debian_bullseye/
                                    """
                                }
                            }
                    }
                    stage('chip-tool ' + arch) {
                            dir(dirPath)
                            {
                                unify_matter_docker.inside("-u root -v${unifyCheckoutDir}:/unify")
                                {
                                    withEnv(['PW_ENVIRONMENT_ROOT=' + dirPath])
                                    {

                                        def pkg_config_export = "export PKG_CONFIG_PATH=:/unify/stage_" + arch + "/share/pkgconfig:/usr/lib/" + triples + "/pkgconfig"
                                        sh 'rm -rf ./.environment'
                                        sh 'git config --global --add safe.directory $(pwd)'
                                        sh 'git config --global --add safe.directory $(pwd)/third_party/pigweed/repo'

                                        // Compile the Unify app
                                        dir ("examples/chip-tool")
                                        {
                                            def archname = arch - 'hf'
                                            def out_path = "../../out/examples/chip-tool/" + arch + "_debian_bullseye"
                                            sh "../../scripts/run_in_build_env.sh \"${pkg_config_export}; gn gen ${out_path} --args='target_cpu=\\\"" + archname + "\\\"'\""
                                            sh "../../scripts/run_in_build_env.sh \"${pkg_config_export}; ninja -C ${out_path}\""
                                        }
                                    }
                                }

                                // Move binaries to standardized output
                                sh """  mkdir -p ${saved_workspace}/out/Chiptool/""" + arch + """_debian_bullseye

                                        cp ./out/examples/chip-tool/""" + arch + """_debian_bullseye/chip-tool ${saved_workspace}/out/Chiptool/""" + arch + """_debian_bullseye/
                                """
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
                                            '-name "unify-matter-*" -o -type f -name "chip-tool" -o -type f -name "*.deb"')
        }
    }
}

def buildUnifyAMD(app)
{
    actionWithRetry {
        node(buildFarmLargeLabel)
        {
            def workspaceTmpDir = createWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                            buildOverlayDir)
            def dirPath = workspaceTmpDir + createWorkspaceOverlay.overlayMatterPath
            def unifyCheckoutDir = workspaceTmpDir + "/overlay/unify"
            def saveDir = 'matter/out/'
            try {

                withDockerRegistry([url: "https://artifactory.silabs.net ", credentialsId: 'svc_gsdk']) {
                    def unify_matter_docker_amd64 = docker.image('artifactory.silabs.net/gsdk-docker-production/unify-cache/unify-matter:1.1.4-amd64')
                    dir(dirPath)
                    {
                        stage('libunify amd64') {
                            unify_matter_docker_amd64.inside("-u root -v${unifyCheckoutDir}:/unify")
                            {
                                withEnv(['PW_ENVIRONMENT_ROOT=' + dirPath])
                                {
                                    echo "Build libunify"
                                    sh 'cd /unify && cmake -DCMAKE_INSTALL_PREFIX=$PWD/stage_amd64 -GNinja -B build_unify_amd64/ -S components -DBUILD_TESTING=OFF'
                                    sh 'cd /unify && cmake --build build_unify_amd64'
                                    sh 'cd /unify && cmake --install build_unify_amd64 --prefix $PWD/stage_amd64'
                                }
                            }
                            stage('Unify Matter ' + app + ' amd64') {
                                unify_matter_docker_amd64.inside("-u root -v${unifyCheckoutDir}:/unify")
                                {
                                    withEnv(['PW_ENVIRONMENT_ROOT=' + dirPath])
                                    {
                                        echo "Build Unify Matter " + app
                                        sh 'rm -rf ./.environment'
                                        sh 'git config --global --add safe.directory $(pwd)'
                                        sh 'git config --global --add safe.directory $(pwd)/third_party/pigweed/repo'
                                        def pkg_config_export = "export PKG_CONFIG_PATH=:/unify/stage_amd64/share/pkgconfig"

                                        // Execute Unit Tests
                                        dir ("silabs_examples/unify-matter-" + app + "/linux")
                                        {
                                            sh "../../../scripts/run_in_build_env.sh \"${pkg_config_export}; ../../unify-matter-common/scripts/compile_tests.sh -t amd64\""
                                            sh "export LD_LIBRARY_PATH=/unify/stage_amd64/lib; ../../unify-matter-common/scripts/run_tests.sh -b out/amd64_test"
                                        }
                                    }
                                }
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
                                            '-name no-files')
        }
    }
}