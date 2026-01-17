#!/usr/bin/env python3

import os
import hashlib
import shutil
import argparse
import sys

DEVICE = "breeze"

ANDROID_MK_HEADER = f"""#
# Automatically generated file. DO NOT MODIFY
#

LOCAL_PATH := $(call my-dir)

ifeq ($(TARGET_DEVICE),{DEVICE})

"""

ANDROID_MK_FOOTER = """
endif
"""

CONFIG_MK_HEADER = """#
# Automatically generated file. DO NOT MODIFY
#

AB_OTA_PARTITIONS += \\
"""

def sha1sum(path, bufsize=1024 * 1024):
    sha1 = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(bufsize), b""):
            sha1.update(chunk)
    return sha1.hexdigest()

def main():
    parser = argparse.ArgumentParser(
        description="Copy radio images and generate Android.mk + config.mk"
    )
    parser.add_argument(
        "path",
        help="Directory containing .img files"
    )

    args = parser.parse_args()
    input_dir = os.path.abspath(args.path)

    if not os.path.isdir(input_dir):
        sys.exit(f"Error: {input_dir} is not a directory")

    os.makedirs("radio", exist_ok=True)

    images = sorted(
        f for f in os.listdir(input_dir)
        if f.lower().endswith(".img")
        and os.path.isfile(os.path.join(input_dir, f))
    )

    if not images:
        sys.exit("No .img files found")

    partitions = []

    # Android.mk
    with open("Android.mk", "w", newline="\n") as mk:
        mk.write(ANDROID_MK_HEADER)

        for img in images:
            src = os.path.join(input_dir, img)
            dst = os.path.join("radio", img)

            shutil.copy2(src, dst)

            sha1 = sha1sum(dst)
            partition = os.path.splitext(img)[0]
            partitions.append(partition)

            mk.write(
                f"$(call add-radio-file-sha1-checked,radio/{img},{sha1})\n"
            )

        mk.write(ANDROID_MK_FOOTER)

    # config.mk
    with open("config.mk", "w", newline="\n") as cfg:
        cfg.write(CONFIG_MK_HEADER)

        for i, part in enumerate(partitions):
            end = "\n" if i == len(partitions) - 1 else " \\\n"
            cfg.write(f"    {part}{end}")

    print("Succssfully extracted radio images")

if __name__ == "__main__":
    main()
