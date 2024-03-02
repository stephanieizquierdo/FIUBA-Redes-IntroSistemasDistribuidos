import socket
import threading
import os

from .logLevelHandler import *
from ..constants import *
from ..protocols.selectiveRepeat import selective_repeat_receive, selective_repeat_send
from ..protocols.stopAndWait import stop_and_wait_receive, stop_and_wait_send


def run_server(args):
    server_port, server_name = args.port, args.host
    log_level = retrieve_level(args.verbose, args.quiet)
    if not os.path.exists(args.storage):
        log(f'Storage path {args.storage} doesn\'t exist', LogLevel.LOW, log_level)
        return
    if args.port < 1024:
        log(f'Can\'t use reserved port {args.port}', LogLevel.LOW, log_level)
        return
    if args.port > 65535:
        log(f'Can\'t use non existent port {args.port}', LogLevel.LOW, log_level)
        return

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind(('', server_port))
        log(f'Starting server at {server_name}:{server_port}', LogLevel.LOW, log_level)
        threads = []
        try:
            while True:
                log('waiting for new connection', LogLevel.HIGH, log_level)
                package, client_address = s.recvfrom(CHUNK_SIZE)

                if len(threads) > MAX_CONNECTIONS:
                    reject_connection(s, client_address)
                log(f'new connection at {client_address}', LogLevel.HIGH, log_level)
                new_thread = threading.Thread(
                    target=handle_connection,
                    args=(package, client_address, args.selectiveRepeat, args.storage, log_level)
                )
                new_thread.start()
                threads.append(new_thread)

                #  remove dead threads
                threads = [thread for thread in threads if thread.is_alive()]

        except KeyboardInterrupt:
            try:
                log("closing...", LogLevel.NORMAL, log_level)
                for thread in threads:
                    thread.join()
                log("server closed successfully", LogLevel.NORMAL, log_level)
            except KeyboardInterrupt:
                exit(1)


def handle_connection(package, client_address, algorithm, storage_path, log_level):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        client_method = int.from_bytes(package[ID_SIZE:ID_SIZE + CLIENT_METHOD_SIZE], byteorder='big')
        if client_method == UPLOAD:
            file_size = int.from_bytes(package[ID_SIZE + CLIENT_METHOD_SIZE:ID_SIZE + CLIENT_METHOD_SIZE + FILE_SIZE],
                                       byteorder='big')
            file_name = package[ID_SIZE + CLIENT_METHOD_SIZE + FILE_SIZE:].decode('utf-8')
            file_name = file_name.rstrip('\0')

            with open(storage_path + '/' + file_name, WRITE_MODE) as f:
                try:
                    s.sendto(int(0).to_bytes(ID_SIZE, byteorder='big') +
                             STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big'), client_address)
                    if algorithm == STOP_AND_WAIT:
                        stop_and_wait_receive(s, f, client_address, file_size, log_level)
                    else:
                        selective_repeat_receive(s, f, client_address, file_size, log_level)
                except:
                    if os.path.exists(storage_path + '/' + file_name):
                        os.remove(storage_path + '/' + file_name)
                finally:
                    f.close()

        elif client_method == DOWNLOAD:
            file_name = package[ID_SIZE + CLIENT_METHOD_SIZE:].decode('utf-8')
            file_name = file_name.rstrip('\0')
            try:
                with open(storage_path + '/' + file_name, READ_MODE) as f:
                    try:
                        file_size = os.path.getsize(storage_path + '/' + file_name)
                        s.sendto(int(0).to_bytes(ID_SIZE, byteorder='big') +
                                 STATUS_OK.to_bytes(STATUS_CODE_SIZE, byteorder='big') +
                                 file_size.to_bytes(FILE_SIZE, byteorder='big'),
                                 client_address)
                        if algorithm == STOP_AND_WAIT:
                            stop_and_wait_send(s, f, client_address, log_level)
                        else:
                            selective_repeat_send(s, f, client_address, log_level)
                    finally:
                        f.close()
            except OSError as err:
                log(f'error while downloading file: {err}', LogLevel.LOW, log_level)
                s.sendto(int(0).to_bytes(ID_SIZE, byteorder='big') +
                         ERR_FILE_NOT_FOUND.to_bytes(STATUS_CODE_SIZE, byteorder='big'), client_address)
    log('finished', LogLevel.LOW, log_level)


def reject_connection(s, address):
    too_many_connections_res = (int(0).to_bytes(ID_SIZE, byteorder='big')
                                + ERR_TOO_MANY_CONNECTIONS.to_bytes(STATUS_CODE_SIZE, byteorder='big'), address)
    s.sendto(too_many_connections_res, address)
