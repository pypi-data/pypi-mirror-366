from __future__ import annotations

from unittest.mock import MagicMock

import pytest
import requests

from fspacker.utils.url import check_url_access_time
from fspacker.utils.url import get_fastest_url
from fspacker.utils.url import ParseUrlError
from fspacker.utils.url import safe_read_url_data
from fspacker.utils.url import validate_url_scheme


class TestCheckUrlAccessTime:
    """测试 check_url_access_time 函数."""

    def test_success(self, mocker: MagicMock) -> None:
        """测试 check_url_access_time 函数在请求成功时返回访问时间."""
        mocker_get = mocker.patch("requests.get")
        mocker_get.return_value.status_code = 200

        url = "https://example.com"
        time_used = check_url_access_time(url)
        assert time_used < 0.1  # noqa: PLR2004

    def test_failure(self, mocker: MagicMock) -> None:
        """测试 check_url_access_time 函数在请求失败时返回 -1."""
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.RequestException("请求失败"),
        )

        url = "https://example.com"
        time_used = check_url_access_time(url)
        assert time_used == -1

    def test_timeout(self, mocker: MagicMock) -> None:
        """测试 check_url_access_time 函数在请求超时时返回 -1."""
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.Timeout("请求超时"),
        )

        url = "https://example.com"
        time_used = check_url_access_time(url)

        assert time_used == -1


class TestGetFastestUrl:
    """测试 get_fastest_url 函数."""

    def test_success(self, mocker: MagicMock) -> None:
        """测试 get_fastest_url 函数在所有 URL 都能访问时返回最快的 URL."""
        urls = {
            "url1": "https://example.com/url1",
            "url2": "https://example.com/url2",
            "url3": "https://example.com/url3",
        }
        mocker.patch(
            "fspacker.utils.url.check_url_access_time",
            side_effect=[0.1, 0.2, 0.3],
        )
        fastest_url = get_fastest_url(urls)
        assert fastest_url == "https://example.com/url1"

    def test_one_failure(self, mocker: MagicMock) -> None:
        """测试 get_fastest_url 函数在有一个 URL 访问失败时返回最快的 URL."""
        urls = {
            "url1": "https://example.com/url1",
            "url2": "https://example.com/url2",
            "url3": "https://example.com/url3",
        }
        mocker.patch(
            "fspacker.utils.url.check_url_access_time",
            side_effect=[-1, 0.2, 0.3],
        )
        fastest_url = get_fastest_url(urls)
        assert fastest_url == "https://example.com/url2"

    def test_all_failure(self, mocker: MagicMock) -> None:
        """测试 get_fastest_url 函数在所有 URL 都访问失败时返回空字符串."""
        urls = {
            "url1": "https://example.com/url1",
            "url2": "https://example.com/url2",
            "url3": "https://example.com/url3",
        }
        mocker.patch(
            "fspacker.utils.url.check_url_access_time",
            side_effect=[-1, -1, -1],
        )
        fastest_url = get_fastest_url(urls)
        assert not fastest_url

    def test_empty_urls(self) -> None:
        """测试 get_fastest_url 函数在 URL 列表为空时返回空字符串."""
        urls = {}
        fastest_url = get_fastest_url(urls)
        assert not fastest_url


class TestValidateUrlScheme:
    """测试 validate_url_scheme 函数."""

    @pytest.mark.parametrize(
        ("url", "allowed_schemes"),
        [
            ("http://example.com", {"http"}),
            ("https://example.com", {"https"}),
            ("ftp://example.com", {"ftp"}),
        ],
    )
    def test_validate_url_scheme_valid(
        self,
        url: str,
        allowed_schemes: set[str],
    ) -> None:
        """测试 _validate_url_scheme 函数允许有效的 scheme."""
        validate_url_scheme(url, allowed_schemes)  # 应该不抛出异常

    @pytest.mark.parametrize(
        ("url", "allowed_schemes"),
        [
            ("http://example.com", {"https"}),
            ("https://example.com", {"http"}),
            ("https://example.com", {"ftp"}),
            ("ftp://example.com", {"https"}),
        ],
    )
    def test_invalid(
        self,
        url: str,
        allowed_schemes: set[str],
    ) -> None:
        """测试 _validate_url_scheme 函数拒绝无效的 scheme."""
        with pytest.raises(ParseUrlError) as e:
            validate_url_scheme(url, allowed_schemes=allowed_schemes)

        assert "不支持的 URL scheme" in str(e.value)


class TestSafeReadUrlData:
    """测试 safe_read_url_data 函数."""

    @staticmethod
    @pytest.mark.parametrize(
        ("content", "expected"),
        [
            (b"test data", b"test data"),
            (b"", b""),
        ],
    )
    def test_success(
        mocker: MagicMock,
        content: bytes,
        expected: bytes,
    ) -> None:
        """测试 safe_read_url_data 函数成功读取数据."""
        mock_response = MagicMock()
        mock_response.content = content

        mocker.patch("requests.get", return_value=mock_response)
        data = safe_read_url_data("https://example.com")
        assert data == expected

    @staticmethod
    def test_timeout(mocker: MagicMock) -> None:
        """测试 safe_read_url_data 函数处理超时情况."""
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.Timeout("timed out"),
        )

        with pytest.raises(ParseUrlError) as execinfo:
            assert safe_read_url_data("https://example.com") is None

        assert "读取URL超时" in str(execinfo.value)

    @staticmethod
    def test_ssl_error(mocker: MagicMock) -> None:
        """测试 safe_read_url_data 函数处理 SSL 错误."""
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.SSLError("SSL error"),
        )

        with pytest.raises(ParseUrlError) as execinfo:
            assert safe_read_url_data("https://example.com") is None

        assert "读取URL失败" in str(execinfo.value)

    @staticmethod
    def test_connection_error(mocker: MagicMock) -> None:
        """测试 safe_read_url_data 函数处理 OS 错误."""
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.ConnectionError("connection error"),
        )

        with pytest.raises(ParseUrlError) as execinfo:
            assert safe_read_url_data("https://example.com") is None

        assert "读取URL失败" in str(execinfo.value)

    @staticmethod
    def test_invalid_url() -> None:
        """测试 safe_read_url_data 函数处理无效的 URL."""
        data = safe_read_url_data("ftp://example.com")
        assert data is None

    @staticmethod
    def test_safe_read_url_data_too_many_redirects(
        mocker: MagicMock,
    ) -> None:
        """测试 safe_read_url_data 函数处理重定向过多."""
        mocker.patch(
            "requests.get",
            side_effect=requests.exceptions.TooManyRedirects("重定向过多"),
        )

        with pytest.raises(ParseUrlError) as execinfo:
            assert safe_read_url_data("https://example.com") is None

        assert "读取URL失败" in str(execinfo.value)
