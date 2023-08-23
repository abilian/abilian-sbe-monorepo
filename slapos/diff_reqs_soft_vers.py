import sys
import configparser
from pathlib import Path
from typing import Any
from collections.abc import Mapping


def version_content(path: Path) -> Mapping:
    config = configparser.ConfigParser()
    config.read(path)
    return config["versions"]


def parse_version(path) -> dict[str, str]:
    result = {}
    versions = version_content(path)
    for key in sorted(versions.keys()):
        result[key.lower()] = str(versions[key])
        # print(f"{key} = {val}")
    return result


def quick_parse_req(path: Path) -> dict[str, str]:
    result = {}
    try:
        content = path.read_text().split("\n")
        for line in content:
            try:
                if "==" not in line:
                    if line.strip():
                        print("skip:", line)
                    continue
                key, val = line.split("==")
                result[key.lower()] = val.split()[0]

            except ValueError:
                print("===============")
                print(line)
                print("===============")
                raise
    except OSError:
        pass
    return result


def diff(path_reqs, path_software_cfg):
    reqs = quick_parse_req(path_reqs)
    versions = parse_version(path_software_cfg)
    show_not_in_versions(reqs, versions)


def show_not_in_versions(reqs, versions):
    not_in_versions = []
    diff_in_versions = []
    not_in_reqs = []
    for key, val in reqs.items():
        if key not in versions:
            not_in_versions.append(f"{key} = {val}")
            continue
        # remove ":whl" if any:
        versions_val = versions[key].split(":")[0]
        if val != versions_val:
            diff_in_versions.append(f"{key} = {val} //  {versions_val}")
    for key, versions_val in versions.items():
        if key not in reqs:
            not_in_reqs.append(f"{key} = {versions_val}")
    print("=========================================================")
    print("Not in software versions:")
    print()
    print("\n".join(not_in_versions))
    print()
    print("Not in requirements:")
    print()
    print("\n".join(not_in_reqs))
    print()
    print("Different versions (reqs // versions):")
    print()
    print("\n".join(diff_in_versions))
    print()


def main():
    path_reqs = Path(sys.argv[-2])
    path_software_cfg = Path(sys.argv[-1])
    diff(path_reqs, path_software_cfg)


if __name__ == "__main__":
    main()
