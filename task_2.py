# 4. Результати порівняння представлені у вигляді таблиці (10 балів).

# 5. Код є адаптованим до великих наборів даних (10 балів).
import os
import ipaddress
import time
import json

import gdown

from datasketch import HyperLogLog


def load_data(file_id: str, file_name: str) -> list[str]:
    """
    Downloads a log file from Google Drive and extracts valid IPv4 addresses.
    Invalid or malformed log lines are ignored.

    Raises:
        RuntimeError: If the file cannot be downloaded.
    """

    ip_addresses = []

    # Download file from Google Drive
    file = gdown.download(
        f"https://drive.google.com/uc?export=download&id={file_id}",
        file_name,
        quiet=False,
    )
    # Check if download was successful
    if file is None or not os.path.exists(file_name):
        raise RuntimeError("Не вдалося завантажити файл з Google Drive")

    # Read log file line by line
    with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()

            # Parse JSON line
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue  # ignore malformed JSON lines

            # Extract remote_addr
            ip_str = obj.get("remote_addr")
            if not ip_str:
                continue  # ignore lines without remote_addr

            try:
                ip = ipaddress.ip_address(ip_str)
                if ip.version == 4:
                    ip_addresses.append(ip_str)
            except ValueError:
                continue  # ignore invalid IP addresses

    return ip_addresses


def count_unique_ips(data: list[str]) -> int:
    """
    Count the number of unique IP addresses in the given list.

    Args:
        data (list[str]): A list of IP addresses.

    Returns:
        int: The number of unique IP addresses.
    """
    return len(set(data))


def hyperloglog(data: list[str]) -> int:
    """
    Count the number of unique IP addresses in the given list using HyperLogLog.

    Args:
        data (list[str]): A list of IP addresses.

    Returns:
        int: The number of unique IP addresses.
    """
    hll = HyperLogLog()
    for ip in data:
        hll.update(ip.encode("utf-8"))
    return int(hll.count())


def compare_methods(data: list[str]):
    """Compare the number of unique IP addresses in the given list using both exact count and HyperLogLog."""
    # Count unique IPs
    start_time = time.time()
    unique_ips = count_unique_ips(data)
    execution_time = time.time() - start_time
    # HyperLogLog
    start_time = time.time()
    unique_ips_hll = hyperloglog(data)
    execution_time_hll = time.time() - start_time

    print("Comparison:")
    print("{:>25} {:>15} {:>15}".format("", "Exact Count", "HyperLogLog"))
    print("{:>25} {:>15.1f} {:>15.1f}".format("Unique IPs", unique_ips, unique_ips_hll))
    print(
        "{:>25} {:>15.5f} {:>15.5f}".format(
            "Execution Time", execution_time, execution_time_hll
        )
    )


if __name__ == "__main__":
    file_id = "13NUCSG7l_z2B7gYuQubYIpIjJTnwOAOb"
    file_name = "lms-stage-access.log"
    ip_addresses = load_data(file_id, file_name)
    # Compare methods
    compare_methods(ip_addresses)
