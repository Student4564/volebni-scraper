# Jednoduchý Scraper Volebních Výsledků

Tento Python skript slouží k **automatickému získávání volebních výsledků** z webových stránek volby.cz, jejich zpracování a následnému uložení do souboru CSV. Je navržen tak, aby rychle extrahoval základní data o voličích, vydaných obálkách, platných hlasech a podrobné výsledky pro jednotlivé politické strany v obcích vybraného kraje.

---

## Jak to funguje?

Skript funguje ve několika logických krocích:

1.  **Stáhnutí hlavní stránky kraje:** Na začátku stáhne HTML obsah hlavní stránky kraje z `volby.cz`, kterou mu zadáte jako argument.
2.  **Identifikace obcí:** Z této hlavní stránky pomocí regulárních výrazů (`PATTERNS`) vyhledá názvy a kódy všech obcí v daném kraji. Zároveň sestaví unikátní URL pro detailní výsledky každé obce.
3.  **Zpracování jednotlivých obcí:** Pro každou nalezenou obec skript:
    * Stáhne její detailní HTML stránku.
    * Pomocí dalších regulárních výrazů extrahuje klíčové statistiky: počet voličů, vydaných obálek a platných hlasů.
    * Sebere výsledky všech politických stran (název strany a počet hlasů, které získala).
4.  **Uložení do CSV:** Všechna získaná data (kód obce, název, statistiky a hlasy pro každou stranu) se shromáždí a uloží do jednoho souboru CSV. Každá obec tvoří jeden řádek a pro každou politickou stranu se vytvoří samostatný sloupec.

**Důležitá poznámka:** Skript je navržen pro konkrétní strukturu stránek `volby.cz` pro **parlamentní volby v roce 2017**. Pokud se struktura webu nebo typ voleb změní, je možné, že bude potřeba aktualizovat `PATTERNS` v kódu.

---

## Jak to spustit?

### Požadavky

* **Python 3.x**
* **Knihovna `requests`**: Pokud ji nemáte, nainstalujte ji pomocí pip:
    ```bash
    pip install requests
    ```

### Použití

Skript se spouští z příkazové řádky. Potřebuje dva argumenty:
1.  **URL hlavní stránky kraje** z `volby.cz`.
2.  **Název výstupního CSV souboru**.

```bash
python nazev_vaseho_souboru.py <URL_HLAVNI_STRANKY_KRAJE> <NAZEV_CSV_SOUBORU>
