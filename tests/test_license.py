"""
License unit testlari
"""
import sys
import os
import tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.license import (
    get_machine_id, generate_user_code, generate_activation_code,
    verify_activation_code, TRIAL_DAYS
)


class TestLicense:
    """License funksiyalarining testlari"""

    # ================================================================
    # MACHINE ID
    # ================================================================

    def test_get_machine_id_returns_string(self):
        """Machine ID string qaytaradi"""
        machine_id = get_machine_id()
        assert isinstance(machine_id, str)

    def test_get_machine_id_length(self):
        """Machine ID uzunligi 16"""
        machine_id = get_machine_id()
        assert len(machine_id) == 16

    def test_get_machine_id_hex(self):
        """Machine ID hexadecimal"""
        machine_id = get_machine_id()
        assert all(c in '0123456789ABCDEF' for c in machine_id)

    def test_get_machine_id_consistent(self):
        """Machine ID har safar bir xil"""
        id1 = get_machine_id()
        id2 = get_machine_id()
        assert id1 == id2

    # ================================================================
    # USER CODE
    # ================================================================

    def test_generate_user_code_format(self):
        """Foydalanuvchi kodi formati: XXXX-XXXX-XXXX-XXXX"""
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)
        assert len(user_code) == 19  # 16 + 3 defis
        assert user_code.count('-') == 3

    def test_generate_user_code_consistent(self):
        """Bir xil machine_id uchun bir xil kod"""
        machine_id = get_machine_id()
        code1 = generate_user_code(machine_id)
        code2 = generate_user_code(machine_id)
        assert code1 == code2

    def test_generate_user_code_different_machines(self):
        """Turli machine_id uchun turli kodlar"""
        code1 = generate_user_code("AAAA1111BBBB2222")
        code2 = generate_user_code("CCCC3333DDDD4444")
        assert code1 != code2

    # ================================================================
    # ACTIVATION CODE
    # ================================================================

    def test_generate_activation_code_format(self):
        """Tasdiqlash kodi formati: ACTV-XXXX-XXXX-XXXX-XXXX"""
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)
        activation_code = generate_activation_code(user_code)
        assert activation_code.startswith("ACTV-")
        assert len(activation_code) == 24  # ACTV-XXXX-XXXX-XXXX-XXXX

    def test_generate_activation_code_consistent(self):
        """Bir xil user_code uchun bir xil activation code"""
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)
        code1 = generate_activation_code(user_code)
        code2 = generate_activation_code(user_code)
        assert code1 == code2

    def test_verify_activation_code_correct(self):
        """To'g'ri tasdiqlash kodi"""
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)
        activation_code = generate_activation_code(user_code)
        assert verify_activation_code(user_code, activation_code) is True

    def test_verify_activation_code_wrong(self):
        """Noto'g'ri tasdiqlash kodi"""
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)
        assert verify_activation_code(user_code, "ACTV-0000-0000-0000") is False

    def test_verify_activation_code_empty(self):
        """Bo'sh tasdiqlash kodi"""
        machine_id = get_machine_id()
        user_code = generate_user_code(machine_id)
        assert verify_activation_code(user_code, "") is False

    # ================================================================
    # TRIAL DAYS
    # ================================================================

    def test_trial_days(self):
        """Sinov muddati 7 kun"""
        assert TRIAL_DAYS == 7


# ================================================================
# Pytest uchun
# ================================================================
if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])
