"""
Script d'automatisation pour synchroniser les styles et templates de cartes Anki EDN
vers AnkiCollab via la session Firefox active.
"""

import os
import re
import glob
import json
import sqlite3
import tempfile
import shutil
import lz4.block
import requests
from bs4 import BeautifulSoup
from urllib3.util import connection

# Contournement du blocage DNS / FAI francais (RST injectes sur 188.114.96.x/188.114.97.x)
# Routage direct vers les adresses Anycast Cloudflare propres
_orig_create_connection = connection.create_connection

def _patched_create_connection(address, *args, **kwargs):
    host, port = address
    if host == "ankicollab.com":
        host = "104.21.32.1"
    return _orig_create_connection((host, port), *args, **kwargs)

connection.create_connection = _patched_create_connection

DROPBOX_DIR = os.path.dirname(os.path.abspath(__file__))

NOTETYPES_CONFIG = [
    {
        "nid": 11761,
        "name": "Basique-EDN-Picat-8b691",
        "css_file": "basique.txt",
        "cards": [
            {"template_id": 16172, "name": "Carte 1", "file": "basique.txt"}
        ]
    },
    {
        "nid": 11762,
        "name": "Texte à trous-EDN-Picat-918aa",
        "css_file": "trou.txt",
        "cards": [
            {"template_id": 16173, "name": "Texte à trous", "file": "trou.txt"}
        ]
    },
    {
        "nid": 11763,
        "name": "Syndrome-EDN-Picat-a47eb",
        "css_file": "syndrome.txt",
        "cards": [
            {"template_id": 16174, "name": "Carte 1", "file": "syndrome.txt"},
            {"template_id": 16175, "name": "Carte 2", "file": "syndrome2.txt"}
        ]
    },
    {
        "nid": 11764,
        "name": "Sémiologie-EDN-Picat-f482c",
        "css_file": "sémio.txt",
        "cards": [
            {"template_id": 16176, "name": "Carte 1", "file": "sémio.txt"},
            {"template_id": 16177, "name": "Carte 2", "file": "sémio2.txt"},
            {"template_id": 16178, "name": "Carte 3", "file": "sémio3.txt"}
        ]
    }
]

def find_firefox_profile():
    profiles_root = os.path.expandvars(r"%APPDATA%\Mozilla\Firefox\Profiles")
    default_release = glob.glob(os.path.join(profiles_root, "*.default-release"))
    if default_release:
        return default_release[0]
    all_profiles = glob.glob(os.path.join(profiles_root, "*.*"))
    if all_profiles:
        return all_profiles[0]
    raise FileNotFoundError("Aucun profil Firefox trouve.")

def get_firefox_session():
    profile_dir = find_firefox_profile()
    session_cookies = {}
    
    # 1. Recuperation des cookies depuis cookies.sqlite (base persistante de Firefox)
    temp_dir = tempfile.mkdtemp()
    try:
        for f in ["cookies.sqlite", "cookies.sqlite-wal", "cookies.sqlite-shm"]:
            src = os.path.join(profile_dir, f)
            if os.path.exists(src):
                shutil.copy2(src, os.path.join(temp_dir, f))
        
        db_path = os.path.join(temp_dir, "cookies.sqlite")
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("SELECT name, value FROM moz_cookies WHERE host LIKE ?", ("%ankicollab%",))
            for name, val in cur.fetchall():
                session_cookies[name] = val
            conn.close()
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    # 2. Recuperation eventuelle depuis recovery.jsonlz4 (session volatile si plus recente)
    recovery_path = os.path.join(profile_dir, "sessionstore-backups", "recovery.jsonlz4")
    if os.path.exists(recovery_path):
        try:
            with open(recovery_path, "rb") as f:
                data = lz4.block.decompress(f.read()[8:])
                session_data = json.loads(data)
                for c in session_data.get("cookies", []):
                    if "ankicollab" in c.get("host", ""):
                        name = c["name"]
                        val = c["value"]
                        if name not in session_cookies:
                            session_cookies[name] = val
                        elif name == "__Host-ankicollabsession":
                            try:
                                import base64
                                def get_jwt_exp(tok):
                                    p = tok.split(".")[1] + "=" * (-len(tok.split(".")[1]) % 4)
                                    return json.loads(base64.b64decode(p)).get("exp", 0)
                                if get_jwt_exp(val) > get_jwt_exp(session_cookies[name]):
                                    session_cookies[name] = val
                            except Exception:
                                pass
        except Exception:
            pass

    if "__Host-ankicollabsession" not in session_cookies:
        raise PermissionError("Cookie __Host-ankicollabsession introuvable dans Firefox. Connectez-vous sur ankicollab.com dans Firefox.")

    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3"
    })
    for k, v in session_cookies.items():
        s.cookies.set(k, v, domain="ankicollab.com")
        s.cookies.set(k, v, domain=".ankicollab.com")
    return s

def parse_note_type_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    def extract_section(label, text):
        pattern = rf"##\s+{re.escape(label)}.*?```(?:html|css)?\s*\r?\n(.*?)```"
        m = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return m.group(1).strip() if m else None

    return (
        extract_section("Front Template", content),
        extract_section("Back Template", content),
        extract_section("Styling", content)
    )

def deposit_all_styles():
    s = get_firefox_session()
    print("Session Firefox ankicollab chargee.")

    for nt in NOTETYPES_CONFIG:
        nid = nt["nid"]
        name = nt["name"]
        print(f"\nDepot du type de note {nid} ({name})...")

        # Recuperation de la page actuelle pour lire la map des champs proteges
        r = s.get(f"https://ankicollab.com/EditNotetype/{nid}")
        if r.status_code != 200:
            print(f"Erreur lors de la lecture de la page ({r.status_code})")
            continue

        soup = BeautifulSoup(r.text, "html.parser")
        p_map = {}
        for cb in soup.find_all("input", type="checkbox"):
            try:
                k = int(cb.get("name", ""))
                p_map[k] = cb.has_attr("checked")
            except ValueError:
                pass

        _, _, exp_css = parse_note_type_file(os.path.join(DROPBOX_DIR, nt["css_file"]))
        template_list = []
        for c in nt["cards"]:
            exp_front, exp_back, _ = parse_note_type_file(os.path.join(DROPBOX_DIR, c["file"]))
            template_list.append({
                "template_id": c["template_id"],
                "name": c["name"],
                "front": exp_front,
                "back": exp_back
            })

        payload = {
            "items": p_map,
            "styling": exp_css,
            "notetype_id": nid,
            "templates": template_list
        }

        headers = {
            "Origin": "https://ankicollab.com",
            "Referer": f"https://ankicollab.com/EditNotetype/{nid}",
            "Content-Type": "application/json"
        }

        resp = s.post("https://ankicollab.com/EditNotetype", json=payload, headers=headers)
        if resp.status_code == 200 and resp.text.strip() == "updated":
            print(f"[Succes] {name} mis a jour sur AnkiCollab.")
        else:
            print(f"[Echec] {name} -> status {resp.status_code}, reponse: {resp.text.strip()}")

    print("\nSynchronisation terminee avec succes.")

if __name__ == "__main__":
    deposit_all_styles()
