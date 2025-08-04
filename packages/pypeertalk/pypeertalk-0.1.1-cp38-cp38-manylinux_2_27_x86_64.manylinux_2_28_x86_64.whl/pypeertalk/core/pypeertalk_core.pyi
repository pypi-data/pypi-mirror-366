class DeviceInfo:
    product_id: int
    udid: str
    handle: int

class PeerTalkClient:
    def __init__(self, device: DeviceInfo, port: int):
        ...

    def get_latest_message(self, timeout_ms: int) -> bytes:
        ...

def get_connected_devices() -> list[DeviceInfo]:
    ...