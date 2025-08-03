from pyinteno import IntenoDevice, IntenoInfo, WirelessIntenoDevice, WiredIntenoDevice

EXAMPLE_DEVICE_LIST = {
    "client-1": {
        "hostname": "device-1",
        "ipaddr": "192.168.0.1",
        "macaddr": "00:00:00:00:00:01",
        "network": "guest",
        "device": "br-guest",
        "dhcp": True,
        "connected": True,
        "active_connections": 1,
        "wireless": True,
        "wdev": "wl1.1",
        "frequency": "2.4GHz",
        "rssi": -65,
        "snr": 13,
        "idle": 2,
        "in_network": 6925,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 505476,
        "rx_bytes": 927209,
        "tx_rate": 65000,
        "rx_rate": 39000,
    },
    "client-2": {
        "hostname": "device-2",
        "ipaddr": "192.168.0.2",
        "macaddr": "00:00:00:00:00:02",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 16,
        "wireless": True,
        "wdev": "wl1",
        "frequency": "2.4GHz",
        "rssi": -58,
        "snr": 20,
        "idle": 7,
        "in_network": 2914,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 394140601,
        "rx_bytes": 5963717,
        "tx_rate": 78000,
        "rx_rate": 1000,
    },
    "client-3": {
        "hostname": "device-3",
        "ipaddr": "192.168.0.3",
        "macaddr": "00:00:00:00:00:03",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 123,
        "wireless": True,
        "wdev": "wl0",
        "frequency": "5GHz",
        "rssi": -60,
        "snr": 11,
        "idle": 0,
        "in_network": 6257,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 298324460,
        "rx_bytes": 58884648,
        "tx_rate": 866667,
        "rx_rate": 650000,
    },
    "client-4": {
        "hostname": "device-4",
        "ipaddr": "192.168.0.4",
        "macaddr": "00:00:00:00:00:04",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 1,
        "wireless": False,
        "ethport": "eth4",
        "linkspeed": "Auto-negotiated 1000 Mbps Full Duplex",
    },
    "client-5": {
        "hostname": "device-5",
        "ipaddr": "192.168.0.5",
        "macaddr": "00:00:00:00:00:05",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 4,
        "wireless": True,
        "wdev": "wl1",
        "frequency": "2.4GHz",
        "rssi": -66,
        "snr": 12,
        "idle": 0,
        "in_network": 6933,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 157539330,
        "rx_bytes": 5052784,
        "tx_rate": 65000,
        "rx_rate": 24000,
    },
    "client-6": {
        "hostname": "device-6",
        "ipaddr": "192.168.0.6",
        "macaddr": "00:00:00:00:00:06",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 1,
        "wireless": True,
        "wdev": "wl1",
        "frequency": "2.4GHz",
        "rssi": -68,
        "snr": 10,
        "idle": 1,
        "in_network": 6918,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 156116082,
        "rx_bytes": 993680,
        "tx_rate": 54000,
        "rx_rate": 24000,
    },
    "client-7": {
        "hostname": "device-7",
        "ipaddr": "192.168.0.7",
        "macaddr": "00:00:00:00:00:07",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 2,
        "wireless": True,
        "wdev": "wl1",
        "frequency": "2.4GHz",
        "rssi": -47,
        "snr": 31,
        "idle": 1,
        "in_network": 6914,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 155972022,
        "rx_bytes": 755234,
        "tx_rate": 58500,
        "rx_rate": 1000,
    },
    "client-8": {
        "hostname": "device-8",
        "ipaddr": "192.168.0.8",
        "macaddr": "00:00:00:00:00:08",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 2,
        "wireless": True,
        "wdev": "wl1",
        "frequency": "2.4GHz",
        "rssi": -59,
        "snr": 19,
        "idle": 0,
        "in_network": 6894,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 155971721,
        "rx_bytes": 749581,
        "tx_rate": 39000,
        "rx_rate": 1000,
    },
    "client-9": {
        "hostname": "device-9",
        "ipaddr": "192.168.0.9",
        "macaddr": "00:00:00:00:00:09",
        "network": "lan",
        "device": "br-lan",
        "dhcp": True,
        "connected": True,
        "active_connections": 0,
        "wireless": True,
        "wdev": "wl0",
        "frequency": "5GHz",
        "rssi": -43,
        "snr": 28,
        "idle": 57,
        "in_network": 7057,
        "wme": True,
        "ps": True,
        "n_cap": True,
        "vht_cap": True,
        "tx_bytes": 155177002,
        "rx_bytes": 47129,
        "tx_rate": 390000,
        "rx_rate": 24000,
    },
    "client-10": {
        "hostname": "device-10",
        "ipaddr": "192.168.0.10",
        "macaddr": "00:00:00:00:00:0A",
        "network": "lan",
        "device": "br-lan",
        "dhcp": False,
        "connected": False,
        "wireless": False,
    },
}

EXAMPLE_DEVICE_SPEC = {
    "keys": {"auth": "AUTH_KEY_PLACEHOLDER", "wpa": "WPA_KEY_PLACEHOLDER"},
    "memoryKB": {
        "buffers": 0,
        "free": 262576,
        "shared": 340,
        "total": 487988,
        "used": 225412,
    },
    "specs": {
        "adsl": False,
        "dect": False,
        "eth_ports": 5,
        "usb": True,
        "vdsl": False,
        "voice": True,
        "voice_ports": 6,
        "wifi": True,
    },
    "system": {
        "basemac": "00:00:00:00:00:00",
        "boardid": "BOARD_ID_PLACEHOLDER",
        "brcmver": "BRCM_VER_PLACEHOLDER",
        "bspver": "BSP_VER_PLACEHOLDER",
        "cfever": "CFE_VER_PLACEHOLDER",
        "cpu_per": 4,
        "date": "Sat Aug  2 14:20:09 2025",
        "filesystem": "UBIFS",
        "firmware": "FIRMWARE_PLACEHOLDER",
        "hardware": "HARDWARE_PLACEHOLDER",
        "kernel": "4.1.38",
        "localtime": 1754137209,
        "model": "MODEL_PLACEHOLDER",
        "name": "DEVICE_NAME_PLACEHOLDER",
        "procs": 155,
        "serialno": "SERIAL_NO_PLACEHOLDER",
        "socmod": "SOCMOD_PLACEHOLDER",
        "socrev": "SOCREV_PLACEHOLDER",
        "uptime": "10d 7h 35m 44s",
    },
}


def test_inteno_device_from_dict():
    device = IntenoDevice.from_dict(EXAMPLE_DEVICE_LIST["client-1"])
    assert device.hostname == "device-1"
    # check that all devices are parsed correctly
    for key, value in EXAMPLE_DEVICE_LIST.items():
        device = IntenoDevice.from_dict(value)
        assert device.hostname == value["hostname"]
        assert device.ipaddr == value["ipaddr"]
        assert device.macaddr == value["macaddr"]
        assert device.network == value["network"]
        assert device.device == value["device"]
        assert device.dhcp == value["dhcp"]
        assert device.connected == value["connected"]
        if "active_connections" in value:
            assert device.active_connections == value["active_connections"]
        if "wireless" in value:
            assert device.wireless == value["wireless"]
            if device.wireless:
                assert isinstance(device, WirelessIntenoDevice)
                assert device.wdev == value["wdev"]
                assert device.frequency == value["frequency"]
                assert device.rssi == value["rssi"]
                assert device.snr == value["snr"]
                assert device.idle == value["idle"]
                assert device.in_network == value["in_network"]
                assert device.wme == value["wme"]
                assert device.ps == value["ps"]
                assert device.n_cap == value["n_cap"]
                assert device.vht_cap == value["vht_cap"]
                assert device.tx_bytes == value["tx_bytes"]
                assert device.rx_bytes == value["rx_bytes"]
                assert device.tx_rate == value["tx_rate"]
                assert device.rx_rate == value["rx_rate"]
            elif "ethport" in value and "linkspeed" in value:
                assert isinstance(device, WiredIntenoDevice)
                assert device.ethport == value["ethport"]
                assert device.linkspeed == value["linkspeed"]


def test_inteno_info_from_dict():
    info = IntenoInfo.from_dict(EXAMPLE_DEVICE_SPEC)
    assert info.keys.auth == EXAMPLE_DEVICE_SPEC["keys"]["auth"]
    assert info.keys.wpa == EXAMPLE_DEVICE_SPEC["keys"]["wpa"]
    assert info.memoryKB.buffers == EXAMPLE_DEVICE_SPEC["memoryKB"]["buffers"]
    assert info.memoryKB.free == EXAMPLE_DEVICE_SPEC["memoryKB"]["free"]
    assert info.memoryKB.shared == EXAMPLE_DEVICE_SPEC["memoryKB"]["shared"]
    assert info.memoryKB.total == EXAMPLE_DEVICE_SPEC["memoryKB"]["total"]
    assert info.memoryKB.used == EXAMPLE_DEVICE_SPEC["memoryKB"]["used"]
    assert info.specs.adsl == EXAMPLE_DEVICE_SPEC["specs"]["adsl"]
    assert info.specs.dect == EXAMPLE_DEVICE_SPEC["specs"]["dect"]
    assert info.specs.eth_ports == EXAMPLE_DEVICE_SPEC["specs"]["eth_ports"]
    assert info.specs.usb == EXAMPLE_DEVICE_SPEC["specs"]["usb"]
    assert info.specs.vdsl == EXAMPLE_DEVICE_SPEC["specs"]["vdsl"]
    assert info.specs.voice == EXAMPLE_DEVICE_SPEC["specs"]["voice"]
    assert info.specs.voice_ports == EXAMPLE_DEVICE_SPEC["specs"]["voice_ports"]
    assert info.system.basemac == EXAMPLE_DEVICE_SPEC["system"]["basemac"]
    assert info.system.boardid == EXAMPLE_DEVICE_SPEC["system"]["boardid"]
    assert info.system.brcmver == EXAMPLE_DEVICE_SPEC["system"]["brcmver"]
    assert info.system.bspver == EXAMPLE_DEVICE_SPEC["system"]["bspver"]
    assert info.system.cfever == EXAMPLE_DEVICE_SPEC["system"]["cfever"]
    assert info.system.cpu_per == EXAMPLE_DEVICE_SPEC["system"]["cpu_per"]
    assert info.system.date == EXAMPLE_DEVICE_SPEC["system"]["date"]
    assert info.system.filesystem == EXAMPLE_DEVICE_SPEC["system"]["filesystem"]
    assert info.system.firmware == EXAMPLE_DEVICE_SPEC["system"]["firmware"]
    assert info.system.hardware == EXAMPLE_DEVICE_SPEC["system"]["hardware"]
    assert info.system.kernel == EXAMPLE_DEVICE_SPEC["system"]["kernel"]
    assert info.system.localtime == EXAMPLE_DEVICE_SPEC["system"]["localtime"]
    assert info.system.model == EXAMPLE_DEVICE_SPEC["system"]["model"]
    assert info.system.name == EXAMPLE_DEVICE_SPEC["system"]["name"]
    assert info.system.procs == EXAMPLE_DEVICE_SPEC["system"]["procs"]
    assert info.system.serialno == EXAMPLE_DEVICE_SPEC["system"]["serialno"]
    assert info.system.socmod == EXAMPLE_DEVICE_SPEC["system"]["socmod"]
    assert info.system.socrev == EXAMPLE_DEVICE_SPEC["system"]["socrev"]
    assert info.system.uptime == EXAMPLE_DEVICE_SPEC["system"]["uptime"]
