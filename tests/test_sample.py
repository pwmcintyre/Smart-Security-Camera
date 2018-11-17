# content of ./test_smtpsimple.py
import pytest

@pytest.fixture
def number():
    return 3

def test_ehlo(number):
    assert number == 3
    assert number * number == 9
