from ..constants import *
import socket

from ..handlers.logLevelHandler import *


def stop_and_wait_receive(s, f, address, file_size, log_level):
    received = 0
    ack = 0
    s.settimeout(HANDSHAKE_TIMEOUT)

    log('receiving file...', LogLevel.LOW, log_level)
    log('Starting receive with stop and wait', LogLevel.HIGH, log_level)
    while received < file_size:
        log(f'received: {received} from total: {file_size}', LogLevel.HIGH, log_level)
        try:
            package, address = s.recvfrom(CHUNK_SIZE)
        except:
            log('TIMEOUT receive with stop and wait', LogLevel.NORMAL, log_level)
            exit(1)
        package_id = int.from_bytes(package[:ID_SIZE], byteorder='big')
        data = package[HEADER_SIZE:]
        if (ack + 1) == package_id:  # Recibi paquete siguiente
            received += len(data)
            f.write(data)
            ack = package_id
        res = package_id.to_bytes(ID_SIZE, byteorder='big')
        s.sendto(res, address)


def stop_and_wait_send(s, f, address, log_level):
    s.settimeout(TIMEOUT)
    timeouts = 0
    package_id = 0
    ack = 0
    data = ''
    log('sending file...', LogLevel.LOW, log_level)
    log('Starting send with stop and wait', LogLevel.HIGH, log_level)
    while True:
        log(f'ack: {ack} package_id:  {package_id}', LogLevel.HIGH, log_level)
        try:
            if ack == package_id:
                package_id = package_id + 1
                data = f.read(CHUNK_SIZE - HEADER_SIZE)
                if not data:
                    break
            else:
                log(f'packet {package_id} will be repeated', LogLevel.NORMAL, log_level)
            header_b = package_id.to_bytes(ID_SIZE, byteorder='big')
            chunk = header_b + data
            s.sendto(chunk, address)

            # Esperar la confirmación del servidor para este paquete
            package, _ = s.recvfrom(HEADER_SIZE)
            ack = int.from_bytes(package[: ID_SIZE], byteorder='big')
            log(f'Confirmation received for pacakge {ack}', LogLevel.NORMAL, log_level)
            timeouts = 0
        except socket.timeout:
            log('TIMEOUT at send with stop and wait', LogLevel.HIGH, log_level)
            timeouts += 1
            if timeouts == MAX_TIMEOUTS:
                log("Too many timeouts, connection abort", LogLevel.HIGH, log_level)
                break
