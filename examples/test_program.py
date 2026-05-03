#!/usr/bin/env python3
import os
import socket
import time


def main() -> None:
    print("Mythos test program started.", flush=True)
    print(f"PID: {os.getpid()}", flush=True)
    print(f"Host: {socket.gethostname()}", flush=True)

    count = 0
    while True:
        count += 1
        print(f"[mythos-test] heartbeat {count} at {time.ctime()}", flush=True)
        time.sleep(5)


if __name__ == "__main__":
    main()
