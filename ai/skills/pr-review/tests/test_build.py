"""Tester för build.py: python3 -m unittest discover -s ai/skills/pr-review/tests"""
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import build  # noqa: E402

SQL_DIFF = """\
diff --git a/q.sql b/q.sql
--- a/q.sql
+++ b/q.sql
@@ -1,5 +1,5 @@
 select 1;
--- gammal kommentar
++++ ny rad som börjar med två plus
 select 2;
-select 3;
+select 3 -- ny;
 select 4;
diff --git a/next.sql b/next.sql
--- a/next.sql
+++ b/next.sql
@@ -1 +1 @@
-a
+b
"""

ODD_NAMES_DIFF = """\
diff --git a/src/ny fil.ts b/src/ny fil.ts
new file mode 100644
--- /dev/null
+++ b/src/ny fil.ts\t
@@ -0,0 +1,2 @@
+ny
+fil
diff --git "a/src/\\303\\245.ts" "b/src/\\303\\245.ts"
new file mode 100644
--- /dev/null
+++ "b/src/\\303\\245.ts"
@@ -0,0 +1 @@
+x
\\ No newline at end of file
diff --git a/old.ts b/old.ts
deleted file mode 100644
--- a/old.ts
+++ /dev/null
@@ -1 +0,0 @@
-gammal
"""

GITLAB_DIFF = """\
diff --git a/f.go b/f.go
--- a/f.go
+++ b/f.go
@@ -10,3 +12,4 @@ func x() {
 a
-b
+c
+d
 e
"""


class ParseDiff(unittest.TestCase):
    def test_lines_starting_with_dashes_or_pluses_are_content_not_headers(self):
        lines, _ = build.parse_diff(SQL_DIFF)
        self.assertEqual(lines[("q.sql", "L", 2)], ("-", 2, 2))  # "-- gammal kommentar"
        self.assertEqual(lines[("q.sql", "R", 2)], ("+", 3, 2))  # "++ ny rad …"
        self.assertEqual(lines[("q.sql", "L", 4)], ("-", 4, 4))  # "select 3;"
        self.assertEqual(lines[("q.sql", "R", 5)], (" ", 5, 5))  # "select 4;"
        self.assertEqual(lines[("next.sql", "R", 1)], ("+", 2, 1))

    def test_paths_with_space_non_ascii_and_deleted_files(self):
        lines, deleted = build.parse_diff(ODD_NAMES_DIFF)
        self.assertIn(("src/ny fil.ts", "R", 2), lines)
        self.assertIn(("src/å.ts", "R", 1), lines)
        self.assertIn(("old.ts", "L", 1), lines)
        self.assertEqual(deleted, {"old.ts"})


class Links(unittest.TestCase):
    def link(self, src, diff, file, side, line):
        lines, deleted = build.parse_diff(diff)
        return build.link(src, file, lines[(file, side, line)], deleted)

    def test_github_pr_and_commit_use_sha256_of_path(self):
        digest = hashlib.sha256(b"f.go").hexdigest()
        pr = {"kind": "github-pr", "repo": "o/r", "number": 7}
        commit = {"kind": "github-commit", "repo": "o/r", "commit": "abc1234"}
        self.assertEqual(self.link(pr, GITLAB_DIFF, "f.go", "R", 13),
                         f"https://github.com/o/r/pull/7/files#diff-{digest}R13")
        self.assertEqual(self.link(commit, GITLAB_DIFF, "f.go", "L", 11),
                         f"https://github.com/o/r/commit/abc1234#diff-{digest}L11")

    def test_gitlab_uses_old_number_except_for_added_lines(self):
        src = {"kind": "gitlab-mr", "repo": "g/sub/p", "number": 3}
        base = "https://gitlab.com/g/sub/p/-/merge_requests/3/diffs#line_" + hashlib.sha1(b"f.go").hexdigest()[:9]
        self.assertEqual(self.link(src, GITLAB_DIFF, "f.go", "R", 12), base + "_10")   # context
        self.assertEqual(self.link(src, GITLAB_DIFF, "f.go", "L", 11), base + "_11")   # removed
        self.assertEqual(self.link(src, GITLAB_DIFF, "f.go", "R", 13), base + "_A13")  # added
        self.assertEqual(self.link(src, GITLAB_DIFF, "f.go", "R", 15), base + "_12")   # context after

    def test_gitlab_file_hash_matches_gitlab_com(self):
        # Read from a real gitlab.com MR page (gitlab-org/cli!4388).
        self.assertEqual(hashlib.sha1(b"docs/source/dependency-firewall/_index.md").hexdigest()[:9], "66300a8c1")

    def test_local_copies_an_escaped_nvim_command_and_skips_deleted_files(self):
        src = {"kind": "local", "root": "/r/my repo"}
        self.assertEqual(self.link(src, ODD_NAMES_DIFF, "src/ny fil.ts", "R", 2), r":e +2 /r/my\ repo/src/ny\ fil.ts")
        self.assertIsNone(self.link(src, ODD_NAMES_DIFF, "old.ts", "L", 1))

    def test_nvim_escape_matches_fnameescape(self):
        # Expected values taken from Neovim's fnameescape().
        self.assertEqual(build.nvim_escape("/a/it's #1 %.ts"), r"/a/it\'s\ \#1\ \%.ts")
        self.assertEqual(build.nvim_escape("/a/[x]{y}$z!<w|v`u.ts"), r"/a/\[x]\{y}\$z\!\<w\|v\`u.ts")


class Validate(unittest.TestCase):
    def data(self, **item):
        return {"title": "t", "source": {"kind": "github-pr", "repo": "o/r", "number": 1},
                "sentences": [{"text": "En mening.", "items": [{"status": "new", "sig": "s", "detail": "d", **item}]}]}

    def test_accepts_a_line_in_the_diff(self):
        lines, _ = build.parse_diff(GITLAB_DIFF)
        self.assertEqual(build.validate(self.data(file="f.go", line=13), lines), [])

    def test_rejects_a_line_outside_the_diff_and_old_code_field(self):
        lines, _ = build.parse_diff(GITLAB_DIFF)
        errs = build.validate(self.data(file="f.go", line=99, code="x"), lines)
        self.assertTrue(any("R99 syns inte i diffen" in e for e in errs))
        self.assertTrue(any("'code' används inte längre" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
