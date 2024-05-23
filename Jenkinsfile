#!groovy
@Library('gsdk-shared-lib@master')
import groovy.json.JsonSlurper

properties([
    disableConcurrentBuilds(),
    parameters([
        // Allows us to manually trigger a Full Build by passing a parameter (boolean) from Jenkins.
        booleanParam(name: 'FULL_BUILD', defaultValue: false, description: 'Set to true if all supported boards are to be built. FULL_BUILD is always true on and RC or main development branch - DEFAULT: false'),
        // Specifies to send code size analysis report; used for end of RC builds
        booleanParam(name: 'SEND_CODE_SIZE_REPORT', defaultValue: false, description: 'Set to true if code size report is to be uploaded. SEND_CODE_SIZE_REPORT is always true on and RC or main development branch - DEFAULT: false'),
        // If Set, will build with workspaces instead of .slcp files 
        booleanParam(name: 'BUILD_WITH_WORKSPACES', defaultValue: true, description: 'Set to false if building examples without using workspaces - DEFAULT: true'),
    ])
])

buildOverlayDir = ''
//TO DO, this is for SQA UTF testing, this value should get from db or somewhere instead of hardcoded
RELEASE_NAME='22Q4-GA'
stashFolder = ''
chiptoolPath = ''
buildFarmLabel = 'Build-Farm'
buildFarmLargeLabel = 'Build-Farm-Large'
extensionPath = 'extension/matter_extension'
wifisdkPath = 'extension/wifi_sdk'
savedDirectory = "saved_workspace"
// Update this value every time the code move to the next CSA Matter release number (1.3, 1.4 etc)
// TODO: Find a better mechanism to pass this info to the SQA pipeline
_CSA_MATTER_VERSION= "1.3"

//This object will be populated by reading the pipeline_metadata.yml file
pipelineMetadata = null

// Populated with jenkins/jenkinsFunctions.groovy
pipelineFunctions = null

// Used to store comments to be made on PR
prComment = [:]

// Docker images
chipBuildEfr32Image = "artifactory.silabs.net/gsdk-dockerhub-proxy/connectedhomeip/chip-build-efr32:0.5.64"
gccImage = "artifactory.silabs.net/gsdk-docker-production/gsdk_nomad_containers/gsdk_23q4:latest"
chipToolImage = "artifactory.silabs.net/gsdk-docker-production/connectedhomeip/chip-build-crosscompile:22"
chipTestImage = 'ghcr.io/project-chip/chip-build:22'
ubaiImage = "artifactory.silabs.net/gsdk-docker-production/gsdk_nomad_containers/gsdk_ubai:latest"



secrets = [[path: 'teams/gecko-sdk/app/svc_gsdk', engineVersion: 2,
            secretValues: [[envVar: 'SL_PASSWORD', vaultKey: 'password'],
                           [envVar: 'SL_USERNAME', vaultKey: 'username']]]]
// helpers
def containerWrapper(String saveFilter,
                     String labelToRunAgainst,
                     String dockerImage,
                     String dockerArgs,
                     String savePath,
                     Closure workloadToExecute)
{
    runInMatterWorkspace( gsdkPipelineMetadata     : pipelineMetadata,
                    nfsWorkspaceDir          : buildOverlayDir,
                    buildStagesList          : advanceStageMarker.getBuildStagesList(),
                    saveFilter               : saveFilter,
                    label                    : labelToRunAgainst,
                    dockerImage              : dockerImage,
                    dockerContainerArgs      : dockerArgs,
                    savePath                 : savePath,
                    wsPath                   : "matter",
                    workloadToExecute)
}
def runInMatterWorkspace(Map args, Closure cl){
    if ( args.gsdkPipelineMetadata == null )
    {
        throw new IllegalArgumentException("You must provide a pipeline metadata object!")
    }
    if ( args.buildStagesList == null )
    {
        throw new IllegalArgumentException("You must provide the current state of advanceStageMarker.getBuildStagesList()!")
    }
    if ( args.nfsWorkspaceDir == null )
    {
        throw new IllegalArgumentException("You must provide the nfs workspace dir!")
    }
    return {
        actionWithRetry ({
            //the worker label to run against. if not specified, fall back to running on the 'Build-Farm'
            label = args.label ?: 'Build-Farm'

            node(label) {

                sh 'hostname && hostname -i'
                def ipAdd = sh returnStdout: true, script: 'hostname -i | awk \'{ print \$1 }\''
   				ipAdd = ipAdd.trim()
    			echo "IP Address: $ipAdd \nNetdata: http://$ipAdd:19999"
                // Build WiFi Examples
                def workspaceTmpDir = createWorkspaceOverlay(args.buildStagesList,
                                                             args.nfsWorkspaceDir)
                def filterPattern = args.saveFilter == 'NONE' ? '-name "no-files"' : args.saveFilter
                def dirPath = "$workspaceTmpDir/overlay/${args.wsPath ?: 'gsdk'}"
                def saveDir = args.savePath ?: 'gsdk/'

                dir(dirPath) {
                    //Add environment variables that can exist in docker workflow because they do not conflict
                    def env = ['UC_CLI_DIR='+workspaceTmpDir+createWorkspaceOverlay.overlayUcCliPath + '/',
                               'STUDIO_ADAPTER_PACK_PATH=' + workspaceTmpDir + createWorkspaceOverlay.overlayPrebuiltZapPath,
                          	   'ARM_GCC_DIR='+ args.gsdkPipelineMetadata.toolchain_info.gccToolLocation,
                               'PATH+JAVA11=' + args.gsdkPipelineMetadata.toolchain_info.java11Location,
                               'PATH+UC_CLI=' + workspaceTmpDir + createWorkspaceOverlay.overlayUcCliPath]

                    if(args.dockerImage != null)
                    {
                        //withDockerContainer needs to mount the full overlay in order to function
                        env += ['WORKSPACE=' + workspaceTmpDir + '/overlay']
                    }
                    else
                    {
                        //Add environment variables that cannot exist in docker workflow due to conflict
                        env += ['WORKSPACE=' + dirPath,
                                //compiler paths
                                'TOOLDIR=' + args.gsdkPipelineMetadata.toolchain_info.gccToolLocation,
                                'PATH_GCC=' + args.gsdkPipelineMetadata.toolchain_info.gccToolLocation + '/bin/',
                          		'ARM_GCC_DIR='+ args.gsdkPipelineMetadata.toolchain_info.gccToolLocation,
                                'ARM_GNU_DIR='+ args.gsdkPipelineMetadata.toolchain_info.gccToolLocation,
                                'PATH+GCC=' + args.gsdkPipelineMetadata.toolchain_info.gccToolLocation + '/bin',]
                    }

                    withEnv(env) {
                        sh 'printenv | sort'
                        try {

                            if(args.dockerImage != null)
                            {
                                if(args.dockerContainerArgs != null){
                                    runInGsdkContainer(args.dockerImage,args.dockerContainerArgs,cl)
                                }
                                else {
                                    runInGsdkContainer(args.dockerImage,cl)
                                }
                            }
                            else
                            {
                                cl()
                            }
                        } catch (e) {
                            echo 'failure: ' + e.toString()
                            deactivateWorkspaceOverlay(args.buildStagesList,
                                                       workspaceTmpDir,
                                                       saveDir,
                                                       '-name no-files')
                            throw e
                        }
                    }
                }
                if (filterPattern != null) {
                    echo "saving custom filter $filterPattern in $saveDir"
                    // use a custom filter (including an empty '')
                    deactivateWorkspaceOverlay(args.buildStagesList,
                                               workspaceTmpDir,
                                               saveDir, filterPattern)
                } else {
                    echo 'saving standard filter'
                    deactivateWorkspaceOverlay(args.buildStagesList,
                                               workspaceTmpDir)
                }
            }
        })
    }
}
def initExtensionWorkspaceAndScm()
{
    buildOverlayDir = sh( script: '/srv/jenkins/createSuperOverlay.sh '+
                                  'createbuildoverlay '+
                                  '/srv/workspaces '+
                                  '/srv/jenkins/reference',
                                  returnStdout: true ).trim()
    echo "Build overlay directory: ${buildOverlayDir}"

    dir(buildOverlayDir+createWorkspaceOverlay.overlayMatterPath)
    {
           
        checkout scm: [$class                            : 'GitSCM',
                        branches                         : scm.branches,
                        browser                          : [$class: 'Stash', repoUrl: 'https://stash.silabs.com/projects/WMN_TOOLS/repos/matter/'],
                        doGenerateSubmoduleConfigurations: scm.doGenerateSubmoduleConfigurations,
                        extensions                       : [[$class: 'ScmName', name: 'matter']],
                        userRemoteConfigs                : scm.userRemoteConfigs]   

        // ************************************************************************************
        //  Clone Matter repo, checkout corresponding branch, verify submodules are updated
        // ************************************************************************************
        sh """
                git submodule set-url ./third_party/silabs/wifi_sdk https://stash.silabs.com/scm/redpine/wifi_sdk.git
                git submodule set-url ./third_party/silabs/simplicity_sdk https://stash.silabs.com/scm/embsw/sisdk_release.git
                git submodule sync --recursive
                git submodule foreach --recursive -q git reset --hard -q
                git fetch || true && git fetch --tags
        """
 
        
        
       
        // Load metadata
        pipelineMetadata = readYaml(file: 'pipeline_metadata.yml')
        pipelineFunctions = load 'jenkins/jenkinsFunctions.groovy'
        sh 'scripts/checkout_submodules.py --shallow  --platform silabs linux'

        // ************************************************************************************
        //          Load variables for SQA Build Pipeline
        // ************************************************************************************

        if (env.BRANCH_NAME.startsWith("sqa_")){
            pipelineFunctions.matterBranchAndBuild()
        }
        
        // ************************************************************************************
        //          Initialize workspace setup to mirror Studio/SLC framework
        // ************************************************************************************

        // Create GSDK to use with SLC generate command later in pipeline
        sh "ls -ll ${buildOverlayDir+createWorkspaceOverlay.overlayGsdkPath}"

        sourceHash = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()

        // Copy GSDK and extensions to simulate Simplicity Studio environment
        sh "cp -R third_party/silabs/simplicity_sdk gsdk"
        sh "mkdir -p gsdk/extension/matter_extension"
        sh './slc/copy-extension.sh gsdk/extension'
        sh "cp -R third_party/silabs/wifi_sdk gsdk/extension/"

        // ************************************************************************************
        //            Obtain necessary tools/dependencies/repos needed by pipeline
        // ************************************************************************************

        // Obtain GSDK side package not available within repo
        dir ("gsdk"){
            pipelineFunctions.downloadGsdkSidePackage()
        }

        // Copy WiFi firmware
        pipelineFunctions.copyWifiFirmware()

        dir(buildOverlayDir+createWorkspaceOverlay.overlayUcCliPath)
        {
            checkout scm: [$class: 'GitSCM', 
                            branches            :    [[name: pipelineMetadata.toolchain_info.ucCliBranch]],
                            extensions          :    [[$class: 'ScmName', name: 'uc_cli']],
                            browser             :    [$class: 'Stash',
                            repoUrl             :    'https://stash.silabs.com/projects/SIMPLICITY_STUDIO/repos/uc_cli'], 
                            userRemoteConfigs   :    [[credentialsId: 'svc_gsdk',
                            url                 :    'ssh://git@stash.silabs.com/simplicity_studio/uc_cli.git']]]
    
         withEnv(['PATH+JAVA11=' + pipelineMetadata.toolchain_info.java11Location])
         {
            sh 'python3 slc -downloadOnly -deleteOutdated -noDownloadPrinting -useArtifactory'
            ucCliCommitFound = sh(returnStdout: true, script: 'git rev-parse HEAD').trim()
         }
            
        }
        dir(buildOverlayDir+createWorkspaceOverlay.overlayPrebuiltZapPath)
        {
            packageManagers.downloadLatestZapBuild(pipelineMetadata.toolchain_info.zap.zapBranch)
        }
        dir('commander'){
            checkout scm: [$class               : 'GitSCM', 
                            branches            : [[name: pipelineMetadata.toolchain_info.commander_info.commanderBranch]],
                            extensions          : [[$class: 'ScmName', name: 'simplicity_commander_linux_x64']],
                            browser             : [$class: 'Stash', repoUrl: pipelineMetadata.toolchain_info.commander_info.browserUrl],
                            userRemoteConfigs   : [[credentialsId: 'svc_gsdk', url: pipelineMetadata.toolchain_info.commander_info.gitUrl]]]

            sh 'pwd'
            sh 'ls'
            commanderBinary = "/commander/commander"
        }
        
        sh 'du -sk'
    }
    dir(buildOverlayDir+'/matter-scripts'){
        checkout scm: [$class                     : 'GitSCM',
                 branches                         : [[name: 'master']],
                 extensions                       : [[$class: 'ScmName', name: 'matter-scripts']],
                 browser                          : [$class: 'Stash',
                                                     repoUrl: 'https://stash.silabs.com/scm/wmn_sqa/matter-scripts/'],
                 userRemoteConfigs                : [[credentialsId: 'svc_gsdk',
                                                      url: 'https://stash.silabs.com/scm/wmn_sqa/matter-scripts.git']]]
    }

    dir(buildOverlayDir+'/sqa-tools'){
        checkout scm: [$class                     : 'GitSCM',
                 branches                         : [[name: 'master']],
                 extensions                       : [[$class: 'ScmName', name: 'sqa-tools']],
                 browser                          : [$class: 'Stash',
                                                     repoUrl: 'https://stash.silabs.com/scm/wmn_sqa/sqa-tools/'],
                 userRemoteConfigs                : [[credentialsId: 'svc_gsdk',
                                                      url: 'https://stash.silabs.com/scm/wmn_sqa/sqa-tools.git']]]
    }

}

// pipeline definition and execution
def pipeline()
{
    stage('Init Workspace and Repos')
    {
        node('buildNFS')
        {
            // set up NFS overlay and git repos
            extensionPath = 'extension/matter_extension'
            initExtensionWorkspaceAndScm()
        
            // export the NFS overlay
            sh 'sudo exportfs -af'
        } 
    }

    stage("Build Examples")
    {
        advanceStageMarker()
        try {
            def parallelNodesBuild = [:]

            def openThreadApps   = pipelineFunctions.getThreadApps()
            def openThreadBoards = pipelineFunctions.getThreadBoards(pipelineFunctions.getBuildType())

            def wifiNCPApps      = pipelineFunctions.getNCPApps()
            def wifi917NCPApps   = pipelineFunctions.get917NCPApps()
            def wifiBoards       = pipelineFunctions.getWifiBoards(pipelineFunctions.getBuildType())
            def wifiNCP          = pipelineFunctions.getGblNcps()
            def socApps          = pipelineFunctions.get917SoCApps()
            def socBoards        = pipelineFunctions.getWifiSocBoards()

            if(!env.BRANCH_NAME.startsWith('sqa_')){
                // Build OpenThread Examples
                openThreadBoards.each { boardToBuild ->
                    parallelNodesBuild["Thread $boardToBuild"]          = containerWrapper('-name "*.s37" -o -name "*.map"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory, { pipelineFunctions.buildThread(openThreadApps, boardToBuild) })
                }

                //Matter Zigbee app
                parallelNodesBuild["Matter Zigbee App"]          = containerWrapper('-name "*.s37" -o -name "*.map"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory, { pipelineFunctions.buildCMP() })

                // Build rs911x/WF200 NCP WiFi Examples
                wifiBoards.each { boardToBuild ->
                    wifiNCP.each { ncp ->
                        parallelNodesBuild["WiFi $boardToBuild $ncp"]  = containerWrapper('-name "*.s37" -o -name "*.map" -o -name "*.rps"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory,{ pipelineFunctions.buildWifi(wifiNCPApps, boardToBuild, ncp, buildWithWorkspaces=params.BUILD_WITH_WORKSPACES) })
                    }
                }

                // Build 917 NCP WiFi Examples
                wifiBoards.each { boardToBuild ->
                    parallelNodesBuild["WiFi $boardToBuild 917-ncp"]  = containerWrapper('-name "*.s37" -o -name "*.map" -o -name "*.rps"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory,{ pipelineFunctions.buildWifi(wifi917NCPApps, boardToBuild, "917-ncp", buildWithWorkspaces=params.BUILD_WITH_WORKSPACES) })
                }

                // Build 917 SoC WiFi Examples
                socBoards.each { boardToBuild ->
                    parallelNodesBuild["917SoC $boardToBuild"]         = containerWrapper('-name "*.s37" -o -name "*.map" -o -name "*.rps"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory,{ pipelineFunctions.buildWifi(socApps, boardToBuild, "917-soc", buildWithWorkspaces=false) })
                }

                // Build chiptool
                parallelNodesBuild['Build Chip-tool']                  = containerWrapper('-name "chip-tool" -o -name "chip-ota-provider-app"', buildFarmLargeLabel, chipToolImage, "-u root", 'matter/' + savedDirectory,{ pipelineFunctions.buildChipToolAndOTAProvider() } )

                // Run Unit Tests
                parallelNodesBuild['Run Unit Tests']                   = containerWrapper('NONE', buildFarmLargeLabel, chipToolImage, "-u root", 'matter/' + savedDirectory,{ pipelineFunctions.RunUnitTests() } )

                // Copy contents check
                parallelNodesBuild['Copy']                             = containerWrapper('NONE', buildFarmLargeLabel, gccImage, "", 'matter/', { pipelineFunctions.testCopyContents() })

                // Component Validation
                parallelNodesBuild['Validate Components'] =            containerWrapper("NONE", buildFarmLargeLabel, null, "", 'matter/', { pipelineFunctions.validateComponents() })
                
                // Build these examples on main development branch, RC, or if enabled
                if (env.BRANCH_NAME.startsWith('silabs') || env.BRANCH_NAME.startsWith('RC_') || params.SEND_CODE_SIZE_REPORT == true){
                    // Create lightweight 'slim' images for code analysis
                    parallelNodesBuild['Slim']                         = containerWrapper('-name "*.s37" -o -name "*.map" -o -name "*.rps"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory,{ pipelineFunctions.buildNoDebugImages() })
                }
                // Build OTA binaries on SQA Branch
            } else {
                parallelNodesBuild['OTA']                              = containerWrapper('-name "*.s37" -o -name "*.gbl" -o -name "*.ota"', buildFarmLargeLabel, gccImage, "", 'matter/' + savedDirectory,{ pipelineFunctions.buildOtaImages() })
            }

            parallelNodesBuild.failFast = false
            parallel parallelNodesBuild
        } catch (err) {
            unstable(message: "Some build failures occured")
        }
    }

    // Have to see if the step below will run or Jenkins with throw error
    if (env.BRANCH_NAME.startsWith('silabs') || env.BRANCH_NAME.startsWith('RC_') || params.SEND_CODE_SIZE_REPORT == true)
    {
        stage("Code Size Reports")
        {
            def parallelNodesBuild = [:]
            advanceStageMarker()
            
            // Run code size analysis if enabled or main development branch
            parallelNodesBuild["Code Size Analysis"]         = containerWrapper('NONE', buildFarmLabel, chipBuildEfr32Image, "-u root", 'matter/', { pipelineFunctions.exportIoTReports() })
            parallelNodesBuild.failFast = true
            parallel parallelNodesBuild
        }
    }

    // This stage is used for RC_slc or silabs_slc branches to create or update the SQA Build Pipeline.
    if(env.BRANCH_NAME.startsWith('RC_slc') || env.BRANCH_NAME.startsWith('silabs_slc')){
        stage("Create/Update SQA Build Pipeline")
        {
            advanceStageMarker()
            def parallelNodesBuild = [:]
            parallelNodesBuild["Create/Update"] = containerWrapper('NONE', buildFarmLargeLabel, null, "", 'matter/', {  pipelineFunctions.createOrUpdateSQABuildPipeline()  })
            parallelNodesBuild.failFast = false
            parallel parallelNodesBuild
        }
    }

    stage("Push to Artifactory and UBAI")
    {
        advanceStageMarker()
        def parallelNodesBuild = [:]
        if(!env.BRANCH_NAME.startsWith('sqa_')){
            parallelNodesBuild["Artifactory"] = containerWrapper('NONE', buildFarmLargeLabel, gccImage, "", 'matter/', { pipelineFunctions.pushToArtifactory()  })
            parallelNodesBuild["UBAI"] = containerWrapper('NONE', buildFarmLargeLabel, ubaiImage, "", 'matter/', { pipelineFunctions.pushToUbai()  })
            // if SQA branch, will push SQA binaries to UBAI
        } else {
            parallelNodesBuild["UBAI"] = containerWrapper('NONE', buildFarmLargeLabel, ubaiImage, "", 'matter/', { pipelineFunctions.pushToUbai(matterBranchName, MATTER_BUILD_NUMBER)  })
        }
        parallelNodesBuild.failFast = false
        parallel parallelNodesBuild
    }
   
    if(!env.BRANCH_NAME.startsWith('sqa_')){
        stage('SQA')
        {

            def parallelNodes = [:]

            parallelNodes['Lighting-App BRD4187C']      = { pipelineFunctions.utfThreadTestSuite('gsdkMontrealNode','utf_matter_thread',
                                                            'matter_thread','lighting-app','thread','BRD4187C','',"/manifest-4187-thread-lighting_slc",
                                                            "--tmconfig tests/.sequence_manager/test_execution_definitions/matter_thread_ci_sequence.yaml","SLC") }

            parallelNodes['lighting 917-SoC BRD4338A']   = { pipelineFunctions.utfWiFiTestSuite('gsdkMontrealNode','utf_matter_wifi_917soc_ci_2','matter_wifi_917soc_ci_2',
                                                            'lighting-app','wifi','BRD4338A','917_soc','',"/manifest-917soc",
                                                            "--tmconfig tests/.sequence_manager/test_execution_definitions/matter_wifi_ci_sequence.yaml","SLC") }

            parallelNodes.failFast = false
            parallel parallelNodes

        }
    }

    if(env.BRANCH_NAME.startsWith('RC_slc') || env.BRANCH_NAME.startsWith('silabs_slc') || env.BRANCH_NAME.startsWith('sqa_')){
        stage("Trigger SQA Smoke and Regression")
        {
            advanceStageMarker()
            // SQA branch will trigger regression, while silabs_slc and RC will trigger smoke
            if(env.BRANCH_NAME.startsWith('sqa_')){
                pipelineFunctions.triggerSqaSmokeAndRegressionTest("slc", matterBranchName, MATTER_BUILD_NUMBER)
            } else {
                pipelineFunctions.triggerSqaSmokeAndRegressionTest("slc")
            }
        }
    }
    currentBuild.result = 'SUCCESS'
}

def postFailure(e)
{
    currentBuild.result = 'FAILURE'
}

def postAlways()
{
    stage('Cleanup Overlays')
    {
        advanceStageMarker()
        node('buildNFS')
        {
            // clean up the things that have been pushed to the overlay
            sh '/srv/jenkins/createSuperOverlay.sh '+
               'removebuildoverlay '+
               buildOverlayDir
            dir('/srv/jenkins/overlays/') {
                sh 'rm -rf ' + advanceStageMarker.nfsOverlayWorkspaceRoot.replace('/mnt/nfs', '/srv/jenkins')
            }
        }
    }
}

// TODO lock the repo resource?
try {
    pipeline()
} catch (e) {
    postFailure(e)
    throw e
} finally {
    postAlways()
}
