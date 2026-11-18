---
name: pr-review
description: Gör en ändring möjlig att förstå på en halv minut – en GitHub-PR, en GitLab-MR, en commit eller lokala ändringar som inte är committade eller pushade. Skriver PR:en som ett kort stycke där varje mening är en sak PR:en gör och problem är inbakade med ⚠; klickar man på en mening ser man signaturerna bakom den, och klickar man på en signatur ser man 1–3 meningar om vad den gör, hur det var förut och hur det är nu, och vilket kantfall som spelar roll. Varje signatur länkar till exakt fil och rad: i PR:ens, MR:ens eller committens diffvy på GitHub/GitLab, eller, för lokala ändringar, ett kopierbart `:e +rad fil`-kommando för Neovim. Sidan är smal nog att ligga i ett eget fönster bredvid. Använd när användaren vill reviewa, granska, förstå, skumma eller sätta sig in i en pull request, merge request, commit, diff, branch eller sina egna ocommittade ändringar, när de klistrar in en diff eller PR-länk, eller frågar "kan du kolla den här PR:en", även om ordet review inte nämns.
---

# PR på en halv minut

Granskaren vill läsa en PR som man skumläser en text: bara första meningen i varje stycke, och dyka ner bara där något verkar konstigt. Sidan har därför tre nivåer, och det mesta av PR:en ska granskaren aldrig behöva öppna:

1. **Stycket**: 2–5 meningar, en per sak PR:en gör. Det som skaver är inbakat i texten med ⚠.
2. **Skelettet**: klick på en mening visar signaturerna bakom den (funktioner, endpoints, komponenter, testnamn), med en rad när något är fel.
3. **Förklaringen**: klick på en signatur visar 1–3 meningar text om ändringen. Ingen kod; koden läser granskaren i GitHub via länken **Öppna i PR:en**, som hoppar till rätt fil och rad.

Ditt jobb är att analysera PR:en och skriva datan. Sidan byggs av en färdig mall; skriv aldrig egen HTML. Skriv på användarens språk (oftast svenska).

**Den viktigaste regeln: mindre är mer.** Varje ord du lägger till är ett ord granskaren måste läsa. Om du tvekar om något ska med, låt bli.

## 1. Samla underlag

1. **Kravet**: ärende, issue, PR/MR-beskrivning eller commit-meddelande. Saknas det, härled syftet från commits och titel. För lokala ändringar: fråga inte, utgå från diffen.
2. **Diffen**, sparad till en fil (den behövs i steg 5). Välj rad efter vad användaren pekar på:

| Användaren pekar på | Hämta diffen | `source.kind` |
|---|---|---|
| GitHub-PR | `gh pr diff <nr> > ändring.diff` | `github-pr` |
| GitHub-commit (pushad) | `git show --format= <sha> > ändring.diff` | `github-commit` |
| GitLab-MR | `glab mr diff <nr> --raw > ändring.diff` | `gitlab-mr` |
| GitLab-commit (pushad) | `git show --format= <sha> > ändring.diff` | `gitlab-commit` |
| Ocommittade ändringar | `git diff HEAD > ändring.diff`, plus nya filer (se nedan) | `local` |
| Lokal branch eller opushade commits | `git diff <bas>...HEAD > ändring.diff` | `local` |

   Värd och repo tar du från `git remote get-url origin` (github.com, gitlab.com eller en egen GitLab-värd). En commit eller branch som bara finns lokalt har ingen webbvy, så använd `local`.
   **Nya, ospårade filer** syns inte i `git diff HEAD`. Lägg till dem utan att röra användarens index: `git ls-files --others --exclude-standard`, och för varje fil `git diff --no-index /dev/null <fil> >> ändring.diff` (avslutas med kod 1, det är normalt).
   `local` länkar till filerna som de ser ut i arbetskatalogen nu. För en branch-diff stämmer raderna bara om arbetskatalogen inte har fler ändringar; säg till om den har det.
3. **Sammanhang** (om du har repot): läs anropare till ändrad kod. Det är så du hittar konsekvenser utanför diffen, som en ändrad hjälpfunktion som används på fler ställen.

## 2. Skriv stycket

Det här är det viktigaste steget. Läs hela diffen först, skriv sedan:

- **En mening per beteendeförändring**, sett från användarens eller systemets perspektiv: "Användaren kan nu spara ett veckomål", inte "Lägger till GoalController och goalRepo".
- **Max cirka 15 ord per mening** (skriptet stoppar vid 25). Inga bisatser med tekniska detaljer; de hör hemma i skelettet.
- **Ordning**: det viktigaste först, oftast huvudfunktionen, sedan följder.
- **Problem som påverkar beteendet får en egen mening med `"warn": true`**, till exempel "Veckan börjar nu på måndag överallt, även i profilstatistiken." Det ska vara något granskaren måste ta ställning till, inte en stilfråga.
- Refaktorering utan beteendeförändring blir en kort mening ("Datumhjälparna har flyttats till en egen fil.") eller hamnar i `other_files` om den är trivial.

Testa stycket: läser granskaren *bara* det, vet de då vad PR:en gör och var de ska titta? Om inte, skriv om.

## 3. Skriv skelettet och förklaringen bakom varje mening

För varje mening, lista det som implementerar den i **exekveringsordning** (ingång först):

- **sig**: en rad, som en rubrik i koden: `POST /goals/weekly → setWeeklyGoal(req, res)`, `validateGoal(n: number): string | null`, `<WeeklyGoalCard />`, `test: "returns true when behind"`. Lägg till en kort parentes bara om den förklarar något icke-uppenbart: `reminderJob (kl. 20 varje dag)`.
- **status**: `new`, `mod`, `del` eller `test`.
- **note**: bara när det finns något att säga, en mening. `"warn": true` för verkliga problem. De flesta items ska inte ha någon note.
- **detail**: 1–3 meningar ren text (max 70 ord): vad signaturen gör, hur det var förut och hur det är nu, och vilket kantfall som spelar roll. Skriv beteende, inte kod: "Tar klockans senaste tid om den ligger högst en minut före telefonen, annars telefonens. Förut användes alltid telefonens tid. Ett meddelande 61 s före räknas inte." Hoppa över delarna som inte finns (ny kod har inget "förut").
- **file**: sökvägen från repots rot, exakt som i diffens `+++ b/`-rad (eller `--- a/` för borttagna filer). Gäller även `local`.
- **line**: radnumret där beslutet fattas, hämtat från diffen: räkna från hunkens `@@ -gammal +ny @@`. Använd numret i nya filen för tillagda och oförändrade rader.
- **side**: utelämna (= `R`, nya filen). Sätt `"L"` bara när raden är borttagen; då är `line` numret i gamla filen.

Länken räknar `build.py` ut från `source`, diffen, `file`, `side` och `line`. Skriv aldrig själv några URL:er, hashar eller radpar.

Tester hör till meningen vars beteende de testar. Läs `references/test-checklist.md` och flagga med warn när ett test inte bevisar det det påstår; det är vanligt i AI-skriven kod.

Kontrollera täckning: varje ändrad funktion ska höra till någon mening eller ligga i `other_files`. Det som inte passar någonstans är ofta scope creep, och det förtjänar en warn-mening.

## 4. Datan

```json
{
  "title": "PR-titel (#nr), commit-rubrik eller kort namn på de lokala ändringarna",
  "source": { "kind": "github-pr", "repo": "ägare/repo", "number": 12 },
  "sentences": [
    {
      "text": "Användaren kan nu spara ett veckomål på 1–14 träningspass.",
      "warn": false,
      "items": [
        { "status": "new", "sig": "validateGoal(n: number): string | null",
          "note": "Släpper igenom NaN.", "warn": true,
          "detail": "Returnerar ett felmeddelande om målet ligger utanför 1–14 pass, annars null. NaN klarar båda jämförelserna och sparas därför.",
          "file": "src/goals/validate.ts", "line": 4 }
      ]
    }
  ],
  "other_files": [ { "file": "package-lock.json", "reason": "beroenden" } ]
}
```

`source` beroende på `kind`:

- `github-pr` / `gitlab-mr`: `repo` och `number` (MR:ens `!`-nummer).
- `github-commit` / `gitlab-commit`: `repo` och `commit` (hash, kort eller lång).
- `local`: `root`, repots absoluta sökväg (`git rev-parse --show-toplevel`). Knappen kopierar `:e +rad /absolut/sökväg` som användaren klistrar in i sin öppna Neovim.
- Valfritt `host` för egen värd, t.ex. `"host": "gitlab.foretaget.se"`. GitLab-`repo` får ha undergrupper: `grupp/undergrupp/projekt`.

Alla strängar är ren text, inte Markdown eller HTML.

## 5. Bygg och leverera

```bash
python <skill-katalog>/scripts/build.py data.json skum.html --diff ändring.diff
```

`--diff` krävs: skriptet kontrollerar att varje `file`/`side`/`line` faktiskt syns i diffen och använder den för att räkna ut länken (GitLab och Neovim-kommandot behöver radpositioner som bara diffen har). Rätta och kör igen om skriptet klagar. Har användaren bara klistrat in en diff utan repo finns inget att länka till; säg det i stället för att hitta på en `source`. Leverera sedan:

- **Claude Code / lokal terminal**: lägg filen utanför repot (t.ex. i `/tmp`) och öppna den i ett eget fönster bredvid GitHub, GitLab eller terminalen (`open` på macOS, `xdg-open` på Linux, `start` på Windows).
- **Claude.ai med Artifact-verktyget**: lägg filen i `/mnt/user-data/outputs/` och publicera den.
- **Annars**: presentera filen.

I chatten: en mening, högst två. Sidan är svaret.

Posta aldrig kommentarer, godkänn aldrig och begär aldrig ändringar på PR:en eller MR:en, och ändra aldrig användarens arbetskatalog eller index, utan att användaren uttryckligen ber om det.
