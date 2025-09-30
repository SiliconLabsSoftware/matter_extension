#!/usr/bin/env python3
"""Python replacement for build.sh.

Usage:
    build.py <slcp/slcw path> <board> [options] [CONFIG ...]

Examples:
    ./build.py slc/sample-app/lighting-app/efr32/lighting-app-thread.slcp brd4187c
    ./build.py slc/sample-app/lighting-app/efr32/lighting-app-thread.slcp brd4187c --skip_gen
    ./build.py slc/sample-app/zigbee-matter-light/efr32/zigbee-matter-light.slcp brd1019a --with matter_zigbee_sequential;matter
    ./build.py slc/solutions/lighting-app/series-2/lighting-app-thread-bootloader.slcw brd4187c \
            --configuration CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION:20,CHIP_DEVICE_CONFIG_DEVICE_SOFTWARE_VERSION_STRING:"1.0.0-1.0"

Options:
    --skip_gen              Skip the `slc generate` step (assumes project previously generated).
    --sisdk <path>          Override SISDK root (defaults to third_party/simplicity_sdk).
    --output_suffix <sfx>   Append a suffix to the output directory name.
    --jobs / -j <N>         Parallel build jobs for make (default 13).
    --rebuild_app           Clean and rebuild only the application components.
    --rebuild_stack         Clean and rebuild only the stack components.
    --rebuild_all           Clean and rebuild both application and stack components.
    --ci                    CI mode (continuous integration build).
    --with <options>        Append additional options to the board using comma separation.
    --cmake                 Generate project using cmake instead of makefile.
    --enable_editable       Enable Matter package editable mode for development.
    --disable_editable      Disable Matter package editable mode.
    --editable_status       Show Matter package editable mode status and exit.
    -v / --verbose          Verbose logging (DEBUG vs INFO).
    -n / --dry_run          Print the steps without executing build/generate/make.

Backward compatibility positional inference:
    For older invocations that supplied a SISDK path or output suffix *without* flags:
        build.py <app> <board> /path/to/sisdk customsuffix --skip_gen
    The first non-dash argument after <board> that is an existing directory and looks like a SDK
    (contains 'simplicity' or 'sdk' or has a 'extension' subdir) will be treated as --sisdk.
    The next non-dash bare token (not containing ':' and not recognized as config) becomes --output_suffix.
    All remaining tokens are forwarded to slc generate as configuration args.

All remaining unrecognized arguments are forwarded verbatim to the slc generate command
(typically configuration flags like --configuration ...).

Exit codes:
    0 success, non-zero on first failing command.
"""
import argparse
import os
import re
import shlex
import subprocess
import sys
import logging
from pathlib import Path

logger = logging.getLogger("build")


class MatterEditableManager:
    """Simple Matter package editable mode manager integrated into build script"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.package_name = "matter"
        self.package_version = self._resolve_package_version()
        self.package_reference = f"{self.package_name}/{self.package_version}@silabs"

    def _resolve_package_version(self) -> str:
        """Resolve the Matter package version from version file.

        Priority:
          1. <workspace_root>/slc/script/matter_package_version
          2. <this_script_dir>/script/matter_package_version
        Falls back to '0.0.0-dev' if not found or empty.
        """
        candidates = [
            self.workspace_root / "slc" / "script" / "matter_package_version",
            Path(__file__).resolve().parent / "script" / "matter_package_version",
        ]
        for path in candidates:
            try:
                if path.is_file():
                    content = path.read_text(encoding="utf-8").strip()
                    if content:
                        logger.debug("Resolved Matter package version '%s' from %s", content, path)
                        return content
                    else:
                        logger.warning("Version file %s is empty", path)
            except Exception as e:
                logger.debug("Failed reading version file %s: %s", path, e)
        logger.warning("Matter package version file not found; defaulting to 0.0.0-dev")
        return "0.0.0-dev"
    
    def run_conan_command(self, command: list) -> bool:
        """Run a conan command and return success status"""
        full_cmd = ["conan"] + command
        
        try:
            logger.debug("Running: %s", ' '.join(full_cmd))
            result = subprocess.run(full_cmd, capture_output=True, text=True, cwd=self.workspace_root)
            
            if result.returncode == 0:
                if result.stdout.strip():
                    logger.info("Conan: %s", result.stdout.strip())
                return True
            else:
                logger.error("Conan command failed: %s", result.stderr.strip())
                return False
        except FileNotFoundError:
            logger.error("Conan command not found. Make sure Conan is installed and in PATH")
            return False
        except Exception as e:
            logger.error("Error running conan command: %s", e)
            return False
    
    def is_editable_enabled(self) -> bool:
        """Check if Matter package is currently in editable mode"""
        try:
            result = subprocess.run(["conan", "editable", "list"], 
                                  capture_output=True, text=True, cwd=self.workspace_root)
            
            if result.returncode != 0:
                return False
            
            # Look for our package in the output
            for line in result.stdout.split('\n'):
                if self.package_name in line and self.package_version in line:
                    return True
            
            return False
        except Exception:
            return False
    
    def enable_editable_mode(self) -> bool:
        """Enable editable mode for Matter package"""
        if self.is_editable_enabled():
            logger.info("Matter package %s is already in editable mode", self.package_reference)
            return True
        
        logger.info("Enabling editable mode for Matter package...")
        success = self.run_conan_command([
            "editable", "add", ".",
            "--name", self.package_name,
            "--version", self.package_version
        ])
        
        if success:
            logger.info("Successfully enabled editable mode for %s", self.package_reference)
        
        return success
    
    def disable_editable_mode(self) -> bool:
        """Disable editable mode for Matter package"""
        if not self.is_editable_enabled():
            logger.info("Matter package %s is not in editable mode", self.package_reference)
            return True
        
        logger.info("Disabling editable mode for Matter package...")
        success = self.run_conan_command([
            "editable", "remove", "-r", self.package_reference
        ])
        
        if success:
            logger.info("Successfully disabled editable mode for %s", self.package_reference)
        
        return success
    
    def show_status(self):
        """Show current status of Matter editable package"""
        is_enabled = self.is_editable_enabled()
        status = "ENABLED" if is_enabled else "DISABLED"
        logger.info("Matter Package Editable Status: %s", status)
        logger.info("  Package: %s", self.package_reference)
        logger.info("  Workspace: %s", self.workspace_root)
        
        if is_enabled:
            logger.info("  Development mode active - changes will be immediately available")
        else:
            logger.info("  Using published package versions")

# Regex patterns for errors that should be ignored (treated as warnings)
IGNORABLE_ERROR_PATTERNS = [
    re.compile(r"Cannot determine package type for", re.IGNORECASE),
]


# ----------------------------- Helpers ----------------------------------

def configure_logging(verbose: bool):
    """Configure root logging based on verbosity."""
    level = logging.DEBUG if verbose else logging.INFO
    # Avoid reconfiguration if already set
    if not logging.getLogger().handlers:
        logging.basicConfig(
            level=level,
            format="[%(levelname)s] %(message)s"
        )
    else:
        logging.getLogger().setLevel(level)
    logger.debug("Logger initialized (verbose=%s)", verbose)

def run(cmd, *, cwd=None, env=None, check=True, verbose=False, capture=False, ignore_error_patterns=None):
    """Run a shell command with logging.

    cmd: list[str] | str
    Returns subprocess.CompletedProcess. Raises on error if check=True.
    verbose: when False and capture=True, output is captured instead of streamed.
    """
    if isinstance(cmd, list):
        printable = " ".join(shlex.quote(c) for c in cmd)
    else:
        printable = cmd
    logger.debug("CMD: %s", printable)
    kwargs = {}
    if cwd:
        kwargs["cwd"] = str(cwd)
    if env:
        kwargs["env"] = env
    if capture or ignore_error_patterns:
        # Force capture if we intend to examine output for ignorable patterns
        kwargs["stdout"] = subprocess.PIPE
        kwargs["stderr"] = subprocess.STDOUT
    try:
        proc = subprocess.run(cmd, text=True, **kwargs, check=False)
    except FileNotFoundError as e:
        logger.error("Command failed to start: %s", e)
        if check:
            sys.exit(127)
        raise
    # Determine if error is ignorable
    output_text = proc.stdout if (capture or ignore_error_patterns) else None
    if proc.returncode != 0 and ignore_error_patterns and output_text:
        for patt in ignore_error_patterns:
            if patt.search(output_text):
                logger.warning("Ignoring known benign error pattern '%s' in command: %s", patt.pattern, printable)
                logger.debug("Ignored command output:\n%s", output_text)
                proc.returncode = 0  # treat as success
                break
    if proc.returncode != 0 and check:
        if output_text:
            logger.error(output_text)
        logger.error("Command failed (exit=%s): %s", proc.returncode, printable)
        sys.exit(proc.returncode)
    
    # Display captured output if verbose is True and we captured output
    if verbose and output_text and proc.returncode == 0:
        logger.info("Command output:\n%s", output_text)
    
    # If capture requested, return process (caller can inspect stdout)
    return proc


def parse_args():
    # Use parse_known_args so we can accept arbitrary flags (e.g., --configuration, --verbose)
    # and process them manually for backwards compatibility with the shell script behavior.
    p = argparse.ArgumentParser(
        add_help=False,  # We'll handle help manually to show all options
        description="Python port of build.sh (accepts arbitrary extra args). Supports editable package management.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Optional Arguments:
  -h, --help            Show this help message and exit
  --skip_gen            Skip the 'slc generate' step (assumes project previously generated)
  --sisdk <path>        Override SISDK root (defaults to third_party/simplicity_sdk)
  --output_suffix <sfx> Append a suffix to the output directory name
  --jobs, -j <N>        Parallel build jobs for make (default: 13)
  --rebuild_app         Clean and rebuild only the application components
  --rebuild_stack       Clean and rebuild only the stack components  
  --rebuild_all         Clean and rebuild both application and stack components
  --ci                  CI mode (continuous integration build)
  --with <options>      Append additional options to the board using comma separation
  --cmake               Generate project using cmake instead of makefile
  --enable_editable     Force enable Matter package editable mode (default unless --ci)
  --disable_editable    Disable Matter package editable mode
  --editable_status     Show Matter package editable mode status and exit
  -v, --verbose         Verbose logging (DEBUG vs INFO)
  -n, --dry_run         Print the steps without executing build/generate/make

Examples:
  ./build.py app.slcp brd4187c
  ./build.py app.slcp brd4187c --skip_gen --verbose
  ./build.py app.slcp brd4187c --with matter_zigbee_sequential;matter
  ./build.py app.slcp brd4187c --enable_editable --verbose
  ./build.py app.slcp brd4187c --editable_status
  ./build.py app.slcp brd4187c --cmake --jobs 8

Editable Package Management:
  The editable package feature allows you to develop against a local copy of the
  Matter package instead of using published versions. This is useful for:
  - Testing local Matter SDK changes immediately
  - Development workflow without publishing packages
  - Debugging package integration issues
  
  BEHAVIOR:
  - Editable mode is ENABLED by default for development builds
  - Editable mode is DISABLED when --ci flag is used (for reproducible CI builds)
  - Use --disable_editable to explicitly disable editable mode
  - Use --enable_editable to force enable (overrides some logic)
  - Use --editable_status to check the current state

All remaining unrecognized arguments are forwarded to the slc generate command.
        """
    )
    p.add_argument("app_path", help="Path to .slcp or .slcw application/solution file")
    p.add_argument("board", help="Board identifier (may contain ';' extras)")
    
    # Check for help manually since we disabled add_help
    if '--help' in sys.argv or '-h' in sys.argv:
        p.print_help()
        sys.exit(0)
    
    known, unknown = p.parse_known_args()
    # Attach 'extras' attribute to mimic previous interface
    known.extras = unknown
    return known


KNOWN_FLAGS = {"--skip_gen", "--sisdk", "--output_suffix", "--jobs", "-j", "-v", "--verbose", "-n", "--dry_run", "--rebuild_app", "--rebuild_stack", "--rebuild_all", "--ci", "--with", "--cmake", "--enable_editable", "--disable_editable", "--editable_status"}


def classify_extra_args(raw_extras):
    """Extract our known flags while preserving unknown config args list.

    Returns dict with keys: skip_gen(bool), sisdk(str|None), output_suffix(str|None),
    jobs(int), verbose(bool), dry_run(bool), rebuild_app(bool), rebuild_stack(bool), 
    rebuild_all(bool), ci(bool), with_options(str|None), cmake(bool), enable_editable(bool), 
    disable_editable(bool), editable_status(bool), config_args(list[str]).
    """
    skip_gen = False
    sisdk = None
    output_suffix = None
    jobs = 13
    verbose = False
    dry_run = False
    rebuild_app = False
    rebuild_stack = False
    rebuild_all = False
    ci = False
    with_options = None
    cmake = False
    enable_editable = False  # Will be set to True by default unless CI mode
    disable_editable = False
    editable_status = False
    config_args = []
    i = 0
    # Pass 0: optional positional inference for sisdk and output suffix.
    # Only attempt if corresponding explicit flags not already present.
    inferred_sisdk = False
    inferred_suffix = False
    if raw_extras:
        scan_indices = []
        for idx, tok in enumerate(raw_extras):
            if tok.startswith('-'):
                continue
            scan_indices.append(idx)
        for idx in scan_indices:
            tok = raw_extras[idx]
            if sisdk is None and not inferred_sisdk:
                # Candidate sisdk path
                if os.path.isdir(tok):
                    # Heuristic: directory hint contains typical sdk markers
                    markers = ['simplicity', 'sdk', 'extension']
                    try:
                        listing = os.listdir(tok)
                    except Exception:
                        listing = []
                    if any(m in tok.lower() for m in markers) or any(m in ' '.join(listing).lower() for m in markers):
                        sisdk = tok
                        inferred_sisdk = True
                        logger.debug("(compat) Inferred --sisdk=%s", sisdk)
                        continue
            if output_suffix is None and not inferred_suffix and not tok.startswith('-') and ':' not in tok:
                # Avoid taking a likely configuration argument (heuristic: contains '=' or ':')
                if tok != sisdk:  # don't reuse sisdk path
                    output_suffix = tok
                    inferred_suffix = True
                    logger.debug("(compat) Inferred --output_suffix=%s", output_suffix)
            if inferred_sisdk and inferred_suffix:
                break

    while i < len(raw_extras):
        token = raw_extras[i]
        if token == "--skip_gen":
            skip_gen = True
            i += 1
        elif token == "--sisdk":
            if i + 1 >= len(raw_extras):
                sys.exit("--sisdk requires a path argument")
            sisdk = raw_extras[i + 1]
            i += 2
        elif token == "--output_suffix":
            if i + 1 >= len(raw_extras):
                sys.exit("--output_suffix requires a value")
            output_suffix = raw_extras[i + 1]
            i += 2
        elif token in ("--jobs", "-j"):
            if i + 1 >= len(raw_extras):
                sys.exit("--jobs/-j requires a number")
            jobs = int(raw_extras[i + 1])
            i += 2
        elif token in ("-v", "--verbose"):
            verbose = True
            i += 1
        elif token in ("-n", "--dry_run"):
            dry_run = True
            i += 1
        elif token == "--rebuild_app":
            rebuild_app = True
            i += 1
        elif token == "--rebuild_stack":
            rebuild_stack = True
            i += 1
        elif token == "--rebuild_all":
            rebuild_all = True
            i += 1
        elif token == "--ci":
            ci = True
            i += 1
        elif token == "--with":
            if i + 1 >= len(raw_extras):
                sys.exit("--with requires a value")
            with_options = raw_extras[i + 1]
            print("with options = ",with_options)
            i += 2
        elif token == "--cmake":
            cmake = True
            i += 1
        elif token == "--enable_editable":
            enable_editable = True
            i += 1
        elif token == "--disable_editable":
            disable_editable = True
            i += 1
        elif token == "--editable_status":
            editable_status = True
            i += 1
        # Skip tokens already consumed by positional inference (do not double-add)
        elif inferred_sisdk and token == sisdk:
            i += 1
        elif inferred_suffix and token == output_suffix:
            i += 1
        else:
            # Unrecognized -> forward to slc generate
            config_args.append(token)
            i += 1
    
    # Enable editable mode by default unless CI mode is enabled or explicitly disabled
    if not ci and not disable_editable and not enable_editable:
        enable_editable = True
        # Note: debug message will be logged later after logging is configured
    elif ci and enable_editable:
        # Warning will be logged later after logging is configured
        enable_editable = False
    
    return dict(skip_gen=skip_gen, sisdk=sisdk, output_suffix=output_suffix,
                jobs=jobs, verbose=verbose, dry_run=dry_run, rebuild_app=rebuild_app, 
                rebuild_stack=rebuild_stack, rebuild_all=rebuild_all, ci=ci, with_options=with_options, cmake=cmake, 
                enable_editable=enable_editable, disable_editable=disable_editable, editable_status=editable_status, config_args=config_args)


def detect_project(app_path: Path, flags: dict):
    name = app_path.name
    logger.debug("Detecting project type for: %s", name)
    logger.debug("CMake flag enabled: %s", flags['cmake'])
    
    if flags['cmake']:
        logger.debug("Using CMake generator logic")
        if name.endswith('.slcw'):
            logger.debug("Detected .slcw file (solution)")
            if '917-soc' in name:
                logger.debug("Detected 917-soc solution")
                silabs_app = name.replace(".slcw","")
                make_file = f"{silabs_app}.solution.Makefile"
            else:
                logger.debug("Detected bootloader solution")
                silabs_app = name.replace("-bootloader.slcw","")  # strip -bootloader.slcw
                make_file = f"{silabs_app}-bootloader.solution.Makefile"
            project_flag = "-w"
        elif name.endswith('.slcp'):
            logger.debug("Detected .slcp file (project)")
            silabs_app = name.replace(".slcp","")
            project_flag = "-p"
            make_file = f"{silabs_app}.Makefile"
        else:
            logger.error("Invalid file extension: %s", name)
            sys.exit("Provided path must end with .slcp or .slcw")
    else:
        logger.debug("Using Makefile generator logic")
        if name.endswith('.slcw'):
            logger.debug("Detected .slcw file (solution)")
            if '917-soc' in name:
                logger.debug("Detected 917-soc solution")
                silabs_app = name.replace(".slcw","")
                make_file = f"{silabs_app}.solution.Makefile"
            else:
                logger.debug("Detected bootloader solution")
                silabs_app = name.replace("-bootloader.slcw","")  # strip -bootloader.slcw
                make_file = f"{silabs_app}-bootloader.solution.Makefile"
            project_flag = "-w"
        elif name.endswith('.slcp'):
            logger.debug("Detected .slcp file (project)")
            silabs_app = name.replace(".slcp","")
            project_flag = "-p"
            make_file = f"{silabs_app}.Makefile"
        else:
            logger.error("Invalid file extension: %s", name)
            sys.exit("Provided path must end with .slcp or .slcw")
    
    logger.debug("Project detection results:")
    logger.debug("  - name: %s", name)
    logger.debug("  - silabs_app: %s", silabs_app)
    logger.debug("  - make_file: %s", make_file)
    logger.debug("  - project_flag: %s", project_flag)
    
    return silabs_app, make_file, project_flag, name


def derive_output_dir(board: str, silabs_app: str, app_path: Path, output_suffix: str | None):
    brd_only = board.split(';', 1)[0]
    if app_path.suffix == '.slcw':
        out = Path('out') / brd_only / f"{silabs_app}-solution"
    else:
        out = Path('out') / brd_only / silabs_app
    if output_suffix:
        out = Path(str(out) + f"-{output_suffix}")
    return out


def read_env_file(matter_root: Path, env: dict, verbose=False):
    env_file = matter_root / 'slc' / 'tools' / '.env'
    if env_file.is_file():
        logger.info("Loading env from %s", env_file)
        for line in env_file.read_text().splitlines():
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip()
        if 'TOOLS_PATH' in env:
            env['PATH'] = f"{env['TOOLS_PATH']}:{env['PATH']}"
    else:
        logger.debug(".env not found. Attempting to locate toolchain via slt locate ...")
        # replicate slt locate logic
        def locate(tool):
            proc = run(["slt", "locate", tool], check=False, capture=True, verbose=verbose)
            if proc.returncode != 0:
                return None
            for l in (proc.stdout or '').splitlines():
                if 'Path' in l:
                    # Accept last whitespace-separated token that is an existing path or contains '/'
                    parts = l.strip().split()
                    candidates = [p for p in parts if '/' in p or p.startswith('/')]
                    if candidates:
                        return candidates[-1]
            return None
        gcc = locate('gcc-arm-none-eabi')
        cmake = locate('cmake')
        slc_cli = locate('slc-cli')
        java21 = locate('java21')
        commander_dir = run(["slt", "where", "commander"], capture=True, check=False, verbose=verbose).stdout or ''
        commander_dir = commander_dir.strip()
        path_segments = []
        if gcc:
            env['ARM_GCC_DIR'] = gcc
            logger.debug("ARM_GCC_DIR set to %s", gcc)
        if java21:
            env['JAVA_HOME'] = java21
            logger.debug("JAVA_HOME set to %s", java21)
            # Add Java bin directory to path based on OS
            import platform
            os_name = platform.system().lower()
            if os_name == 'darwin':  # macOS
                java_bin_path = str(Path(java21) / 'jre' / 'Contents' / 'Home' / 'bin')
            else:  # Windows and Linux
                java_bin_path = str(Path(java21) / 'jre' / 'bin')
            # Only add to path_segments if the directory exists
            if Path(java_bin_path).exists():
                path_segments.append(java_bin_path)
                logger.debug("Java bin path added: %s", java_bin_path)
            else:
                logger.warning("Java bin path does not exist: %s", java_bin_path)
        if gcc:
            path_segments.append(str(Path(gcc)/'bin'))
        if cmake:
            path_segments.append(str(Path(cmake)/'bin')) if not cmake.endswith('/bin') else path_segments.append(cmake)
        if slc_cli:
            path_segments.append(slc_cli)
        if commander_dir:
            path_segments.append(commander_dir)
        prepend = ':'.join([p for p in path_segments if p])
        if prepend:
            env['PATH'] = f"{prepend}:{env['PATH']}"
            logger.debug("PATH prepended with %s", prepend)
        # POST_BUILD_EXE
        commander_exe = shutil.which('commander', path=env['PATH']) if 'PATH' in env else shutil.which('commander')
        if commander_exe:
            env['POST_BUILD_EXE'] = commander_exe
            logger.debug("POST_BUILD_EXE=%s", commander_exe)
        if verbose:
            logger.debug("Updated PATH prepend: %s", prepend)
            logger.debug("POST_BUILD_EXE=%s", env.get('POST_BUILD_EXE'))


def main():
    args = parse_args()
    flags = classify_extra_args(args.extras)
    configure_logging(flags['verbose'])
    
    # Log editable mode decisions now that logging is configured
    if flags['ci'] and '--enable_editable' in args.extras:
        logger.warning("Both --ci and --enable_editable specified. CI mode takes precedence.")
    elif flags['enable_editable'] and not flags['disable_editable'] and not flags['ci'] and '--enable_editable' not in args.extras:
        logger.debug("Editable mode enabled by default (not in CI mode)")
    
    logger.debug("input flags = %s", flags)
    matter_root = Path.cwd().resolve()
    logger.debug("Matter root = %s", matter_root)
    
    # Initialize Matter editable manager
    editable_manager = MatterEditableManager(matter_root)
    
    # Handle editable-only commands (exit after completion)
    if flags['editable_status']:
        editable_manager.show_status()
        return
    
    if flags['enable_editable']:
        success = editable_manager.enable_editable_mode()
        if not success:
            sys.exit(1)
        # Continue with build if other flags are present
        if not any([flags['disable_editable'], not args.app_path]):
            logger.info("Editable mode enabled, continuing with build...")
    
    if flags['disable_editable']:
        success = editable_manager.disable_editable_mode()
        if not success:
            sys.exit(1)
        # Exit if this was the only operation requested
        if not args.app_path or args.app_path == 'dummy':
            return
    
    logger.info("slt update --self")
    if not flags['dry_run']:
        run(["slt", "update", "--self"], verbose=flags['verbose'])

    app_path = Path(args.app_path)
    if not app_path.exists():
        logger.error("Application path not found: %s", app_path)
        sys.exit(1)

    silabs_app, make_file, project_flag, app_name = detect_project(app_path, flags)
    output_dir = derive_output_dir(args.board, silabs_app, app_path, flags['output_suffix'])

    # Initial pre-steps (mimic original script top lines)
    env = os.environ.copy()

    if not flags['ci']:
        # Comment revision_mode="scm"
        run(["make", "comment_revision_mode"])

    # Handle rebuild options
    if flags['rebuild_all']:
        logger.info("Rebuilding all packages (app and stack)...")
        logger.debug("Removing all matter packages...")
        clean_cmd = ["make", "remove_all_matter_packages", "-f", "Makefile"]
        if flags['dry_run']:
            logger.info("[DRY-RUN] Would run: %s", " ".join(shlex.quote(c) for c in clean_cmd))
        else:
            run(clean_cmd, env=env, verbose=flags['verbose'])

    if flags['rebuild_app'] or flags['rebuild_all']:
        logger.info("Rebuilding application components...")
        clean_app_cmd = ["make", "create_app_package", "-f", "Makefile"]
        if flags['dry_run']:
            logger.info("[DRY-RUN] Would run: %s", " ".join(shlex.quote(c) for c in clean_app_cmd))
        else:
            run(clean_app_cmd, env=env, verbose=flags['verbose'], check=False)  # May not exist in all makefiles

    if flags['rebuild_stack'] or flags['rebuild_all']:
        logger.info("Rebuilding stack components...")
        clean_stack_cmd = ["make", "create_stack_package", "-f", "Makefile"]
        if flags['dry_run']:
            logger.info("[DRY-RUN] Would run: %s", " ".join(shlex.quote(c) for c in clean_stack_cmd))
        else:
            run(clean_stack_cmd, env=env, verbose=flags['verbose'], check=False)  # May not exist in all makefiles

    if flags['ci']:
        logger.info("make install_app_package")
        install_app_command = ["make", "install_app_package"]
        proc = run(install_app_command, capture=True, verbose=flags['verbose'])
        where_matter_app_command = ["slt", "where", "matter_app"]
        proc = run(where_matter_app_command, capture=True, verbose=flags['verbose'])
        sample_app_path = (proc.stdout).strip()
        logger.info("Sample app path: %s", sample_app_path)
        # Change directory to sample app path
        try:
            os.chdir(sample_app_path)
        except FileNotFoundError:
            logger.error("Cannot cd to sample app path: %s", sample_app_path)
            sys.exit(1)
    else:
        sample_app_path = str(matter_root)

    # Determine GSDK root
    gsdk_root = flags['sisdk'] or str(matter_root / ' App dir = ' / 'simplicity_sdk')
    logger.debug("current path = %s", os.getcwd())
    app_dir = app_path.parent
    os.chdir(app_dir)
    if not flags['ci']:
        logger.debug("current working directory %s",os.getcwd())
        run(["slt", "install"], verbose=flags['verbose'], capture=True, ignore_error_patterns=IGNORABLE_ERROR_PATTERNS)
        logger.debug("Done slt install")
    else:
        # slt install within the project directory of app_path
        logger.debug("App dir = %s", app_dir)
        if not flags['dry_run']:
            logger.debug("Running SLT install...")
            run(["slt", "install"], verbose=flags['verbose'], capture=True, ignore_error_patterns=IGNORABLE_ERROR_PATTERNS)
        else:
            logger.info("[DRY-RUN] Would run: slt install in %s", app_dir)

    run(["slt", "locate", "matter"], verbose=flags['verbose'], capture=True, ignore_error_patterns=IGNORABLE_ERROR_PATTERNS)

    # Environment (.env or locate tools)
    read_env_file(matter_root, env, verbose=flags['verbose'])
    
    #update out dir to be same as dev dir
    output_dir = os.path.join(matter_root,str(output_dir))


    # slc generate
    if not flags['skip_gen']:
        # Construct board argument with optional --with options
        # Merge board with --with options using comma separation
        if flags['with_options']:
            board_arg = f"{args.board},{flags['with_options']}"
        else:
            board_arg = args.board

        # Choose generator based on --cmake flag
        generator = "cmake" if flags['cmake'] else "makefile"
        logger.info("Output dir = %s", output_dir)
        logger.info("App name = %s", app_name)
        gen_cmd = ["slc", "generate", "-d", output_dir, project_flag, str(app_name), "--with", board_arg]
        gen_cmd.extend(flags['config_args'])
        gen_cmd.extend(["--generator-timeout=2000", "-o", generator])
        logger.info("Generating project files using %s generator...", generator)
        logger.debug("Current Dir = %s", os.getcwd())
        if flags['dry_run']:
            logger.info("[DRY-RUN] Would run: %s", " ".join(shlex.quote(c) for c in gen_cmd))
        else:
            # Always stream slc generate output so logs are visible regardless of --verbose
            run(gen_cmd, env=env)
    else:
        logger.info("Skipping generation step (--skip_gen)")

    # Build step - choose between make and cmake
    if flags['cmake']:
        # Use cmake build with preset
        cmake_presets_path = os.path.join(output_dir,"cmake_gcc")
        os.chdir(cmake_presets_path)
        cmake_cmd = ["cmake", "--workflow", "--preset", "project"]
        logger.info("Building via cmake with preset...")
        logger.debug("CMake presets path: %s", cmake_presets_path)
        
        if flags['dry_run']:
            logger.info("[DRY-RUN] Would run: %s", " ".join(shlex.quote(c) for c in cmake_cmd))
        else:
            # Always stream cmake output
            run(cmake_cmd, env=env, verbose=True)
    else:
        # Use make build
        make_cmd = ["make", "all", "-C", str(output_dir), "-f", make_file, f"-j{flags['jobs']}"]    
        logger.info("Building via make...")
        if flags['dry_run']:
            logger.info("[DRY-RUN] Would run: %s", " ".join(shlex.quote(c) for c in make_cmd))
        else:
            # Always stream make output
            run(make_cmd, env=env, verbose=True)
    
    # Return to matter root
    logger.debug("Changing dir to Matter Root = %s", matter_root)
    os.chdir(matter_root)
    if not flags['ci']:
        # uncomment revision_mode="scm"
        run(["make", "uncomment_revision_mode"])
        run(["make", "disable_editable"])
    logger.info("Build complete.")

if __name__ == '__main__':
    try:
        import shutil  # used in read_env_file
        main()
    except KeyboardInterrupt:
        logger.error("Build interrupted.")
        sys.exit(130)
