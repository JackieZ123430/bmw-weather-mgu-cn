#!/usr/bin/env python3
"""Build BMW Weather with the pinned upstream iDrive 7 app kit on the head unit."""
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

UPSTREAM_COMMIT = "f5e4b8daa6c930f83a93fd6d6a158ab08c00c748"
UPSTREAM_URL = "https://codeload.github.com/cauliflowermossgrape/idrive7-apps/tar.gz/" + UPSTREAM_COMMIT


def safe_extract(archive, destination):
    root = os.path.realpath(destination)
    for member in archive.getmembers():
        target = os.path.realpath(os.path.join(destination, member.name))
        if target != root and not target.startswith(root + os.sep):
            raise RuntimeError("Unsafe path in upstream source archive")
    archive.extractall(destination)


def add_internet_permission(package_file):
    with open(package_file, "r", encoding="utf-8") as stream:
        package = json.load(stream)
    package["mguInternet"] = True
    package["mguHmi"] = ["ID7"]
    with open(package_file, "w", encoding="utf-8") as stream:
        json.dump(package, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: build_unit.py <id> <version> <app-dir>")
    app_id, version, app_dir = sys.argv[1:4]
    repo = os.getcwd()
    app_source = os.path.realpath(os.path.join(repo, app_dir))
    sdk_source = os.path.join(repo, "oap-sdk")
    if not os.path.isdir(app_source):
        raise RuntimeError("App source folder not found: " + app_source)
    if not os.path.isdir(sdk_source):
        raise RuntimeError("MGU Store did not provide the BMW SDK donor (oap-sdk)")

    with tempfile.TemporaryDirectory(prefix="bmw-weather-build-") as work:
        request = urllib.request.Request(UPSTREAM_URL, headers={"User-Agent": "BMW-Weather-MGU-build"})
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read()
        archive = tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz")
        safe_extract(archive, work)
        archive.close()

        roots = [os.path.join(work, n) for n in os.listdir(work) if os.path.isdir(os.path.join(work, n))]
        if len(roots) != 1:
            raise RuntimeError("Unexpected upstream source archive layout")
        upstream = roots[0]

        target_app = os.path.join(upstream, "apps", app_id)
        if os.path.exists(target_app):
            shutil.rmtree(target_app)
        shutil.copytree(app_source, target_app)
        target_sdk = os.path.join(upstream, "oap-sdk")
        if os.path.exists(target_sdk):
            shutil.rmtree(target_sdk)
        shutil.copytree(sdk_source, target_sdk)

        subprocess.check_call([sys.executable, os.path.join(upstream, "kit", "tools", "build.py"), app_id], cwd=upstream)
        built = os.path.join(upstream, "dist", app_id + "@" + version + ".tgz")
        if not os.path.isfile(built):
            raise RuntimeError("Upstream builder did not produce " + os.path.basename(built))

        with tempfile.TemporaryDirectory(prefix="bmw-weather-package-") as stage:
            with tarfile.open(built, "r:gz") as source:
                safe_extract(source, stage)
            package_files = []
            for root, dirs, names in os.walk(stage):
                for name in names:
                    if name == "package.json":
                        package_files.append(os.path.join(root, name))
            if not package_files:
                raise RuntimeError("Built OAP package has no package.json")
            add_internet_permission(package_files[0])
            repacked = os.path.join(work, "repacked.tgz")
            with tarfile.open(repacked, "w:gz") as output_tar:
                for root, dirs, names in os.walk(stage):
                    dirs.sort()
                    for name in sorted(names):
                        full = os.path.join(root, name)
                        output_tar.add(full, arcname=os.path.relpath(full, stage), recursive=False)
            shutil.copy2(repacked, built)

        output = os.path.join(repo, "dist", app_id + "@" + version + ".tgz")
        os.makedirs(os.path.dirname(output), exist_ok=True)
        shutil.copy2(built, output)


if __name__ == "__main__":
    main()
