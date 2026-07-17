#!/usr/bin/env python
"""whereami — WiFi geolocation via Apple's location service, zero API key.

Uses your nearby WiFi BSSIDs to query gs-loc-cn.apple.com (China CDN).
Returns GPS coordinates ±~100m. No GPS hardware needed.

Credit: based on darkosancanin/apple_bssid_locator and iSniff-GPS.
"""

import subprocess
import re
import sys
import struct
import statistics
import os

import requests
import AppleWLoc_pb2

# Auto-detect Windows system proxy (requests doesn't use it by default)
_proxy_ok = False

def _setup_proxy() -> bool:
    global _proxy_ok
    if sys.platform != "win32":
        return False
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings") as key:
            enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")
            if enabled:
                server, _ = winreg.QueryValueEx(key, "ProxyServer")
                os.environ.setdefault("HTTPS_PROXY", f"http://{server}")
                os.environ.setdefault("HTTP_PROXY", f"http://{server}")
                _proxy_ok = True
                return True
    except Exception:
        pass
    return False

_setup_proxy()

CHINA_URL = "https://gs-loc-cn.apple.com/clls/wloc"
GLOBAL_URL = "https://gs-loc.apple.com/clls/wloc"
DEFAULT_URL = CHINA_URL  # we live here


def scan_wifi() -> list[str]:
    """Return all visible BSSIDs. Windows only for now."""
    raw = subprocess.run(
        ["netsh", "wlan", "show", "networks", "mode=bssid"],
        capture_output=True,
    ).stdout.decode("gbk", errors="replace")
    return list(set(re.findall(r"BSSID\s+\d+\s*:\s*([0-9a-fA-F:]{17})", raw)))


def _envelope(payload: bytes) -> bytes:
    """Wrap protobuf in ARPC envelope (mimics iOS locationd)."""
    return b"".join(
        [
            struct.pack(">H", 1),
            b"\x00\x05en_US",
            b"\x00\x13com.apple.locationd",
            b"\x00\x0a8.1.12B411",
            struct.pack(">I", 1),
            struct.pack(">I", len(payload)),
            payload,
        ]
    )


def query(bssids: list[str], *, china: bool = True) -> list[dict]:
    """Send BSSIDs to Apple, return all nearby AP coordinates."""
    wloc = AppleWLoc_pb2.AppleWLoc()
    wloc.unknown_value1 = 0
    wloc.return_single_result = 0
    for b in bssids:
        wloc.wifi_devices.add().bssid = b.lower()

    body = _envelope(wloc.SerializeToString())
    url = CHINA_URL if china else GLOBAL_URL

    r = requests.post(
        url,
        headers={
            "User-Agent": "locationd/1753.17 CFNetwork/889.9 Darwin/17.2.0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "*/*",
        },
        data=body,
        timeout=30,
    )
    if r.status_code != 200:
        print(f"HTTP {r.status_code}", file=sys.stderr)
        return []

    resp = AppleWLoc_pb2.AppleWLoc()
    resp.ParseFromString(r.content[10:])

    results = []
    for dev in resp.wifi_devices:
        if dev.HasField("location"):
            lat = dev.location.latitude * 1e-8
            lon = dev.location.longitude * 1e-8
            if lat == -180.0 and lon == -180.0:
                continue
            results.append({"lat": lat, "lon": lon})
    return results



def geocode(lat: float, lon: float) -> str:
    """Reverse geocode via Nominatim (OpenStreetMap)."""
    try:
        r = requests.get(
            "https://nominatim.openstreetmap.org/reverse",
            params={"lat": lat, "lon": lon, "format": "json", "accept-language": "zh"},
            headers={"User-Agent": "whereami/0.1"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return data.get("display_name", "")
    except Exception:
        return ""

def main() -> None:
    bssids = scan_wifi()
    if not bssids:
        sys.exit("未检测到 WiFi 网络")

    print(f"扫描到 {len(bssids)} 个WiFi，查询中...")
    aps = query(bssids)

    if not aps:
        sys.exit("当前位置不在 Apple 数据库中")

    lats = [a["lat"] for a in aps]
    lons = [a["lon"] for a in aps]
    med_lat, med_lon = statistics.median(lats), statistics.median(lons)

    std_m = (statistics.stdev(lats) if len(lats) > 1 else 0) * 111_000

    print(f"坐标       : {med_lat:.6f}, {med_lon:.6f}")
    print(f"精度       : ±{std_m:.0f}m")
    addr = geocode(med_lat, med_lon)
    if addr:
        print(f"地址       : {addr}")
    elif not _proxy_ok:
        print("地址       : (开启代理可显示街道级地址)")
    print(f"https://maps.google.com/?q={med_lat:.6f},{med_lon:.6f}")


if __name__ == "__main__":
    main()
