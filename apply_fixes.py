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

js_target = "if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE' || node.tagName === 'A' || node.tagName === 'SUP') return false;"
js_replacement = "if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE' || node.tagName === 'A' || node.tagName === 'SUP' || node.tagName === 'ANKI-MATHJAX' || node.tagName === 'MJX-CONTAINER' || node.tagName === 'MATH') return false;"

css_target = """.nightMode #edn-preview-box, .night_mode #edn-preview-box {
background-color: #373a41;
border-color: #e5e6e9 #dfe0e4 #d0d1d5;
color: #fff;
}"""

css_replacement = """.nightMode #edn-preview-box, .night_mode #edn-preview-box {
background-color: #373a41;
border-color: #e5e6e9 #dfe0e4 #d0d1d5;
color: #fff;
}

#edn-preview-box a {
color: #365899;
text-decoration: none;
}
#edn-preview-box a:hover {
text-decoration: underline;
}
.nightMode #edn-preview-box a, .night_mode #edn-preview-box a {
color: #5b9bd5;
}"""

css_target2 = """.nightMode #edn-preview-box, .night_mode #edn-preview-box {\nbackground-color: #373a41;\nborder-color: #e5e6e9 #dfe0e4 #d0d1d5;\ncolor: #fff;\n}"""
css_replacement2 = """.nightMode #edn-preview-box, .night_mode #edn-preview-box {\nbackground-color: #373a41;\nborder-color: #e5e6e9 #dfe0e4 #d0d1d5;\ncolor: #fff;\n}\n\n#edn-preview-box a {\ncolor: #365899;\ntext-decoration: none;\n}\n#edn-preview-box a:hover {\ntext-decoration: underline;\n}\n.nightMode #edn-preview-box a, .night_mode #edn-preview-box a {\ncolor: #5b9bd5;\n}"""

for filename in files_to_modify:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace JS
        content = content.replace(js_target, js_replacement)
        
        # Replace CSS
        if "#edn-preview-box a" not in content:
            if css_target in content:
                content = content.replace(css_target, css_replacement)
            elif css_target2 in content:
                content = content.replace(css_target2, css_replacement2)
            else:
                # Fallback, just append before </style>
                content = content.replace("</style>", "\n" + css_replacement.split("}\n\n")[1] + "\n</style>")
                
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Modified {filename}")
    else:
        print(f"File not found: {filename}")
