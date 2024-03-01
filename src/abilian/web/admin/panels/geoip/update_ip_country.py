#!/usr/bin/env python
"""Read public domain (CC-0) database of IP/country and export to MMDB format.

Resulting file file is written in curent working directory.
"""
import csv
import ssl
import urllib.request
from collections import defaultdict
from pathlib import Path
from tempfile import TemporaryDirectory

import certifi
import maxminddb
from mmdb_writer import MMDBWriter
from netaddr import IPRange, IPSet

CSV_DB = (
    "https://cdn.jsdelivr.net/npm/@ip-location-db/geo-whois-asn-country/"
    "geo-whois-asn-country-ipv4.csv"
)
MMDB_FILENAME = "ip_country.mmdb"


def fetch_csv_db(csv_db_path: Path) -> None:
    with urllib.request.urlopen(  # noqa: S310
        CSV_DB, context=ssl.create_default_context(cafile=certifi.where())
    ) as response:
        csv_db_path.write_bytes(response.read())
    size = csv_db_path.stat().st_size / 2**20
    print(f"CSV DB: {csv_db_path.name} {size:.1f} MB")


def write_db(db_path: Path, csv_db_path: Path):
    data = defaultdict(list)
    with open(csv_db_path) as file:
        reader = csv.reader(file)
        for line in reader:
            data[line[2]].append(IPRange(line[0], line[1]))

    writer = MMDBWriter()
    for country, cidrs in data.items():
        writer.insert_network(IPSet(cidrs), {"country": country})
    writer.to_db_file(str(db_path))


def check_db_done(db_path: Path) -> None:
    free_fr_ip = "212.27.48.10"
    ibm_com_ip = "104.85.45.20"
    db = maxminddb.open_database(db_path)
    result1 = db.get(free_fr_ip)
    assert result1["country"] == "FR"
    result2 = db.get(ibm_com_ip)
    assert result2["country"] == "US"


def main() -> None:
    local_path = Path.cwd()
    db_path = local_path / MMDB_FILENAME
    with TemporaryDirectory(prefix="ipcountry-", dir=local_path) as temp_dir:
        print(f"temp dir: {temp_dir}")
        csv_db_path = Path(temp_dir) / "ip_country.csv"
        fetch_csv_db(csv_db_path)
        write_db(db_path, csv_db_path)
    check_db_done(db_path)
    size = db_path.stat().st_size // 2**20
    print(f"MMDB: {db_path.name} {size:.1f} MB")


if __name__ == "__main__":
    main()
