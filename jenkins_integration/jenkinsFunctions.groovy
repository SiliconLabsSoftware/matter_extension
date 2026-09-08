def upload_artifacts(sqa=false, commit_sha="null", workflow_id="null", run_number="null") {
    withCredentials([
    usernamePassword(credentialsId: 'svc_gsdk', passwordVariable: 'SL_PASSWORD', usernameVariable: 'SL_USERNAME'),
    usernamePassword(credentialsId: 'Matter-Extension-GitHub', usernameVariable: 'GITHUB_APP', passwordVariable: 'GITHUB_ACCESS_TOKEN')
    ])
    {
        def output = sh(script: "python3 -u jenkins_integration/artifacts/upload_artifacts.py --branch_name ${env.BRANCH_NAME} --build_number ${env.BUILD_NUMBER} --sqa ${sqa} --commit_sha ${commit_sha} --workflow_id ${workflow_id} --run_number ${run_number}", returnStdout: true).trim()
        echo "Output from upload_artifacts.py: ${output}"
        if(!sqa){
            result = parse_upload_artifacts_output(output)
            return [commit_sha: result.commit_sha, run_number: result.run_number, workflow_id: result.workflow_id, bypass_results: result.bypass_send_results_gh, pr_number: result.pr_number]
        }
    }
}

def download_coverage_artifact(workflow_id) {
    withCredentials([
        usernamePassword(credentialsId: 'Matter-Extension-GitHub', usernameVariable: 'GITHUB_APP', passwordVariable: 'GITHUB_ACCESS_TOKEN')
    ])
    {
        sh "python3 -u jenkins_integration/artifacts/download_coverage_artifact.py --workflow_id ${workflow_id} --dest_dir ./coverage"
    }
}

def run_code_size_analysis() {
    echo "Starting code size analysis for branch: ${env.BRANCH_NAME}"

    sh 'python3 -m venv code_size_analysis_venv'
    sh '. code_size_analysis_venv/bin/activate && python3 -m pip install --upgrade pip'
    sh '. code_size_analysis_venv/bin/activate && pip3 install code_size_analyzer_client-python>=1.0.1'

    echo "Build number: ${env.BUILD_NUMBER}"
    echo "Branch name: ${env.BRANCH_NAME}"

    withEnv([
        "BRANCH_NAME=${env.BRANCH_NAME}",
        "BUILD_NUMBER=${env.BUILD_NUMBER}"
    ]) {
            sh '''
                extract_app_from_path() {
                    local path=$1
                    local app_name

                    local solution_dir=\$(echo "\$path" | grep -oE "[^/]*_solution(_lto|_llvm(-lto)?)?" | head -1)

                    if [ -n "$solution_dir" ]; then
                        local base_name=\$(echo "\$solution_dir" | sed -E 's/_solution(_lto|_llvm(-lto)?)?\$//')

                        # Extract app name from file name
                        case "\$base_name" in
                            *zigbee_light*)
                                app_name="zigbee-matter-light"
                                ;;
                            *lighting_app*)
                                app_name="lighting-app"
                                ;;
                            *lock_app*)
                                app_name="lock-app"
                                ;;
                            *multi_sensor_app*)
                                app_name="multi-sensor-app"
                                ;;
                        esac
                    else
                        echo "ERROR: Could not find solution directory in path: \$path" >&2
                        return 1
                    fi

                    echo "\$app_name"
                }

                determine_protocol() {
                    local path=$1
                    if [[ "$path" == *"wifi_soc"* ]]; then
                        echo "wifi"
                    else
                        echo "thread"
                    fi
                }

                determine_build_options() {
                    local path=$1
                    if [[ "$path" == *"_solution_lto/"* ]]; then
                        echo "-lto"
                    elif [[ "$path" == *"_solution_nolto/"* ]]; then
                        echo "-nolto"
                    elif [[ "$path" == *"_solution_llvm-lto/"* ]]; then
                        echo "-lto"
                    else
                        echo "-debug"
                    fi
                }

                determine_compiler() {
                    local path=$1
                    if [[ "$path" == *"_solution_llvm"* ]]; then
                        echo "llvm"
                    else
                        echo "gcc"
                    fi
                }

                determine_compiler() {
                    local path=$1
                    if [[ "$path" == *"_solution_llvm"* ]]; then
                        echo "llvm"
                    else
                        echo "gcc"
                    fi
                }

                perform_code_analysis() {
                    local map_file_path=$1

                    local brd
                    case "$map_file_path" in
                        *brd4187c*)
                            brd="BRD4187C"
                            ;;
                        *brd4407a*)
                            brd="BRD4407A"
                            ;;
                        *brd4338a*)
                            brd="BRD4338A"
                            ;;
                        *)
                            echo "Skipping the codesize Analysis for board in path: $map_file_path"
                            return 0
                            ;;
                    esac

                    local app=\$(extract_app_from_path "\$map_file_path")
                    if [ $? -ne 0 ] || [ -z "$app" ]; then
                        echo "ERROR: Failed to extract app name from $map_file_path"
                        return 1
                    fi

                    local protocol=\$(determine_protocol "\$map_file_path")
                    local options=\$(determine_build_options "\$map_file_path")
                    local compiler=\$(determine_compiler "\$map_file_path")

                    echo "Processing: $map_file_path"
                    echo "  Board: $brd, App: $app, Protocol: $protocol, Options: $options, Compiler: $compiler"

                    if [ "$brd" = "BRD4338A" ]; then
                        if [[ "$app" == *"-app" ]]; then
                            app_stripped=\$(echo "$app" | sed 's/-app\$//')
                            app="SiWx917-${app_stripped}"
                        else
                            app="SiWx917-${app}"
                        fi
                    fi

                    if [ "$protocol" = "thread" ]; then
                        example_type="OpenThread"
                    elif [ "$protocol" = "wifi" ]; then
                        example_type="WiFi"
                    else
                        echo "ERROR: Unknown protocol: $protocol"
                        return 1
                    fi

                    if [ "$brd" = "BRD4187C" ]; then
                        family="MG24"
                        target_part="efr32mg24b210f1536im48"
                    elif [ "$brd" = "BRD4407A" ]; then
                        family="MG301"
                        target_part="simg301m114lih"
                    elif [ "$brd" = "BRD4338A" ]; then
                        family="Si917"
                        target_part="siwg917m111mgtba"
                    fi

                    output_file="${app}-${example_type}-${family}.json"

                    if [ "$options" = "-lto" ]; then
                        application_name="slc-${app}-release-${family}"
                    elif [ "$options" = "-nolto" ]; then
                        application_name="slc-${app}-release-${family}-nolto"
                        output_file="${output_file%.json}-nolto.json"
                    else
                        application_name="slc-${app}-debug-${family}"
                        output_file="${output_file%.json}-debug.json"
                    fi

                    echo "  Running analysis:"
                    echo "    Application name: $application_name"
                    echo "    Output file: $output_file"

                    . code_size_analysis_venv/bin/activate
                    unset OTEL_EXPORTER_OTLP_ENDPOINT || true
                    if code_size_analyzer_cli \\
                        --map_file "$map_file_path" \\
                        --stack_name matter \\
                        --target_part "$target_part" \\
                        --compiler "$compiler" \\
                        --target_board "$brd" \\
                        --app_name "$application_name" \\
                        --service_url https://code-size-analyzer.silabs.net \\
                        --branch_name "$BRANCH_NAME" \\
                        --build_number "b$BUILD_NUMBER" \\
                        --output_file "$output_file" \\
                        --store_results True \\
                        --verify_ssl False \\
                        --uc_component_branch_name "silabs_slc/$BRANCH_NAME"; then
                        echo "  Analysis completed successfully"
                    else
                        echo "  Analysis failed"
                    fi
                }

                echo "Cleaning up leftover JSON files"
                rm -f *.json

                echo "Available map files:"
                map_files_found=\$(find . -name "*.map" | grep -v "sqa-artifacts" | sort)
                if [ -z "$map_files_found" ]; then
                    echo "ERROR: No map files found"
                    exit 1
                fi
                echo "$map_files_found"
                echo ""

                CODE_SIZE_BUILDS='
                    brd4187c/matter_thread_soc_lighting_app_series_2_freertos_solution
                    brd4187c/matter_thread_soc_lock_app_series_2_freertos_solution
                    brd4187c/matter_thread_soc_zigbee_light_series_2_freertos_solution
                    brd4187c/matter_thread_soc_multi_sensor_app_series_2_freertos_solution
                    brd4407a/matter_thread_soc_lighting_app_series_3_freertos_solution
                    brd4407a/matter_thread_soc_lock_app_series_3_freertos_solution
                    brd4407a/matter_thread_soc_multi_sensor_app_series_3_freertos_solution
                    brd4407a/matter_thread_soc_zigbee_light_series_3_freertos_solution
                    brd4338a/matter_wifi_soc_lighting_app_freertos_solution
                    brd4338a/matter_wifi_soc_lock_app_freertos_solution
                '

                PATTERN=""
                for build in $CODE_SIZE_BUILDS; do
                [ -n "$PATTERN" ] && PATTERN="${PATTERN}|"
                PATTERN="${PATTERN}${build}/.*\\.map\\$|${build}_lto/.*\\.map\\$|${build}_nolto/.*\\.map\\$"
                done

                filtered_map_files=$(echo "$map_files_found" | grep -E "$PATTERN")

                if [ -z "$filtered_map_files" ]; then
                echo "WARNING: No map files found matching target build patterns"
                echo "Available apps in map files:"
                echo "$map_files_found" | sed -E 's|.*/([^/]*_solution[^/]*)/.*|\1|' | sort -u
                exit 0
                fi

                echo "Target app map files to process:"
                echo "$filtered_map_files"
                echo ""

                echo "Processing map files for target apps only..."
                echo "$filtered_map_files" | while read map_file; do
                    perform_code_analysis "$map_file"
                done
            '''
        }

        echo "Code size analysis completed"
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

def execute_sanity_tests(nomadNode, deviceGroup, deviceGroupId, appName, matterType, board, wifi_module, branchName, buildNumber)
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
                            "SDK_BUILD_NUM=${buildNumber}",
                            "TESTBED_NAME=${deviceGroup}",
                            "GROUP_ID=${deviceGroupId}",
                            "BUILD_URL=$BUILD_URL",
                            "JENKIN_RUN_NUM=${buildNumber}",
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
                            "CSA_MATTER_VERSION=1.6",
                            "PATH+COMMANDER_PATH=${commanderDir}"
                        ])
                        {
                            def test_log_file = 'test_logs.log'
                            sh 'printenv'
                            sh(script: """
                                echo ${TESTBED_NAME}
                                ${commanderPath} --version
                                ./workspace_setup.sh
                                executor/launch_utf_tests.sh --publish_test_results true --hwmux_token ${HW_MUX_TOKEN} --hwmux_group_id ${GROUP_ID} --harness matter_harness_template.yaml --render_harness_template --executor_type local --pytest_command "pytest --tb=native -m ${matterType} tests/ci/test_matter_ci.py" > ${test_log_file} 2>&1 || true
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
        def matcher = line =~ /(FAILED|ERROR)\s+tests\/ci\/test_matter_ci\.py::(test_tc[\w\d_]+)\s+-\s+(.*)/
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

def trigger_sqa_pipelines(pipeline_type)
{
    if(sqaFunctions.isProductionJenkinsServer())
    {
        def smoke_list = ['smoke-thread', 'smoke-wifi', 'smoke-cmp']
        def regression_list = ['feature-thread', 'feature-wifi', 'feature-cmp', 'regression-thread', 'regression-wifi', 'regression-cmp',
                               'regression-ota-thread', 'regression-ota-wifi', 'regression-ota-cmp', 'regression-metrics',
                               'ext-regression-thread', 'ext-regression-wifi', 'ext-regression-cmp',
                               'ext-smoke-thread', 'ext-smoke-wifi', 'ext-smoke-cmp',
                               'endurance-thread', 'endurance-wifi', 'endurance-cmp']
        def errorOccurred = false
        try{
            sshagent(['svc_gsdk-ssh']) {
                if (!fileExists('sqa-pipelines')) {
                    sh 'git clone ssh://git@stash.silabs.com/wmn_sqa/sqa-pipelines.git'
                }
                if(pipeline_type == "smoke") {
                        smoke_list.each { smoke_type ->
                        dir('sqa-pipelines') {
                            try{
                                sqaFunctions.commitToMatterSqaPipelines(smoke_type, "${env.BRANCH_NAME}", "${env.BUILD_NUMBER}")
                            } catch (e) {
                                unstable("Error when triggering ${smoke_type}: ${e.message}")
                                errorOccurred = true
                            }
                        }
                    }
                } else {
                    regression_list.each { regression_type ->
                        dir('sqa-pipelines') {
                            try{
                                sqaFunctions.commitToMatterSqaPipelines(regression_type, "${env.BRANCH_NAME}", "${env.BUILD_NUMBER}")
                            } catch (e) {
                                unstable("Error when triggering ${regression_type}: ${e.message}")
                                errorOccurred = true
                            }
                        }
                    }
                }
            }
        } catch (e) {
            unstable("Error when triggering SQA pipelines: ${e.message}")
            errorOccurred = true
        }
        if (errorOccurred) {
            currentBuild.result = 'UNSTABLE'
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

/**
 * Slack-formatted summary of commits since last Jenkins run (parent repo + matter_sdk gitlink only).
 * Baseline: GIT_PREVIOUS_SUCCESSFUL_COMMIT, then GIT_PREVIOUS_COMMIT if unset.
 */
def buildCommitChangeSummaryForSlack() {
    def prev = (env.GIT_PREVIOUS_SUCCESSFUL_COMMIT ?: '').trim()
    if (!prev) {
        prev = (env.GIT_PREVIOUS_COMMIT ?: '').trim()
    }
    def summary = ''
    withEnv(["PREV_BASELINE=${prev}"]) {
        summary = sh(script: 'bash jenkins_integration/commit_change_summary.sh', returnStdout: true).trim()
    }
    if (summary.length() > 3500) {
        summary = summary.substring(0, 3500) + '\n...(truncated)'
    }
    return summary
}

// ---------------------------------------------------------------------------
// Matter Conan package publish / promote helpers
// ---------------------------------------------------------------------------
// Note: Jenkins `sh` runs under /bin/sh (dash). Use `bash <<'EOF'` for bash features
// and `pipefail`.

/**
 * Checkout a GitHub repo into dirName using the github-app credential.
 * branchSpec examples: 'refs/tags/v2.5.5', '*\/main'
 */
def checkoutGithubActionRepo(String dirName, String repoUrl, String branchSpec) {
    dir(dirName) {
        checkout([
            $class: 'GitSCM',
            branches: [[name: branchSpec]],
            extensions: [[$class: 'CloneOption', depth: 1, shallow: true, noTags: false]],
            userRemoteConfigs: [[
                url: repoUrl,
                credentialsId: 'github-app'
            ]]
        ])
        sh 'ls -la'
        sh 'find . -maxdepth 2 -type d | sort'
    }
}

/** Init Matter package-related git submodules (shallow). */
def initMatterPackageSubmodules() {
    sh '''
        bash <<'EOF'
set -euo pipefail
git config --global --add safe.directory "${WORKSPACE}"
git submodule update --init --depth 1 --jobs 8 \
  third_party/matter_sdk \
  third_party/matter_support \
  third_party/QR-Code-generator \
  third_party/mbedtls \
  third_party/nlio \
  third_party/nlassert
EOF
    '''
}

/** Install uv into ~/.local/bin if missing. */
def setupUv() {
    sh '''
        bash <<'EOF'
set -euo pipefail
export PATH="${HOME}/.local/bin:${PATH}"
if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi
uv --version
EOF
    '''
}

/** Install SLT CLI and Conan engine; puts conan on PATH via ~/.local/bin. */
def setupSltAndConan() {
    sh '''
        bash <<'EOF'
set -euo pipefail
export PATH="${HOME}/.local/bin:${PATH}"

SLT_ARTIFACTORY_URL="${SLT_ARTIFACTORY_URL:-https://www.silabs.com/documents/public/software}"
SLT_PKG_NAME="${SLT_PKG_NAME:-slt-cli-1.2.0-linux-x64.zip}"
curl -fsSL "${SLT_ARTIFACTORY_URL}/${SLT_PKG_NAME}" --output "/tmp/${SLT_PKG_NAME}"
mkdir -p "${HOME}/.local/bin"
unzip -o "/tmp/${SLT_PKG_NAME}" -d "${HOME}/.local/bin"
rm -f "/tmp/${SLT_PKG_NAME}"
export SLT_CI=true
slt update --self
slt --version

export CONAN_HOME="${CONAN_HOME:-${HOME}/.silabs/slt/installs/conan}"
CONAN_HOME="${CONAN_HOME/#\\~/$HOME}"
export CONAN_HOME
export PATH="${HOME}/.silabs/slt/engines/conan/conan:${PATH}"

slt install conan
CONAN_BIN="${HOME}/.silabs/slt/engines/conan/conan/conan"
if [ ! -f "${CONAN_BIN}" ]; then
  echo "Error: conan not found at ${CONAN_BIN}" >&2
  exit 1
fi
ln -fs "${CONAN_BIN}" "${HOME}/.local/bin/conan"
conan --version

conan remote add -f silabs-conan-production \
  https://artifactory.silabs.net/artifactory/api/conan/silabs-conan-production
conan remote list
EOF
    '''
    // Persist for later sh steps (exports inside bash do not carry across Jenkins sh steps)
    env.CONAN_HOME = "${env.HOME}/.silabs/slt/installs/conan"
    echo "CONAN_HOME=${env.CONAN_HOME}"
}

/**
 * Write prerelease qualifier to a workspace file and set SL_PRERELEASE to that path.
 * Returns the absolute path of the label file.
 */
def writePrereleaseLabel(String qualifier) {
    def labelPath = "${env.WORKSPACE}/.sl_prerelease_label"
    writeFile file: '.sl_prerelease_label', text: "${qualifier}\n"
    env.SL_PRERELEASE = labelPath
    echo "SL_PRERELEASE=${env.SL_PRERELEASE} (qualifier=${qualifier})"
    return labelPath
}

/**
 * Read conan_package_output.json written by action-conan-create-publish@v2.5.4
 * (set_script_output / _create_json_output). File is created in the process cwd.
 * Returns a Map with keys like full_package_ref, package_ref, prerelease_number, ...
 */
def readConanPackageOutputJson(String jsonPath = null) {
    def path = jsonPath ?: "${env.WORKSPACE}/conan_package_output.json"
    if (!fileExists(path)) {
        error("conan_package_output.json not found at ${path}")
    }
    def data = readJSON file: path
    echo "Read conan_package_output.json: ${data}"
    return data
}

/**
 * Run action-conan-create-publish for one recipe (create + publish).
 * Requires ARTIFACTORY_TOKEN in the environment (use withCredentials).
 * Runs from WORKSPACE so v2.5.4 writes conan_package_output.json there.
 */
def runActionConanCreatePublish(String name, String conanfile, String remoteName, String remoteUrl, String actionDir) {
    sh("""
        bash <<'EOF'
set -euo pipefail
cd "\${WORKSPACE}"
export PATH="\${HOME}/.local/bin:\${PATH}"
export CONAN_HOME="\${CONAN_HOME:-\${HOME}/.silabs/slt/installs/conan}"
export CONAN_HOME
echo "CONAN_HOME=\${CONAN_HOME}"
conan remote list
echo "Running action-conan-create-publish for ${name} (${conanfile})"
rm -f "\${WORKSPACE}/conan_package_output.json"
env \\
  "CONAN_HOME=\${CONAN_HOME}" \\
  "INPUT_CONANFILE_PATH=${conanfile}" \\
  "INPUT_REMOTE_USERNAME=svc_gsdk" \\
  "INPUT_REMOTE_NAME=${remoteName}" \\
  "INPUT_REMOTE_URL=${remoteUrl}" \\
  "INPUT_REMOTE_TOKEN=\${ARTIFACTORY_TOKEN}" \\
  "INPUT_STACK_NAME=matter" \\
  "INPUT_CREATE=true" \\
  "INPUT_PUBLISH=true" \\
  "INPUT_CONAN_COMMAND_OPTIONS=export-pkg" \\
  "INPUT_PACKAGE_USER=silabs" \\
  "INPUT_JIRA_PROJECT=MATTER" \\
  uv run --project "${actionDir}" action-conan-create-publish
test -f "\${WORKSPACE}/conan_package_output.json"
echo "Wrote \${WORKSPACE}/conan_package_output.json"
cat "\${WORKSPACE}/conan_package_output.json"
EOF
    """.stripIndent().trim())
}

/**
 * Promote each package ref via action-conan-promote@v2 (uv + JFrog CLI).
 * Requires ARTIFACTORY_TOKEN in the environment.
 * v2 reads PACKAGE_REF / SOURCE_REMOTE_URL / DESTINATION_REMOTE_URL.
 */
def runActionConanPromote(String packageRefs, String sourceRemoteUrl, String destRemoteUrl, String actionDir) {
    def jfUrl = sourceRemoteUrl.replaceAll(/^(https?:\/\/[^\/]+).*/, '$1')

    sh("""
        bash <<'EOF'
set -euo pipefail
export PATH="\${HOME}/.local/bin:\${PATH}"

if ! command -v uv >/dev/null 2>&1; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="\${HOME}/.local/bin:\${PATH}"
fi
uv --version

# JFrog CLI (v2 action uses jfrog/setup-jfrog-cli)
if ! command -v jf >/dev/null 2>&1; then
  curl -fL https://install-cli.jfrog.io | sh
  if [ -x ./jf ]; then
    mkdir -p "\${HOME}/.local/bin"
    mv ./jf "\${HOME}/.local/bin/jf"
  fi
  export PATH="\${HOME}/.local/bin:\${PATH}"
fi
jf --version

export JF_URL='${jfUrl}'
export JF_ACCESS_TOKEN="\${ARTIFACTORY_TOKEN}"

# setup-jfrog-cli configures a server; plain env vars are not enough for jf rt cp
jf config add matter-promote \\
  --url="\${JF_URL}" \\
  --access-token="\${JF_ACCESS_TOKEN}" \\
  --interactive=false \\
  --overwrite=true
jf config use matter-promote

for ref in ${packageRefs}; do
  echo "Promoting: \${ref}"
  echo "From: ${sourceRemoteUrl}"
  echo "To:   ${destRemoteUrl}"
  env \\
    "PACKAGE_REF=\${ref}" \\
    "SOURCE_REMOTE_URL=${sourceRemoteUrl}" \\
    "DESTINATION_REMOTE_URL=${destRemoteUrl}" \\
    "JF_URL=\${JF_URL}" \\
    "JF_ACCESS_TOKEN=\${JF_ACCESS_TOKEN}" \\
    uv run --no-dev --project "${actionDir}" action-conan-promote
done
EOF
    """.stripIndent().trim())
}

return this
