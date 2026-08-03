"""Copy example AppConfig headers into matter_app app dirs for package builds.

matter_app does not ship third_party/matter_sdk. Project .slcp files that need an
early include path (to beat src/app/AppConfig.h) should reference in-package
paths like slc/apps/<app>/<variant>/include/.

Catalog: packages/_shared/app_include_map.yaml
  app_dir (repo-relative) -> examples/.../silabs/include (matter_sdk-relative)

Sync copies all *.h from each mapped SDK include dir into <app_dir>/include/.
"""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Mapping

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore

_SHARED_DIR = Path(__file__).resolve().parent
DEFAULT_MAP_PATH = _SHARED_DIR / "app_include_map.yaml"


def resolve_sdk_root_for_sync(repo_root: Path) -> Path:
    """Locate matter_sdk sources without importing Conan-backed helpers.

    Order: MATTER_SDK_SOURCE_ROOT, then repo third_party/matter_sdk submodule.
    """
    env_root = os.environ.get("MATTER_SDK_SOURCE_ROOT", "").strip()
    if env_root:
        return Path(env_root).resolve()
    submodule = repo_root / "third_party" / "matter_sdk"
    if submodule.is_dir() and (submodule / "src").is_dir():
        return submodule.resolve()
    raise FileNotFoundError(
        "matter_sdk sources not found for app include sync. "
        "Init third_party/matter_sdk or set MATTER_SDK_SOURCE_ROOT."
    )


def load_app_include_map(map_path: Path | None = None) -> dict[str, str]:
    """Load app_dir -> sdk_include_dir mapping from YAML."""
    path = Path(map_path) if map_path else DEFAULT_MAP_PATH
    if not path.is_file():
        raise FileNotFoundError(f"App include map not found: {path}")
    if yaml is None:
        raise RuntimeError("PyYAML is required to load app_include_map.yaml")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(f"App include map must be a mapping: {path}")
    out: dict[str, str] = {}
    for key, value in data.items():
        if key is None or value is None:
            continue
        app_rel = str(key).strip().replace("\\", "/")
        sdk_rel = str(value).strip().replace("\\", "/")
        if not app_rel or app_rel.startswith("#") or not sdk_rel:
            continue
        out[app_rel] = sdk_rel
    if not out:
        raise ValueError(f"App include map is empty: {path}")
    return out


def sync_app_includes(
    dst_root: Path,
    sdk_root: Path,
    app_map: Mapping[str, str] | None = None,
    map_path: Path | None = None,
) -> list[Path]:
    """Copy mapped *.h headers under dst_root. Returns list of written files."""
    dst_root = Path(dst_root).resolve()
    sdk_root = Path(sdk_root).resolve()
    mapping = dict(app_map) if app_map is not None else load_app_include_map(map_path)
    written: list[Path] = []
    for app_rel, sdk_inc_rel in sorted(mapping.items()):
        src_dir = sdk_root / sdk_inc_rel
        dst_dir = dst_root / app_rel / "include"
        if not src_dir.is_dir():
            raise FileNotFoundError(f"Missing SDK include dir: {src_dir}")
        headers = sorted(src_dir.glob("*.h"))
        if not headers:
            raise FileNotFoundError(f"No *.h headers in SDK include dir: {src_dir}")
        dst_dir.mkdir(parents=True, exist_ok=True)
        for src in headers:
            dst = dst_dir / src.name
            shutil.copy2(src, dst)
            written.append(dst)
    return written
