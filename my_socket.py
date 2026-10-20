import ctypes
import ctypes.wintypes
import struct

# Load Windows Winsock API directly
ws2 = ctypes.WinDLL('ws2_32', use_last_error=True)

# Constants
AF_INET = 2
SOCK_STREAM = 1
IPPROTO_TCP = 6
INVALID_SOCKET = ctypes.c_size_t(-1).value
SOCKET_ERROR = -1


class WSADATA(ctypes.Structure):
    _fields_ = [
        ('wVersion',      ctypes.c_ushort),
        ('wHighVersion',  ctypes.c_ushort),
        ('szDescription', ctypes.c_char * 257),
        ('szSystemStatus',ctypes.c_char * 129),
        ('iMaxSockets',   ctypes.c_ushort),
        ('iMaxUdpDg',     ctypes.c_ushort),
        ('lpVendorInfo',  ctypes.c_char_p),
    ]


class SOCKADDR_IN(ctypes.Structure):
    _fields_ = [
        ('sin_family', ctypes.c_short),
        ('sin_port',   ctypes.c_ushort),
        ('sin_addr',   ctypes.c_uint32),
        ('sin_zero',   ctypes.c_char * 8),
    ]


def _init_winsock():
    wsadata = WSADATA()
    result = ws2.WSAStartup(0x0202, ctypes.byref(wsadata))
    if result != 0:
        raise OSError(f"WSAStartup failed: {result}")


def _make_addr(host, port):
    addr = SOCKADDR_IN()
    addr.sin_family = AF_INET
    addr.sin_port = ws2.htons(port)
    addr.sin_addr = ws2.inet_addr(host.encode())
    return addr


class MySocket:
    """Client socket — connects to a server and exchanges messages."""

    def __init__(self):
        _init_winsock()
        self._sock = ws2.socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        if self._sock == INVALID_SOCKET:
            raise OSError(f"socket() failed: {ctypes.get_last_error()}")
        print("[MySocket] Socket created via Windows API.")

    def connect(self, host, port):
        addr = _make_addr(host, port)
        result = ws2.connect(self._sock, ctypes.byref(addr), ctypes.sizeof(addr))
        if result == SOCKET_ERROR:
            raise OSError(f"connect() failed: {ctypes.get_last_error()}")
        print(f"[MySocket] Connected to {host}:{port}")

    def send(self, message):
        data = message.encode('utf-8')
        result = ws2.send(self._sock, data, len(data), 0)
        if result == SOCKET_ERROR:
            raise OSError(f"send() failed: {ctypes.get_last_error()}")
        print(f"[MySocket] Sent: {message}")

    def receive(self, buffer_size=1024):
        buf = ctypes.create_string_buffer(buffer_size)
        result = ws2.recv(self._sock, buf, buffer_size, 0)
        if result == SOCKET_ERROR:
            raise OSError(f"recv() failed: {ctypes.get_last_error()}")
        message = buf.raw[:result].decode('utf-8')
        print(f"[MySocket] Received: {message}")
        return message

    def close(self):
        ws2.closesocket(self._sock)
        ws2.WSACleanup()
        print("[MySocket] Connection closed.")


class MyServerSocket:
    """Server socket — listens for a client and exchanges messages."""

    def __init__(self, host, port):
        _init_winsock()
        self._sock = ws2.socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)
        if self._sock == INVALID_SOCKET:
            raise OSError(f"socket() failed: {ctypes.get_last_error()}")

        addr = _make_addr(host, port)
        if ws2.bind(self._sock, ctypes.byref(addr), ctypes.sizeof(addr)) == SOCKET_ERROR:
            raise OSError(f"bind() failed: {ctypes.get_last_error()}")

        if ws2.listen(self._sock, 1) == SOCKET_ERROR:
            raise OSError(f"listen() failed: {ctypes.get_last_error()}")

        print(f"[MyServerSocket] Listening on {host}:{port}")
        self._conn = None

    def accept(self):
        addr = SOCKADDR_IN()
        addr_len = ctypes.c_int(ctypes.sizeof(addr))
        self._conn = ws2.accept(self._sock, ctypes.byref(addr), ctypes.byref(addr_len))
        if self._conn == INVALID_SOCKET:
            raise OSError(f"accept() failed: {ctypes.get_last_error()}")
        print(f"[MyServerSocket] Client connected.")

    def receive(self, buffer_size=1024):
        buf = ctypes.create_string_buffer(buffer_size)
        result = ws2.recv(self._conn, buf, buffer_size, 0)
        if result == SOCKET_ERROR:
            raise OSError(f"recv() failed: {ctypes.get_last_error()}")
        message = buf.raw[:result].decode('utf-8')
        print(f"[MyServerSocket] Received: {message}")
        return message

    def send(self, message):
        data = message.encode('utf-8')
        result = ws2.send(self._conn, data, len(data), 0)
        if result == SOCKET_ERROR:
            raise OSError(f"send() failed: {ctypes.get_last_error()}")
        print(f"[MyServerSocket] Sent: {message}")

    def close(self):
        if self._conn:
            ws2.closesocket(self._conn)
        ws2.closesocket(self._sock)
        ws2.WSACleanup()
        print("[MyServerSocket] Server closed.")
