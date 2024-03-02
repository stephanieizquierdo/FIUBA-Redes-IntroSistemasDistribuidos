# Connections
MAX_CONNECTIONS = 10

# Sizes as bytes
ID_SIZE = 3
HEADER_SIZE = ID_SIZE
CHUNK_SIZE = 256 + HEADER_SIZE
CLIENT_METHOD_SIZE = 1
FILE_SIZE = 4  # 4 GB
STATUS_CODE_SIZE = 2

# Timeouts
TIMEOUT = 0.1
MAX_TIMEOUTS = 5
MAX_RECV_TIMEOUTS = 50
MAX_WINDOW_SIZE = 5
HANDSHAKE_TIMEOUT = 5

# Client methods
UPLOAD = 0
DOWNLOAD = 1

# Opening file modes
READ_MODE = "rb"
WRITE_MODE = "wb"

# Files paths
CLIENT_FILE_PATH = "lib/files/client-files/"
SERVER_FILE_PATH = "lib/files/server-files/"

# Algorithms
STOP_AND_WAIT = False

MAXIMUM_RETRIES = 5

# Status codes
STATUS_OK = 0
ERR_FILE_TOO_BIG = 1
ERR_FILE_NOT_FOUND = 2
ERR_TOO_MANY_CONNECTIONS = 3

ERR_MESSAGES = {
    STATUS_OK: "OK",
    ERR_FILE_TOO_BIG: "The file you are trying to transfer is too big",
    ERR_FILE_NOT_FOUND: "File doesn't exist",
    ERR_TOO_MANY_CONNECTIONS: "The server has too many connections. Try again later."
}
