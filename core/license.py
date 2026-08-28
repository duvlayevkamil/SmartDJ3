"""
Litsenziya tizimi — SmartDJ3
Qattiq disk serial raqami asosida litsenziyalash.
"""
import hashlib
import json
import os
import subprocess
import platform
import re
from datetime import datetime, timedelta


LICENSE_FILE = "license.dat"
TRIAL_DAYS = 7


def _get_disk_serial_wmic():
    """Windows: wic orqali Qattiq disk serial raqamini olish"""
    try:
        result = subprocess.run(
            ["wmic", "diskdrive", "get", "serialnumber"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            serial = line.strip()
            if serial and serial != "SerialNumber" and len(serial) > 3:
                return serial
    except Exception:
        pass
    return None


def _get_disk_serial_powershell():
    """Windows: PowerShell orqali disk serialini olish"""
    try:
        cmd = "Get-WmiObject Win32_DiskDrive | Select-Object -ExpandProperty SerialNumber"
        result = subprocess.run(
            ["powershell", "-Command", cmd],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        serial = result.stdout.strip().split("\n")[0].strip()
        if serial and len(serial) > 3:
            return serial
    except Exception:
        pass
    return None


def _get_disk_serial_cmd():
    """Windows: cmd /c orqali disk serialini olish"""
    try:
        result = subprocess.run(
            ["cmd", "/c", "wmic diskdrive get serialnumber"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            serial = line.strip()
            if serial and serial != "SerialNumber" and len(serial) > 3:
                return serial
    except Exception:
        pass
    return None


def _get_motherboard_serial():
    """Windows: Motherboard serial raqami"""
    try:
        result = subprocess.run(
            ["wmic", "baseboard", "get", "serialnumber"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            serial = line.strip()
            if serial and serial != "SerialNumber" and len(serial) > 3:
                return serial
    except Exception:
        pass
    return None


def _get_cpu_id():
    """Windows: Processor ID"""
    try:
        result = subprocess.run(
            ["wmic", "cpu", "get", "ProcessorId"],
            capture_output=True, text=True, timeout=10,
            creationflags=subprocess.CREATE_NO_WINDOW if platform.system() == "Windows" else 0
        )
        lines = result.stdout.strip().split("\n")
        for line in lines:
            serial = line.strip()
            if serial and serial != "ProcessorId" and len(serial) > 3:
                return serial
    except Exception:
        pass
    return None


def get_machine_id():
    """
    Kompyuterni aniqlash uchun maxsus ID yaratish.
    Bir nechta usuldan foydalanadi — qaysi biri ishlasa.
    """
    parts = []

    # 1. Disk serial
    disk = _get_disk_serial_wmic() or _get_disk_serial_powershell() or _get_disk_serial_cmd()
    if disk:
        parts.append(f"DISK:{disk}")

    # 2. Motherboard serial
    mb = _get_motherboard_serial()
    if mb:
        parts.append(f"MB:{mb}")

    # 3. CPU ID
    cpu = _get_cpu_id()
    if cpu:
        parts.append(f"CPU:{cpu}")

    # Agar hech narsa topilmasa — fallback
    if not parts:
        parts.append(f"HOST:{platform.node()}")
        parts.append(f"OS:{platform.system()}-{platform.machine()}")

    raw = "|".join(parts)
    # 8 ta belgilik qisqa hash
    return hashlib.sha256(raw.encode()).hexdigest()[:16].upper()


def generate_user_code(machine_id):
    """
    Foydalanuvchi kodini yaratish.
    Muallifga yuborish uchun.
    Format: XXXX-XXXX-XXXX-XXXX
    """
    h = hashlib.sha256(f"SmartDJ3:{machine_id}:user".encode()).hexdigest()[:16].upper()
    return f"{h[0:4]}-{h[4:8]}-{h[8:12]}-{h[12:16]}"


def generate_activation_code(user_code):
    """
    Muallif tomonidan yaratiladigan Tasdiqlash kodi.
    Foydalanuvchi kodi asosida maxsus algoritm.
    """
    # Bo'sh joylarni olib tashlash
    clean = user_code.replace("-", "").replace(" ", "").upper()
    if len(clean) != 16:
        return None

    # Maxsus algoritm: qatlamlangan hash
    step1 = hashlib.sha256(f"AUTH:{clean}:STEP1".encode()).hexdigest()[:8].upper()
    step2 = hashlib.sha256(f"AUTH:{clean}:STEP2:{step1}".encode()).hexdigest()[:8].upper()
    step3 = hashlib.sha256(f"ACTIVATE:{step1}:{step2}:{clean}".encode()).hexdigest()[:16].upper()

    # Natija: ACTV-XXXX-XXXX-XXXX
    return f"ACTV-{step3[0:4]}-{step3[4:8]}-{step3[8:12]}-{step3[12:16]}"


def verify_activation_code(user_code, activation_code):
    """
    Tasdiqlash kodini tekshirish.
    To'g'ri bo'lsa True, noto'g'ri bo'lsa False.
    """
    expected = generate_activation_code(user_code)
    if not expected:
        return False
    return activation_code.strip().upper() == expected


# ================================================================
# LITSENZIYA SAQLASH / YUKLASH
# ================================================================

def _license_path():
    """Litsenziya fayli yo'li"""
    # Dastur ishlayotgan papkada
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), LICENSE_FILE)


def save_license(install_date, activation_code=None):
    """Litsenziya ma'lumotlarini saqlash"""
    data = {
        "install_date": install_date.isoformat(),
        "activation_code": activation_code,
        "machine_id": get_machine_id(),
    }
    path = _license_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_license():
    """Litsenziya ma'lumotlarini yuklash"""
    path = _license_path()
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def check_license():
    """
    Litsenziya holatini tekshirish.

    Qaytaradi:
        (status, message)
        status: "trial" | "licensed" | "expired"
        message:foydalanuvchiga xabar
    """
    data = load_license()
    now = datetime.now()

    # Birinchi marta ishga tushirish — sana saqlash
    if data is None:
        save_license(now)
        remaining = TRIAL_DAYS
        return "trial", f"sinov muddati: {remaining} kun qoldi"

    install_date = datetime.fromisoformat(data["install_date"])
    days_passed = (now - install_date).days

    # Agar faollashtirilgan bo'lsa
    if data.get("activation_code"):
        # Machine ID tekshirish
        current_id = get_machine_id()
        if current_id != data.get("machine_id"):
            return "expired", "Litsenziya boshqa kompyuterga bog'langan!"

        # Activation code ni ham tekshirish — xavfsizlik uchun
        user_code = generate_user_code(current_id)
        if not verify_activation_code(user_code, data["activation_code"]):
            return "expired", "Litsenziya kodi yaroqsiz!"

        return "licensed", "Litsenziya faol"

    # Sinov muddati
    if days_passed < TRIAL_DAYS:
        remaining = TRIAL_DAYS - days_passed
        return "trial", f"sinov muddati: {remaining} kun qoldi"

    # Muddati tugagan
    return "expired", f"Sinov muddati tugadi ({TRIAL_DAYS} kun)"


def activate(activation_code):
    """
    Dasturni faollashtirish.
    To'g'ri kod bo'lsa saqlaydi.
    """
    data = load_license()
    if data is None:
        return False, "Litsenziya fayli topilmadi"

    machine_id = get_machine_id()
    user_code = generate_user_code(machine_id)

    if verify_activation_code(user_code, activation_code):
        data["activation_code"] = activation_code.strip().upper()
        data["machine_id"] = machine_id
        save_license(datetime.fromisoformat(data["install_date"]), activation_code)
        return True, "Dastur faollashtirildi!"
    else:
        return False, "Tasdiqlash kodi noto'g'ri!"
