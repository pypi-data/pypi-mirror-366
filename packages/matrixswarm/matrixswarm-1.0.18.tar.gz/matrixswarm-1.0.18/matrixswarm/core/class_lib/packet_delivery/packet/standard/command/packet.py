import time, uuid
from matrixswarm.core.class_lib.packet_delivery.interfaces.base_packet import BasePacket

class Packet(BasePacket):

    def set_data(self, data: dict):
        try:
            required = ["handler"]
            for r in required:
                if r not in data:
                    raise ValueError(f"Missing required field: {r}")

            self._payload = {
                "timestamp": int(time.time()),
                "nonce": uuid.uuid4().hex,  # or os.urandom(16).hex() for a cryptographic nonce
                "handler": data.get("handler"),  #msg.send.warning.message_do_something
                "origin": data.get("origin", "unknown"),
                "sig": data.get("sig", "unknown"),
                "hash": data.get("hash", "unknown"),
                "service_injection": data.get("service_injection", {}), #if set locate the service under matrixswarm.core.* and inject data then inject inside handler
                "content": data.get("content", {}),
                # if set locate the service under matrixswarm.core.* and inject data then inject inside handler
            }
            self._data = data
            self._error_code = 0
            self._error_msg = ""
        except Exception as e:
            self._valid = False
            self._error_code = 1
            self._error_msg = str(e)

