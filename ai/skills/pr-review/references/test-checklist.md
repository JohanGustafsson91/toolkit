# Checklista: granska tester

Gå igenom detta för varje testfil som ändrats eller borde ha ändrats.

## Testar det rätt sak?
- **Beteende, inte implementation**: testar det *vad* koden gör (indata → utdata, synliga effekter) eller *hur* (vilka interna metoder som anropas i vilken ordning)? Implementationstester går sönder vid refaktorering men fångar sällan buggar.
- **Speglar testet koden?** Om förväntat värde räknas ut med samma logik som produktkoden bevisar testet ingenting. Förväntade värden ska vara hårdkodade eller härledda oberoende.
- **Matchar testnamnet innehållet?** AI skriver ofta `should_handle_invalid_input` som sedan bara testar giltig indata.

## Mockar
- Körs den verkliga logiken, eller bara mockar? Ett test där det som testas själv är mockat testar ingenting.
- Är det rätt sak som mockas (externa beroenden: nätverk, databas, klocka) och inte koden under test?
- Returnerar mockarna realistiska data, inklusive felfall?

## Asserts
Svaga asserts att flagga:
- `assertNotNull`, `toBeDefined`, `toBeTruthy` som enda kontroll.
- "Anropades" (`verify`, `toHaveBeenCalled`) utan kontroll av argument eller resultat.
- Snapshot-tester av stora strukturer som ingen kommer att läsa vid diff.
- Test utan assert alls, eller try/catch som sväljer felet.
- Assert på något som alltid är sant.

## Täckning av beteende
För kärnlogiken, finns det tester för:
- Lyckat fall (oftast finns det).
- Felfall: ogiltig indata, beroende som misslyckas, timeout.
- Gränsvärden: 0, 1, max, precis över/under gräns.
- Tomt/null/saknat.
- Dubbletter, ordning, samtidighet där det är relevant.
- Varje krav från kravformuleringen: finns minst ett test som skulle falla om kravet bröts?

## Mutationstankeexperiment
Välj 2–4 konkreta ställen i den ändrade logiken och fråga om något test skulle falla vid:
- `>` → `>=`, `&&` → `||`, `+1` borttaget.
- Ett villkor inverterat eller en gren borttagen.
- Ett returvärde ersatt med en konstant.
- Ett felfall som ignoreras i stället för att kastas.

Redovisa: "Om X ändras till Y på fil:rad faller [test] / faller inget test."

## Underhåll
- Är testerna läsbara? Arrange/act/assert tydligt?
- Hårdkodade datum, slumpvärden eller beroende på körordning (flakiga)?
- Duplicerad setup som borde vara en hjälpfunktion, eller tvärtom en hjälpfunktion som döljer vad testet gör?
