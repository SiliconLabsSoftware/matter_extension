#!/usr/bin/env python3
"""
Validate Matter extension using `slc validate matter.slce`.
This validates all extension metadata in the repo (components, studio metadata,
templates.xml references) in a single pass.

Ownership model:
  MATTER_FAILURE   Files under the repo root and outside third_party/. These
                   are Matter owned, any finding causes a non-zero exit and
                   fails CI.
  MATTER_ADVISORY  Matter owned files where the finding is intentionally
                   deferred. Reported but do not fail CI.
  SUBMODULE        Files under third_party/ Not Matter extension 
                   responsibility, reported as informational only.

Per section policy:
  SDK warnings
    Path based ownership. MATTER_FAILURE if matter owned, SUBMODULE otherwise.

  Config File on Include Path
    Path based on the config file path embedded in the finding.
    MATTER_FAILURE if matter owned, SUBMODULE otherwise.

  Studio SDK Metadata
    "not defined in a templates.xml file": path based on the slcp path.
      SUBMODULE if under third_party/, MATTER_FAILURE if under slc/apps.
    "No board data found for": MATTER_ADVISORY. Board data depends on the
      SDK version being validated against, advisory until boards are GA.

  Missing Documentation Reference
    MATTER_ADVISORY for all findings. User visible components
    lack documentation: blocks today, advisory until work is done.

  Any other section
    Fully enforced, path based: SUBMODULE if third_party/, otherwise
    MATTER_FAILURE.

Usage (from repo root):
  python3 slc/script/validate_extension.py
  python3 slc/script/validate_extension.py --full-log # show full slc validate log
"""

import argparse
import logging
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple, Optional, Tuple

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_SLCE_PATH = _REPO_ROOT / "matter.slce"
_SDK_PATH = _REPO_ROOT / "third_party" / "simplicity_sdk"
_WISECONNECT_SLCE = _REPO_ROOT / "third_party" / "wifi_sdk" / "wiseconnect.slce"
_THIRD_PARTY_ROOT = _REPO_ROOT / "third_party"

# Finding categories
MATTER_FAILURE = "matter-failure"
MATTER_ADVISORY = "matter-advisory"
SUBMODULE = "submodule"

def _parse_sections(output: str) -> Dict[str, List[str]]:
    """
    Split slc validate output into named sections.

    Returns a dict mapping section name -> list of finding lines.
    The key "preamble" holds lines before the first section delimiter.
    """
    sections: Dict[str, List[str]] = {"preamble": []}
    current = "preamble"
    for line in output.splitlines():
        if line.strip() == ".-----~*~-----.":
            current = None
            continue
        if current is None:
            current = line.strip()
            sections[current] = []
            continue
        sections[current].append(line)
    return sections

def _finding_lines(section_lines: List[str]) -> List[str]:
    """ Return finding lines from a section. """
    return [
        stripped
        for line in section_lines
        if (stripped := line.strip()).startswith("-")
    ]

def _parse_sdk_warning_findings(preamble_lines: List[str]) -> List[Tuple[str, str]]:
    """
    Parse SDK metadata warnings from the slc validate preamble.

    Returns (filepath, message) pairs grouped under:
      SDK warnings:
      Parsing metadata encountered some warnings
      /path/to/file.slcc
        - finding text
    """
    findings: List[Tuple[str, str]] = []
    in_sdk_warnings = False
    current_file: Optional[str] = None

    for line in preamble_lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped == "SDK warnings:":
            in_sdk_warnings = True
            current_file = None
            continue
        if not in_sdk_warnings:
            continue
        if stripped.startswith("Parsing metadata encountered"):
            continue
        if stripped.startswith("- "):
            if current_file is not None:
                findings.append((current_file, stripped[2:]))
            continue
        current_file = stripped

    return findings

def _output_is_parseable(output: str) -> bool:
    """Return True if output contains at least one section delimiter or SDK warnings header."""
    return ".-----~*~-----." in output or "SDK warnings:" in output

def _is_matter_owned_path(path_str: str) -> bool:
    """ Return True if a path is owned by this extension (CI failure on finding). """
    path = Path(path_str)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    try:
        path.resolve().relative_to(_REPO_ROOT.resolve())
    except ValueError:
        return True
    try:
        path.resolve().relative_to(_THIRD_PARTY_ROOT.resolve())
        return False
    except ValueError:
        return True

def _extract_path_from_finding(finding: str) -> Optional[str]:
    """
    Extract the most relevant file path from a finding string.

    Tries absolute paths first, then repo-relative paths starting with 'third_party/' or 'slc/'.
    """
    m = re.search(r"(?:^|\s)(/[^\s(]+)", finding)
    if m:
        return m.group(1)
    m = re.search(r"(?:^|\s)((?:third_party|slc)/[^\s(]+)", finding)
    if m:
        return m.group(1)
    return None

class SectionStats(NamedTuple):
    """Per-section finding tally."""
    section: str
    total: int
    matter_failures: int
    matter_advisories: int
    submodule: int

def _path_based(path_str: Optional[str]) -> str:
    """SUBMODULE if the path is under third_party/, else MATTER_FAILURE."""
    if path_str and not _is_matter_owned_path(path_str):
        return SUBMODULE
    return MATTER_FAILURE

def _classify_finding(section: str, finding: str, filepath: Optional[str] = None) -> str:
    """
    Return MATTER_FAILURE, MATTER_ADVISORY, or SUBMODULE for a single finding.

    filepath: for SDK warnings the path is known separately, pass it explicitly.
              For all other sections it is extracted from the finding string.
    """
    # Advisory sections: Matter owned but intentionally deferred.
    if section == "Missing Documentation Reference":
        return MATTER_ADVISORY
    if section == "Studio SDK Metadata" and "No board data found for" in finding:
        return MATTER_ADVISORY

    # Everything else is decided by path ownership.
    path_str = filepath if filepath is not None else _extract_path_from_finding(finding)
    return _path_based(path_str)

def _iter_findings(
    sections: Dict[str, List[str]],
) -> Iterator[Tuple[str, str, Optional[str]]]:
    """
    Yield (section, finding, filepath) for every finding across all sections.

    SDK warnings live in the preamble with a known filepath, all other findings
    are bulleted lines within a delimited section.
    """
    for filepath, message in _parse_sdk_warning_findings(sections.get("preamble", [])):
        yield "SDK warnings", f"{filepath}: {message}", filepath
    for section, lines in sections.items():
        if section == "preamble":
            continue
        for finding in _finding_lines(lines):
            yield section, finding, None

def _classify(
    sections: Dict[str, List[str]],
) -> Tuple[
    List[Tuple[str, str]],
    List[Tuple[str, str]],
    List[Tuple[str, str]],
    List[SectionStats],
]:
    """
    Classify findings from every slc validate section.

    Returns:
        matter_failures   - (section, finding) that must fail CI
        matter_advisories - (section, finding) that are Matter owned but deferred
        submodule_finds   - (section, finding) from submodule code
        section_stats     - per-section tallies, in first-seen order
    """
    buckets: Dict[str, List[Tuple[str, str]]] = {
        MATTER_FAILURE: [],
        MATTER_ADVISORY: [],
        SUBMODULE: [],
    }
    counts: Dict[str, List[int]] = {}
    order: List[str] = []

    for section, finding, filepath in _iter_findings(sections):
        cat = _classify_finding(section, finding, filepath=filepath)
        buckets[cat].append((section, finding))
        if section not in counts:
            counts[section] = [0, 0, 0]  # [failures, advisories, submodule]
            order.append(section)
        idx = {MATTER_FAILURE: 0, MATTER_ADVISORY: 1, SUBMODULE: 2}[cat]
        counts[section][idx] += 1

    section_stats = [
        SectionStats(section, sum(counts[section]), *counts[section])
        for section in order
    ]
    return (
        buckets[MATTER_FAILURE],
        buckets[MATTER_ADVISORY],
        buckets[SUBMODULE],
        section_stats,
    )

def _log_section_summary(section_stats: List[SectionStats]) -> None:
    """Log a oneline summary per slc validate section."""
    logger.info("slc validate sections:")
    for stat in section_stats:
        logger.info(
            "  %s: %d findings (%d matter-failure, %d matter-advisory, %d submodule)",
            stat.section,
            stat.total,
            stat.matter_failures,
            stat.matter_advisories,
            stat.submodule,
        )

def _resolve_slc_executable() -> str:
    """Return the path to the slc executable, falling back to slt where slc-cli."""
    slc = shutil.which("slc")
    if slc:
        return slc

    try:
        result = subprocess.run(
            ["slt", "where", "slc-cli"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            cli_dir = result.stdout.strip()
            candidate = Path(cli_dir) / "slc"
            if candidate.is_file():
                return str(candidate)
    except FileNotFoundError:
        pass

    logger.error(
        "slc not found, ensure slc-cli is installed and on PATH.\n"
        "Install with: slt install slc-cli\n"
        'Then add to PATH: export PATH="$(slt where slc-cli):$PATH"'
    )
    sys.exit(2)

def _require_sdk_paths() -> Tuple[str, str]:
    """Return (simplicity_sdk, wiseconnect.slce) paths or exit if submodules are missing."""
    if not _SDK_PATH.is_dir():
        logger.error(
            "Simplicity SDK not found at %s, init the submodule: "
            "git submodule update --init third_party/simplicity_sdk",
            _SDK_PATH,
        )
        sys.exit(2)
    if not _WISECONNECT_SLCE.is_file():
        logger.error(
            "WiseConnect extension not found at %s, init the submodule: "
            "git submodule update --init third_party/wifi_sdk",
            _WISECONNECT_SLCE,
        )
        sys.exit(2)
    return str(_SDK_PATH), str(_WISECONNECT_SLCE)

def _run_slc_validate(sdk_path: str, wiseconnect_path: str) -> Tuple[int, str]:
    """Run `slc validate matter.slce` and return (exit_code, combined_output)."""
    cmd = [
        _resolve_slc_executable(),
        "validate",
        str(_SLCE_PATH),
        "--sdk-package-path",
        f"{sdk_path},{wiseconnect_path}",
    ]
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(_REPO_ROOT),
    )
    combined = (result.stdout or "") + (result.stderr or "")
    return result.returncode, combined

def _parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the Matter SLC extension via `slc validate matter.slce`.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--full-log",
        action="store_true",
        help="Print the full slc validate log (stdout/stderr combined).",
    )
    return parser.parse_args(argv)

def main(argv: List[str]) -> int:
    args = _parse_args(argv)

    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
    )

    sdk_path, wiseconnect_path = _require_sdk_paths()
    logger.info(
        "Running: slc validate %s --sdk-package-path %s,%s",
        _SLCE_PATH,
        sdk_path,
        wiseconnect_path,
    )

    slc_exit_code, output = _run_slc_validate(sdk_path, wiseconnect_path)

    if args.full_log and output:
        print(output if output.endswith("\n") else output + "\n")

    if slc_exit_code >= 128:
        logger.error(
            "slc was killed by a signal (exit %d), treating as tool error.",
            slc_exit_code,
        )
        return 2

    if slc_exit_code != 0 and not _output_is_parseable(output):
        logger.error(
            "slc validate exited %d with no parseable output, treating as tool error.",
            slc_exit_code,
        )
        return 2

    if slc_exit_code != 0:
        logger.info("slc validate exited with code %d", slc_exit_code)

    sections = _parse_sections(output)
    if not args.full_log:
        preamble_lines = [ln for ln in sections.get("preamble", []) if ln.strip()]
        if preamble_lines:
            logger.info("slc validate preamble:\n%s", "\n".join(preamble_lines))

    matter_failures, matter_advisories, submodule_finds, section_stats = _classify(sections)
    _log_section_summary(section_stats)

    if matter_failures:
        logger.error(
            "Validation failed with %d Matter owned finding(s):", len(matter_failures)
        )
        for section, finding in matter_failures:
            logger.error("  [%s] %s", section, finding)
        return 1

    parts = []
    if matter_advisories:
        parts.append(f"{len(matter_advisories)} Matter-advisory (extension owned, deferred)")
    if submodule_finds:
        parts.append(f"{len(submodule_finds)} submodule (not extension owned)")

    if parts:
        logger.info(
            "Validation passed. %s. Run with --full-log for the full slc validate log.",
            "; ".join(parts),
        )
    else:
        logger.info("Validation passed. No issues detected.")

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
