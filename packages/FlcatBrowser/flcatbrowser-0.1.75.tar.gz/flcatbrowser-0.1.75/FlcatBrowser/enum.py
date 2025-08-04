from enum import Enum

class ListenEventType(Enum):
    REQUEST = 'request'

class NetworkListenMode(Enum):
    XHR = 'xhr'
    # CDP方式优先级较低
    CDP = 'cdp'