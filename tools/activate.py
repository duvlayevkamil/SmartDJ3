"""
SmartDJ3 — Muallif aktivatsiya vositasi
Foydalanuvchi kodi asosida Tasdiqlash kodini yaratish.

Ishlatish:
    python tools/activate.py          — Konsol versiyasi
    python tools/activate_gui.py      — Chiroyli GUI oyna
"""
import sys
import os

# core papkasini path ga qo'shish
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.license import generate_activation_code


def main():
    print("=" * 50)
    print("  SmartDJ3 — Muallif Aktivatsiya Vositasi")
    print("=" * 50)
    print()

    user_code = input("Foydalanuvchi kodini kiriting (XXXX-XXXX-XXXX-XXXX): ").strip()

    if not user_code:
        print("Xatolik: Kod bo'sh!")
        return

    activation = generate_activation_code(user_code)
    if not activation:
        print("Xatolik: Noto'g'ri format! (XXXX-XXXX-XXXX-XXXX)")
        return

    print()
    print("=" * 50)
    print(f"  TASDIQLASH KODI: {activation}")
    print("=" * 50)
    print()
    print("Bu kodni foydalanuvchiga bering.")


if __name__ == "__main__":
    main()
