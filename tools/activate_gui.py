"""
MUALLIF UCHUN LITSENZIYA GENERATOR
Foydalanuvchi kodini kiritish → Tasdiqlash kodini olish

Ishlatish:
  python tools/activate_gui.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.license import generate_activation_code, verify_activation_code


def generate_code(user_code):
    """Foydalanuvchi kodi uchun tasdiqlash kodi yaratish"""
    activation_code = generate_activation_code(user_code)
    return activation_code


def verify_code(user_code, activation_code):
    """Tasdiqlash kodini tekshirish"""
    return verify_activation_code(user_code, activation_code)


def main():
    print("=" * 60)
    print("SMARTDJ3 — LITSENZIYA GENERATOR")
    print("=" * 60)
    print()
    print("Foydalanuvchi kodini kiriting (masalan: ABCD-1234-EFGH-5678):")
    print()

    user_code = input("Foydalanuvchi kodi: ").strip()

    if not user_code:
        print("Xatolik: Kod bo'sh!")
        return

    # Tasdiqlash kodini generatsiya qilish
    activation_code = generate_code(user_code)

    print()
    print("=" * 60)
    print("TASDIQLASH KODI:")
    print("=" * 60)
    print()
    print(f"  {activation_code}")
    print()
    print("=" * 60)
    print()
    print("Foydalanuvchiga yuboring:")
    print(f"  Telegram: @DUVLAYEV_KAMI")
    print(f"  Telefon: +998 77-500-04-69")
    print()

    # Tekshirish
    is_valid = verify_code(user_code, activation_code)
    if is_valid:
        print("✅ Kod to'g'ri — faollashtirish mumkin!")
    else:
        print("❌ Kod noto'g'ri — qaytadan urinib ko'ring!")


if __name__ == "__main__":
    main()
