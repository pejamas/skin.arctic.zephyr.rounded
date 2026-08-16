"""Repoint the video flag textures from Def_Flag_Color (colour|white) to the 3-way
Def_Flag_Color_Set (colourful|colour|white).

Run this after merging upstream. If a merge conflicts inside the flag texture lines of
Includes_Flags.xml / Includes_Images.xml, the cheapest resolution is to take UPSTREAM's
version of those hunks wholesale and then re-run this script - the change is mechanical
and idempotent, so nothing is lost by regenerating it.

Deliberately excluded: `other/` and `audiochannels/`, which stay on the 2-way
Def_Flag_Color because the colourful set has no art for them.

Usage:  python .tools/repoint_flag_color_set.py
"""

import io
import os

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "1080i")
CATS = ["resolution", "videocodec", "aspectratio", "audiocodec", "source", "hdr"]

for fn in ["Includes_Flags.xml", "Includes_Images.xml"]:
    p = os.path.join(ROOT, fn)
    with io.open(p, encoding="utf-8") as f:
        txt = f.read()
    n = 0
    for c in CATS:
        old = "flags/video/$VAR[Def_Flag_Color]/%s/" % c
        new = "flags/video/$VAR[Def_Flag_Color_Set]/%s/" % c
        n += txt.count(old)
        txt = txt.replace(old, new)
    with io.open(p, "w", encoding="utf-8", newline="") as f:
        f.write(txt)
    print("%-24s %d repointed" % (fn, n))

print("\nAlready-repointed lines are left alone, so re-running is safe.")
