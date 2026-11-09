#!/usr/bin/env python3
"""Build this app with the upstream iDrive 7 app kit on the head unit.

The MGU Store supplies the BMW SDK donor in ./oap-sdk. We fetch a pinned
public revision of idrive7-apps, overlay this app, and use its normal builder.
"""
import io
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.request

UPSTREAM_COMMIT = "f5e4b8daa6c930f83a93fd6d6a158ab08c00c748"
UPSTREAM_URL = (
    "https://codeload.github.com/cauliflowermossgrape/idrive7-apps/"
    "tar.gz/" + UPSTREAM_COMMIT
)


def safe_extract(archive, destination):
    root = os.path.realpath(destination)
    for member in archive.getmembers():
        target = os.path.realpath(os.path.join(destination, member.name))
        if target != root and not target.startswith(root + os.sep):
            raise RuntimeError("Unsafe path in upstream source archive")
    archive.extractall(destination)


def main():
    if len(sys.argv) != 4:
        raise SystemExit("usage: build_unit.py <id> <version> <app-dir>")
    app_id, version, app_dir = sys.argv[1:4]
    repo = os.getcwd()
    app_source = os.path.realpath(os.path.join(repo, app_dir))
    if not os.path.isdir(app_source):
        raise RuntimeError("App source folder not found: " + app_source)

    sdk_source = os.path.join(repo, "oap-sdk")
    if not os.path.isdir(sdk_source):
        raise RuntimeError("MGU Store did not provide the BMW SDK donor (oap-sdk)")

    with tempfile.TemporaryDirectory(prefix="bmw-weather-build-") as work:
        request = urllib.request.Request(
            UPSTREAM_URL,
            headers={"User-Agent": "BMW-Weather-MGU-build"}
        )
        with urllib.request.urlopen(request, timeout=90) as response:
            payload = response.read()

        archive = tarfile.open(fileobj=io.BytesIO(payload), mode="r:gz")
        safe_extract(archive, work)
        archive.close()

        roots = [
            os.path.join(work, name)
            for name in os.listdir(work)
            if os.path.isdir(os.path.join(work, name))
        ]
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

        subprocess.check_call(
            [sys.executable, os.path.join(upstream, "kit", "tools", "build.py"), app_id],
            cwd=upstream
        )

        built = os.path.join(upstream, "dist", app_id + "@" + version + ".tgz")
        if not os.path.isfile(built):
            raise RuntimeError("Upstream builder did not produce " + os.path.basename(built))

        output = os.path.join(repo, "dist", app_id + "@" + version + ".tgz")
        os.makedirs(os.path.dirname(output), exist_ok=True)
        shutil.copy2(built, output)


if __name__ == "__main__":
    main()
