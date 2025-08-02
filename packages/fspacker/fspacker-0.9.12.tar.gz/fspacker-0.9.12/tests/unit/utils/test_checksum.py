import hashlib
from pathlib import Path
from unittest.mock import MagicMock

from fspacker.utils.checksum import calc_checksum


class TestChecksum:
    """测试计算校验和功能."""

    def test_valid_file(self, tmp_path: Path) -> None:
        """Calculate checksum for a valid file."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content", encoding="utf-8")
        checksum = calc_checksum(Path(test_file))

        expected_checksum = hashlib.sha256(b"test content").hexdigest()
        assert checksum == expected_checksum

    def test_file_not_found(self) -> None:
        """Calculate checksum for a non-existent file."""
        non_existent_file = Path("non_existent_file.txt")
        checksum = calc_checksum(non_existent_file)
        assert not checksum

    def test_empty_file(self, tmp_path: Path) -> None:
        """Calculate checksum for an empty file."""
        test_file = tmp_path / "empty_file.txt"
        test_file.write_text("", encoding="utf-8")
        checksum = calc_checksum(Path(test_file))

        expected_checksum = hashlib.sha256(b"").hexdigest()
        assert checksum == expected_checksum

    def test_calc_checksum_different_block_size(self, tmpdir: Path) -> None:
        """Calculate checksum with a different block size."""
        test_file = tmpdir / "test_file.txt"
        test_file.write_text("test content", encoding="utf-8")
        checksum = calc_checksum(Path(test_file), block_size=2)

        expected_checksum = hashlib.sha256(b"test content").hexdigest()
        assert checksum == expected_checksum

    def test_calc_checksum_os_error(
        self,
        mocker: MagicMock,
        tmpdir: Path,
    ) -> None:
        """Calculate checksum when an OSError occurs."""
        test_file = tmpdir / "test_file.txt"
        test_file.write_text("test content", encoding="utf-8")
        test_file_path = Path(test_file)

        mocker.patch("pathlib.Path.open", side_effect=OSError("Mocked OSError"))

        checksum = calc_checksum(test_file_path)
        assert not checksum
