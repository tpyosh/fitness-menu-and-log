import importlib.util
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "export_today_menu_to_apple_notes.py"
)
SPEC = importlib.util.spec_from_file_location("apple_notes_export", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ExportTodayMenuTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = MODULE.CURRENT_MENUS.read_text(encoding="utf-8")

    def test_extracts_only_selected_menu(self):
        menu_a = MODULE.extract_menu(self.source, "A")
        self.assertTrue(menu_a.startswith("# A（"))
        self.assertIn("## ② Seated Leg Press", menu_a)
        self.assertNotIn("# B（", menu_a)

    def test_extracts_c_without_following_section(self):
        menu_c = MODULE.extract_menu(self.source, "C")
        self.assertTrue(menu_c.startswith("# C（"))
        self.assertIn("## Recovery（30分）", menu_c)
        self.assertIn("## Standard（45分）", menu_c)
        self.assertIn("## Endurance（60分）", menu_c)
        self.assertNotIn("# 8〜12週間の運用とDeload", menu_c)

    def test_extracts_only_selected_c_mode_and_common_rules(self):
        menu_c = MODULE.extract_menu(self.source, "C")
        standard = MODULE.extract_c_mode(menu_c, "standard")
        self.assertIn("## Standard（45分）", standard)
        self.assertIn("6.0 km/h・傾斜8%", standard)
        self.assertIn("## 共通の実施・中止基準", standard)
        self.assertNotIn("## Recovery（30分）", standard)
        self.assertNotIn("## Endurance（60分）", standard)

    def test_note_body_keeps_fixed_title_as_first_heading(self):
        menu_b = MODULE.extract_menu(self.source, "B")
        body = MODULE.build_note_body(menu_b, "B", "2026-08-29")
        self.assertTrue(body.startswith(f"<h1>{MODULE.NOTE_TITLE}</h1>"))
        self.assertIn("2026-08-29 / Menu B", body)
        self.assertIn("<h3>② Lat Pulldown</h3>", body)


if __name__ == "__main__":
    unittest.main()
