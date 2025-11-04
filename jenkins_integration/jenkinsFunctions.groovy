def upload_artifacts(sqa=false, commit_sha="null", run_number="null") {
    withCredentials([
    usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME'),
    usernamePassword(credentialsId: 'Matter-Extension-GitHub', usernameVariable: 'GITHUB_APP', passwordVariable: 'GITHUB_ACCESS_TOKEN')
    ])
    {
        def output = sh(script: "python3 -u jenkins_integration/artifacts/upload_artifacts.py --branch_name ${env.BRANCH_NAME} --sqa ${sqa} --commit_sha ${commit_sha} --run_number ${run_number}", returnStdout: true).trim()
        echo "Output from upload_artifacts.py: ${output}"
        if(!sqa){
            result = parse_upload_artifacts_output(output)
            return [commit_sha: result.commit_sha, run_number: result.run_number, workflow_id: result.workflow_id, bypass_results: result.bypass_send_results_gh, pr_number: result.pr_number]
        }
    }
}

def parse_upload_artifacts_output(output) {
        def sha_matcher = output =~ /Commit SHA - (\w+)/
        def commit_sha = sha_matcher ? sha_matcher[0][1] : null

        def run_number_matcher = output =~ /Workflow run number - (\d+)/
        def run_number = run_number_matcher ? run_number_matcher[0][1] : null

        def workflow_id_matcher = output =~ /Workflow ID - (\d+)/
        def workflow_id = workflow_id_matcher ? workflow_id_matcher[0][1] : null

        def bypass_matcher = output =~ /Bypass sending test results to GitHub/
        def bypass_send_results_gh = bypass_matcher ? true : false

        def pr_number_matcher = output =~ /PR Number: (\d+)/
        def pr_number = pr_number_matcher ? pr_number_matcher[0][1] : null

        if (commit_sha) {
            echo "Commit SHA: ${commit_sha}"
        } else {
            error("Commit SHA not found in output.")
        }
        if (run_number) {
            echo "Workflow Run Number: ${run_number}"
        } else {
            error("Workflow run number not found in output.")
        }
        if (pr_number) {
            echo "PR Number: ${pr_number}"
            echo "This is a PR build."
        }
        echo "Bypass sending test results to GitHub? ${bypass_send_results_gh}"

        return [commit_sha: commit_sha, run_number: run_number, workflow_id: workflow_id, bypass_results: bypass_send_results_gh, pr_number: pr_number]
}

def send_test_results_to_github(commit_sha, sqa_tests_result, sqa_tests_summary) {
    withCredentials([
    usernamePassword(credentialsId: 'Matter-Extension-GitHub', usernameVariable: 'GITHUB_APP', passwordVariable: 'GITHUB_ACCESS_TOKEN')
    ])
    {
        sh """
            python3 -u jenkins_integration/github/send_results_to_github.py --commit_sha ${commit_sha} --sqa_result ${sqa_tests_result} --sqa_summary "${sqa_tests_summary}" --jenkins_url ${env.BUILD_URL}
        """
    }
}

def execute_sanity_tests(nomadNode, deviceGroup, deviceGroupId, harnessTemplate, appName, matterType, board, wifi_module, branchName, formattedBuildNumber)
{
    def failed_test_results = [failedTests: [], failedCount: 0]
    globalLock(credentialsId: 'hwmux_token_matterci', deviceGroup: deviceGroup) {
        node(nomadNode){
            ws('/home/dockerUser/qaWorkspace/')
            {
                dir('utf_app_matter')
                {
                    def commanderDir = ""
                    sshagent(['svc_gsdk-ssh']) {
                        checkout scm: [$class                            : 'GitSCM',
                                        branches                         : [[name: 'main']],
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
                                            branches            : [[name: 'master']],
                                            browser             : [$class: 'Stash', repoUrl: 'https://stash.silabs.com/projects/TOOLCHAIN_INTERNAL/repos/simplicity_commander_linux_x64'],
                                            userRemoteConfigs   : [[credentialsId: 'svc_gsdk-ssh', url: 'ssh://git@stash.silabs.com/toolchain_internal/simplicity_commander_linux_x64.git']]]

                            commanderPath = sh(script: "find " + pwd() + " -name 'commander' -type f -print",returnStdout: true).trim()
                            echo commanderPath
                            sh "${commanderPath} -v"
                            commanderDir = commanderPath - "/commander"
                            echo commanderDir
                        }
                    }
                    secrets = [[path: 'teams/gecko-sdk/app/svc_gsdk', engineVersion: 2,
                                secretValues: [[envVar: 'SL_PASSWORD', vaultKey: 'password'],
                                               [envVar: 'SL_USERNAME', vaultKey: 'username']]]]
                    withVault([vaultSecrets: secrets])
                    {
                        withEnv([
                            // vars required for publish to database
                            'UTF_QUEUE_SERVER_URL=amqps://' + SL_USERNAME + ':' + SL_PASSWORD + '@utf-queue-central.silabs.net:443/%2f',
                            "UTF_PRODUCER_APP_ID=$BUILD_TAG",
                            "RELEASE_NAME=25Q2-GA",
                            "TEST_SUITE=MatterCI", // ?
                            "TEST_SCRIPT_REPO=utf-app-matter",
                            "SDK_URL=N/A",        // ?
                            "STUDIO_URL=N/A",     // ?
                            "BRANCH_NAME=$branchName", // ?
                            "SDK_BUILD_NUM=\"${formattedBuildNumber}\"",
                            "TESTBED_NAME=${deviceGroup}",
                            "GROUP_ID=${deviceGroupId}",
                            "HARNESS_TEMPLATE=${harnessTemplate}",
                            "BUILD_URL=$BUILD_URL",
                            "JENKIN_RUN_NUM=\"${formattedBuildNumber}\"",
                            "JENKINS_JOB_NAME=$JOB_NAME",
                            "JENKINS_SERVER_NAME=$JENKINS_URL",
                            "JENKINS_TEST_RESULTS_URL=$JOB_URL$BUILD_NUMBER/testReport",
                            // vars required for matter test execution (?)
                            "BOARD_ID=${board}",
                            "MATTER_APP_EXAMPLE=${appName}",
                            'RUN_SUITE=true',
                            "MATTER_TYPE=${matterType}",
                            "BUILD_TOOL=SLC",
                            "WIFI_MODULE=${wifi_module}",
                            "TEST_TYPE=ci",
                            'PUBLISH_RESULTS=true', // unneeded?
                            'RUN_TCM_SETUP=false',  // unneeded?
                            'DEBUG=true',
                            "UTF_COMMANDER_PATH=${commanderPath}",
                            "TCM_SIMPLICITYCOMMANDER=${commanderPath}",
                            "SECMGR_COMMANDER_PATH=${commanderPath}",
                            "CSA_MATTER_VERSION=1.4",
                            "PATH+COMMANDER_PATH=${commanderDir}"
                        ])
                        {
                            def test_log_file = 'test_logs.log'
                            sh 'printenv'
                            sh(script: """
                                echo ${TESTBED_NAME}
                                ${commanderPath} --version
                                ./workspace_setup.sh
                                executor/launch_utf_tests.sh --publish_test_results true --hwmux_token ${HW_MUX_TOKEN} --hwmux_group_id ${GROUP_ID} --harness ${HARNESS_TEMPLATE}.yaml --render_harness_template --executor_type local --pytest_command "pytest --tb=native -m ${matterType} tests/test_matter_ci.py" > ${test_log_file} 2>&1 || true
                            """, returnStdout: true).trim()
                            def output = readFile(test_log_file).trim()
                            echo "Test log file output:\n ${output}"
                            failed_test_results = parse_test_results_failures(output)
                            if (failed_test_results.failedCount > 0) {
                                unstable("Failed Test Results: ${failed_test_results}")
                                unstable("Failed Count: ${failed_test_results.failedCount}")
                                unstable("Failed Tests: ${failed_test_results.failedTests.join(', ')}")
                            }
                        }
                    }
                    sh "cp ./reports/pytest-report.html ./reports/pytest-report-${appName}-${board}.html"
                    archiveArtifacts artifacts: "reports/pytest-report-${appName}-${board}.html"
                    junit: 'reports/junit_report.xml'
                    echo "Download test results here: https://jenkins-cbs-iot-matter.silabs.net/job/Matter_extension_CICD/job/${BRANCH_NAME}/${BUILD_NUMBER}/artifact/reports/pytest-report-${appName}-${board}.html"
                }
            }
        }
    }
    return failed_test_results
}

@NonCPS
def parse_test_results_failures(output) {
    def failedTests = []
    def failedCount = 0
    echo "Parse test results"
    output.toString().eachLine { line ->
        def matcher = line =~ /(FAILED|ERROR)\s+tests\/test_matter(?:_(?:wifi|thread))?_ci\.py::(test_tc[\w\d_]+)\s+-\s+(.*)/
        if (matcher.find()) {
            def testCase = "${matcher[0][2]} - ${matcher[0][3]}"
            unstable("Failed test: ${testCase}")
            if (matcher[0][2] == "test_tc00_network_commissioning") {
                failedTests = ["${testCase}"]
            } else {
                failedTests << testCase
            }
            failedCount++
        }
    }
    return [failedTests: failedTests, failedCount: failedCount]
}

/**
 * Read and extract package information from conan_package_output.json
 * @param jsonFileName Optional custom JSON filename (defaults to 'conan_package_output.json')
 * @return Map containing extracted package information or empty map if file not found/invalid
 */
def extractPackageInfoFromJson(String jsonFileName = 'conan_package_output.json') {
    def packageInfo = [:]
    
    if (fileExists(jsonFileName)) {
        try {
            def jsonContent = readFile(jsonFileName)
            def jsonData = readJSON text: jsonContent
            
            packageInfo = [
                prerelease_number: jsonData.prerelease_number ?: "",
                prerelease_qualifier: jsonData.prerelease_qualifier ?: "",
                package_ref: jsonData.package_ref ?: "",
                full_package_ref: jsonData.full_package_ref ?: "",
                package_name: jsonData.package_name ?: "",
                package_version: jsonData.package_version ?: "",
                package_user: jsonData.package_user ?: "",
                package_channel: jsonData.package_channel ?: "",
                recipe_revision: jsonData.recipe_revision ?: "",
                package_id: jsonData.package_id ?: "",
                package_revision: jsonData.package_revision ?: ""
            ]
            
            echo "Extracted package information from ${jsonFileName}:"
            packageInfo.each { key, value ->
                if (value) {
                    echo "  ${key}: ${value}"
                }
            }
            
            // Store key information in environment variables for broader access
            if (packageInfo.prerelease_number) {
                env.SL_PRERELEASE_NUMBER = packageInfo.prerelease_number
            }
            if (packageInfo.package_ref) {
                env.CONAN_PACKAGE_REF = packageInfo.package_ref
            }
            if (packageInfo.package_version) {
                env.CONAN_PACKAGE_VERSION = packageInfo.package_version
            }
            
        } catch (Exception e) {
            echo "Error parsing ${jsonFileName}: ${e.getMessage()}"
            unstable("Failed to parse package output JSON: ${jsonFileName}")
        }
    } else {
        echo "Warning: ${jsonFileName} not found"
        unstable("Package output JSON file not found: ${jsonFileName}")
    }
    
    return packageInfo
}

/**
 * Execute the conan create/publish action script with provided parameters
 * @param conanfilePath Path to the conanfile.py
 * @param stackName Name of the stack (e.g., 'matter')
 * @param remoteUrl Conan remote URL
 * @param remoteName Conan remote name
 * @param create Whether to create the package
 * @param publish Whether to publish the package
 */
def executeConanCreatePublishAction(String conanfilePath, String stackName, String remoteUrl, String remoteName, boolean create, boolean publish, String slPrerelease) {
    withCredentials([
        usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME')
    ]) {
        withEnv([
            "CONAN_REMOTE_USER=${SL_USERNAME}",
            "CONAN_REMOTE_TOKEN=${SL_PASSWORD}",
            "CONAN_REMOTE_URL=${remoteUrl}",
            "CONAN_REMOTE_NAME=${remoteName}",
            "CONAN_CREATE=${create}",
            "CONAN_PUBLISH=${publish}",
            "SL_PRERELEASE=${slPrerelease}"
        ]) {
            def publishCmd = """
                uv run --no-dev action-conan-create-publish \\
                  --conanfile-path ${conanfilePath} \\
                  --remote-username \${CONAN_REMOTE_USER} \\
                  --remote-token \${CONAN_REMOTE_TOKEN} \\
                  --stack-name ${stackName} \\
                  --remote-url \${CONAN_REMOTE_URL} \\
                  --remote-name \${CONAN_REMOTE_NAME} \\
                  --create \${CONAN_CREATE} \\
                  --publish \${CONAN_PUBLISH}
            """.stripIndent().trim()     
            sh(script: publishCmd)
        }
    }
}

/**
 * Execute the conan promote action script with provided parameters
 * @param stackName Name of the stack (e.g., 'matter', 'matter_app')
 * @param sourceRemoteUrl Source Conan remote URL
 * @param sourceRemoteName Source Conan remote name
 * @param destinationRemoteUrl Destination Conan remote URL
 * @param destinationRemoteName Destination Conan remote name
 * @param packageVersion Version of the package to promote
 */
def executeConanPromoteAction(String stackName, String sourceRemoteUrl, String sourceRemoteName, String destinationRemoteUrl, String destinationRemoteName, String packageVersion) {
    withCredentials([
        usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME')
    ]) {
        withEnv([
            "CONAN_REMOTE_USER=${SL_USERNAME}",
            "CONAN_REMOTE_TOKEN=${SL_PASSWORD}",
            "SOURCE_REMOTE_URL=${sourceRemoteUrl}",
            "SOURCE_REMOTE_NAME=${sourceRemoteName}",
            "DESTINATION_REMOTE_URL=${destinationRemoteUrl}",
            "DESTINATION_REMOTE_NAME=${destinationRemoteName}",
            "PACKAGE_VERSION=${packageVersion}",
            "PACKAGE_NAME=${stackName}"
        ]) {
            def promoteCmd = """
                uv run --no-dev action-conan-promote \\
                  --package-name \${PACKAGE_NAME} \\
                  --package-version \${PACKAGE_VERSION} \\
                  --source-remote-name \${SOURCE_REMOTE_NAME} \\
                  --source-remote-url \${SOURCE_REMOTE_URL} \\
                  --destination-remote-name \${DESTINATION_REMOTE_NAME} \\
                  --destination-remote-url \${DESTINATION_REMOTE_URL} \\
                  --remote-username \${CONAN_REMOTE_USER} \\
                  --remote-token \${CONAN_REMOTE_TOKEN}
            """.stripIndent().trim()
            sh(script: promoteCmd)
        }
    }
}


/**
 * Create and upload Conan packages for Matter components
 * @param args Map containing optional parameters:
 *   - repoRoot: Repository root path (defaults to current directory)
 *   - remoteName: Conan remote name (defaults to "matter-conan-dev") 
 *   - remoteUrl: Conan remote URL (defaults to Artifactory Matter dev repository)
 * @return Map containing:
 *   - prerelease_number: The prerelease number extracted from the package
 *   - package_ref: The package reference
 *   - package_version: The package version
 */
def create_and_upload_package(Map args = [:]) {
    echo "Creating and uploading package..."

    // Determine repo root (allow override)
    def REPO_ROOT = args.repoRoot ?: pwd()
    
    dir(REPO_ROOT) {
        sh 'conan config install -t file packages/remotes.json'
    }

    // Local scoped vars
    def MATTER_CONANFILE_PATH     = "${REPO_ROOT}/packages/matter/conanfile.py"
    def MATTER_APP_CONANFILE_PATH = "${REPO_ROOT}/packages/matter_app/conanfile.py" // reserved for future use
    def DEV_REMOTE_NAME           = "matter-conan-dev"
    def DEV_REMOTE_URL            = "https://artifactory.silabs.net/artifactory/api/conan/matter-conan-dev"
    def SQA_REMOTE_NAME           = "matter-conan-sqa"
    def SQA_REMOTE_URL            = "https://artifactory.silabs.net/artifactory/api/conan/matter-conan-sqa"
    def SILABS_REMOTE_NAME        = "silabs-conan-dev"
    def SILABS_REMOTE_URL         = "https://artifactory.silabs.net/artifactory/api/conan/silabs-conan-dev"
    def SL_PRERELEASE             = "${REPO_ROOT}/packages/.prerelease"
    def SL_PRERELEASE_NUMBER      = "" // Initialize prerelease number variable

    // Pre-flight checks
    if (!fileExists(MATTER_CONANFILE_PATH)) {
        error("Conanfile not found: ${MATTER_CONANFILE_PATH}")
    } 
    // Ensure uv tool available
    sh 'command -v uv >/dev/null 2>&1 || { echo "uv not found in PATH"; exit 1; }'

    // Checkout conan create/publish script
    dir('conan repos') {
        checkout([$class: 'GitSCM',
            branches: [[name: 'main']],
            userRemoteConfigs: [[credentialsId: 'github-app', 
            url: 'https://github.com/SiliconLabsInternal/action-conan-create-publish.git']]
        ])
        dir('action-conan-create-publish') {
            sh 'pwd'
            sh 'slt update --self'
            
            // Execute the conan action using the reusable function
            // executeConanCreatePublishAction(String conanfilePath, String stackName, String remoteUrl, String remoteName, boolean create, boolean publish)
            echo "Uploading the matter component package"
            executeConanCreatePublishAction(MATTER_CONANFILE_PATH, 'matter', DEV_REMOTE_URL, DEV_REMOTE_NAME, true, true, SL_PRERELEASE)
            echo "Uploading the matter app package"
            executeConanCreatePublishAction(MATTER_APP_CONANFILE_PATH, 'matter_app', DEV_REMOTE_URL, DEV_REMOTE_NAME, true, true, SL_PRERELEASE)
            // Run after the final upload is done, matter and matter_app package should have same version and revision
            extractPackageInfoFromJson()
            echo "Package creation and upload to matter-conan-dev completed."
        }

        checkout([$class: 'GitSCM',
            branches: [[name: 'main']],
            userRemoteConfigs: [[credentialsId: 'github-app',
            url: 'https://github.com/SiliconLabsInternal/action-conan-promote.git']]
        ])
        dir('action-conan-promote') {
            sh 'pwd'
            sh 'slt update --self'
            echo 'promoting packages to SQA'
            echo "Start promoting matter/${CONAN_PACKAGE_VERSION} to matter-conan-sqa"
            // executeConanPromoteAction(String stackName, String sourceRemoteUrl, String sourceRemoteName, String destinationRemoteUrl, String destinationRemoteName, String packageVersion)
            executeConanPromoteAction('matter', DEV_REMOTE_URL, DEV_REMOTE_NAME, SQA_REMOTE_URL, SQA_REMOTE_NAME, CONAN_PACKAGE_VERSION)
            echo "Done promoting matter/${CONAN_PACKAGE_VERSION} to matter-conan-sqa"
            echo "Start promoting matter_app/${CONAN_PACKAGE_VERSION} to matter-conan-sqa"
            executeConanPromoteAction('matter_app', DEV_REMOTE_URL, DEV_REMOTE_NAME, SQA_REMOTE_URL, SQA_REMOTE_NAME, CONAN_PACKAGE_VERSION)
            echo "Done promoting matter_app/${CONAN_PACKAGE_VERSION} to matter-conan-sqa"
            echo "Start promoting matter/${CONAN_PACKAGE_VERSION} to silabs-conan-dev"
            executeConanPromoteAction('matter', SQA_REMOTE_URL, SQA_REMOTE_NAME, SILABS_REMOTE_URL, SILABS_REMOTE_NAME, CONAN_PACKAGE_VERSION)
            echo "Done promoting matter/${CONAN_PACKAGE_VERSION} to silabs-conan-dev"
            echo "Start promoting matter_app/${CONAN_PACKAGE_VERSION} to silabs-conan-dev"
            executeConanPromoteAction('matter_app', SQA_REMOTE_URL, SQA_REMOTE_NAME, SILABS_REMOTE_URL, SILABS_REMOTE_NAME, CONAN_PACKAGE_VERSION)
            echo "Done promoting matter_app/${CONAN_PACKAGE_VERSION} to silabs-conan-dev"
        }

    }
}


/**
 * Take a Jenkins action (closure) such as node(){} and retry it in the event
 * of an exception where we think the node was reclaimed by AWS or otherwise
 * crashed
 */
def actionWithRetry(Closure action)
{
    def retryCount = 0
	def abortStepTime = 2
    timeout(time: 2, unit: 'HOURS')
    {
	    while(retryCount <= 5)
	    {
	        try
	        {
	            timeout(time: abortStepTime, unit: 'HOURS') {
					action.call()
				}
	            return
	        }
			//catch(org.jenkinsci.plugins.workflow.steps.FlowInterruptedException abort){ throw abort } //Throw this error if it is a Jenkins abort
			catch(Throwable ex)
	        {

	            def totalError = "Abort information: " + determineIfAbortOrTimeout(ex) + "\nOriginal errors: " + "\n" + ex.toString() + "\n" + "Full stack trace: " + "\n"+ "\n" + ex.getStackTrace().toString()

	            echo 'action threw exception at ' + java.time.LocalDateTime.now() + "\n" + "\n" + totalError

				//Treat null exceptions as ChannelClosedException, due to issues with hanging exceptions that dont return text with ChannelClosedException
				if(totalError.contains("Full stack trace: null") && !totalError.contains("hudson.AbortException: script returned exit code"))
					totalError += "\nNull exception detected, treating as AWS ChannelClosedException"


	            //if(totalError.contains('script returned exit code 2'))
	            //{
	            //	sendDevopsDebugMessage("SUDS failure detected, freezing worker")
	            //	input "Frozen for devops analysis"
	            //}
				if(totalError.contains('Aborted by'))
					throw ex
	            else if((!totalError.contains('ClosedChannelException')           &&
	                !totalError.contains('ChannelClosedException')                &&
					!totalError.contains('Unexpected termination of the channel') &&
					!totalError.contains('FlowInterruptedException')              &&
	                !totalError.contains('RemovedNodeListener')                   &&
	                !totalError.contains('missing workspace')                     &&
	                !totalError.contains('Unable to create live FilePath')        &&
					!totalError.contains('StringIndexOutOfBoundsException')       &&
	                !totalError.contains('MissingContextVariableException') )     ||
	                retryCount == 5)
	            {
					if(retryCount == 5)
	            	{
	            		echo "Retry count limit reached for AWS issues, throwing exception"
	                	throw ex
	                }
	                else
	                {
	                	//Print uc log if core dump detected. Don't fail if log doesn't exist for some reason
	                	//This did not work as the node has been left at this pointp

                      	//if(totalError.contains("script returned exit code 139"))
	                	//{
	                	//	sh "cat /home/buildengineer/.uc/uc.core.log 2>/dev/null"
	                	//}

	                	echo "No AWS errors found, throwing exception"
	                	throw ex
	                }
	            }

	            echo 'Lost slave connection. Retrying with count ' + retryCount
                sleep 90
	            retryCount++
	        }
	    }
	}
}
return this