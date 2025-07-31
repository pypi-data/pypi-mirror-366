"""Tests for identification of wheels."""
from wheel_matrix import get_triples


def test_manylinux():
    """We can identify a manylinux CPython wheel."""
    assert get_triples(
        'wasabi_geom-2.1.1-cp311-cp311-manylinux_2_5_i686.manylinux1_i686.manylinux_2_17_i686.manylinux2014_i686.whl',
        cpythons=['cp38', 'cp39'],
    ) == {
        ('cp311', 'linux', 'i686'),
    }


def test_universal2():
    """We can identify a universal2 mac wheel."""
    assert get_triples(
        'argon2_cffi_bindings-21.2.0-cp38-abi3-macosx_10_9_universal2.whl',
        cpythons=['cp37', 'cp38', 'cp39'],
    ) == {
        ('cp38', 'mac', 'x86_64'),
        ('cp39', 'mac', 'x86_64'),
        ('cp38', 'mac', 'arm64'),
        ('cp39', 'mac', 'arm64'),
    }


def test_windows_arm64():
    """We can identify a Windows ARM64 wheel."""
    assert get_triples(
        'foo-1.0-cp311-cp311-win_arm64.whl',
        cpythons=['cp311'],
    ) == {('cp311', 'windows', 'arm64')}
