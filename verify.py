import os

d = r"c:\Users\Pipou\ECN_Anki_Addons\notes type"
files = ["basique.txt","syndrome.txt","syndrome2.txt","trou.txt","sémio.txt","sémio2.txt","sémio3.txt"]

for f in files:
    c = open(os.path.join(d, f), encoding="utf-8").read()
    checks = {
        "hasPreceding_GONE": "hasPrecedingNonSpace" not in c,
        "SUP_present": "tagName === 'SUP'" in c,
        "afterCloze_back": "afterCloze" in c,
        "overflow_css": ".mobile .items" in c,
        "dark_zoom_css": ".mobile .night_mode .card img.fullscreen-img" in c,
        "no_iOS_zoom": "if (!document.documentElement.classList.contains('mobile'))" in c,
    }
    status = " | ".join(f"{k}={'OK' if v else 'FAIL'}" for k,v in checks.items())
    print(f"{f:15s} {status}")
