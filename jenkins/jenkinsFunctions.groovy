def getBuildType()
{
    if (env.BRANCH_NAME.startsWith('RC_') || params.FULL_BUILD == true) {
        return "FULL"
    } 
    else {
        return "NORMAL"
    } 
} 
def getThreadBoards(buildType='')
{
    if (buildType == "FULL") {
        // Only A00 revision of BRD4319A is supported, enforced at generation time 
        return ["BRD4116A", "BRD4117A", "BRD4118A", "BRD4121A", "BRD4186C", "BRD4187C", "BRD2703A", "BRD2704A", "BRD2601B",
                "BRD2608A", "BRD4316A", "BRD4317A", "BRD4319A", "BRD4337A", "BRD4318A"]     
    } 
    else if (buildType == "GBL")
    {
        return ["BRD4187C"]
    }
    else {
        return ["BRD4187C", "BRD4316A", "BRD4337A"]
    } 
}
def getWifiBoards(buildType='')
{
    if (buildType == "FULL") {
        return ["BRD4186C", "BRD4187C"]
    } 
    else if (buildType == "GBL")
    {
        return ["BRD4187C"]
    }
    else{
        return ["BRD4187C"]
    }
}

def getWifiSocBoards()
{
    return ["BRD4338A"]
}
def getThreadApps()
{
    return ["lighting-app", "lock-app", "thermostat", "light-switch-app", "window-app", "onoff-plug-app", "sensor-app", "dishwasher-app"]
}
def getBoardsWithInternalBootloader()
{
    return ["BRD4337A", "BRD2704A", "BRD2703A", "BRD4319A", "BRD4116A"]
}
def getNCPApps()
{
    return [ "lock-app", "thermostat"]
}

def get917NCPApps()
{
    return [ "lock-app", "thermostat", "window-app"]
}

def get917SoCApps()
{
    return ["lighting-app", "lock-app", "light-switch-app", "window-app", "onoff-plug-app", "dishwasher-app", "thermostat"]
}

def getGblNcps()
{
    return ["wf200","rs911x"]
}
// Used to clarify stashed binary
def getStashName(brd, app, ncp='')
{
    if (ncp == ''){
        return "OpenThreadExamples-${app}-${brd}"
    }
    else{
        return "WiFiExamples-${app}-${brd}-${ncp}"
    }
}
// Removes unsupported board/app combos
def getAppsForBoard(brd, allApps)
{
    // Only supported app for 2704
    if (brd == "BRD2704A"){
        return ["lighting-app"]
    }
    
    // Remove thermostat and performance-test-app from unsupported boards
    def unsupportedThermostatBoards = ["BRD4319A", "BRD2703A", "BRD2601B", "BRD4337A"]
    def unsupportedPerformanceTestBoards = [
                "BRD4186C", "BRD2703A", "BRD2704A", "BRD2601B",
                "BRD4316A", "BRD4317A", "BRD4319A", "BRD4337A", "BRD4318A"]
    if ((brd in unsupportedThermostatBoards) && (brd in unsupportedPerformanceTestBoards)){
        return allApps - "thermostat" - "performance-test-app"
    } else if(brd in unsupportedPerformanceTestBoards){
        return allApps - "performance-test-app"
    }
    else{
        return allApps
    }
}

// Returns corresponding slcp/slcw provided an application name
def getPrjFileName(targetBoard, appName, useWorkspaces, ncp="")
{
    def isInternalBootloader = ""
    def slcProjFileName = ""

    if (ncp){   // WiFi
        if (useWorkspaces){
            slcProjFileName = appName + "-" + ncp + "-bootloader"
        }
        else{
            slcProjFileName = appName + "-" + ncp
        }
    }
    else{   // Thread
        if (useWorkspaces){
            def internalBootloaderBoards = getBoardsWithInternalBootloader()
            if (targetBoard in internalBootloaderBoards){
                isInternalBootloader = "-internal"
            }
            if (appName == "zigbee-matter-light"){
                slcProjFileName = appName+"${isInternalBootloader}-bootloader"
            }
            else {
                slcProjFileName = appName+"-thread${isInternalBootloader}-bootloader"
            }

        }
        else{
            if (appName == "zigbee-matter-light"){
                slcProjFileName = appName
            }
            else {
                slcProjFileName = appName+"-thread"
            }
            
        }
    }
    return slcProjFileName
}
def getProtocol(ncp=""){
    if(ncp){
        return "WiFi"
    }
    else{
        return "OpenThread"
    }
}
def getSeries(brd){
    seriesTwoBoards = ["BRD4116A", "BRD4117A", "BRD4118A", "BRD4121A", "BRD4186C", "BRD4187C", "BRD2608A", "BRD2703A", "BRD2704A", "BRD2601B", "BRD4316A", "BRD4317A", "BRD4318A","BRD4319A", "BRD4337A"]
    if(brd.toUpperCase() in seriesTwoBoards){
        return "series-2"
    }
    else{
        return ""
    }
}

def getBuildConfigs(board="", appName="", otaVersion="", ncp = "", configs = "", useWorkspace = false, applicationComponents = "", bootloaderComponents = "", customPath = ""){
    def buildMap = [:]
    buildMap["board"] = board
    buildMap["appName"] = appName
    buildMap["otaVersion"] = otaVersion
    buildMap["ncp"] = ncp
    buildMap["configs"] = configs
    buildMap["applicationComponents"] = applicationComponents
    buildMap["bootloaderComponents"] = bootloaderComponents
    buildMap["useWorkspace"] = useWorkspace
    buildMap["customPath"] = customPath
    return buildMap
}

def testCopyContents(){
    def appsToBuild = []
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app", otaVersion="", ncp = "",        configs = "--copy-sources", useWorkspace = false, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="thermostat",   otaVersion="", ncp = "rs911x",  configs = "--copy-sources", useWorkspace = false, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4338A", appName="lighting-app", otaVersion="", ncp = "917-soc", configs = "--copy-sources", useWorkspace = false, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",     otaVersion="", ncp = "wf200",   configs = "--copy-sources", useWorkspace = false, applicationComponents = "")
    slcBuild(appsToBuild, "Copy Contents")
}
def buildNoDebugImages(){
    def componentsToRemove = '--without "matter_shell;matter,matter_qr_code;matter,matter_lcd;matter"'
    def appsToBuild = []
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app",     otaVersion="", ncp = "",       configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="light-switch-app", otaVersion="", ncp = "",       configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",         otaVersion="", ncp = "",       configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="window-app",       otaVersion="", ncp = "",       configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="dishwasher-app",   otaVersion="", ncp = "",       configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",         otaVersion="", ncp = "rs911x", configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="thermostat",       otaVersion="", ncp = "rs911x", configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_no_debug;matter")
    slcBuild(appsToBuild, "No Debug")
}
def buildCMP()
{
    def appsToBuild = []
    // Sequential
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="zigbee-matter-light", otaVersion="", ncp = "", configs = "", useWorkspace = false, applicationComponents = ",matter_zigbee_sequential;matter", bootloaderComponents = "", customPath="")
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="zigbee-matter-light", otaVersion="", ncp = "", configs = "", useWorkspace = true, applicationComponents = ",matter_zigbee_sequential;matter", bootloaderComponents = "", customPath="")
    appsToBuild += getBuildConfigs(board="BRD4118A", appName="zigbee-matter-light", otaVersion="", ncp = "", configs = "", useWorkspace = false, applicationComponents = ",matter_zigbee_sequential;matter", bootloaderComponents = "", customPath="")
    // Concurrent
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="zigbee-matter-light", otaVersion="", ncp = "", configs = "", useWorkspace = false, applicationComponents = ",matter_zigbee_concurrent;matter", bootloaderComponents = "", customPath="")
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="zigbee-matter-light", otaVersion="", ncp = "", configs = "", useWorkspace = true, applicationComponents = ",matter_zigbee_concurrent;matter", bootloaderComponents = "", customPath="")
    appsToBuild += getBuildConfigs(board="BRD4117A", appName="zigbee-matter-light", otaVersion="", ncp = "", configs = "", useWorkspace = false, applicationComponents = ",matter_zigbee_concurrent;matter", bootloaderComponents = "", customPath="")
    slcBuild(appsToBuild, "CMP")
}
//Built in SQA Branches
def buildThreadOTAImages(){
    def software_version_2 = '--configuration CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION:2,CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION_STRING:\\"2\\"'
    def software_version_3 = '--configuration CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION:3,CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION_STRING:\\"3\\"'
    def appsToBuild = []

    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app",     otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",         otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="dishwasher-app",   otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="light-switch-app", otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="thermostat",       otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="window-app",       otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app",     otaVersion="3", ncp = "",        configs = software_version_3, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="lighting-app",     otaVersion="2", ncp = "",        configs = software_version_2, useWorkspace = true, applicationComponents = "")
    // LZ4 Images
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app", otaVersion="2-lz4", ncp = "", configs = software_version_2, useWorkspace = true, applicationComponents = "", bootloaderComponents = ",bootloader_gbl_compression_lz4")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app", otaVersion="3-lz4", ncp = "", configs = software_version_3, useWorkspace = true, applicationComponents = "", bootloaderComponents = ",bootloader_gbl_compression_lz4")

    slcBuild(appsToBuild, "OTA Thread Images")
}
//Built in SQA Branches
def buildWiFiOTAImages(){
    def software_version_2 = '--configuration CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION:2,CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION_STRING:\\"2\\"'
    def software_version_3 = '--configuration CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION:3,CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION_STRING:\\"3\\"'
    def appsToBuild = []

    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",     otaVersion="2", ncp = "wf200",   configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",     otaVersion="2", ncp = "917-ncp", configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",     otaVersion="2", ncp = "rs911x",  configs = software_version_2, useWorkspace = true, applicationComponents = "")
    appsToBuild += getBuildConfigs(board="BRD4338A", appName="lighting-app",     otaVersion="2", ncp = "917-soc",  configs = software_version_2, useWorkspace = false, applicationComponents = "")

    slcBuild(appsToBuild, "OTA WiFi Images")
}
//Built in SQA Branches
def buildLowPowerImages(){
    def componentsToRemove = '--without "matter_shell;matter,matter_qr_code;matter,matter_lcd;matter,matter_lcd_917SOC;matter,matter_thread_cli;matter,matter_default_lcd_config;matter"'
    def appsToBuild = []
    appsToBuild += getBuildConfigs("BRD4186C", appName="lighting-app", otaVersion="", ncp = "", configs = componentsToRemove, useWorkspace = true, applicationComponents = ",matter_platform_low_power;matter")
    appsToBuild += getBuildConfigs("BRD4338A", appName="lock-app", otaVersion="", ncp = "917-soc", configs = componentsToRemove, useWorkspace = false, applicationComponents = ",matter_platform_low_power;matter")
    slcBuild(appsToBuild, "Low Power Images")
}
def buildMultiOtaImages(){
    def componentsToAdd = ',matter_multi_image_ota;matter,matter_multi_image_custom_processor;matter'
    def componentsToRemove = '--without "matter_ota_support;matter"'

    def appsToBuild = []

    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app",     otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",         otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="window-app",       otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="dishwasher-app",   otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)

    appsToBuild += getBuildConfigs(board="BRD4116A", appName="lighting-app",     otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="lock-app",         otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="window-app",       otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="dishwasher-app",   otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)

    slcBuild(appsToBuild, "M-OTA Images")
}

def buildMultiOtaEncImages(){
    def componentsToAdd = ',matter_multi_image_ota;matter,matter_multi_image_ota_encryption;matter,matter_multi_image_custom_processor;matter'
    def componentsToRemove = '--without "matter_ota_support;matter"'

    def appsToBuild = []

    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lighting-app",     otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="lock-app",         otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="window-app",       otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4187C", appName="dishwasher-app",   otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)

    appsToBuild += getBuildConfigs(board="BRD4116A", appName="lighting-app",     otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="lock-app",         otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="window-app",       otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)
    appsToBuild += getBuildConfigs(board="BRD4116A", appName="dishwasher-app",   otaVersion="", ncp = "",        configs = componentsToRemove, useWorkspace = true, applicationComponents = componentsToAdd)

    slcBuild(appsToBuild, "M-OTA-enc Images")
}


// Builds all Wifi examples by board (depending on build type)
def buildWifi(appsToBuild, boardToBuild, ncpToBuild, buildWithWorkspaces)
{
    // Node information to be displayed within Jenkins GUI
    def nodeDescription = boardToBuild + " " + ncpToBuild

    // List of projects to build and their specific build configurations (to be ran on the same node)
    def buildConfigurations = []

    for (int i = 0; i < appsToBuild.size(); i++) {
        buildConfigurations += getBuildConfigs(board=boardToBuild, appName=appsToBuild[i], otaVersion="", ncp=ncpToBuild, configs="", useWorkspace=buildWithWorkspaces, applicationComponents="")
    }
    slcBuild(buildConfigurations, nodeDescription)
}
// Builds all Thread examples by board (depending on build type)
def buildThread(appList, boardToBuild)
{
    // List of projects to build and their specific build configurations (to be ran on the same node)
    def buildConfigurations = []

    // Node information to be displayed within Jenkins GUI
    def nodeDescription = boardToBuild

    // Remove unsupported combinations
    def appsToBuild = getAppsForBoard(boardToBuild, appList)

    // Add each build configuration to a list
    for (int i = 0; i < appsToBuild.size(); i++) {
        buildConfigurations += getBuildConfigs(board=boardToBuild, appName=appsToBuild[i], otaVersion="", ncp="", configs="", useWorkspace=params.BUILD_WITH_WORKSPACES, applicationComponents="")
    }

    // Build for compiled build configuration list
    slcBuild(buildConfigurations, nodeDescription)
}
// Builds list of apps based within buildList and their corresponding build configurations
// See getBuildConfigs() for buildList structure
def slcBuild(buildList, jobDescription)
{
    def matterPath = env.WORKSPACE + "/matter"
    def gsdkPath = matterPath + '/gsdk'
    def outputDirList = []

    dir(matterPath){
        stage("Generate - " + jobDescription){

            trustSdk(gsdkPath)
            buildList.each { paramMap ->

                outputDirList += generateProjects(paramMap)
            }
            sh "${UC_CLI_DIR}slc --daemon daemon-shutdown"
        }
        stage("Compile - " + jobDescription){
            sh "${matterPath}${commanderBinary} -version"

            // Create iterator to map designated output directories with their corresponding build configurations
            def outputIter = 0
            buildList.each { paramMap ->

                generateSlcBinary(paramMap, outputDirList[outputIter])

                // Copy generated binaries to more formalized layout - do not save --copy-sources builds
                if (!paramMap["configs"].contains("copy")){
                    saveGeneratedBinaries(paramMap, gsdkPath, matterPath, outputDirList[outputIter])
                }
                outputIter++
            }

        }
    }
}
// Runs code to generate example based on input
def generateProjects(paramMap){
    def commanderPath = pwd() + commanderBinary

    def brd = paramMap["board"]
    def app = paramMap["appName"]
    def ncp = paramMap["ncp"]
    def ota = paramMap["otaVersion"]
    def parameters = paramMap["configs"]
    def appComponents = paramMap["applicationComponents"]
    def blComponents = paramMap["bootloaderComponents"]
    def useWorkspaces = paramMap["useWorkspace"]
    def slcPrjName = getPrjFileName(brd, app, useWorkspaces, ncp)
    def platform = "/efr32/"
    def brdLowerCase = brd.toLowerCase()

    if (getWifiSocBoards().contains(brd)) {
        platform = "/siwx917/"
    }

    if(brdLowerCase == 'brd4319a') {
        // Only A00 revision of BRD4319A is supported
        brdLowerCase = 'brd4319a_a00'
    }
    if (ncp.startsWith('917-soc')) {
        // Must specify extension
        brdLowerCase = brdLowerCase + ';wiseconnect3_sdk'
    }

    def projectPath = "slc/sample-app/"
    if (paramMap["customPath"] != ""){
        projectPath = paramMap["customPath"]
        platform = "/"
    }

    def projFilePath = ""
    def projTypeFlag = ""
    if(useWorkspaces){
        projFilePath = "gsdk/extension/matter_extension/slc/workspaces/" + app + "/" + getSeries(brd) + "/" + slcPrjName + ".slcw"
        projTypeFlag = "-w"
    }
    else{
        projFilePath = "gsdk/extension/matter_extension/" + projectPath + app + platform + slcPrjName + ".slcp"
        projTypeFlag = "-p"
    }

    echo "Generating ${app} for ${brd}"
    sh "printenv"

    def output = brd + "/" + app + ncp + ota

    // CMP
    if(appName == "zigbee-matter-light")
    {
        // retrieve the variant from the component name (sequential or concurrent)
        def tmpStr = paramMap["applicationComponents"].split(";").first().split("_").last()
        output += tmpStr.replace(",","")
    }

    if(appComponents.contains("matter_siwx917_m4_sleep")){
        // Overriding the sleep mode for 917 SOC
        sh """
            mkdir -p ${output}/config/zcl
            cp gsdk/extension/matter_extension/examples/lock-app/lock-common/lock-app.zap ${output}/config/zcl/zcl_config.zap
        """
    }

    if ((blComponents || appComponents) && useWorkspaces){
        // Build for solutions
        sh """
            export POST_BUILD_EXE=${commanderPath}
            ${commanderPath} -version
            ${UC_CLI_DIR}slc generate --daemon -d ${output} ${projTypeFlag} ${projFilePath} --with '${brdLowerCase}${blComponents}' -pids bootloader ${parameters} -data gsdk/out/dmp_uc.data --generator-timeout=1800
            ${UC_CLI_DIR}slc generate --daemon -d ${output} ${projTypeFlag} ${projFilePath} --with '${brdLowerCase}${appComponents}' -pids application ${parameters} -data gsdk/out/dmp_uc.data --generator-timeout=1800
        """
    }
    else{
        // Build for just application
        sh """
            export POST_BUILD_EXE=${commanderPath}
            ${commanderPath} -version
            ${UC_CLI_DIR}slc generate --daemon -d ${output} ${projTypeFlag} ${projFilePath} --with '${brdLowerCase}${appComponents}' ${parameters} -data gsdk/out/dmp_uc.data --generator-timeout=1800
        """
    }


    return output
}
// Runs code to generate example based on input
def generateSlcBinary(paramMap, outputDir)
{
    def commanderPath = pwd() + commanderBinary

    def brd = paramMap["board"]
    def app = paramMap["appName"]
    def ncp = paramMap["ncp"]
    def buildWithWorkspaces = paramMap["useWorkspace"]
    def slcPrjName = getPrjFileName(brd, app, buildWithWorkspaces, ncp)
    
    if (buildWithWorkspaces){
        slcPrjName += ".solution"
    }
    echo "Building ${app} for ${brd}"

    sh """
        export POST_BUILD_EXE=${commanderPath}
        make all -C ${outputDir} -f ${slcPrjName}.Makefile -j12
    """
}
// Builds chip tool and OTA provider
def buildChipToolAndOTAProvider()
{
    def matterPath = env.WORKSPACE + "/matter"
    dir(matterPath){
        withEnv(['PW_ENVIRONMENT_ROOT='+matterPath])
        {
            sh 'rm -rf ./.environment;pwd'
            sh 'git config --global --add safe.directory $(pwd)'
            sh 'git config --global --add safe.directory $(pwd)/third_party/pigweed/repo'
            sh './scripts/run_in_build_env.sh  "./scripts/build/build_examples.py --target linux-arm64-chip-tool-ipv6only-clang build"'
            sh './scripts/run_in_build_env.sh  "./scripts/build/build_examples.py --target linux-arm64-ota-provider-ipv6only-clang build"'
        }

        sh "mkdir -p ${savedDirectory}/out/Chiptool/linux-arm64-ipv6only-clang; cp out/linux-arm64-chip-tool-ipv6only-clang/chip-tool ${savedDirectory}/out/Chiptool/linux-arm64-ipv6only-clang/"
        sh "mkdir -p ${savedDirectory}/out/OTA/linux-arm64-ipv6only-clang; cp out/linux-arm64-ota-provider-ipv6only-clang/chip-ota-provider-app ${savedDirectory}/out/OTA/linux-arm64-ipv6only-clang/"
        stash name: 'ChipTool', includes: savedDirectory + '/**/chip-tool'
    }
}
// Run Cirque Tests
def RunCirqueTests()
{
    node(buildFarmLabel)
    {
        def workspaceTmpDir = createWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                        buildOverlayDir)

        def matterPath = workspaceTmpDir + createWorkspaceOverlay.overlayMatterPath

        dir(matterPath) {
            withEnv(['DOCKER_BUILD_VERSION=21', 'DOCKER_RUN_VERSION=21', 'DOCKER_RUN_IMAGE=chip-build-cirque'])
            {
                try {
                    sh 'rm -rf ./.environment;pwd'
                    sh 'git config --global --add safe.directory $(pwd)'
                    sh 'git config --global --add safe.directory $(pwd)/third_party/pigweed/repo'
                    sh 'scripts/checkout_submodules.py --allow-changing-global-git-config --shallow --platform linux'
                    //sh 'integrations/docker/images/stage-2/chip-build-cirque/run.sh && bash scripts/bootstrap.sh && && chown -R $(id -u):$(id -g) .environment'

                    /*sh """
                    integrations/docker/images/stage-2/chip-build-cirque/run.sh \
                    -- sh -c " \
                    git config --global --add safe.directory '*' \
                    && bash scripts/bootstrap.sh \
                    "
                    """*/
                    sh """
                    integrations/docker/images/stage-2/chip-build-cirque/run.sh -- sh -c " git config --global --add safe.directory '*' && bash scripts/activate.sh && chown -R \$(id -u):\$(id -g) .environment"
                    """

                    sh """
                    integrations/docker/images/stage-2/chip-build-cirque/run.sh --env GITHUB_ACTION_RUN=1 --env GITHUB_CACHE_PATH=/tmp/cirque-cache --volume /tmp:/tmp -- scripts/tests/cirque_tests.sh bootstrap
                    """

                    sh """
                    integrations/docker/images/stage-2/chip-build-cirque/run.sh -- sh -c " git config --global --add safe.directory '*' && scripts/build/gn_gen_cirque.sh "
                    """

                    sh 'mkdir reports'

                    sh """
                    integrations/docker/images/stage-2/chip-build-cirque/run.sh --env LOG_DIR=${matterPath}/reports --env CLEANUP_DOCKER_FOR_CI=1 --env GITHUB_ACTION_RUN=1 --privileged --volume /tmp:/tmp --volume /dev/pts:/dev/pts -- sh -c " git config --global --add safe.directory '*'"
                    """

                    sh "scripts/tests/cirque_tests.sh run_all_tests"

                } catch (e) {
                    step([$class: 'ArtifactArchiver', artifacts: "reports/*.log", fingerprint: true])

                    deactivateWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                workspaceTmpDir,
                                                "matter/",
                                                '-name no-files')
                    throw e
                }
            }

      }
    deactivateWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                workspaceTmpDir,
                                "matter/" + savedDirectory,
                                '-name no-files')
    }
}

// Run Unit Tests
def RunUnitTests()
{
    def matterPath = env.WORKSPACE + "/matter"
    dir(matterPath){
        withEnv(['PW_ENVIRONMENT_ROOT='+matterPath])
        {
            sh 'rm -rf ./.environment;pwd'
            sh 'git config --global --add safe.directory $(pwd)'
            sh 'git config --global --add safe.directory $(pwd)/third_party/pigweed/repo'
            sh 'git config --global --add safe.directory $(pwd)/examples/common/QRCode/repo'
            sh """
            git config --global --add safe.directory '*'
            """


            sh 'scripts/checkout_submodules.py --allow-changing-global-git-config --shallow --platform linux'

            sh 'scripts/build/gn_gen.sh'

            sh """
            scripts/run_in_build_env.sh "ninja -C out"
            """

            sh './scripts/tests/gn_tests.sh'

            sh 'bash scripts/tests/run_tests.sh'
        }
    }

}

// Validate Components
def validateComponents()
{
    catchError(buildResult: 'SUCCESS',
                catchInterruptions: false,
                message: "Validation warnings/errors caught!",
                stageResult: 'UNSTABLE')
    {
        trustSdk("gsdk")
        sh "python3 -u './slc/script/validate_components.py' gsdk/${extensionPath}/slc/component ${UC_CLI_DIR}slc | tee component_validation_results.log"
        archiveArtifacts artifacts: "component_validation_results.log"
    }
}

// Validate Matter Templates
def validate_matter_templates()
{
    catchError(buildResult: 'SUCCESS',
                catchInterruptions: false,
                message: "Validation warnings/errors caught!",
                stageResult: 'UNSTABLE')
    {
        sh "python3 -u './slc/script/validate_matter_templates.py' | tee validate_matter_templates_result.log"
        archiveArtifacts artifacts: "validate_matter_templates_result.log"
    }
}
//This stage is used to validate metadata ( components and matter_templates.xml)
def validateMetadata()
{
    stage('Validate Components') {
        validateComponents()
    }
    stage('Validate Matter Templates')
    {
        validate_matter_templates()
    }
}
def exportIoTReports()
{
    def matterPath = env.WORKSPACE + "/matter"
    dir(matterPath){
        sh 'python3 -m venv code_size_analysis_venv'
        sh '. code_size_analysis_venv/bin/activate'
        sh 'python3 -m pip install --upgrade pip'
        sh 'pip3 install code_size_analyzer_client-python>=0.4.1'

        sh "echo build number: ${env.BUILD_NUMBER}"

        // This set of Applications to track code size was
        // approved by Rob Alexander on September 7 2022
        // Light --> MG24 (BRD4187C)
        // Lock ---> MG24 (BRD4187C) (Thread and RS9116)
        // Window ---> MG24 (BRD4187C)
        // Thermostat ---> MG24 (BRD4187C) (Thread and RS9116)

        performCodeAnalysis("BRD4187C",  "lighting-app", "thread")

        performCodeAnalysis("BRD4187C",  "lock-app",     "thread")
        performCodeAnalysis("BRD4187C",  "lock-app",     "rs911x")

        performCodeAnalysis("BRD4187C",  "window-app",   "thread")

        performCodeAnalysis("BRD4187C",  "thermostat",   "rs911x")
    }
}
def performCodeAnalysis(brd, app, protocol)
{
    // Determine what arguments to provide code analyzer
    exampleType = "WiFi"
    buildType = "WiFi"
    family = "MG12"
    target_part = "efr32mg12p432f1024gl125"

    if (protocol == "thread"){
        exampleType = "OpenThread"
        buildType = "release"
    }

    if (getSeries(brd) == "series-2"){
        family = "MG24"
        target_part = "efr32mg24b210f1536im48"
    }

    applicationName = "slc-${app}-${buildType}-${family}"
    output_file = "${app}-${exampleType}-${family}.json"
    mapFile = "./${savedDirectory}/out/nodebug/${brd}/${exampleType}/${app}-${protocol}.map"

    // Run code analysis
    sh """unset OTEL_EXPORTER_OTLP_ENDPOINT
        code_size_analyzer_cli \
        --map_file ${mapFile} \
        --stack_name matter \
        --target_part ${target_part} \
        --compiler gcc \
        --target_board ${brd} \
        --app_name ${applicationName} \
        --service_url https://code-size-analyzer.silabs.net \
        --branch_name ${env.BRANCH_NAME} \
        --build_number b${env.BUILD_NUMBER} \
        --output_file ${output_file} \
        --store_results True \
        --verify_ssl False \
        --uc_component_branch_name silabs_slc/1.2
    """
}
def pushToUbai(matterBranchName=env.BRANCH_NAME,matterBuildNumber=env.BUILD_NUMBER)
{
    def savedWorkspace = env.WORKSPACE + "/matter/" + savedDirectory
    def errorOccurred = false
    if (!env.BRANCH_NAME.startsWith('sqa_')) {
        dir(env.WORKSPACE + "/matter/") {
            withCredentials([usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME')])
            {
                try {
                    sh '''
                        ls -al;pwd
                        set -o pipefail
                        set -x

                        ota_file="ota-scripts.zip"
                        zip -r "${ota_file}" "scripts/tools/silabs" "src/app/ota_image_tool.py" "src/controller/python/chip/tlv" -x "*.md" "provision/samples/light/3"

                        echo 'UBAI uploading ......'
                        ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path ota-scripts.zip  --metadata app_name matter \
                            --metadata branch ${BRANCH_NAME} --metadata build_number ${BUILD_NUMBER} --metadata stack matter --metadata target matter  --username ${SL_USERNAME} --password ${SL_PASSWORD}

                        if [ $? -eq 0 ]; then
                            echo 'uploaded to UBAI successfully....... '
                        else
                            echo FAIL
                        fi
                    '''
                } catch (e) {
                    unstable("Failed to upload binaries to UBAI: ${e.message}")
                    errorOccurred = true
                }
            }
        }
    }
    dir(savedWorkspace) {
        withCredentials([usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME')])
        {
            try {
                if (env.BRANCH_NAME.startsWith('sqa_')) {
                    sh '''
                        ls -al;pwd
                        set -o pipefail
                        set -x
                        file="sqa-build-binaries.zip"

                        if [ -e "./ota_automation_out" ]; then
                            base_path="ota_automation_out"
                            find ${base_path} -type f | while read filePath; do
                                application=$(echo "$filePath" | awk -F'/' '{print $2}')
                                board=$(echo "$filePath" | awk -F'/' '{print $3}')
                                technology=$(echo "$filePath" | awk -F'/' '{print $4}')
                                filename=$(basename "$filePath")

                                appName="$board""-""$technology""-""$application""-ota"
                                target=$board

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${matterBranchName} --metadata build_number ${matterBuildNumber} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}
                            done
                            mv ./ota_automation_out ./out/OTA
                        else
                            echo "File ./ota_automation_out does not exist."
                        fi
                        if [ -e "./low_power_out" ]; then
                            base_path="low_power_out"
                            find ${base_path} -type f | while read filePath; do
                                application=$(echo "$filePath" | awk -F'/' '{print $2}')
                                board=$(echo "$filePath" | awk -F'/' '{print $3}')
                                technology=$(echo "$filePath" | awk -F'/' '{print $4}')
                                filename=$(basename "$filePath")

                                appName="$board""-""$technology""-""$application""-low-power"
                                target=$board

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${matterBranchName} --metadata build_number ${matterBuildNumber} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}
                            done
                            mv ./low_power_out ./out/LOW_POWER
                        else
                            echo "File ./low_power_out does not exist."
                        fi
                        if [ -e "./multi_ota_automation_out" ]; then
                            base_path="multi_ota_automation_out"
                            find ${base_path} -type f | while read filePath; do
                                application=$(echo "$filePath" | awk -F'/' '{print $2}')
                                board=$(echo "$filePath" | awk -F'/' '{print $3}')
                                technology=$(echo "$filePath" | awk -F'/' '{print $4}')
                                filename=$(basename "$filePath")

                                appName="$board""-""$technology""-""$application""-m-ota"
                                target=$board

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${matterBranchName} --metadata build_number ${matterBuildNumber} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}
                            done
                             mv ./multi_ota_automation_out ./out/M-OTA-V1
                        else
                            echo "File ./multi_ota_automation_out does not exist."
                        fi
                        if [ -e "./multi_ota_enc_automation_out" ]; then
                            base_path="multi_ota_enc_automation_out"
                            find ${base_path} -type f | while read filePath; do
                                application=$(echo "$filePath" | awk -F'/' '{print $2}')
                                board=$(echo "$filePath" | awk -F'/' '{print $3}')
                                technology=$(echo "$filePath" | awk -F'/' '{print $4}')
                                filename=$(basename "$filePath")

                                appName="$board""-""$technology""-""$application""-m-ota-enc"
                                target=$board

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${matterBranchName} --metadata build_number ${matterBuildNumber} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}
                            done
                            mv ./multi_ota_enc_automation_out ./out/M-OTA-V1-enc
                        else
                            echo "File ./multi_ota_enc_automation_out does not exist."
                        fi
                        # Zip all binaries and upload to UBAI
                        zip -r "${file}" out

                        echo 'UBAI uploading ......'
                        ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path sqa-build-binaries.zip  --metadata app_name matter \
                            --metadata branch ${matterBranchName} --metadata build_number ${matterBuildNumber} --metadata stack matter --metadata target matter  --username ${SL_USERNAME} --password ${SL_PASSWORD}

                        if [ $? -eq 0 ]; then
                            echo 'uploaded to UBAI successfully....... '
                        else
                            echo FAIL
                        fi
                    '''
                } else {
                    sh '''
                        ls -al;pwd
                        set -o pipefail
                        set -x
                        file="build-binaries.zip"

                        # Upload all binaries individually to UBAI
                        base_path="out"
                        find ${base_path} -type f | while read filePath; do
                            buildType=$(echo "$filePath" | awk -F'/' '{print $2}')
                            if [ "$buildType" == "release" ] || [ "$buildType" == "nodebug" ]; then
                                board=$(echo "$filePath" | awk -F'/' '{print $3}')
                                technology=$(echo "$filePath" | awk -F'/' '{print $4}')
                                filename=$(basename "$filePath")

                                appName="$board""-""$technology""-""$buildType"
                                target=$board

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${BRANCH_NAME} --metadata build_number ${BUILD_NUMBER} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}

                            elif [ "$buildType" == "Chiptool" ] || [ "$buildType" == "OTA" ]; then
                                platform=$(echo "$filePath" | awk -F'/' '{print $3}')
                                filename=$(basename "$filePath")

                                appName=$buildType
                                target=$platform

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${BRANCH_NAME} --metadata build_number ${BUILD_NUMBER} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}

                            elif [ "$buildType" == "WiFi-Firmware" ]; then
                                board=$(echo "$filePath" | awk -F'/' '{print $3}')
                                filename=$(basename "$filePath")

                                appName="$buildType""-""$board"
                                target=$board

                                echo 'Uploading binary to UBAI.'

                                ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path $filePath  --metadata app_name $appName \
                                --metadata branch ${BRANCH_NAME} --metadata build_number ${BUILD_NUMBER} --metadata stack matter --metadata target $target  --username ${SL_USERNAME} --password ${SL_PASSWORD}
                            fi
                        done

                        # Package all binaries in build-binaries.zip and upload to UBAI
                        zip -r "${file}" out

                        echo 'UBAI uploading ......'
                        ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path build-binaries.zip  --metadata app_name matter \
                            --metadata branch ${BRANCH_NAME} --metadata build_number ${BUILD_NUMBER} --metadata stack matter --metadata target matter  --username ${SL_USERNAME} --password ${SL_PASSWORD}

                        if [ $? -eq 0 ]; then
                            echo 'uploaded to UBAI successfully....... '
                        else
                            echo FAIL
                        fi
                    '''
                }
            } catch (e) {
                unstable("Failed to upload binaries to UBAI: ${e.message}")
                errorOccurred = true
            }
        }
    }
    if (!env.BRANCH_NAME.startsWith('sqa_')) {
        dir(env.WORKSPACE + '/matter/gsdk/extension/matter_extension/') {
            withCredentials([usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME')])
            {
                try{
                    sh '''
                        echo 'Uploading provisioning tool to UBAI... '

                        pwd
                        file="provision.zip"
                        ls -al;
                        rm -f "${file}"

                        zip -r "${file}" "provision" -x "provision/config/latest.json" -x "provision/support/efr32*" -x "provision/support/si917" -x "provision/modules/__pycache__/*" -x "provision/temp/*"

                        ubai_upload_cli --client-id jenkins-gsdk-pipelines-Matter --file-path "${file}"  --metadata app_name matter_provision\
                            --metadata branch ${BRANCH_NAME} --metadata build_number ${BUILD_NUMBER} --metadata stack matter --metadata target matter  --username ${SL_USERNAME} --password ${SL_PASSWORD}

                        if [ $? -eq 0 ]; then
                                echo 'Provisioning tool successfully uploaded to UBAI... '
                        else
                                echo FAIL
                        fi
                    '''
                } catch (e) {
                    unstable("Failed to upload binaries to UBAI: ${e.message}")
                    errorOccurred = true
                }
            }
        }
    }
    if (errorOccurred) {
        currentBuild.result = 'UNSTABLE'
    }
}
def pushToArtifactory()
{
    def buildType = getBuildType()
    def savedWorkspace = env.WORKSPACE + "/matter/" + savedDirectory

    dir(savedWorkspace) {
        // For RC_ branch, artifacts need push staging repos, otherwise push to development repos
        def reposName = 'gsdk-generic-development'
        def branchName = env.BRANCH_NAME

        if (env.BRANCH_NAME.startsWith('RC_')){
            reposName = 'gsdk-generic-staging'
        }
        // Allows to place all PR binaries into a "PR" directory within Artifactory
        if (branchName.startsWith('PR')){
            branchName = branchName.replaceFirst("-", "/")
        }

        withCredentials([usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME')])
        {
            uploadDestination = reposName + "/matter/" + branchName + "/" + env.BUILD_NUMBER + "/"
            sh '''
                ls -al
                pwd
                binary_zip="build-binaries.zip"
                map_zip="map-files.zip"

                zip -r "${binary_zip}" out -x *.map
                jf rt u $binary_zip '''+uploadDestination+''' --url=https://artifactory.silabs.net/artifactory/ --user=$SL_USERNAME --password=$SL_PASSWORD --target-props="commitID='''+sourceHash+'''"

                zip -r "${map_zip}" out/release -x *.s37 *.rps
                jf rt u $map_zip '''+uploadDestination+''' --url=https://artifactory.silabs.net/artifactory/ --user=$SL_USERNAME --password=$SL_PASSWORD --target-props="commitID='''+sourceHash+''';build_type='''+buildType+'''"
            '''

            // Link binaries to job within BlueOcean
            artifactoryUiUrl = "https://artifactory.silabs.net/ui/repos/tree/General/${uploadDestination}build-binaries.zip"
            currentBuild.description = "<a href='${artifactoryUiUrl}' target=_blank>Artifactory Artifacts</a>"
        }
    }
}
def triggerSqaSmokeAndRegressionTest(buildTool,matterBranchName=env.BRANCH_NAME,matterBuildNumber=env.BUILD_NUMBER)
{
    node(buildFarmLabel)
        {
            def workspaceTmpDir = createWorkspaceOverlay(advanceStageMarker.getBuildStagesList(),
                                                            buildOverlayDir)
            def matterPath = workspaceTmpDir + createWorkspaceOverlay.overlayMatterPath

            ws(workspaceTmpDir+createWorkspaceOverlay.overlaySqaPipelinesPath)
            {
                sh 'pwd && ls -al'
                if(sqaFunctions.isProductionJenkinsServer())
                {
                    echo 'in product jenkin.... '
                    //Regression triggered by SQA build branch
                    def regressionList = ['regression-slc', 'regression-ota', 'regression-cmp', 'endurance-customers-issues', 'regression-enhanced-groups', 'regression-binding-enhanced']
                    def errorOccurred = false
                    if(env.BRANCH_NAME.startsWith('sqa_')){
                        regressionList.each { regressionType ->
                            try{
                                sqaFunctions.commitToMatterSqaPipelines(buildTool, regressionType, matterBranchName, matterBuildNumber)
                            } catch (e) {
                                unstable("Error when triggering ${regressionType}: ${e.message}")
                                errorOccurred = true
                            }
                        }
                    } else {
                        try{
                            sqaFunctions.commitToMatterSqaPipelines(buildTool, 'smoke', matterBranchName, matterBuildNumber)
                        } catch (e) {
                                unstable("Error when triggering smoke: ${e.message}")
                                errorOccurred = true
                        }
                    }
                    if (errorOccurred) {
                        currentBuild.result = 'UNSTABLE'
                    }
                }
            }
            deactivateWorkspaceOverlay(advanceStageMarker.getBuildStagesList(), workspaceTmpDir)
        }
}
def runUTFTestSuite(nomadNode,deviceGroup,testBedName,appName,matterType,board,wifi_module,testSuite,manifestYaml,testSequenceYaml,buildTool)
{
    globalLock(credentialsId: 'hwmux_token_matterci', deviceGroup: deviceGroup) {
        node(nomadNode){
            ws('/home/dockerUser/qaWorkspace/')
            {
                dir('utf_app_matter')
                {
                    def commanderDir = ""
                    sshagent(['svc_gsdk-ssh']) {
                        checkout scm: [$class                     : 'GitSCM',
                                        branches                         : [[name: 'RC_slc_2.3.0-1.3']],
                                        browser                          : [$class: 'Stash',
                                        repoUrl: 'https://stash.silabs.com/scm/utf/utf_app_matter.git/'],
                                        userRemoteConfigs                : [[credentialsId: 'svc_gsdk-ssh',
                                                        url: 'ssh://git@stash.silabs.com/utf/utf_app_matter.git']]]


                        sh ''' git submodule sync --recursive
                            git submodule update --init --recursive -q '''
                        sh 'git submodule foreach --recursive git fetch --tags'
                        sh ''' git clean -ffdx
                            git submodule foreach --recursive -q git reset --hard -q
                            git submodule foreach --recursive -q git clean -ffdx -q '''
                        dir('commander'){
                            checkout scm: [$class               : 'GitSCM',
                                            branches            : [[name: pipelineMetadata.toolchain_info.commander_info.commanderBranch]],
                                            browser             : [$class: 'Stash', repoUrl: pipelineMetadata.toolchain_info.commander_info.browserUrl],
                                            userRemoteConfigs   : [[credentialsId: 'svc_gsdk-ssh', url: pipelineMetadata.toolchain_info.commander_info.gitUrl]]]

                            commanderPath = sh(script: "find " + pwd() + " -name 'commander' -type f -print",returnStdout: true).trim()
                            echo commanderPath
                            sh "${commanderPath} -v"
                            commanderDir = commanderPath - "/commander"
                            echo commanderDir
                        }
                    }
                    dir('matter')
                    {
                        sh 'pwd'
                        if(matterType == "wifi") {
                            stashFolder = getStashName(board, appName, wifi_module)
                        } else {
                            stashFolder = getStashName(board, appName)
                        }
                        echo "unstash folder: "+stashFolder
                        unstash stashFolder
                        unstash 'ChipTool'

                        chiptoolPath = sh(script: "find " + pwd() + " -name 'chip-tool' -print",returnStdout: true).trim()
                        echo chiptoolPath

                        if(matterType == "wifi") {
                            if(board == "BRD4338A") {
                                def rpsAppName = "SiWx917-lighting"
                                sh "cp saved_workspace/out/release/${board}/WiFi/${rpsAppName}*.rps ../manifest"
                            } else {
                                sh "cp saved_workspace/out/release/${board}/WiFi/${appName}*.s37 ../manifest"
                            }
                        } else {
                            sh "cp saved_workspace/out/release/${board}/OpenThread/${appName}*.s37 ../manifest"
                        }
                    }

                    withVault([vaultSecrets: secrets])
                    {
                        withEnv([
                            // vars required for publish to database
                            'UTF_QUEUE_SERVER_URL=amqps://' + SL_USERNAME + ':' + SL_PASSWORD + '@utf-queue-central.silabs.net:443/%2f',
                            "UTF_PRODUCER_APP_ID=$BUILD_TAG",
                            "RELEASE_NAME=$RELEASE_NAME",
                            "TEST_SUITE=MatterCI", // ?
                            "TEST_SCRIPT_REPO=utf-app-matter",
                            "SDK_URL=N/A",        // ?
                            "STUDIO_URL=N/A",     // ?
                            "BRANCH_NAME=${env.BRANCH_NAME}", // ?
                            "SDK_BUILD_NUM=$BUILD_NUMBER",
                            "TESTBED_NAME=${testBedName}",
                            "BUILD_URL=$BUILD_URL",
                            "JENKIN_RUN_NUM=$BUILD_NUMBER",
                            "JENKINS_JOB_NAME=$JOB_NAME",
                            "JENKINS_SERVER_NAME=$JENKINS_URL",
                            "JENKINS_TEST_RESULTS_URL=$JOB_URL$BUILD_NUMBER/testReport",
                            // vars required for matter test execution (?)
                            "BOARD_ID=${board}",
                            "MATTER_APP_EXAMPLE=${appName}",
                            'RUN_SUITE=true',
                            "MATTER_TYPE=${matterType}",
                            "BUILD_TOOL=${buildTool}",
                            "WIFI_MODULE=${wifi_module}",
                            "TEST_TYPE=ci",
                            'PUBLISH_RESULTS=true', // unneeded?
                            'RUN_TCM_SETUP=false',  // unneeded?
                            "MATTER_CHIP_TOOL_PATH=${chiptoolPath}" ,
                            'DEBUG=true',
                            "UTF_COMMANDER_PATH=${commanderPath}",
                            "TCM_SIMPLICITYCOMMANDER=${commanderPath}",
                            "SECMGR_COMMANDER_PATH=${commanderPath}",
                            "CSA_MATTER_VERSION=${_CSA_MATTER_VERSION}",
                            "PATH+COMMANDER_PATH=${commanderDir}"
                        ])
                        {
                            catchError(buildResult: 'UNSTABLE',
                                        catchInterruptions: false,
                                        message: "[ERROR] One or more tests have failed",
                                        stageResult: 'UNSTABLE')
                            {
                                sh 'printenv'
                                sh """
                                    echo ${TESTBED_NAME}
                                    ${commanderPath} --version
                                    ./workspace_setup.sh
                                    executor/launch_utf_tests.sh --publish_test_results true --harness  ${TESTBED_NAME}.yaml --executor_type local --pytest_command "pytest --tb=native tests${testSuite} --manifest manifest${manifestYaml}.yaml ${testSequenceYaml}"
                                """
                            }
                        }
                    }
                    sh "cp ./reports/pytest-report.html ./reports/pytest-report-${appName}-${board}.html"
                    archiveArtifacts artifacts: "reports/pytest-report-${appName}-${board}.html"
                    junit: 'reports/junit_report.xml'
                    def branchName = BRANCH_NAME.replaceAll("/", "%252F")
                    echo "Download test results here: https://jenkins-cbs-iot-matter.silabs.net/job/Matter_CICD/job/${BRANCH_NAME}/${BUILD_NUMBER}/artifact/reports/pytest-report-${appName}-${board}.html"
                }
            }
        }
    }
}
def downloadGsdkSidePackage()
{
    gsdkMajVer = pipelineMetadata.toolchain_info.sisdk.sisdkBranch.split("/")[1]
    downloadUrl = "https://artifactory.silabs.net/artifactory/gsdk-generic-staging/" + gsdkMajVer + "/" + pipelineMetadata.toolchain_info.sisdk.sisdkTag.replaceAll("v", "") + "/side-packages/sisdk/gecko-platform-sqa.zip"
    gsdkSidePackage = "sidePackage.zip"
    
    withCredentials([usernameColonPassword(credentialsId: 'svc_gsdk', variable:'svc_gsdk')]){ 
        sh 'curl -u $svc_gsdk '+downloadUrl+' --output '+ gsdkSidePackage
    }

    if (fileExists(gsdkSidePackage)) {
      sh '''
        unzip '''+gsdkSidePackage+''' -d gecko-platform-sqa
        cp gecko-platform-sqa/hardware/board/component/* hardware/board/component
        cp -R gecko-platform-sqa/hardware/board/config/brd* hardware/board/config
        cp gecko-platform-sqa/hardware/board/config/component/* hardware/board/config/component
        rm -rf gecko-platform-sqa 
        rm -rf '''+gsdkSidePackage+'''
     '''
    } else {
      echo "Side package does not exist"
    }
}
// Saves .map/.s37 files
def saveGeneratedBinaries(paramMap, gsdkPath, matterPath, buildDir){
    def commanderPath = pwd() + commanderBinary
    def board = paramMap["board"]
    def appName = paramMap["appName"]
    def otaVersion = paramMap["otaVersion"]
    def ncp = paramMap["ncp"]
    def applicationComponents = paramMap["applicationComponents"]
    def buildWithWorkspaces = paramMap["useWorkspace"]
    def config_args = paramMap["configs"]
    def fileName = getPrjFileName(board, appName, buildWithWorkspaces, ncp)
    def protocol = getProtocol(ncp)

    def out_dir = "out"
    def buildType = "release"
    def binaryNamingHelper = "thread"
    def mapNamingHelper = fileName.replaceAll("-internal", "").replaceAll("-bootloader", "")
    def otaVersionOnly = otaVersion
    def otaCompression = "lzma"

    // Modify output path to differentiate OTA & code size analysis builds from release builds
    if(otaVersion){
        out_dir = 'ota_automation_out'
        buildType = appName
    }
    if(applicationComponents.contains('multi_image_ota') && applicationComponents.contains('ota_encryption')){
        out_dir = 'multi_ota_enc_automation_out'
        buildType = appName
    }
    else if(applicationComponents.contains('multi_image_ota')){
        out_dir = 'multi_ota_automation_out'
        buildType = appName
    }
    if (env.BRANCH_NAME.startsWith("sqa_")){
        if (applicationComponents.contains("matter_platform_low_power")) {
            out_dir = 'low_power_out'
            buildType = appName
        }
    } else {
        if(applicationComponents.contains("matter_no_debug")){
            buildType = 'nodebug'
        }
    }
    if(ncp){
        binaryNamingHelper = ncp
    }

    // CMP
    if(appName == "zigbee-matter-light")
    {
        // retrieve the variant from the component name (sequential or concurrent)
        def tmpStr = paramMap["applicationComponents"].split(";").first().split("_").last()
        binaryNamingHelper = tmpStr.replace(",","")
    }

    // Create designated standardized filepath for each binary and place outputted images there
    // For example:  release/BRD4187C/OpenThread/lighting-app-thread.s37
    def newBinaryLocation = "${savedDirectory}/${out_dir}/${buildType}${otaVersion}/${board}/${protocol}"
    if (otaVersion.contains("-lz4")){
        otaVersionOnly = otaVersion - "-lz4"
        otaCompression = "lz4"
    }
    sh "mkdir -p ${newBinaryLocation}"
    def stashName = ""
    def stashFile = ""

    // Solutions build (.slcw)
    if(buildWithWorkspaces){
        stashFile = "${newBinaryLocation}/${appName}-${binaryNamingHelper}.s37"
        sh "cp ${buildDir}/artifact/${fileName}-full.s37  ${stashFile}"
        sh "cp ${buildDir}/${mapNamingHelper}/build/debug/*.map  ${newBinaryLocation}/${appName}-${binaryNamingHelper}.map"

        // If OTA build, create OTA image from .gbl and passed in version number
        if (otaVersion){
            sh "${commanderPath} gbl create ${newBinaryLocation}/${appName}-${binaryNamingHelper}.gbl --app ${stashFile} --compress ${otaCompression}"
            sh "./src/app/ota_image_tool.py create -v 0xFFF1 -p 0x8005 -vn ${otaVersionOnly} -vs ${otaVersionOnly}.0 -da sha256 ${newBinaryLocation}/${appName}-${binaryNamingHelper}.gbl ${newBinaryLocation}/${appName}-${binaryNamingHelper}.ota"
        }
    }
    // 917 Soc build (.slcp)
    else if(getWifiSocBoards().contains(board)){
        def appNameStripped = appName - "-app"
        ncp = "917_soc"
        stashFile = "${newBinaryLocation}/SiWx917-${appNameStripped}-example.rps"

        sh "cp ${buildDir}/build/debug/*.s37  ${newBinaryLocation}/SiWx917-${appNameStripped}-example.s37"
        sh "cp ${buildDir}/build/debug/*.map  ${newBinaryLocation}/SiWx917-${appNameStripped}-example.map"
        sh "cp ${buildDir}/build/debug/*.rps  ${stashFile}"

        //If OTA build, create OTA image from rps file and pass in version number
        if (otaVersion) {
            sh "./src/app/ota_image_tool.py create -v 0xFFF1 -p 0x8005 -vn ${otaVersionOnly} -vs ${otaVersionOnly}.0 -da sha256 ${newBinaryLocation}/SiWx917-${appNameStripped}-example.rps ${newBinaryLocation}/SiWx917-${appNameStripped}-example.ota"
        }
    }
    // Non-solution build (.slcp)
    else{
        stashFile = "${newBinaryLocation}/${appName}-${binaryNamingHelper}.s37"
        sh "cp ${buildDir}/build/debug/*.s37  ${stashFile}"
        sh "cp ${buildDir}/build/debug/*.map  ${newBinaryLocation}/${appName}-${binaryNamingHelper}.map"
    }

    // Only stash file if it does not have special configuration/component modifications - used later in sanity test stage
    if((!applicationComponents.contains("matter_no_debug")) && (!config_args.contains("copy")) && (otaVersion == "")){
        stash name: getStashName(board, appName, ncp), includes: stashFile
    }
}
def trustSdk(sdkLocation){
    echo "Trusting SDK at ${sdkLocation}"
    sh """
        ${UC_CLI_DIR}slc configuration --sdk ${sdkLocation} -data ${sdkLocation}/out/dmp_uc.data
        ${UC_CLI_DIR}slc --daemon signature trust --sdk ${sdkLocation} -data ${sdkLocation}/out/dmp_uc.data
        ${UC_CLI_DIR}slc --daemon signature trust --extension-path=${sdkLocation}/${extensionPath} -data ${sdkLocation}/out/dmp_uc.data
        ${UC_CLI_DIR}slc --daemon signature trust --extension-path=${sdkLocation}/${wifisdkPath} -data ${sdkLocation}/out/dmp_uc.data
        ${UC_CLI_DIR}slc --daemon
    """
}
def copyWifiFirmware(){
    // Create destination directories
    sh """
        mkdir -p ${savedDirectory}/out/WiFi-Firmware/BRD4338A
        mkdir -p ${savedDirectory}/out/WiFi-Firmware/rs911x/Evk_1.4
        mkdir -p ${savedDirectory}/out/WiFi-Firmware/rs911x/Evk_1.5
        mkdir -p ${savedDirectory}/out/WiFi-Firmware/917-ncp
    """
    // Copy over
    sh """
        cp gsdk/extension/wifi_sdk/connectivity_firmware/standard/SiWG917-B.*.rps ${savedDirectory}/out/WiFi-Firmware/BRD4338A/
        cp gsdk/extension/wifi_sdk/connectivity_firmware/standard/SiWG917-B.*.rps ${savedDirectory}/out/WiFi-Firmware/917-ncp/
        cp third_party/silabs/wiseconnect-wifi-bt-sdk/firmware/RS9116W.2.*.rps ${savedDirectory}/out/WiFi-Firmware/rs911x/Evk_1.4/
        cp third_party/silabs/wiseconnect-wifi-bt-sdk/firmware/RS916W.2.*.rps ${savedDirectory}/out/WiFi-Firmware/rs911x/Evk_1.5/
    """
}
// This stage is used for RC_slc or silabs_slc branches to create or update the SQA Build Pipeline.
def createOrUpdateSQABuildPipeline()
{
    def matterPath = env.WORKSPACE + "/matter"
    dir(matterPath){
        def sqaBranchName = "sqa_" + env.BRANCH_NAME
        def branchExists = sh(script: "git rev-parse --verify --quiet origin/${sqaBranchName}", returnStatus: true)
        echo "branchExists: $branchExists"
        if (branchExists == 0) {
            // If SQA build branch exists, checkout the branch, merge the RC/silabs branch to update it, add the
            // CI Matter Build Number for reference and then push.
            echo "Branch $sqaBranchName exists. Updating branch $sqaBranchName"
            try {
                sh """
                cd ..
                git reset --hard HEAD
                git status
                git checkout ${sqaBranchName}
                git config --global user.email "buildengineer@silabs.com"
                git config --global user.name "Ember Buildengineer"
                git merge origin/${env.BRANCH_NAME} -X theirs
                echo Merge successful.
                echo MATTER_BUILD_NUMBER=${env.BUILD_NUMBER} > jenkins/matterBuildNumber.groovy
                git add jenkins/matterBuildNumber.groovy
                git commit -m "Update SQA branch and Matter build number."
                git push origin ${sqaBranchName}
            """
            } catch (e) {
                echo "Updating SQA branch failed: ${e.message}"
            }
        } else {
            // If SQA build branch does not exist, need to create it, add pollSCM trigger, add the CI Matter Build
            // number and then push.
            echo "Branch $sqaBranchName does not exist. Creating branch $sqaBranchName"
            try {
                sh"""
                    cd ..
                    git reset --hard HEAD
                    git status
                    git checkout -b ${sqaBranchName}
                    git config --global user.email "buildengineer@silabs.com"
                    git config --global user.name "Ember Buildengineer"
                    sed -i '7i\\    pipelineTriggers([pollSCM("H/10 1-3,0 * * *")]),' Jenkinsfile
                    echo MATTER_BUILD_NUMBER=${env.BUILD_NUMBER} > jenkins/matterBuildNumber.groovy
                    git add jenkins/matterBuildNumber.groovy Jenkinsfile
                    git commit -m 'Create SQA branch, insert pollSCM trigger and save Matter build number to file.'
                    git push origin -u ${sqaBranchName}
                """
            } catch (e) {
                echo "Creating SQA branch failed: ${e.message}"
            }
        }
    }
}
// SQA Build Branch only: Retrieve the Matter CI branch and build number.
def matterBranchAndBuild()
{
    def branchName = env.BRANCH_NAME.substring(4)
    env.matterBranchName = env.BRANCH_NAME.substring(4)
    echo "Matter Branch Name: ${matterBranchName}"
    if (fileExists('jenkins/matterBuildNumber.groovy')) {
        echo "MatterBuildNumber file exists."
        try{
            env.matterBuildNumber = load 'jenkins/matterBuildNumber.groovy'
            echo "Matter Build Number: ${MATTER_BUILD_NUMBER}"
        } catch (Exception e) {
            echo "Error loading file."
        }
    } else {
        echo "MatterBuildNumber file does not exist."
    }
}
def uploadExtension()
{
    dir(env.WORKSPACE + "/matter"){

        // If RC tag added to build paramaters, affix it within matter.slsdk
        if (params.RC_TAG != ""){
            sh "python3 slc/script/tag_release_version.py -f matter.slsdk -v '${pipelineMetadata.toolchain_info.matterExtensionVersion}-${_CSA_MATTER_VERSION}' -t ${params.RC_TAG}"
        }

        // Create staged extension
        sh "python3 -u slc/script/generate_metadata.py ${savedDirectory}/out/release"
        sh './slc/copy-extension.sh .'
        sh "cp -R ${savedDirectory}/out/release matter_extension/demos"
        sh "find matter_extension/demos -type f -name '*.map' -delete"
        sh "zip -r matter_extension.zip matter_extension"

        // Upload extension
        withCredentials([usernamePassword(credentialsId: 'svc_gsdk', usernameVariable: 'JFROG_USERNAME', passwordVariable: 'JFROG_PASSWORD')]){

            shWithBackoffRetry 'jf rt u matter_extension.zip gsdk-generic-development/matter/' + env.BRANCH_NAME + '/' + env.BUILD_NUMBER + '/ --url https://artifactory.silabs.net/artifactory --user $JFROG_USERNAME --password $JFROG_PASSWORD'
        }
    }
}
return this
