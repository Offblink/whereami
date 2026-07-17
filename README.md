# whereami

WiFi 定位。无需 GPS，无需 API Key——有 WiFi 就行。

```
$ whereami
扫描到 8 个WiFi，查询中...
坐标       : 39.904200, 116.407396
精度       : ±87m
地址       : 北京市东城区东长安街, 中国
https://maps.google.com/?q=39.904200,116.407396

```
未检测到代理时：

```
$ whereami
提示: 未检测到代理，地址反查将不可用
      使用 --proxy 7890 手动指定端口号

扫描到 8 个WiFi，查询中...
坐标       : 39.904200, 116.407396
精度       : ±87m
地址       : (开启代理可显示街道级地址)
https://maps.google.com/?q=39.904200,116.407396
```
## 原理

1. 扫描周围 WiFi 的 BSSID
2. 发给 Apple 中国定位服务器 (`gs-loc-cn.apple.com`)
3. Apple 返回该区域所有已知 AP 的 GPS 坐标
4. 取中位数 → 你的位置 ±100m

**为什么能定位：** 每台 iPhone 定位时都会把周围的 WiFi 热点上报给 Apple。Apple 建了全球 WiFi-坐标映射库。我们反向查询——"这些 BSSID 对应什么坐标？"

**前提：** 你附近有过 iPhone 用户。

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

### 手动指定代理端口

```bash
whereami --proxy 7890
```

自动检测 Windows 系统代理，无需手动指定。仅当检测失败或使用非标准端口时才需 `--proxy`。

## 为什么存在

三个项目散落在 GitHub 角落，各自解决了一个子问题，但从未被整合：

| 项目 | 发现了什么 | 缺什么 |
|---|---|---|
| [iSniff-GPS](https://github.com/hubert3/iSniff-GPS) | Apple 定位 API 的 protobuf 协议 | 需要手动抓 BSSID，命令行复杂 |
| [apple_bssid_locator](https://github.com/darkosancanin/apple_bssid_locator) | 封装成简洁 Python 脚本 | 只支持全球端点，国内不可用 |
| [apple-corelocation-experiments](https://github.com/acheong08/apple-corelocation-experiments) | 发现中国专线 `gs-loc-cn.apple.com` | Go 实现，普通人用不了 |

**whereami = 三条河流汇到一处。**

扫描 WiFi → 调中国端点 → 中位数三角定位 → 逆地理编码 → 一个命令出结果。

好的项目不缺，缺的是散落在各处无人发现、无人整合。这个项目不过是整合了三者而已。
