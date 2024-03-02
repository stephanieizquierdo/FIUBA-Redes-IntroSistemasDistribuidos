import datetime
import socket
import time
from queue import PriorityQueue

from ..constants import *
from ..handlers.logLevelHandler import *


class Package:
    def __init__(self, package_id, data):
        self.__id = package_id
        self.__data = data
        self.__is_ack = False
        self.__created_at = 0
        self.__retry_count = 0

    def get_id(self):
        return self.__id

    def get_data(self):
        return self.__data

    def has_the_id(self, package_id):
        return self.__id == package_id

    def mark_as_received(self):
        self.__is_ack = True

    def set_timestamp(self):
        self.__created_at = time.time()

    def serialize_id_and_data(self):
        return self.serialize_id() + self.__data

    def serialize_id(self):
        return self.__id.to_bytes(ID_SIZE, byteorder='big')

    def has_been_received(self):
        return self.__is_ack

    def retry_times_over(self, max_times):
        return self.__retry_count > max_times

    def has_expired(self):
        new_time = time.time()
        is_old = ((self.__created_at + TIMEOUT) < new_time)
        has_expired = (not self.__is_ack) and is_old
        return has_expired

    def __lt__(self, other):
        return self.__id < other.__id

    def update_retry(self):
        self.__retry_count += 1


def wait_for_ack(s, log_level):
    try:
        package, server_address = s.recvfrom(ID_SIZE)
        return int.from_bytes(package, byteorder='big')
    except socket.timeout:
        log('socket timeout waiting for ACK', LogLevel.NORMAL, log_level)
        return None


def selective_repeat_send(s, f, send_address, log_level):
    sent_window = []
    all_file_read = False
    newest_package_id = 0
    s.settimeout(TIMEOUT)
    log('Starting send with selective repeat', LogLevel.HIGH, log_level)
    while not all_file_read or len(sent_window) > 0:
        # fill the window
        log(f'len(sent_window) {len(sent_window)}', LogLevel.HIGH, log_level)

        while len(sent_window) < MAX_WINDOW_SIZE and not all_file_read:
            data = f.read(CHUNK_SIZE - ID_SIZE)
            if not data:
                all_file_read = True
                break
            newest_package_id += 1
            package = Package(newest_package_id, data)
            s.sendto(package.serialize_id_and_data(), send_address)
            log(f'sent package: {newest_package_id}', LogLevel.HIGH, log_level)
            package.set_timestamp()
            sent_window.append(package)
        log('waiting for some ack', LogLevel.NORMAL, log_level)
        ack = wait_for_ack(s, log_level)
        log(f'received ack: {ack}', LogLevel.HIGH, log_level)

        # mark the acknowledged packages as received
        if ack:
            for package in sent_window:
                log(f'package: {package.get_id()} ack: {package.has_been_received()}', LogLevel.HIGH, log_level)
                if package.has_the_id(ack):
                    package.mark_as_received()
                    log(f'Found package with ack: {ack}', LogLevel.HIGH, log_level)
                    break

        # remove packages until first unacknowledged (slide window)
        while len(sent_window) > 0 and sent_window[0].has_been_received():
            log(f'Poped acked package: {sent_window[0].get_id()}', LogLevel.HIGH, log_level)

            sent_window.pop(0)

        # resend all expired
        for package in sent_window:
            if package.retry_times_over(MAXIMUM_RETRIES):
                log('Quit because no response for MAXIMUM_RETRIES times', LogLevel.HIGH, log_level)
                log(f'TIMEOUT at package: {package}', LogLevel.NORMAL, log_level)
                exit(1)
            if package.has_expired():
                s.sendto(package.serialize_id_and_data(), send_address)
                package.set_timestamp()
                package.update_retry()
                log(f'Resent: {package.get_id()}', LogLevel.HIGH, log_level)


def selective_repeat_receive(s, file, client_address, file_size, log_level):
    amount_received = 0
    expected_package_id = 1
    s.settimeout(TIMEOUT)
    receive_window = PriorityQueue(MAX_WINDOW_SIZE)
    timeout_count = 0
    log('Starting receive with selective repeat', LogLevel.HIGH, log_level)
    while amount_received < file_size:
        while not receive_window.full() and amount_received < file_size:
            try:
                package, address = s.recvfrom(CHUNK_SIZE)
                timeout_count = 0
            except socket.timeout:
                timeout_count += 1
                if timeout_count > MAX_RECV_TIMEOUTS:
                    log('TIMEOUT at socket receive', LogLevel.NORMAL, log_level)
                    exit(1)
                break
            package_id = int.from_bytes(package[:ID_SIZE], byteorder='big')

            log(f'received: {str(package_id)}', LogLevel.HIGH, log_level)
            data = package[ID_SIZE:]
            s.sendto(package[:ID_SIZE], client_address)
            if package_id != expected_package_id:
                if package_id < expected_package_id:
                    log(f'discarded package: {str(package_id)}', LogLevel.HIGH, log_level)
                    continue
                #  check if its already in buffer
                for item in receive_window.queue:
                    if item[0] == package_id:
                        continue
                #  add to buffer
                ooo_package = Package(package_id, data)
                receive_window.put((package_id, ooo_package))
                log(f'added package: {str(package_id)} to queue', LogLevel.HIGH, log_level)
            else:
                file.write(data)
                amount_received += len(data)
                expected_package_id += 1
                log(f'amount_received: {amount_received} fileSize {file_size}', LogLevel.NORMAL, log_level)

        while not receive_window.empty() and receive_window.queue[0][1].has_the_id(expected_package_id):
            package = receive_window.get()[1]
            file.write(package.get_data())
            amount_received += len(package.get_data())
            log(f'amount_received: {amount_received} fileSize {file_size}', LogLevel.NORMAL, log_level)
            expected_package_id += 1
