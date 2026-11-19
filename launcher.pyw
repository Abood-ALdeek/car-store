"""Car store launcher: keeps the website running in the background (no black window).

    pythonw launcher.pyw            make sure the site runs, then open the website
    pythonw launcher.pyw --admin    make sure the site runs, then open the admin panel
    pythonw launcher.pyw --server   only make sure the site runs (used at Windows startup)
    pythonw launcher.pyw --stop     stop the site and its guard

How it stays up: a hidden "guard" process runs the web server and checks it every 10 seconds.
If the server stops or stops answering, the guard restarts it automatically.
"""
import ctypes
import os
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path

BASE = Path(__file__).resolve().parent
HOST, PORT = "127.0.0.1", 8000
URL = f"http://{HOST}:{PORT}/"
PYTHONW = BASE / ".venv" / "Scripts" / "pythonw.exe"
LOG = BASE / "server.log"
GUARD_PID = BASE / "guard.pid"
MUTEX_NAME = "Local\\CarStoreWebsiteGuard"
NO_WINDOW = 0x08000000               # CREATE_NO_WINDOW
DETACHED = 0x00000008 | 0x00000200   # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
BREAKAWAY = 0x01000000               # CREATE_BREAKAWAY_FROM_JOB
kernel32 = ctypes.windll.kernel32


def site_is_up(timeout=2):
    try:
        with urllib.request.urlopen(URL + "admin/login/", timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def message(text, error=False):
    ctypes.windll.user32.MessageBoxW(0, text, "معرض السيارات / Car Store", 0x10 if error else 0x40)


def log_line(text):
    try:
        if LOG.exists() and LOG.stat().st_size > 5_000_000:
            LOG.unlink()
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"[guard {time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
    except OSError:
        pass


def guard_running():
    h = kernel32.OpenMutexW(0x00100000, False, MUTEX_NAME)  # SYNCHRONIZE
    if h:
        kernel32.CloseHandle(h)
        return True
    return False


def kill_tree(pid):
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True, creationflags=NO_WINDOW)


def free_port():
    """Kill anything listening on our port (a stuck old server)."""
    try:
        out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True,
                             creationflags=NO_WINDOW).stdout
    except Exception:
        return
    for line in out.splitlines():
        if f"{HOST}:{PORT} " in line and "LISTENING" in line:
            kill_tree(line.split()[-1])


# ---------------------------------------------------------------- guard process
def run_guard():
    mutex = kernel32.CreateMutexW(None, False, MUTEX_NAME)
    if kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS: another guard is running
        return
    GUARD_PID.write_text(str(os.getpid()))
    log_line("guard started")
    subprocess.run([str(PYTHONW), "manage.py", "migrate", "--noinput"], cwd=BASE,
                   capture_output=True, creationflags=NO_WINDOW)
    cmd = [str(PYTHONW), "manage.py", "runserver", f"{HOST}:{PORT}", "--noreload"]
    while True:
        if not site_is_up(timeout=3):
            free_port()
        log_file = open(LOG, "a", encoding="utf-8")
        proc = subprocess.Popen(cmd, cwd=BASE, stdout=log_file, stderr=log_file,
                                stdin=subprocess.DEVNULL, creationflags=NO_WINDOW)
        log_line(f"server started (pid {proc.pid})")
        time.sleep(4)
        fails, tick = 0, 0
        while proc.poll() is None:
            time.sleep(1)              # notice a crashed server within a second
            tick += 1
            if tick % 10:
                continue
            if site_is_up(timeout=8):  # every 10 s: is it still answering?
                fails = 0
            else:
                fails += 1
                if fails >= 3:  # not answering for ~30 seconds: restart it
                    log_line("server not answering - restarting")
                    kill_tree(proc.pid)
                    break
        log_file.close()
        log_line(f"server stopped (code {proc.poll()}) - restarting")
        time.sleep(1)
    # never reached; the mutex is released when the process ends
    del mutex


# ---------------------------------------------------------------- commands
def start_guard():
    cmd = [str(PYTHONW), str(BASE / "launcher.pyw"), "--guard"]
    try:
        # Break away from the parent's job so nothing that started us can take the site down.
        subprocess.Popen(cmd, cwd=BASE, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, creationflags=DETACHED | NO_WINDOW | BREAKAWAY, close_fds=True)
    except OSError:
        subprocess.Popen(cmd, cwd=BASE, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, creationflags=DETACHED | NO_WINDOW, close_fds=True)


def ensure_running():
    if site_is_up():
        if not guard_running():
            # An old unguarded server is running: replace it with a guarded one.
            free_port()
            start_guard()
        else:
            return True
    elif not guard_running():
        free_port()
        start_guard()
    for _ in range(80):  # wait up to ~40 seconds
        if site_is_up(timeout=1):
            return True
        time.sleep(0.5)
    message("تعذر تشغيل الموقع. افتح الملف server.log لمعرفة السبب.\n"
            "The site could not start. See server.log for details.\n\n" + str(LOG), error=True)
    return False


def stop_all():
    if GUARD_PID.exists():
        try:
            kill_tree(int(GUARD_PID.read_text().strip()))
        except ValueError:
            pass
        GUARD_PID.unlink(missing_ok=True)
    free_port()


def main():
    if not PYTHONW.exists():
        message("لم يتم العثور على بيئة بايثون (.venv).\nPython environment (.venv) not found.", error=True)
        return
    os.chdir(BASE)
    args = sys.argv[1:]
    if "--guard" in args:
        run_guard()
        return
    if "--stop" in args:
        stop_all()
        return
    if not ensure_running():
        return
    if "--server" in args:
        return
    webbrowser.open(URL + "admin/" if "--admin" in args else URL)


if __name__ == "__main__":
    main()
