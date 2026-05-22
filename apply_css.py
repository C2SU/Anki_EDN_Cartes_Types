import os

directory = r"C:\Users\Pipou\Scandi&Sodi Dropbox\A Z\pole inf\ECN Anki\Addons\notes type"
files_to_modify = [
    "basique.txt",
    "trou.txt",
    "sémio.txt",
    "sémio2.txt",
    "sémio3.txt",
    "syndrome.txt",
    "syndrome2.txt"
]

css_to_add = """
/* Correction des liens dans la preview */
#edn-preview-box a {
    color: #365899;
    text-decoration: none;
}
#edn-preview-box a:hover {
    text-decoration: underline;
}
.nightMode #edn-preview-box a, .night_mode #edn-preview-box a {
    color: #5b9bd5;
}
"""

for filename in files_to_modify:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Insert CSS
        if "#edn-preview-box a" not in content:
            # We look for the preview-verso block
            target = ".preview-verso {\n  font-size: 14px;\n}"
            if target in content:
                content = content.replace(target, target + "\n" + css_to_add)
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(content)
                print(f"Added CSS to {filename}")
            else:
                # Try CRLF
                target_crlf = ".preview-verso {\n  font-size: 14px;\n}".replace("\n", "\r\n")
                if target_crlf in content:
                    content = content.replace(target_crlf, target_crlf + "\r\n" + css_to_add.replace("\n", "\r\n"))
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(content)
                    print(f"Added CSS (CRLF) to {filename}")
                else:
                    print(f"Target not found in {filename}")
        else:
            print(f"CSS already in {filename}")
    else:
        print(f"File not found: {filename}")
