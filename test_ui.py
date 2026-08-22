import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from ui import add_url, ensure_runtime_files, stop_url, validate_url


class ValidateUrlTests(unittest.TestCase):
    def test_accepts_douyin_live_url(self):
        self.assertEqual(
            validate_url("https://live.douyin.com/123456789012#section"),
            "https://live.douyin.com/123456789012",
        )

    def test_accepts_tiktok_live_url(self):
        self.assertTrue(validate_url("https://www.tiktok.com/@creator/live").startswith("https://"))

    def test_rejects_unknown_host(self):
        with self.assertRaises(ValueError):
            validate_url("https://example.com/live")

    def test_rejects_embedded_credentials(self):
        with self.assertRaises(ValueError):
            validate_url("https://user:pass@live.douyin.com/123")

    def test_rejects_markup_and_control_characters(self):
        for url in (
            "https://live.douyin.com/123?<script>alert(1)</script>",
            "https://live.douyin.com/123\nmalicious",
            'https://live.douyin.com/123?value="onclick',
        ):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_url(url)

    def test_start_and_stop_update_config_without_duplicates(self):
        with TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "URL_config.ini"
            with patch("ui.URL_CONFIG", config_file):
                url = "https://live.douyin.com/123456789012"
                add_url(url, "主播一")
                add_url(url, "主播一")
                self.assertEqual(config_file.read_text(encoding="utf-8-sig").splitlines(), [f"{url},主播: 主播一"])

                stop_url(url)
                self.assertEqual(config_file.read_text(encoding="utf-8-sig").splitlines(), [f"#{url},主播: 主播一"])

    def test_runtime_files_are_created_without_overwriting_user_config(self):
        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            templates = root / "templates"
            templates.mkdir()
            config_template = templates / "config.example.ini"
            url_template = templates / "URL_config.example.ini"
            config_template.write_text("safe-template", encoding="utf-8")
            url_template.write_text("# empty", encoding="utf-8")
            runtime_url = root / "app" / "config" / "URL_config.ini"

            with (
                patch("ui.APP_DIR", root / "app"),
                patch("ui.URL_CONFIG", runtime_url),
                patch("ui.CONFIG_TEMPLATE", config_template),
                patch("ui.URL_CONFIG_TEMPLATE", url_template),
            ):
                ensure_runtime_files()
                runtime_config = root / "app" / "config" / "config.ini"
                self.assertEqual(runtime_config.read_text(encoding="utf-8"), "safe-template")
                runtime_config.write_text("user-secret", encoding="utf-8")
                ensure_runtime_files()
                self.assertEqual(runtime_config.read_text(encoding="utf-8"), "user-secret")


if __name__ == "__main__":
    unittest.main()
