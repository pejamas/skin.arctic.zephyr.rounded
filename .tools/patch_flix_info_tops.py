from pathlib import Path
import re

p = Path(__file__).resolve().parents[1] / "1080i" / "script-skinshortcuts-includes.xml"
text = p.read_text(encoding="utf-8")
orig = text

# Revert experimental offsets from prior attempt
text = text.replace("\n\t\t\t\t<top>-440</top>", "")
text = text.replace("\n\t\t\t\t<top>440</top>", "")

if text == orig:
    print("NO CHANGES")
else:
    p.write_text(text, encoding="utf-8")
    print("reverted tops in", p)
    print("remaining -440", text.count("<top>-440</top>"))
    print("remaining 440", text.count("<top>440</top>"))
