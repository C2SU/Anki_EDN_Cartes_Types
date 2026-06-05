import os
import re

directory = r"C:\Users\Pipou\Scandi&Sodi Dropbox\A Z\pole inf\ECN Anki\Addons\notes type"
files = ["basique.txt", "syndrome.txt", "syndrome2.txt", "sémio.txt", "sémio2.txt", "sémio3.txt", "trou.txt"]

NEW_CAPITALIZE_TEXT_NODE = r"""    // -- Capitaliser la première lettre de chaque champ et de chaque puce --
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

                    var hasUpperElsewhere = false;
                    var wordMatch = text.substring(index).match(/^[a-zA-ZÀ-ÿœŒæÆ]+/);
                    if (wordMatch) {
                        var word = wordMatch[0];
                        var restOfWord = word.substring(1);
                        for (var i = 0; i < restOfWord.length; i++) {
                            var char = restOfWord.charAt(i);
                            if (char === char.toUpperCase() && char !== char.toLowerCase()) {
                                hasUpperElsewhere = true;
                                break;
                            }
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

                    if (!hasUpperElsewhere && !hasNumberBefore && !precedingText.trim().endsWith('\\')) {
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

NEW_CAPITALIZE_IN_NODE = r"""    // -- Capitaliser la première lettre de chaque ENTRÉE dans les cartes liées --
    // (chaque segment séparé par <br> ou après un <kbd> doit avoir sa propre majuscule)
    try {
    var clItems = document.querySelectorAll('.cartesLiees');
    clItems.forEach(function(container) {
        // Fonction récursive pour capitaliser le premier texte d'un segment
        function capitalizeFirstInNode(node) {
            if (node.nodeType === Node.TEXT_NODE) {
                var txt = node.nodeValue;
                var m = txt.match(/[a-zA-ZÀ-ÿœŒæÆ]/);
                if (m) {
                    var idx = m.index;
                    var hasUpperElsewhere = false;
                    var wordMatch = txt.substring(idx).match(/^[a-zA-ZÀ-ÿœŒæÆ]+/);
                    if (wordMatch) {
                        var word = wordMatch[0];
                        var restOfWord = word.substring(1);
                        for (var i = 0; i < restOfWord.length; i++) {
                            var char = restOfWord.charAt(i);
                            if (char === char.toUpperCase() && char !== char.toLowerCase()) {
                                hasUpperElsewhere = true;
                                break;
                            }
                        }
                    }

                    // Récupérer tout le texte qui précède la lettre dans le même segment (depuis le dernier BR/KBD ou début)
                    var precedingText = '';
                    var current = node;
                    while (current && current !== container) {
                        var sib = current.previousSibling;
                        while (sib) {
                            if (sib.tagName === 'BR' || sib.tagName === 'KBD') break;
                            precedingText = (sib.textContent || '') + precedingText;
                            sib = sib.previousSibling;
                        }
                        if (sib && (sib.tagName === 'BR' || sib.tagName === 'KBD')) break;
                        current = current.parentNode;
                    }
                    precedingText += txt.substring(0, idx);

                    var hasNumberBefore = precedingText.match(/[0-9](?:%|‰|°|er|re|e|ème|nd|rd|th)?\s*$/i) ? true : false;

                    if (!hasUpperElsewhere && !hasNumberBefore && !precedingText.trim().endsWith('\\')) {
                        node.nodeValue = txt.substring(0, idx) + txt.charAt(idx).toUpperCase() + txt.substring(idx + 1);
                    }
                    return true;
                }
                return false;
            } else if (node.nodeType === Node.ELEMENT_NODE) {
                if (node.tagName === 'KBD' || node.tagName === 'BR' || node.tagName === 'SCRIPT' || node.tagName === 'STYLE' || node.tagName === 'SUP') return false;
                if (node.tagName === 'SPAN' && node.classList.contains('edn-nid')) return false;
                // Descendre récursivement dans les éléments inline (B, I, U, SPAN, etc.)
                for (var j = 0; j < node.childNodes.length; j++) {
                    if (capitalizeFirstInNode(node.childNodes[j])) return true;
                }
            }
            return false;
        }
        var childNodes = Array.from(container.childNodes);
        var segmentStart = true;
        for (var ci = 0; ci < childNodes.length; ci++) {
            var cnode = childNodes[ci];
            if (cnode.nodeName === 'BR') { segmentStart = true; continue; }
            if (cnode.nodeType === Node.ELEMENT_NODE && cnode.tagName === 'KBD') { segmentStart = true; continue; }
            if (cnode.nodeType === Node.ELEMENT_NODE && cnode.tagName === 'SPAN' && cnode.classList.contains('edn-nid')) continue;
            if (segmentStart) {
                if (capitalizeFirstInNode(cnode)) {
                    segmentStart = false;
                }
            }
        }
    });
    } catch(e) {}"""

for f in files:
    path = os.path.join(directory, f)
    if not os.path.exists(path):
        print(f"[--] Skip (not found): {f}")
        continue
        
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()
    
    original = content
    
    # 1. Replace elements/bullets capitalize blocks
    cap_pattern = r'    // -- Capitaliser la première lettre de chaque champ et de chaque puce --\s*\n\s*try \{[\s\S]*?\} catch\(e\) \{\}'
    content = re.sub(cap_pattern, lambda m: NEW_CAPITALIZE_TEXT_NODE, content)
    
    # 2. Replace cartesLiees capitalize blocks (if present)
    cl_pattern = r'    // -- Capitaliser la première lettre de chaque ENTRÉE dans les cartes liées --\s*\n\s*// \(chaque segment séparé par <br> ou après un <kbd> doit avoir sa propre majuscule\)\s*\n\s*try \{[\s\S]*?\} catch\(e\) \{\}'
    content = re.sub(cl_pattern, lambda m: NEW_CAPITALIZE_IN_NODE, content)
    
    if content != original:
        with open(path, "w", encoding="utf-8") as file:
            file.write(content)
        print(f"[OK] Patched: {f}")
    else:
        print(f"[--] No changes: {f}")

print("\nDone!")
