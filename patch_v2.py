"""
Patch v2 — Améliorations des styles de notes Anki
===================================================
1. Majuscule auto : fonctionne même après des caractères spéciaux (◊, //, etc.)
   - hasPrecedingNonSpace ne bloque plus la capitalisation
2. Exception <sup>e</sup> : ne pas capitaliser le "e" dans <sup>
3. Cloze : ne pas capitaliser le mot APRÈS un cloze ({{c1::je}} suis → Je suis)
4. Thème sombre : fond du zoom d'image sombre (pas blanc)
5. Pas de zoom image sur iOS (mobile)
6. iOS : overflow texte/tableaux dans les cadres
"""

import os
import re

directory = r"c:\Users\Pipou\ECN_Anki_Addons\notes type"
files = ["basique.txt", "syndrome.txt", "syndrome2.txt", "sémio.txt", "sémio2.txt", "sémio3.txt", "trou.txt"]

# =====================================================================
# NEW capitalize function (Front Template version — compact, one block)
# =====================================================================
# This version:
# - Capitalizes first letter even after special chars (◊, //, etc.)
# - Skips <SUP> elements (exception for <sup>e</sup>)
# - Does NOT auto-capitalize the word right after a cloze deletion
#   (the cloze itself gets capitalized since it's the "first letter")

NEW_CAPITALIZE_FRONT = r"""    // -- Capitaliser la première lettre de chaque champ et de chaque puce --
    try {
    var elementsToCapitalize = document.querySelectorAll('.items, .items li');
    elementsToCapitalize.forEach(function (item) {
        var foundLetter = false;
        var afterCloze = false;

        function capitalizeFirstTextNode(node) {
            if (foundLetter) return true;

            if (node.nodeType === Node.TEXT_NODE) {
                var text = node.nodeValue;
                var match = text.match(/[a-zA-ZÀ-ÿœŒæÆ]/);
                if (match) {
                    var index = match.index;

                    // Si on est juste après un cloze, ne pas capitaliser ce mot
                    // mais mettre en minuscule si c'est une majuscule isolée
                    if (afterCloze) {
                        var char = text.charAt(index);
                        if (char === char.toUpperCase() && char !== char.toLowerCase()) {
                            // Vérifier si c'est suivi d'une minuscule (= majuscule isolée à corriger)
                            if (index + 1 < text.length) {
                                var next = text.charAt(index + 1);
                                if (next === next.toLowerCase() && next !== next.toUpperCase()) {
                                    node.nodeValue = text.substring(0, index) + char.toLowerCase() + text.substring(index + 1);
                                }
                            }
                        }
                        foundLetter = true;
                        return true;
                    }

                    var followedByUpper = false;
                    if (index + 1 < text.length) {
                        var nextChar = text.charAt(index + 1);
                        if (nextChar === nextChar.toUpperCase() && nextChar !== nextChar.toLowerCase()) {
                            followedByUpper = true;
                        }
                    }

                    // Récupérer tout le texte qui précède la lettre dans le même élément
                    var precedingText = '';
                    var current = node;
                    while (current && current !== item) {
                        var sib = current.previousSibling;
                        while (sib) {
                            precedingText = (sib.textContent || '') + precedingText;
                            sib = sib.previousSibling;
                        }
                        current = current.parentNode;
                    }
                    precedingText += text.substring(0, index);

                    var hasNumberBefore = precedingText.match(/[0-9](?:%|‰|°|er|re|e|ème|nd|rd|th)?\s*$/i) ? true : false;

                    if (!followedByUpper && !hasNumberBefore) {
                        node.nodeValue = text.substring(0, index) + text.charAt(index).toUpperCase() + text.substring(index + 1);
                    }
                    foundLetter = true;
                    return true;
                }
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE' || node.tagName === 'A' || node.tagName === 'SUP' || node.tagName === 'ANKI-MATHJAX' || node.tagName === 'MJX-CONTAINER' || node.tagName === 'MATH') return false;
                // Détecter les spans cloze pour ne pas capitaliser le mot suivant
                if (node.classList && node.classList.contains('cloze')) {
                    if (!foundLetter) {
                        // Si le cloze est le premier élément, capitaliser le texte à l'intérieur
                        for (var ci = 0; ci < node.childNodes.length; ci++) {
                            if (capitalizeFirstTextNode(node.childNodes[ci])) break;
                        }
                    }
                    afterCloze = true;
                    return false;
                }
                for (var i = 0; i < node.childNodes.length; i++) {
                    if (capitalizeFirstTextNode(node.childNodes[i])) return true;
                }
            }
            return false;
        }
        capitalizeFirstTextNode(item);
    });
    } catch(e) {}"""

# =====================================================================
# NEW capitalize function (Back Template version — full, with cloze fix)
# =====================================================================
# Same as above but also handles cloze: after a .cloze span,
# the next word should NOT be uppercased (it's not the first word)

NEW_CAPITALIZE_BACK = NEW_CAPITALIZE_FRONT


def replace_capitalize_block(content, new_block):
    """Replace the capitalize block in a script section."""
    pattern = r'    // -- Capitaliser la première lettre de chaque champ et de chaque puce --\s*\n\s*try \{[\s\S]*?\} catch\(e\) \{\}'
    return re.sub(pattern, new_block, content)


def fix_dark_mode_zoom_css(content):
    """
    Fix: in dark mode, the fullscreen image zoom should NOT have a white background.
    The .nightMode rule already has dark bg, but the base .fullscreen-img has white bg
    which can flash. We ensure the nightMode rule is properly applied.
    This is already correct in CSS — the issue is that on some renderers the
    .nightMode/.night_mode selector might not apply. We add .mobile .night_mode variant.
    """
    # The existing nightMode rule is correct but we need to make sure
    # the CSS specificity covers all cases
    old_night_zoom = ".nightMode .card img.fullscreen-img, .night_mode .card img.fullscreen-img {"
    new_night_zoom = ".nightMode .card img.fullscreen-img, .night_mode .card img.fullscreen-img, .mobile .night_mode .card img.fullscreen-img {"
    content = content.replace(old_night_zoom, new_night_zoom)
    return content


def disable_zoom_on_ios(content):
    """
    Remove image zoom click handler on iOS/mobile.
    Wrap the click listener in a !mobile check.
    """
    # In the JS: replace the img click handler to be desktop-only
    # Current: img.addEventListener('click', function(e) { ... toggle fullscreen ... });
    # New: wrap in !mobile check
    
    old_click = """        img.addEventListener('click', function(e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            e.preventDefault();
            this.classList.toggle('fullscreen-img');
            this.style.cursor = this.classList.contains('fullscreen-img') ? 'zoom-out' : 'zoom-in';
        });"""
    
    new_click = """        if (!document.documentElement.classList.contains('mobile')) {
            img.addEventListener('click', function(e) {
                e.stopPropagation();
                e.stopImmediatePropagation();
                e.preventDefault();
                this.classList.toggle('fullscreen-img');
                this.style.cursor = this.classList.contains('fullscreen-img') ? 'zoom-out' : 'zoom-in';
            });
        }"""
    
    content = content.replace(old_click, new_click)
    
    # Also handle the variant with different indentation (trou.txt uses less indentation)
    old_click_alt = """    img.addEventListener('click', function(e) {
        e.stopPropagation();
        e.stopImmediatePropagation();
        e.preventDefault();
        this.classList.toggle('fullscreen-img');
        this.style.cursor = this.classList.contains('fullscreen-img') ? 'zoom-out' : 'zoom-in';
    });"""
    
    new_click_alt = """    if (!document.documentElement.classList.contains('mobile')) {
        img.addEventListener('click', function(e) {
            e.stopPropagation();
            e.stopImmediatePropagation();
            e.preventDefault();
            this.classList.toggle('fullscreen-img');
            this.style.cursor = this.classList.contains('fullscreen-img') ? 'zoom-out' : 'zoom-in';
        });
    }"""
    
    content = content.replace(old_click_alt, new_click_alt)
    
    return content


def fix_ios_overflow(content):
    """
    Fix iOS text/table overflow in field containers.
    Add overflow-x rules to .items and .section for mobile.
    """
    # Add after existing .items rule
    overflow_css = """
.mobile .items {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
  max-width: 100%;
  word-wrap: break-word;
  overflow-wrap: break-word;
}

.mobile .section {
  max-width: 90%;
  overflow-x: hidden;
}

.mobile .items table {
  max-width: 100%;
  display: block;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}"""
    
    # Insert after the .items { ... } block
    # Find the closing of .items block
    items_pattern = r'(\.items\s*\{\s*\n[^}]+\})'
    match = re.search(items_pattern, content)
    if match and '.mobile .items {' not in content:
        pos = match.end()
        content = content[:pos] + "\n" + overflow_css + content[pos:]
    
    return content


def determine_template_type(content, section):
    """Determine if a section is front or back template"""
    # Find position of "## Back Template"
    back_pos = content.find("## Back Template")
    if back_pos == -1:
        return "front"
    
    # Find position of this capitalize block
    cap_pos = content.find(section)
    if cap_pos < back_pos:
        return "front"
    return "back"


for f in files:
    path = os.path.join(directory, f)
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    original = content
    
    # 1. Replace capitalize blocks
    # We need to handle both front and back templates separately
    # Front: standard capitalize (no cloze handling needed on front for basique/syndrome/sémio)
    # Back: capitalize with cloze fix
    
    # Strategy: find all capitalize blocks and replace them in order
    # The first one is in the Front Template, the rest are in the Back Template
    
    cap_pattern = r'    // -- Capitaliser la première lettre de chaque champ et de chaque puce --\s*\n\s*try \{[\s\S]*?\} catch\(e\) \{\}'
    matches = list(re.finditer(cap_pattern, content))
    
    back_template_pos = content.find("## Back Template")
    
    # Replace from last to first to preserve positions
    for m in reversed(matches):
        if back_template_pos != -1 and m.start() > back_template_pos:
            # This is in the back template
            if f == "trou.txt":
                # trou.txt uses cloze — need the cloze-aware version
                content = content[:m.start()] + NEW_CAPITALIZE_BACK + content[m.end():]
            else:
                content = content[:m.start()] + NEW_CAPITALIZE_BACK + content[m.end():]
        else:
            # This is in the front template
            if f == "trou.txt":
                # trou.txt front also shows cloze
                content = content[:m.start()] + NEW_CAPITALIZE_FRONT + content[m.end():]
            else:
                content = content[:m.start()] + NEW_CAPITALIZE_FRONT + content[m.end():]
    
    # 2. Fix dark mode zoom background
    content = fix_dark_mode_zoom_css(content)
    
    # 3. Disable image zoom on iOS
    content = disable_zoom_on_ios(content)
    
    # 4. Fix iOS overflow
    content = fix_ios_overflow(content)
    
    if content != original:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[OK] Patched: {f}")
    else:
        print(f"[--] No changes: {f}")

print("\nDone!")
