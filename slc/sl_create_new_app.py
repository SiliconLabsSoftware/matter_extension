
"""
 * @file sl_create_new_app.py
 * @brief Create a new Matter application from a reference project file.
 *
 * This script generates a new Matter application directory using a reference .slcp or .slcw project file
 * and a Silicon Labs board name. It sets up environment variables
 * and ensures all required trust and configuration steps are performed for the new app.
 *
 * Usage:
 *   python3 sl_create_new_app.py <NewAppName> <PathToReferenceProjectFile(.slcp or .slcw)> <SilabsBoard> [--verbose]
 *
 * Example:
 *   python3 sl_create_new_app.py MyApp slc/apps/lighting-app/thread/lighting-app.slcp brd4187c --verbose
 *
 """

#!/usr/bin/env python3

import argparse
import logging
import os
import sys
import subprocess
import shutil
import yaml
import json
from dotenv import load_dotenv
from pathlib import Path

class createApp:
    def __init__(self, skip_gen=False):
        self.EXAMPLE_USAGE = "python slc/sl_create_new_app.py <NewAppName> <PathToReferenceProjectFile(.slcp or .slcw)> <SilabsBoard> [options]"
        self.skip_gen = skip_gen
        self.output_suffix = None
        self.with_app_components = None
        self.without_app_components = None
        self.with_bootloader_components = None
        self.without_bootloader_components = None
        self.configuration = None
        self.pids_arg = None
        self.generate_bootloader = True
        self.generate_application = True
        self.generate_tz_secure = False
        self.get_environment()

    def print_usage_and_exit(self):
        logging.info(f"Example usage: {self.EXAMPLE_USAGE}")
        sys.exit(1)

    # Helper to extract src/include paths from a .slcp file
    def extract_from_slcp(self,app_slcp_full_path):
        src_paths = []
        include_paths = []
        project_name = None
        try:
            with open(self.app_slcp_full_path, 'r') as f:
                doc = yaml.safe_load(f)
            # Parse project_name
            if 'project_name' in doc:
                project_name = doc['project_name']
            # Extract 'source' paths
            if 'source' in doc:
                for entry in doc['source']:
                    if isinstance(entry, dict) and 'path' in entry:
                        src_paths.append(entry['path'])
            # Extract 'include' file_list paths, prepending the parent include path
            if 'include' in doc:
                for entry in doc['include']:
                    if isinstance(entry, dict):
                        include_base = entry.get('path', '')
                        if 'file_list' in entry and isinstance(entry['file_list'], list):
                            for file_entry in entry['file_list']:
                                if isinstance(file_entry, dict) and 'path' in file_entry:
                                    file_path = file_entry['path']
                                    if include_base and not file_path.startswith(include_base):
                                        file_path = os.path.join(include_base, file_path)
                                    include_paths.append(file_path)
            return src_paths, include_paths, project_name
        except Exception as e:
            logging.error(f"Failed to extract from slcp: {e}")
            return [], [], None

    # Only keep the paths starting from 'third_party' in original_paths
    def trim_to_str(self, path, substr):
        idx = path.find(substr)
        return path[idx:] if idx != -1 else path

    def extract_and_save_paths(self):
        self.app_slcp_full_path = self.get_project_name_from_slcp()
        matter_sdk_src, matter_sdk_inc, project_name = self.extract_from_slcp(self.app_slcp_full_path)

        if self.use_solutions:
            self.sample_app_out_path = os.path.join(self.new_app_name, project_name)
        else:
            self.sample_app_out_path = self.new_app_name

        # Copy the folder self.sample_app_out_path/src to .bak/original/src/
        try:
            src_dir = os.path.join(self.sample_app_out_path, 'src')
            dest_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'src')
            if os.path.exists(src_dir):
                shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
                logging.info(f"Copied {src_dir} to {dest_dir}")
            else:
                logging.warning(f"Source directory {src_dir} does not exist, skipping copy.")
        except Exception as e:
            logging.error(f"Failed to copy src directory: {e}")

        # Copy the folder self.sample_app_out_path/include to .bak/original/include/
        try:
            include_dir = os.path.join(self.sample_app_out_path, 'include')
            dest_include_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'include')
            if os.path.exists(include_dir):
                shutil.copytree(include_dir, dest_include_dir, dirs_exist_ok=True)
                logging.info(f"Copied {include_dir} to {dest_include_dir}")
            else:
                logging.warning(f"Include directory {include_dir} does not exist, skipping copy.")
        except Exception as e:
            logging.error(f"Failed to copy include directory: {e}")
        trimmed_src_paths = [self.trim_to_str(p, 'third_party') for p in matter_sdk_src]
        trimmed_inc_paths = [self.trim_to_str(p, 'third_party') for p in matter_sdk_inc]
        customer_src = [os.path.join(self.sample_app_out_path, 'src', os.path.basename(p)) for p in trimmed_src_paths]
        customer_inc = [os.path.join(self.sample_app_out_path, 'include', os.path.basename(p)) for p in trimmed_inc_paths]
        upgrade_src_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'src')
        upgrade_inc_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'include')
        upgrade_src = []
        upgrade_inc = []
        if os.path.exists(upgrade_src_dir):
            for fname in os.listdir(upgrade_src_dir):
                fpath = os.path.join(upgrade_src_dir, fname)
                if os.path.isfile(fpath):
                    upgrade_src.append(fpath)
        if os.path.exists(upgrade_inc_dir):
            for fname in os.listdir(upgrade_inc_dir):
                fpath = os.path.join(upgrade_inc_dir, fname)
                if os.path.isfile(fpath):
                    upgrade_inc.append(fpath)
        output_data = {
            'matter_sdk_paths': {
                'source': trimmed_src_paths,
                'include': trimmed_inc_paths
            },
            'customer_paths': {
                'source': customer_src,
                'include': customer_inc
            },
            'backups_paths': {
                'source': upgrade_src,
                'include': upgrade_inc
            }
        }
        output_file_json = os.path.join(self.sample_app_out_path, '.bak', 'source_and_include_paths.json')
        os.makedirs(self.sample_app_out_path, exist_ok=True)
        with open(output_file_json, 'w') as out_json:
            json.dump(output_data, out_json, indent=2)
        logging.info(f"Saved source and include paths to {output_file_json}")
        
    def get_project_name_from_slcp(self):
        # If .slcp, extract directly; if .slcw, find application .slcp and extract from that
        if not self.use_solutions:
            return self.reference_project_file
        else:
            try:
                with open(self.reference_project_file, 'r') as f:
                    doc = yaml.safe_load(f)
                app_slcp_path = None
                if 'project' in doc and isinstance(doc['project'], list):
                    for proj in doc['project']:
                        if isinstance(proj, dict) and proj.get('id') == 'application' and 'path' in proj:
                            app_slcp_path = proj['path']
                            break
                if app_slcp_path is None:
                    logging.error("No application project with .slcp path found in .slcw file.")
                    return

                self.app_slcp_full_path = os.path.join("slc", self.trim_to_str(app_slcp_path,"sample-app"))
                if not os.path.exists(self.app_slcp_full_path):
                    logging.error(f"Application .slcp file does not exist: {self.app_slcp_full_path}")

                return self.app_slcp_full_path
            except Exception as e:
                logging.error(f"Failed to parse .slcw file for application .slcp: {e}")

    def validate_board_argument(self, board):
        import re
        if not re.fullmatch(r"brd\d{4}[abc]", board, re.IGNORECASE):
            logging.error("The second positional argument (silabs_board) must be of the form 'brdXXXXY', where XXXX are digits and Y is a/b/c.")
            return False
        return True

    def validate_arguments(self):
        if len(sys.argv) < 4:
            logging.error("Missing arguments")
            self.print_usage_and_exit()

        self.new_app_name = sys.argv[1]
        self.reference_project_file = sys.argv[2]
        self.silabs_board = sys.argv[3].lower()
        self.use_solutions = False

        if not os.path.exists(self.reference_project_file):
            logging.error(f"ReferenceProject File does not exist: {self.reference_project_file}")
            sys.exit(1)

        if not self.reference_project_file.endswith('.slcp') and not self.reference_project_file.endswith('.slcw'):
            logging.error("ReferenceSlcp File should have a .slcp or .slcw extension")
            sys.exit(1)

        if not self.silabs_board:
            logging.error("Missing SilabsBoard argument")
            self.print_usage_and_exit()
        
        if self.reference_project_file.endswith(".slcw"):
            self.use_solutions = True

        if not self.validate_board_argument(self.silabs_board):
            sys.exit(1)

        # Checkout third_party_hw_drivers_extension submodule for air-quality-sensor-app-sparkfun-thread app and trust the extension
        if "sparkfun" in self.reference_project_file:
            third_party_hw_drivers_extension_path = os.path.join(os.getcwd(),"third_party","third_party_hw_drivers_extension")
            subprocess.run(["git", "submodule", "update", "--init", "--checkout",third_party_hw_drivers_extension_path ])
            subprocess.run([self.slc_path, "signature", "trust", "--extension-path", third_party_hw_drivers_extension_path])

    def get_environment(self):
        try:
            env_path = os.path.join(os.getcwd(), "slc", "tools", ".env")
            load_dotenv(env_path, override=True)
            os.environ["PATH"] = os.getenv("TOOLS_PATH") + os.environ["PATH"]
            self.java_path = os.getenv("JAVA_HOME")
            self.silabs_chip_root = os.getenv("silabs_chip_root")
            self.POST_BUILD_EXE = os.getenv("POST_BUILD_EXE")
            self.NINJA_EXE_PATH = os.getenv("NINJA_EXE_PATH")
            self.sisdk_root = os.getenv("SISDK_ROOT")
            self.wiseconnect_root = os.getenv("WISECONNECT_ROOT")
            self.arm_toolchain_path = os.path.join(os.getenv("ARM_GCC_DIR"))
        except Exception:
            logging.error("Could not load the .env file. Run sl_setup_env.py to generate .env file")
            sys.exit(1)

        self.slc_path = "slc"
        subprocess.run([self.slc_path, "configuration","-gcc", self.arm_toolchain_path])

    def generate(self):
        # Apply output suffix if provided
        if self.output_suffix:
            self.new_app_name = f"{self.new_app_name}-{self.output_suffix}"
            logging.info(f"Applied output suffix. New output directory: {self.new_app_name}")
        
        if self.skip_gen:
            logging.info("Skipping project generation as --skip-gen was specified.")
            self.extract_and_save_paths()
            return
        
        # Use appropriate build flag for sample-app/solutions
        project_flag = "-p" if self.reference_project_file.endswith('.slcp') else "-w"
        
        # Build --with argument
        with_components = []
        if self.use_solutions:
            if self.with_app_components:
                with_components.append(f"{self.silabs_board},{self.with_app_components}")
                logging.info(f"Adding application components: {self.with_app_components}")
            else:
                with_components.append(self.silabs_board)
        else:
            with_components.append(self.silabs_board)
        
        # Build --without argument
        without_components = []
        if self.use_solutions and self.without_app_components:
            without_components.append(self.without_app_components)
            logging.info(f"Excluding application components: {self.without_app_components}")
        
        # Build configuration arguments
        config_args = ""
        if self.configuration:
            config_args = f" {self.configuration}"
            logging.info(f"Using configuration: {self.configuration}")
        
        # Run slc generate to create copy of sample app at the 'new_app_name' location
        try:
            # For solutions with -pids, generate specific parts
            if self.use_solutions and self.pids_arg:
                self._generate_solution_with_pids(project_flag, config_args)
            else:
                # Standard generation for .slcp or full solution
                cmd = [self.slc_path, "--java-location", self.java_path, "generate", "-d", self.new_app_name,
                       project_flag, self.reference_project_file]
                
                # Add --with arguments
                for with_comp in with_components:
                    cmd.extend(["--with", with_comp + config_args])
                
                # Add --without arguments
                for without_comp in without_components:
                    cmd.extend(["--without", without_comp])
                
                cmd.extend(["--new-project", "--force", "--generator-timeout=180", "-o", "makefile"])
                
                # Add SDK package paths
                sdk_package_paths = ["--sdk-package-path", self.sisdk_root, "--sdk-package-path", 
                                   self.silabs_chip_root, "--sdk-package-path", self.wiseconnect_root]
                cmd.extend(sdk_package_paths)
                
                logging.info(f"Running command: {' '.join(cmd)}")
                subprocess.run(cmd, check=True)
            
            # After generation, extract and save src/include paths
            self.extract_and_save_paths()
        except subprocess.CalledProcessError as e:
            logging.error(f"Error running 'slc generate': {e}")
            sys.exit(1)
    
    def _generate_solution_with_pids(self, project_flag, config_args):
        """Generate solution parts based on -pids argument"""
        # Build component arguments
        with_app_arg = f"{self.silabs_board},{self.with_app_components}" if self.with_app_components else self.silabs_board
        with_bootloader_arg = f"{self.silabs_board},{self.with_bootloader_components}" if self.with_bootloader_components else self.silabs_board
        
        sdk_package_paths = ["--sdk-package-path", self.sisdk_root, "--sdk-package-path", 
                           self.silabs_chip_root, "--sdk-package-path", self.wiseconnect_root]
        
        if self.generate_bootloader and not self.generate_tz_secure:
            logging.info("Generating bootloader...")
            cmd = [self.slc_path, "--java-location", self.java_path, "generate", "-d", self.new_app_name,
                   project_flag, self.reference_project_file, "--with", with_bootloader_arg]
            
            if self.without_bootloader_components:
                cmd.extend(["--without", self.without_bootloader_components])
            
            cmd.extend(["-pids", "bootloader"] + sdk_package_paths + 
                      ["--new-project", "--force", "--generator-timeout=180", "-o", "makefile"])
            
            if config_args:
                cmd.append(config_args.strip())
            
            logging.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        
        if self.generate_tz_secure:
            logging.info("Generating trustzone-secure...")
            cmd = [self.slc_path, "--java-location", self.java_path, "generate", "-d", self.new_app_name,
                   project_flag, self.reference_project_file, "--with", with_app_arg,
                   "-pids", "trustzone-secure"] + sdk_package_paths + \
                  ["--new-project", "--force", "--generator-timeout=180", "-o", "makefile"]
            
            if config_args:
                cmd.append(config_args.strip())
            
            logging.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
        
        if self.generate_application:
            logging.info("Generating application...")
            cmd = [self.slc_path, "--java-location", self.java_path, "generate", "-d", self.new_app_name,
                   project_flag, self.reference_project_file, "--with", with_app_arg]
            
            if self.without_app_components:
                cmd.extend(["--without", self.without_app_components])
            
            cmd.extend(["-pids", "application"] + sdk_package_paths + 
                      ["--new-project", "--force", "--generator-timeout=180", "-o", "makefile"])
            
            if config_args:
                cmd.append(config_args.strip())
            
            logging.info(f"Running command: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)

    # Helper to extract src/include paths from a .slcp file
    def extract_from_slcp(self, app_slcp_full_path):
        import yaml
        src_paths = []
        include_paths = []
        project_name = None
        try:
            with open(app_slcp_full_path, 'r') as f:
                doc = yaml.safe_load(f)
            # Parse project_name
            if 'project_name' in doc:
                project_name = doc['project_name']
            # Extract 'source' paths
            if 'source' in doc:
                for entry in doc['source']:
                    if isinstance(entry, dict) and 'path' in entry:
                        src_paths.append(entry['path'])
            # Extract 'include' file_list paths, prepending the parent include path
            if 'include' in doc:
                for entry in doc['include']:
                    if isinstance(entry, dict):
                        include_base = entry.get('path', '')
                        if 'file_list' in entry and isinstance(entry['file_list'], list):
                            for file_entry in entry['file_list']:
                                if isinstance(file_entry, dict) and 'path' in file_entry:
                                    file_path = file_entry['path']
                                    if include_base and not file_path.startswith(include_base):
                                        file_path = os.path.join(include_base, file_path)
                                    include_paths.append(file_path)
            return src_paths, include_paths, project_name
        except Exception as e:
            print(f"Failed to extract from slcp: {e}")
            return [], [], None

    # Helper to trim paths to a specific substring
    def trim_to_str(self, path, substr):
        idx = path.find(substr)
        return path[idx:] if idx != -1 else path

    def extract_and_save_paths(self):
        import json
        self.app_slcp_full_path = self.get_project_name_from_slcp()
        matter_sdk_src, matter_sdk_inc, project_name = self.extract_from_slcp(self.app_slcp_full_path)

        if self.use_solutions:
            self.sample_app_out_path = os.path.join(self.new_app_name, project_name)
        else:
            self.sample_app_out_path = self.new_app_name

        # Copy the folder self.sample_app_out_path/src to .bak/original/src/
        try:
            import shutil
            src_dir = os.path.join(self.sample_app_out_path, 'src')
            dest_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'src')
            if os.path.exists(src_dir):
                shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
            else:
                print(f"ERROR: Source directory {src_dir} does not exist.")
                sys.exit(1)
        except Exception as e:
            print(f"Failed to copy src directory: {e}")
            sys.exit(1)

        # Copy the folder self.sample_app_out_path/include to .bak/original/include/
        try:
            include_dir = os.path.join(self.sample_app_out_path, 'include')
            dest_include_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'include')
            if os.path.exists(include_dir):
                shutil.copytree(include_dir, dest_include_dir, dirs_exist_ok=True)
            else:
                print(f"ERROR: Include directory {include_dir} does not exist.")
                sys.exit(1)
        except Exception as e:
            print(f"Failed to copy include directory: {e}")
            sys.exit(1)

        # Trim paths to remove leading ../ or ./
        def trim_and_clean(path):
            while path.startswith('../') or path.startswith('./'):
                path = path[path.find('/')+1:]
            return path

        # Trim paths to third_party and save them as the original paths are relative to .slcp
        trimmed_src_paths = [trim_and_clean(p) for p in matter_sdk_src]
        trimmed_inc_paths = [trim_and_clean(p) for p in matter_sdk_inc]
        customer_src = [os.path.join(self.sample_app_out_path, 'src', os.path.basename(p)) for p in trimmed_src_paths]
        customer_inc = [os.path.join(self.sample_app_out_path, 'include', os.path.basename(p)) for p in trimmed_inc_paths]
        upgrade_src_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'src')
        upgrade_inc_dir = os.path.join(self.sample_app_out_path, '.bak', 'original', 'include')
        upgrade_src = []
        upgrade_inc = []
        if os.path.exists(upgrade_src_dir):
            for fname in os.listdir(upgrade_src_dir):
                fpath = os.path.join(upgrade_src_dir, fname)
                if os.path.isfile(fpath):
                    upgrade_src.append(fpath)
        if os.path.exists(upgrade_inc_dir):
            for fname in os.listdir(upgrade_inc_dir):
                fpath = os.path.join(upgrade_inc_dir, fname)
                if os.path.isfile(fpath):
                    upgrade_inc.append(fpath)
        output_data = {
            'matter_sdk_paths': {
                'source': trimmed_src_paths,
                'include': trimmed_inc_paths
            },
            'customer_paths': {
                'source': customer_src,
                'include': customer_inc
            },
            'backups_paths': {
                'source': upgrade_src,
                'include': upgrade_inc
            }
        }
        output_file_json = os.path.join(self.sample_app_out_path, '.bak', 'source_and_include_paths.json')
        os.makedirs(self.sample_app_out_path, exist_ok=True)
        with open(output_file_json, 'w') as out_json:
            json.dump(output_data, out_json, indent=2)
        print(f"Saved source and include paths to {output_file_json}")

    def get_project_name_from_slcp(self):
        # If .slcp, extract directly; if .slcw, find application .slcp and extract from that
        if self.reference_project_file.endswith('.slcp'):
            return self.reference_project_file
        else:
            try:
                import yaml
                with open(self.reference_project_file, 'r') as f:
                    doc = yaml.safe_load(f)
                app_slcp_path = None
                if 'project' in doc and isinstance(doc['project'], list):
                    for proj in doc['project']:
                        if isinstance(proj, dict) and proj.get('id') == 'application' and 'path' in proj:
                            app_slcp_path = proj['path']
                            break
                if app_slcp_path is None:
                    print("No application project with .slcp path found in .slcw file.")
                    return

                self.app_slcp_full_path = os.path.join("slc", self.trim_to_str(app_slcp_path,"sample-app"))
                if not os.path.exists(self.app_slcp_full_path):
                    print(f"Application .slcp file does not exist: {self.app_slcp_full_path}")

                return self.app_slcp_full_path
            except Exception as e:
                print(f"Failed to parse .slcw file for application .slcp: {e}")
            

def main():
    parser = argparse.ArgumentParser(
        description="Create a new Matter app from a reference project file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sl_create_new_app.py MyApp slc/apps/lighting-app/thread/lighting-app.slcp brd4187c
  python3 sl_create_new_app.py MyApp slc/apps/lighting-app/thread/lighting-app.slcp brd4187c --skip_gen
  python3 sl_create_new_app.py MyApp slc/apps/lighting-app/thread/lighting-app-series-2.slcw brd4187c --with_app component1,component2
  python3 sl_create_new_app.py MyApp slc/apps/lighting-app/thread/lighting-app-series-2.slcw brd4187c -pids application
        """)
    parser.add_argument("-n", "--new_app_name", dest="new_app_name", required=False, help="Name of the new app directory to create")
    parser.add_argument("-p", "--reference_project_file", dest="reference_project_file", required=False, help="Path to the reference .slcp or .slcw project file")
    parser.add_argument("-b", "--silabs_board", dest="silabs_board", required=False, help="Silabs board name")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose (debug) logging")
    parser.add_argument("-s", "--skip_gen", action="store_true", help="Skip project generation step")
    parser.add_argument("--output_suffix", dest="output_suffix", help="Suffix to append to output directory name")
    parser.add_argument("--with_app", dest="with_app_components", help="Additional components for application build (solutions only, comma-separated)")
    parser.add_argument("--without_app", dest="without_app_components", help="Components to exclude from application build (solutions only, comma-separated)")
    parser.add_argument("--with_bootloader", dest="with_bootloader_components", help="Additional components for bootloader build (solutions only, comma-separated)")
    parser.add_argument("--without_bootloader", dest="without_bootloader_components", help="Components to exclude from bootloader build (solutions only, comma-separated)")
    parser.add_argument("--configuration", dest="configuration", help="Configuration options (e.g., KEY1:value1,KEY2:value2)")
    parser.add_argument("-pids", dest="pids_arg", choices=["bootloader", "application", "trustzone"], help="Generate only specific parts of a solution: 'bootloader', 'application', or 'trustzone' (solutions only)")
    # Accept positional arguments for backward compatibility
    parser.add_argument("args", nargs="*", help=argparse.SUPPRESS)
    args = parser.parse_args()

    # Support both positional and optional arguments for main required fields
    # Priority: optional flags > positional
    if not args.new_app_name or not args.reference_project_file or not args.silabs_board:
        if len(args.args) >= 3:
            args.new_app_name = args.args[0]
            args.reference_project_file = args.args[1]
            args.silabs_board = args.args[2]
        else:
            parser.error("new_app_name, reference_project_file, and silabs_board are required.")

    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format='[%(levelname)s] %(message)s')

    # Patch sys.argv for legacy code
    sys.argv = [sys.argv[0], args.new_app_name, args.reference_project_file, args.silabs_board]

    app = createApp(skip_gen=args.skip_gen)
    app.output_suffix = args.output_suffix
    app.with_app_components = args.with_app_components
    app.without_app_components = args.without_app_components
    app.with_bootloader_components = args.with_bootloader_components
    app.without_bootloader_components = args.without_bootloader_components
    app.configuration = args.configuration
    app.pids_arg = args.pids_arg
    
    # Handle -pids argument logic
    if app.pids_arg:
        if app.pids_arg == "bootloader":
            app.generate_application = False
        elif app.pids_arg == "application":
            app.generate_bootloader = False
        elif app.pids_arg == "trustzone":
            app.generate_application = True
            app.generate_bootloader = True
            app.generate_tz_secure = True
    
    app.validate_arguments()
    app.generate()

if __name__ == "__main__":
    main()
