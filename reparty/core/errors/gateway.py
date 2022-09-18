class RepartyException(Exception):
    """Base class for all exception made by reparty"""
    
class GatewayClosed(RepartyException):
    def __init__(self, code: int, msg: str):
        self.code = code
        self.msg = msg
        super().__init__(f"Gateway closed with code {code}: {msg}")