import pytest

class TestCalculator:
    def test_add(self):
        assert 2 + 2 == 4

    def test_subtract(self):
        assert 2 - 2 == 0

    def test_multiply(self):
        assert 2 * 2 == 4

    def test_divide(self):
        assert 2 / 2 == 1

    def test_divide_by_zero(self):
        with pytest.raises(ZeroDivisionError):
            result = 2 / 0
