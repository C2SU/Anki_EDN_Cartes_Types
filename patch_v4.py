import os

directory = r"c:\Users\Pipou\Scandi&Sodi Dropbox\A Z\pole inf\ECN Anki\Addons\notes type"
files = ["basique.txt", "syndrome.txt", "syndrome2.txt", "sémio.txt", "sémio2.txt", "sémio3.txt", "trou.txt"]

old_bar_css = """.mobile .bar {
  flex-shrink: 0;
  min-width: 35px;
  max-width: 35px;
  background-size: 25px auto;
  overflow: hidden;
}

.mobile .barHider {
  flex-shrink: 0;
  min-width: 35px;
  max-width: 35px;
  background-size: 25px auto;
  overflow: hidden;
}"""

new_bar_css = """.mobile .bar {
  box-sizing: border-box;
  flex-shrink: 0;
  width: 35px;
  min-width: 35px;
  max-width: 35px;
  padding-left: 0;
  background-size: 25px auto;
  overflow: hidden;
}

.mobile .barHider {
  box-sizing: border-box;
  flex-shrink: 0;
  width: 35px;
  min-width: 35px;
  max-width: 35px;
  padding-left: 0;
  background-size: 25px auto;
  overflow: hidden;
}"""

for f in files:
    path = os.path.join(directory, f)
    if not os.path.exists(path):
        print(f"[ERROR] File not found: {f}")
        continue
        
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
        
    if old_bar_css in content:
        content = content.replace(old_bar_css, new_bar_css)
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[OK] Patched bar styles in: {f}")
    else:
        # Check if it was already updated or has different spacing
        if new_bar_css in content:
            print(f"[ALREADY PATCHED] {f}")
        else:
            print(f"[WARNING] Old bar CSS pattern not found in: {f}")

print("Done!")
