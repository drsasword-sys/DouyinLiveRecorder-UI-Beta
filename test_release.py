import unittest
from pathlib import Path


class ReleaseScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = Path("build_beta.ps1").read_text(encoding="utf-8")

    def test_build_uses_version_specific_output_directories(self):
        self.assertIn('"dist\\$Version"', self.script)
        self.assertIn('"build\\$Version"', self.script)

    def test_build_stops_when_pyinstaller_fails(self):
        self.assertIn("if ($LASTEXITCODE -ne 0)", self.script)
        self.assertIn('throw "PyInstaller failed', self.script)

    def test_archive_creation_retries_transient_file_locks(self):
        self.assertIn("for ($Attempt = 1; $Attempt -le 3; $Attempt++)", self.script)
        self.assertIn("Start-Sleep -Seconds 2", self.script)

    def test_self_test_version_must_match_release_version(self):
        self.assertIn("$SelfTestReport.version -ne $Version", self.script)


if __name__ == "__main__":
    unittest.main()
