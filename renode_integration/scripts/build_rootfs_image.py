#!/usr/bin/env python3
"""Build matter-rootfs.ext2 from the Antmicro base plus the Matter overlay"""

import os
import shutil
import subprocess
import urllib.request

import common


def debugfs_cat(debugfs, image, path):
    result = subprocess.run(
        [debugfs, "-R", f"cat {path}", image],
        capture_output=True,
        text=True,
    )
    return result.stdout


def main():
    out_dir = os.path.join(common.RENODE_INTEGRATION_DIR, "out", "guest-rootfs")
    output = os.path.join(out_dir, "matter-rootfs.ext2")
    overlay = os.path.join(common.RENODE_INTEGRATION_DIR, "guest", "rootfs-overlay")
    base_cache = os.path.join(common.CACHE_DIR, "base-rootfs.ext2")
    work = os.path.join(out_dir, "rootfs-work")
    os.makedirs(work, exist_ok=True)
    os.makedirs(common.CACHE_DIR, exist_ok=True)

    debugfs = common.find_debugfs()
    url = common.manifest_lookup("base_rootfs.url")
    expected_sha = common.manifest_lookup("base_rootfs.sha256")

    if not os.path.isfile(base_cache) or common.sha256_file(base_cache) != expected_sha:
        print("Downloading base rootfs...")
        partial = base_cache + ".partial"
        urllib.request.urlretrieve(url, partial)
        os.replace(partial, base_cache)
    actual_sha = common.sha256_file(base_cache)
    if actual_sha != expected_sha:
        common.die(f"base rootfs sha256 {actual_sha} != {expected_sha}")

    shutil.copyfile(base_cache, output)

    fstab_lines = []
    for line in debugfs_cat(debugfs, base_cache, "/etc/fstab").splitlines(keepends=True):
        fields = line.split()
        if len(fields) >= 2 and fields[1] == "/docker":
            continue
        fstab_lines.append(line)
    fstab_path = os.path.join(work, "fstab")
    with open(fstab_path, "w", encoding="utf-8") as handle:
        handle.writelines(fstab_lines)

    commands = [
        "rm /etc/fstab",
        f"write {fstab_path} /etc/fstab",
        "rm /etc/init.d/S60dockerd",
    ]
    overlay_files = []
    for root, _, names in os.walk(overlay):
        for name in names:
            overlay_files.append(os.path.join(root, name))
    for src in sorted(overlay_files):
        dest = "/" + os.path.relpath(src, overlay)
        mode = "0100755" if os.access(src, os.X_OK) else "0100644"
        commands.extend(
            [
                f"mkdir {os.path.dirname(dest)}",
                f"rm {dest}",
                f"write {src} {dest}",
                f"set_inode_field {dest} mode {mode}",
                f"set_inode_field {dest} uid 0",
                f"set_inode_field {dest} gid 0",
            ]
        )

    cmds_path = os.path.join(work, "debugfs.cmds")
    with open(cmds_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(commands) + "\n")

    print("Applying rootfs changes...")
    log_path = os.path.join(work, "debugfs.log")
    with open(log_path, "w", encoding="utf-8") as log:
        subprocess.run([debugfs, "-w", "-f", cmds_path, output], stdout=subprocess.DEVNULL, stderr=log)

    services = debugfs_cat(debugfs, output, "/etc/init.d/S99matter-services")
    if "matter-services" not in services:
        common.die(f"overlay not applied, see {log_path}")
    if "/docker" in debugfs_cat(debugfs, output, "/etc/fstab"):
        common.die("fstab still mounts /docker")

    size = os.path.getsize(output)
    print(f"Built {output} ({size // (1024 * 1024)}M)")


if __name__ == "__main__":
    main()
