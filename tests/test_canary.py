import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "canary" / "scripts" / "canary.py"


class CanaryCLI(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.cwd = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], cwd=self.cwd, capture_output=True, text=True)

    def test_init_creates_state(self):
        self.assertEqual(self.run_cli("init").returncode, 0)
        for p in ("golden", "held", "outbox", "rules.md", "ledger.jsonl"):
            self.assertTrue((self.cwd / ".canary" / p).exists(), p)

    def test_record_without_init_creates_state(self):
        r = self.run_cli("record", "a.txt", "sampled")
        self.assertEqual(r.returncode, 0, r.stderr)
        rec = json.loads((self.cwd / ".canary" / "ledger.jsonl").read_text().strip())
        self.assertEqual((rec["item"], rec["status"]), ("a.txt", "sampled"))

    def test_record_rejects_bad_status_and_wave(self):
        self.assertNotEqual(self.run_cli("record", "a.txt", "finished").returncode, 0)
        self.assertNotEqual(self.run_cli("record", "a.txt", "done", "--wave", "two").returncode, 0)
        self.assertNotEqual(self.run_cli("record", "a.txt", "done", "--wave").returncode, 0)

    def test_status_uses_latest_record_per_item(self):
        self.run_cli("record", "a", "sampled")
        self.run_cli("record", "a", "approved")
        self.run_cli("record", "b", "done", "--wave", "2")
        self.run_cli("record", "c", "held", "--wave", "2", "--reason", "formal")
        out = self.run_cli("status", "--total", "10", "--waves", "3").stdout
        self.assertIn("2 done of 10 · 1 held · 0 sampled · 0 rejected · wave 2/3", out)
        self.assertIn("held: c", out)

    def test_held_lists_reasons(self):
        self.run_cli("record", "c", "held", "--reason", "asks about money")
        self.assertIn("- c: asks about money", self.run_cli("held").stdout)
        self.run_cli("record", "c", "done")
        self.assertIn("nothing held", self.run_cli("held").stdout)

    def test_malformed_ledger_line_is_skipped(self):
        self.run_cli("record", "a", "done")
        with (self.cwd / ".canary" / "ledger.jsonl").open("a") as fh:
            fh.write("{not json\n")
        r = self.run_cli("status")
        self.assertEqual(r.returncode, 0)
        self.assertIn("1 done", r.stdout)
        self.assertIn("malformed", r.stderr)

    def test_list_flat_and_recursive(self):
        src = self.cwd / "src"
        (src / "api").mkdir(parents=True)
        (src / "node_modules" / "x").mkdir(parents=True)
        (src / "a.js").write_text("const a = 1\n")
        (src / "api" / "users.js").write_text("export {}\n")
        (src / "node_modules" / "x" / "i.js").write_text("junk\n")
        (src / "img.bin").write_bytes(b"\xff\xd8\xff\x00")
        flat = self.run_cli("list", "src").stdout
        self.assertIn("api  ", flat)
        self.assertIn("(dir)", flat)
        self.assertIn("(binary)", flat)
        rec = self.run_cli("list", "src", "-r").stdout
        self.assertIn("api/users.js", rec)
        self.assertNotIn("node_modules", rec)
        self.assertIn("3 items", rec)

    def test_list_missing_dir_fails(self):
        self.assertNotEqual(self.run_cli("list", "nope").returncode, 0)


if __name__ == "__main__":
    unittest.main()
