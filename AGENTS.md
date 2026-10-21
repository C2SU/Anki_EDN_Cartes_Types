# Directives et Procedure de Depot des Styles de Cartes sur AnkiCollab

## 1. Contexte et Objectif
Ce dossier contient les definitions sources (HTML/CSS) des types de cartes du deck Anki EDN.

> **ATTENTION - CONDITION STRICTE** :
> Ne JAMAIS lancer le script de mise à jour ni pusher sur Git de manière automatique ou implicite.
> Toute actualisation sur AnkiCollab ou GitHub requiert impérativement une **demande expresse** de l'utilisateur.
> L'invocation de la commande `/ankicollab-notetypes` vaut ordre formel de déploiement vers AnkiCollab.

Lorsqu'une demande expresse de l'utilisateur requiert de mettre a jour ("deposer" / "update") les styles de cartes sur AnkiCollab (via `https://ankicollab.com/ManageDecks`), la mise a jour doit obligatoirement utiliser la session authentifiee du navigateur Firefox.

## 2. Extraction de la Session Firefox
AnkiCollab est protege par Cloudflare et utilise une session HTTP securisee.

1. **Localisation du profil Firefox** :
   Chemin : `%APPDATA%\Mozilla\Firefox\Profiles\*.default-release`
2. **Cookie de session `__Host-ankicollabsession`** :
   Ce cookie de session volatile se trouve en memoire ou dans le fichier de sauvegarde de session :
   `sessionstore-backups\recovery.jsonlz4`.
   Decompression : `lz4.block.decompress(data[8:])` (apres avoir ignore les 8 premiers octets du magic header `mozLz40\0`).
3. **Cookie Cloudflare `cf_clearance`** :
   Stocke dans le fichier SQLite :
   `cookies.sqlite` (copier temporairement la base et ses fichiers WAL/SHM pour eviter les verrous d'ecriture).

## 3. Correspondance Fichiers Dropbox vers Types de Notes AnkiCollab

Tableau des correspondances :

| Type de note AnkiCollab | ID Type | Fichier CSS | Cartes / Templates | ID Template | Fichier Template |
| :--- | :--- | :--- | :--- | :--- | :--- |
| Basique-EDN-Picat-8b691 | 11761 | basique.txt | Carte 1 | 16172 | basique.txt |
| Texte a trous-EDN-Picat-918aa | 11762 | trou.txt | Texte a trous | 16173 | trou.txt |
| Syndrome-EDN-Picat-a47eb | 11763 | syndrome.txt | Carte 1<br>Carte 2 | 16174<br>16175 | syndrome.txt<br>syndrome2.txt |
| Semiologie-EDN-Picat-f482c | 11764 | semio.txt | Carte 1<br>Carte 2<br>Carte 3 | 16176<br>16177<br>16178 | semio.txt<br>semio2.txt<br>semio3.txt |

## 4. Structure des Fichiers .txt
Chaque fichier texte contient trois sections balisees par des blocs de code Markdown :
- `## Front Template` : contenu HTML du recto
- `## Back Template` : contenu HTML du verso
- `## Styling` : contenu CSS de la feuille de style commune

## 5. Protocole de Soumission HTTP (API AnkiCollab)
Pour chaque type de note :

1. **Effectuer un GET préalable** sur `https://ankicollab.com/EditNotetype/<ID>` pour recuperer l'etat des cases a cocher des champs proteges (`items: { <field_id>: boolean }`).
2. **Effectuer un POST** sur `https://ankicollab.com/EditNotetype` :
   - **Headers requis** :
     - `Origin: https://ankicollab.com`
     - `Referer: https://ankicollab.com/EditNotetype/<ID>`
     - `Content-Type: application/json`
     - `User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:142.0) Gecko/20100101 Firefox/142.0`
   - **Payload JSON** :
     ```json
     {
       "items": { "70435": false, "70441": true, ... },
       "styling": "<css_content>",
       "notetype_id": 11761,
       "templates": [
         {
           "template_id": 16172,
           "name": "Carte 1",
           "front": "<front_html>",
           "back": "<back_html>"
         }
       ]
     }
     ```
3. **Reponse attendue** : Statut HTTP `200` avec corps de reponse brut `updated`.

## 6. Execution Rapide
Un script autonome est disponible a la racine du dossier :
```powershell
python "c:\Users\Pipou\Scandi&Sodi Dropbox\A Z\pole inf\ECN Anki\Addons\notes type\deposit_to_ankicollab.py"
```

## 7. Verification et Affichage
Apres soumission, verifier que le contenu retourne par `GET /EditNotetype/<ID>` correspond strictement au contenu local.
Pour ouvrir la page de gestion dans Firefox pour confirmation visuelle de l'utilisateur :
```powershell
Start-Process "C:\Program Files\Mozilla Firefox\firefox.exe" "https://ankicollab.com/ManageDecks"
```
