# whereami

WiFi 定位。无需 GPS，无需 API Key——有 WiFi 就行。

```
$ whereami
扫描到 8 个WiFi，查询中...
坐标       : 22.974209, 114.712296
精度       : ±104m
地址       : 惠东县自然资源局, 景民路, 平山街道, 惠东县, 惠州市, 广东省, 516300, 中国
https://maps.google.com/?q=22.974209,114.712296
```

关代理时：

```
地址       : (开启代理可显示街道级地址)
```

## 原理

1. 扫描周围 WiFi 的 BSSID
2. 发给 Apple 中国定位服务器 (`gs-loc-cn.apple.com`)
3. Apple 返回该区域所有已知 AP 的 GPS 坐标
4. 取中位数 → 你的位置 ±100m

## 安装

```bash
pip install git+https://github.com/Offblink/whereami.git
```

或 clone 后本地安装：

```bash
git clone https://github.com/Offblink/whereami.git
cd whereami
pip install .
```

## 使用

```bash
whereami
```

终端任意位置直接敲，不需要参数，不需要注册，不需要 key。

## Credit

- [darkosancanin/apple_bssid_locator](https://github.com/darkosancanin/apple_bssid_locator) — Python BSSID 定位
- [hubert3/iSniff-GPS](https://github.com/hubert3/iSniff-GPS) — Apple protobuf 逆向
- [acheong08/apple-corelocation-experiments](https://github.com/acheong08/apple-corelocation-experiments) — 发现中国端点
