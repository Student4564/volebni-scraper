import requests
import re
import csv
import sys

PATTERNS = {
    "municipality_name": r'<td class="overflow_name".*?>(.*?)</td>',
    "municipality_code": r'<a href="ps311\?.*?xobec=(\d+?)&amp;.*?">\d+?</a>',
    "voters": r'<td class="cislo" headers="sa2"[^>]*>([^<]+)</td>',
    "ballot_envelopes": r'<td class="cislo" headers="sa3"[^>]*>([^<]+)</td>',
    "valid_votes": r'<td class="cislo" headers="sa6"[^>]*>([^<]+)</td>',
    "parties": re.compile(
        r'<td class="cislo" headers="t1sa1 t1sb1">\s*(\d+)\s*</td>\s*'
        r'<td class="overflow_name" headers="t1sa1 t1sb2">([^<]*)</td>\s*'
        r'<td class="cislo" headers="t1sa2 t1sb3">([^<]*)</td>'
    )
}

def read_numbers(html):
    """
    Reads voter, ballot envelope, and valid vote counts from municipality HTML.
    """
    def get_number(pattern):
        match = re.search(pattern, html)
        if match:
            try:
                return int(match.group(1).replace('&nbsp;', '').replace(' ', ''))
            except ValueError:
                return 0
        return 0

    return {
        "voters": get_number(PATTERNS["voters"]),
        "ballot_envelopes": get_number(PATTERNS["ballot_envelopes"]),
        "valid_votes": get_number(PATTERNS["valid_votes"])
    }

def read_parties(html):
    """
    Reads party results (name and vote count) from municipality HTML.
    """
    parties = {}
    for found_match in PATTERNS["parties"].finditer(html):
        party_name = found_match.group(2).strip()
        try:
            parties[party_name] = int(found_match.group(3).replace('&nbsp;', '').replace(' ', ''))
        except ValueError:
            parties[party_name] = 0
    return parties

def download_page(url):
    """
    Downloads the HTML content from the specified URL.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování stránky: {e}")
        return None

def find_municipalities(url):
    """
    Finds municipality names, codes, and constructs detail URLs from a regional page.
    """
    html = download_page(url)
    if not html:
        return None

    names = re.findall(PATTERNS["municipality_name"], html)
    codes = re.findall(PATTERNS["municipality_code"], html)

    if len(names) != len(codes):
        print("Počet obcí a kódů nesouhlasí, asi je stránka jiná než očekáváme.")
        return None

    kraj_match = re.search(r"xkraj=(\d+)", url)
    nuts_match = re.search(r"xnumnuts=(\d+)", url)

    if not kraj_match or not nuts_match:
        print("Nepodařilo se najít parametry 'xkraj' nebo 'xnumnuts'.")
        return None

    kraj_id = kraj_match.group(1)
    nuts_id = nuts_match.group(1)

    result = []
    for name, code in zip(names, codes):
        detail_url = f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj_id}&xobec={code}&xvyber={nuts_id}"
        result.append({
            "code": code,
            "name": name,
            "url": detail_url,
            "voters": 0,
            "ballot_envelopes": 0,
            "valid_votes": 0,
            "parties": {}
        })
    return result

def process_municipalities(municipality_list):
    """
    Iterates through municipalities, downloads detail pages, and extracts data.
    """
    processed_data = []
    for municipality in municipality_list:
        print(f"Zpracovávám obec: {municipality['name']}")
        html = download_page(municipality["url"])
        if not html:
            continue
        municipality.update(read_numbers(html))
        municipality["parties"] = read_parties(html)
        processed_data.append(municipality)
    return processed_data

def save_csv(data, filename):
    """
    Saves the processed election data to a CSV file.
    """
    if not data:
        print("Žádná data k uložení.")
        return

    all_parties = set()
    for municipality in data:
        all_parties.update(municipality["parties"].keys())
    
    headers = ["code", "name", "voters", "ballot_envelopes", "valid_votes"] + sorted(all_parties)

    try:
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for municipality in data:
                row = [
                    municipality["code"],
                    municipality["name"],
                    municipality["voters"],
                    municipality["ballot_envelopes"],
                    municipality["valid_votes"]
                ]
                for party in sorted(all_parties):
                    row.append(municipality["parties"].get(party, 0))
                writer.writerow(row)
        print(f"Soubor uložen jako {filename}")
    except IOError as e:
        print(f"Chyba při ukládání CSV: {e}")

def main():
    """
    Main function to run the scraper.
    """
    if len(sys.argv) != 3:
        print("Použití: python skript.py <URL_HLAVNI_STRANKY> <NAZEV_CSV>")
        sys.exit(1)

    url = sys.argv[1]
    output_filename = sys.argv[2]

    print(f"Stahuju data z: {url}")
    print(f"Výstupní soubor bude: {output_filename}")

    municipalities = find_municipalities(url)
    if municipalities:
        data = process_municipalities(municipalities)
        save_csv(data, output_filename)
    else:
        print("Nepodařilo se načíst seznam obcí.")

if __name__ == "__main__":
    main()
