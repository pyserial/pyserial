"""
serial_diagnostics.py

Diagnoses common serial port connection problems.

Usage:
    python serial_diagnostics.py                       # list available ports
    python serial_diagnostics.py /dev/ttyUSB0         # check port at 9600 baud
    python serial_diagnostics.py COM3 --baud 115200   # custom baud rate
    python serial_diagnostics.py COM3 --loopback      # include loopback test
    python serial_diagnostics.py COM3 --verbose       # full exception details
"""

import argparse
import sys
import time
import platform
import serial
import serial.tools.list_ports

READ_BYTES   = 64
COMMON_BAUDS = [1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200, 230400]
SEP          = "-" * 60

EXIT_OK             = 0
EXIT_PORT_NOT_FOUND = 1
EXIT_PERMISSION     = 2
EXIT_NO_DATA        = 3
EXIT_LOOPBACK_FAIL  = 4


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def header(title: str) -> None:
    print(f"\n{SEP}\n  {title}\n{SEP}")


def exc_info(exc: Exception, verbose: bool) -> dict:
    result = {"ok": False, "error": str(exc)}
    if verbose:
        result["exception"] = repr(exc)
    return result


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------

def check_for_data(port, baud, timeout, verbose=False):
    try:
        with serial.Serial(port, baud, timeout=timeout) as ser:
            data = ser.read(READ_BYTES)
            return {"ok": bool(data), "data": data}
    except serial.SerialException as exc:
        return exc_info(exc, verbose)


def can_open_port(port, baud, verbose=False):
    try:
        with serial.Serial(port, baud, timeout=1):
            return {"ok": True}
    except serial.SerialException as exc:
        return exc_info(exc, verbose)


def baud_sweep(port, verbose=False):
    results = []
    for b in COMMON_BAUDS:
        try:
            with serial.Serial(port, b, timeout=1) as ser:
                data = ser.read(32)
                results.append({"ok": True, "baud": b, "bytes": len(data)})
        except serial.SerialException as exc:
            results.append({"ok": False, "baud": b, **exc_info(exc, verbose)})
    return results


def loopback_test(port, baud, verbose=False):
    payload = b"PYSERIAL_LOOPBACK"
    try:
        with serial.Serial(port, baud, timeout=1) as ser:
            ser.write(payload)
            time.sleep(0.1)
            echo = ser.read(len(payload))
            return {"ok": True, "sent": payload, "received": echo}
    except serial.SerialException as exc:
        return exc_info(exc, verbose)


def get_line_signals(port, verbose=False):
    try:
        with serial.Serial(port, timeout=1) as ser:
            return {
                "ok": True,
                "CTS": ser.cts,
                "DSR": ser.dsr,
                "CD": ser.cd,
                "RI": ser.ri,
            }
    except serial.SerialException as exc:
        return exc_info(exc, verbose)


# ---------------------------------------------------------------------------
# Printing
# ---------------------------------------------------------------------------

def print_environment():
    header("ENVIRONMENT")
    print(f"  pyserial : {getattr(serial, '__version__', 'unknown')}")
    print(f"  python   : {sys.version.split()[0]}")
    print(f"  platform : {platform.platform()}")


def print_ports():
    header("DIAG 1 – Available serial ports")
    ports = list(serial.tools.list_ports.comports())
    if ports:
        for p in ports:
            print(f"  {p.device:20s}  {p.description}")
    else:
        print("  WARNING  No serial ports found by the OS.")
    return [p.device for p in ports]


def print_check_for_data(port, baud, timeout, verbose):
    header(f"STEP 1 – Checking for incoming data on {port} @ {baud}")
    result = check_for_data(port, baud, timeout, verbose)

    if result["ok"]:
        print(f"  OK  Received {len(result['data'])} bytes")
        return True

    if "error" in result:
        print(f"  FAIL  Could not open port: {result['error']}")
        if verbose and "exception" in result:
            print(f"        {result['exception']}")
    else:
        print("  FAIL  No data received (device may be idle or misconfigured)")
    return False


def print_open_test(port, baud, verbose):
    header(f"DIAG 3 – Can we open '{port}'?")
    result = can_open_port(port, baud, verbose)

    if result["ok"]:
        print(f"  OK  Port opened successfully at {baud} baud.")
        return True, None

    print(f"  FAIL  {result['error']}")
    msg = result["error"].lower()

    if "permission" in msg or "access" in msg:
        print("        Permission denied or port already in use.")
        print("        Linux/macOS: add user to 'dialout' group.")
        print("        Windows: close Arduino IDE, VSCode, PuTTY, Tera Term.")
        return False, EXIT_PERMISSION

    return False, EXIT_PORT_NOT_FOUND


def print_baud_sweep(port, verbose):
    header("DIAG 4 – Baud-rate sweep")
    results = baud_sweep(port, verbose)

    found = False
    for r in results:
        if r["ok"]:
            status = f"{r['bytes']} bytes" if r["bytes"] else "(no data)"
            print(f"  {r['baud']:>7} baud  {status}")
            if r["bytes"]:
                found = True
        else:
            print(f"  {r['baud']:>7} baud  ERROR  {r['error']}")

    if not found:
        print("\n  FAIL  No data at any baud.")
    return found


def print_loopback(port, baud, verbose):
    header("DIAG 5 – Loopback test")
    result = loopback_test(port, baud, verbose)

    if not result["ok"]:
        print(f"  WARNING  {result['error']}")
        return None

    if result["received"] == result["sent"]:
        print("  OK  Loopback successful")
        return True

    print("  FAIL  Loopback mismatch")
    return False


def print_line_signals(port, verbose):
    header("DIAG 6 – Control-line states")
    result = get_line_signals(port, verbose)

    if not result["ok"]:
        print(f"  WARNING  {result['error']}")
        return

    for k in ("CTS", "DSR", "CD", "RI"):
        print(f"  {k} : {'HIGH' if result[k] else 'LOW'}")


def print_summary():
    header("SUMMARY & NEXT STEPS")
    print("  1. Wrong port?          Use a port from DIAG 1.")
    print("  2. Permission issue?    Close other apps or fix permissions.")
    print("  3. Wrong baud?          Try the baud that returned data in DIAG 4.")
    print("  4. No data at any baud? Check device power and TX->RX wiring.")
    print("  5. Loopback failed?     Adapter may be faulty.")
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Diagnose serial port connection problems.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "examples:\n"
            "  python serial_diagnostics.py                      # list available ports\n"
            "  python serial_diagnostics.py /dev/ttyUSB0        # check port at 9600 baud\n"
            "  python serial_diagnostics.py COM3 --baud 115200  # custom baud rate\n"
            "  python serial_diagnostics.py COM3 --loopback     # include loopback test\n"
            "  python serial_diagnostics.py COM3 --verbose      # full exception details\n"
        ),
    )
    parser.add_argument(
        "port",
        nargs="?",
        help="Serial port to diagnose (e.g. COM3 or /dev/ttyUSB0). "
             "If omitted, available ports are listed and the script exits.",
    )
    parser.add_argument(
        "--baud", "-b",
        type=int,
        default=9600,
        help="Baud rate for the initial data check (default: 9600).",
    )
    parser.add_argument(
        "--timeout", "-t",
        type=int,
        default=2,
        help="Seconds to wait for data in the initial check (default: 2).",
    )
    parser.add_argument(
        "--loopback",
        action="store_true",
        help="Run a loopback test (requires TX->RX jumper on the connector).",
    )
    parser.add_argument(
        "--no-sweep",
        action="store_true",
        help="Skip the baud-rate sweep.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show full exception details in diagnostic output.",
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    print("\n" + "=" * 60)
    print("  PySerial Diagnostic Tool")
    print("=" * 60)

    print_environment()

    if not args.port:
        print_ports()
        sys.exit(EXIT_OK)

    if print_check_for_data(args.port, args.baud, args.timeout, args.verbose):
        sys.exit(EXIT_OK)

    ports = print_ports()
    if args.port not in ports:
        print(f"\n  FAIL  Port '{args.port}' not found")
        sys.exit(EXIT_PORT_NOT_FOUND)

    opened, err = print_open_test(args.port, args.baud, args.verbose)
    if not opened:
        sys.exit(err or EXIT_PORT_NOT_FOUND)

    found_data = True
    if not args.no_sweep:
        found_data = print_baud_sweep(args.port, args.verbose)

    loop_ok = None
    if args.loopback:
        loop_ok = print_loopback(args.port, args.baud, args.verbose)

    print_line_signals(args.port, args.verbose)
    print_summary()

    if loop_ok is False:
        sys.exit(EXIT_LOOPBACK_FAIL)
    if not found_data:
        sys.exit(EXIT_NO_DATA)

    sys.exit(EXIT_OK)


if __name__ == "__main__":
    main()