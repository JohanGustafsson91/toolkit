#!/usr/bin/env python3
"""Bygger skumläsningssidan.

    python build.py data.json ut.html --diff ändringen.diff

Räknar ut länken för varje signatur från `source` i datan och diffen:
GitHub-PR, GitHub-commit, GitLab-MR, GitLab-commit eller lokala ändringar
(kopierar ett :e-kommando för Neovim). Varje file/side/line kontrolleras mot diffen, så att
ingen länk hamnar fel utan att någon märker det.
"""
import codecs
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STATUSES = ("new", "mod", "del", "test")
SIDES = ("R", "L")
MAX_DETAIL_WORDS = 70
HUNK = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
REPO = re.compile(r"[\w.-]+(/[\w.-]+)+")
SHA = re.compile(r"[0-9a-f]{7,40}")

KINDS = {
    "github-pr": {"host": "github.com", "needs": ("repo", "number"), "label": "Öppna i PR:en"},
    "github-commit": {"host": "github.com", "needs": ("repo", "commit"), "label": "Öppna i committen"},
    "gitlab-mr": {"host": "gitlab.com", "needs": ("repo", "number"), "label": "Öppna i MR:en"},
    "gitlab-commit": {"host": "gitlab.com", "needs": ("repo", "commit"), "label": "Öppna i committen"},
    "local": {"host": None, "needs": ("root",), "label": "Kopiera för Neovim"},
}


def header_path(rest):
    """Sökvägen i en ---/+++-rad. Git lägger en tabb efter namn med mellanslag
    och citerar namn med t.ex. å som "b/src/\\303\\245.ts"."""
    rest = rest.rstrip("\t")
    if rest.startswith('"') and rest.endswith('"'):
        rest = codecs.escape_decode(rest[1:-1].encode("latin-1"))[0].decode("utf-8")
    return rest[2:] if rest[:2] in ("a/", "b/") else None


def parse_diff(diff_text):
    """(fil, sida, rad) -> (typ, gammal rad, ny rad) för varje rad som syns i diffen.

    R = nya filen, L = gamla. För en tillagd rad är "gammal rad" positionen i
    gamla filen, och för en borttagen rad är "ny rad" positionen i nya filen;
    GitLab och editorlänkar behöver de positionerna.
    """
    lines, deleted = {}, set()
    old_file = file = None
    old = new = old_left = new_left = 0
    for raw in diff_text.splitlines():
        # Inside a hunk, count down its lengths: a removed "-- x" or added "++ x"
        # looks exactly like a ---/+++ file header otherwise.
        if old_left or new_left:
            kind = raw[:1] or " "  # some tools strip the space off empty context lines
            if kind not in (" ", "+", "-"):
                continue  # "\ No newline at end of file"
            if file and kind in (" ", "-"):
                lines[(file, "L", old)] = (kind, old, new)
            if file and kind in (" ", "+"):
                lines[(file, "R", new)] = (kind, old, new)
            if kind in (" ", "-"):
                old, old_left = old + 1, old_left - 1
            if kind in (" ", "+"):
                new, new_left = new + 1, new_left - 1
        elif raw.startswith("diff "):
            old_file = file = None
        elif raw.startswith("--- "):
            old_file = header_path(raw[4:])
        elif raw.startswith("+++ "):
            file = header_path(raw[4:]) or old_file
            if raw.rstrip("\t") == "+++ /dev/null" and old_file:
                deleted.add(old_file)
        elif m := HUNK.match(raw):
            old, new = int(m[1]), int(m[3])
            old_left, new_left = int(m[2] or 1), int(m[4] or 1)
    return lines, deleted


def link(src, file, pos, deleted):
    kind, old, new = pos
    k = src["kind"]
    host = src.get("host") or KINDS[k]["host"]
    if k.startswith("github"):
        side = "L" if kind == "-" else "R"
        line = old if kind == "-" else new
        frag = f"diff-{hashlib.sha256(file.encode()).hexdigest()}{side}{line}"
        path = f"pull/{src['number']}/files" if k == "github-pr" else f"commit/{src['commit']}"
        return f"https://{host}/{src['repo']}/{path}#{frag}"
    if k.startswith("gitlab"):
        # GitLabs diffvy: borttagna och oförändrade rader har gamla radnumret, tillagda "A" + nya.
        num = f"A{new}" if kind == "+" else str(old)
        frag = f"line_{hashlib.sha1(file.encode()).hexdigest()[:9]}_{num}"
        path = f"-/merge_requests/{src['number']}/diffs" if k == "gitlab-mr" else f"-/commit/{src['commit']}"
        return f"https://{host}/{src['repo']}/{path}#{frag}"
    if file in deleted:
        return None
    # En borttagen rad finns inte längre; "new" är där den stod i filen som den ser ut nu.
    return f":e +{max(new, 1)} {nvim_escape(str(Path(src['root']) / file))}"


def nvim_escape(path):
    """Som Neovims fnameescape(), så att :e klarar mellanslag och specialtecken."""
    return re.sub(r"""([ \t*?[{`$\\%#'"|!<])""", r"\\\1", path)


def validate_source(src):
    if not isinstance(src, dict) or src.get("kind") not in KINDS:
        return [f"'source.kind' ska vara en av {tuple(KINDS)}"]
    errs = [f"source saknar '{f}'" for f in KINDS[src["kind"]]["needs"] if f not in src]
    if "repo" in src and not REPO.fullmatch(str(src["repo"])):
        errs.append(f"source.repo ska vara ägare/namn (GitLab: grupp/…/projekt), är '{src['repo']}'")
    if "number" in src and not isinstance(src["number"], int):
        errs.append("source.number ska vara ett heltal")
    if "commit" in src and not SHA.fullmatch(str(src["commit"])):
        errs.append(f"source.commit ska vara en commit-hash, är '{src['commit']}'")
    if "root" in src and not (Path(src["root"]).is_absolute() and Path(src["root"]).is_dir()):
        errs.append(f"source.root ska vara repots absoluta sökväg, är '{src['root']}'")
    return errs


def validate(d, lines):
    errs = [] if d.get("title") else ["saknar 'title'"]
    errs += validate_source(d.get("source"))
    sents = d.get("sentences") or []
    if not 1 <= len(sents) <= 6:
        errs.append(f"stycket ska ha 1–6 meningar, har {len(sents)}")
    for i, s in enumerate(sents, 1):
        text = s.get("text", "")
        if not text:
            errs.append(f"mening {i} saknar text")
        elif len(text.split()) > 25:
            errs.append(f"mening {i} har {len(text.split())} ord, max 25: '{text}'")
        if not s.get("items"):
            errs.append(f"mening {i} saknar items (signaturerna bakom meningen)")
        for it in s.get("items", []):
            where = f"mening {i}, {it.get('sig')}"
            if not it.get("sig"):
                errs.append(f"mening {i}: item saknar 'sig'")
            if it.get("status") not in STATUSES:
                errs.append(f"{where}: status måste vara en av {STATUSES}")
            if "code" in it:
                errs.append(f"{where}: 'code' används inte längre, skriv 'detail' i stället")
            detail = it.get("detail") or ""
            if not detail:
                errs.append(f"{where}: saknar 'detail' (1–3 meningar)")
            elif len(detail.split()) > MAX_DETAIL_WORDS:
                errs.append(f"{where}: detail har {len(detail.split())} ord, max {MAX_DETAIL_WORDS}")
            side = it.get("side", "R")
            if side not in SIDES:
                errs.append(f"{where}: 'side' ska vara R (ny eller oförändrad rad) eller L (borttagen rad)")
            elif not it.get("file") or not isinstance(it.get("line"), int):
                errs.append(f"{where}: behöver 'file' (sökväg från repots rot) och 'line' (heltal)")
            elif (it["file"], side, it["line"]) not in lines:
                errs.append(f"{where}: {it['file']} {side}{it['line']} syns inte i diffen")
    return errs


def with_links(d, lines, deleted):
    src = d["source"]

    def add(it):
        pos = lines[(it["file"], it.get("side", "R"), it["line"])]
        target = link(src, it["file"], pos, deleted)
        return {**it, ("copy" if src["kind"] == "local" else "href"): target}

    return {
        **d,
        "link_label": KINDS[src["kind"]]["label"],
        "sentences": [{**s, "items": [add(it) for it in s["items"]]} for s in d["sentences"]],
    }


def main():
    args = sys.argv[1:]
    if len(args) != 4 or args[2] != "--diff":
        sys.exit("Användning: python build.py data.json ut.html --diff ändringen.diff")
    data = json.loads(Path(args[0]).read_text(encoding="utf-8"))
    lines, deleted = parse_diff(Path(args[3]).read_text(encoding="utf-8"))
    if not lines:
        sys.exit(f"Hittade inga diffrader i {args[3]}. Är diffen tom?")
    errs = validate(data, lines)
    if errs:
        sys.exit("Fel i datan:\n- " + "\n- ".join(errs))
    payload = json.dumps(with_links(data, lines, deleted), ensure_ascii=False).replace("</", "<\\/")
    html = (ROOT / "assets" / "viewer.html").read_text(encoding="utf-8").replace("__PR_DATA__", payload)
    Path(args[1]).write_text(html, encoding="utf-8")
    print(f"Skrev {args[1]}")


if __name__ == "__main__":
    main()
