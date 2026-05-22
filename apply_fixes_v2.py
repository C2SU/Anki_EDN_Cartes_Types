import os
import re

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

js_target_re = re.compile(r"if\s*\(\s*node\.tagName\s*===\s*'SCRIPT'\s*\|\|\s*node\.tagName\s*===\s*'STYLE'\s*\|\|\s*node\.tagName\s*===\s*'A'\s*\|\|\s*node\.tagName\s*===\s*'SUP'\s*\)\s*return\s*false\s*;")
js_replacement = "if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE' || node.tagName === 'A' || node.tagName === 'SUP' || node.tagName === 'ANKI-MATHJAX' || node.tagName === 'MJX-CONTAINER' || node.tagName === 'MATH') return false;"

for filename in files_to_modify:
    filepath = os.path.join(directory, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace JS
        content = js_target_re.sub(js_replacement, content)
        
        # Insert CSS just before </style>
        if "#edn-preview-box a" not in content:
            # find all </style> and replace the first one or all of them? 
            # In anki cards, there's usually one </style> block per template (Front / Back), so we can just replace all </style> with the CSS + </style>
            content = content.replace("</style>", css_to_add + "</style>")
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Modified {filename}")
    else:
        print(f"File not found: {filename}")
