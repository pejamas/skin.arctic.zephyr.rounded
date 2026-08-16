"""Import an Arctic Fuse `flags` folder into the paths Arctic Zephyr Rounded expects,
as loose PNGs that override media/Textures.xbt.

Imports two of Fuse's three sets:
    color    -> media/flags/video/color/...     (the skin's existing "Colour" mode)
    colorful -> media/flags/video/colorful/...  (the added third mode)

Fuse's `monochrome` set is partial (4 folders) and Rounded's `white` set is tinted at
runtime via colordiffuse, so the bundled white art is left alone.

The colorful set is SEEDED from the color set first, then overlaid with colorful's own
art. This matters: `colorful` does not exist inside Textures.xbt, so unlike color/white
a missing loose file has no bundle to fall back to and would simply render blank.

Only the video flags are imported for colorful (resolution, videocodec, aspectratio,
audiocodec, source, hdr) - matching 1080i/Includes_Defs.xml's Def_Flag_Color_Set.
mpaa/rating/lang stay on Def_Flag_Color (color|white) and keep the bundled art.

Usage:  python .tools/import_fuse_flags.py [--dry-run]
Undo:   delete media/flags/ and revert the XML changes
"""

import os
import shutil
import sys

SRC = r"C:\Users\pejam\OneDrive\Desktop\flags"
DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "media", "flags")

DRY = "--dry-run" in sys.argv
copied = skipped = 0


def put(src, dst):
    global copied, skipped
    if not os.path.isfile(src):
        print("    MISSING  %s" % os.path.relpath(src, SRC))
        skipped += 1
        return
    if not DRY:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copy2(src, dst)
    copied += 1


def copy_folder(s, d):
    sd = os.path.join(SRC, s.replace("/", os.sep))
    if not os.path.isdir(sd):
        print("    MISSING DIR  %s" % s)
        return
    names = [n for n in os.listdir(sd) if n.lower().endswith(".png")]
    print("  %-26s -> %-34s (%d)" % (s, d, len(names)))
    for n in names:
        put(os.path.join(sd, n), os.path.join(DST, d.replace("/", os.sep), n))


def copy_file(s, d):
    print("  %-26s -> %s" % (s, d))
    put(os.path.join(SRC, s.replace("/", os.sep)), os.path.join(DST, d.replace("/", os.sep)))


def import_color(dest_set):
    """Fuse `color` -> video/<dest_set>/ plus the rating tree (color only)."""
    for s, d in [("resolution",  "resolution"),
                 ("aspectratio", "aspectratio"),
                 ("audio",       "audiocodec"),
                 ("source",      "videocodec"),
                 ("hdr",         "hdr")]:
        copy_folder("color/" + s, "video/%s/%s" % (dest_set, d))
    # Rounded emits "dts-x"; Fuse ships "dts_x".
    copy_file("color/audio/dts_x.png", "video/%s/audiocodec/dts-x.png" % dest_set)
    # Rounded's source/ holds physical-media icons only, not codecs.
    copy_file("color/source/bluray.png", "video/%s/source/bluray.png" % dest_set)
    copy_file("color/source/3dbd.png",   "video/%s/source/3d.png" % dest_set)
    copy_file("color/source/dvd.png",    "video/%s/source/dvd.png" % dest_set)


def import_colorful():
    """Fuse `colorful` overlaid on top of the color seed."""
    for s, d in [("resolution",  "resolution"),
                 ("aspectratio", "aspectratio"),
                 ("audio",       "audiocodec"),
                 ("source",      "videocodec")]:
        copy_folder("colorful/" + s, "video/colorful/" + d)
    copy_file("colorful/audio/dts_x.png", "video/colorful/audiocodec/dts-x.png")
    # colorful keeps its HDR and physical-media icons in other/, not in dedicated folders.
    for n in ["dolbyvision", "hdr10", "hdr10plus", "hlg"]:
        copy_file("colorful/other/%s.png" % n, "video/colorful/hdr/%s.png" % n)
    copy_file("colorful/other/bluray.png",     "video/colorful/source/bluray.png")
    copy_file("colorful/other/4K_BluRay.png",  "video/colorful/source/ultrahd.png")
    copy_file("colorful/other/3D.png",         "video/colorful/source/3d.png")
    copy_file("colorful/other/dvd.png",        "video/colorful/source/dvd.png")
    # No colorful hddvd art; the color seed above covers that slot.

    # Kodi reports UHD as either "4K" or "2160" depending on the stream, so both names get
    # requested. Fuse's 4k.png is a bare gold "4K" that does not match the set's house style
    # (HD1080 / HD720 / SD480 - a big label plus a small descriptor); 2160.png does
    # ("4K ULTRA 2160p"). Alias 4K to it so the flag looks the same whichever name is asked
    # for. 8k.png is the remaining outlier - Fuse ships no house-style 8K art.
    copy_file("colorful/resolution/2160.png", "video/colorful/resolution/4K.png")


def import_ratings():
    """Rounded nests each rating provider in its own folder. Colour set only."""
    for name, sub in [("imdb", "imdb/imdb"), ("tmdb", "tmdb/tmdb"), ("trakt", "trakt/trakt"),
                      ("letterboxd", "letterboxd/letterboxd"), ("mdblist", "mdblist/mdblist"),
                      ("metacritic", "metacritic/mc")]:
        copy_file("color/ratings/%s.png" % name, "rating/color/%s.png" % sub)


# Categories where matching a single canvas aspect cannot work, because the art mixes
# layouts: Fuse's resolution set has one-line wordmarks (HD1080, ~3.5:1) next to two-line
# badges (4K ULTRA 2160p, ~1.7:1). Any single aspect either letterboxes the wordmarks to
# half height or blows them out to 120px wide. These are fitted into a box instead, in
# render pixels at the row's 36px flag height.
# Nothing is fitted for the colour/white sets - they keep the bundled-aspect
# normalisation, because their controls are the skin's original fixed/auto slots.
FIT = {}

# The colourful flag controls use width="auto" (see the "* Colourful" controls in
# Includes_Flags.xml), so the slot hugs the texture and the gap between two flags is
# exactly A's right margin + B's left margin. Fitting every category the same way makes
# that sum constant, which is what makes the row evenly spaced. The colour/white sets are
# NOT fitted: their slots are fixed widths tuned around the bundled art, so they keep the
# bundled-aspect normalisation instead.
FIT_COLORFUL = {
    "resolution":  dict(max_h=32, max_w=84, pad=8),
    "videocodec":  dict(max_h=32, max_w=84, pad=8),
    "hdr":         dict(max_h=32, max_w=90, pad=8),
    "aspectratio": dict(max_h=32, max_w=80, pad=8),
    "audiocodec":  dict(max_h=32, max_w=92, pad=8),
    "source":      dict(max_h=32, max_w=84, pad=8),
}

# Cell width = max_w + 2*pad. These MUST match the <width> of the corresponding
# "* Colourful" controls in Includes_Flags.xml, or the row spaces unevenly again.
CELLS = dict((c, v["max_w"] + 2 * v["pad"]) for c, v in
             list(FIT.items()) + list(FIT_COLORFUL.items()))

FLAG_H = 36.0     # rendered height of a flag; see Def_Flag_Image_Without_Label
MIN_MARGIN = 8    # rendered px of transparent margin guaranteed on each side


def fit_category(cat_dir, files, max_h, max_w, pad):
    """Scale each icon's ink to fit a max_w x max_h box on a UNIFORM cell canvas.

    Every file in the category ends up the same rendered size - (max_w + 2*pad) wide by
    FLAG_H tall - with the ink centred inside it. The matching control in
    Includes_Flags.xml is then given that exact width as a FIXED value.

    Why fixed and not width="auto": on image controls this Kodi build does not size the
    slot to the texture, it falls back to the `max` of the auto range. Raising the caps
    therefore widened every slot and blew the gaps out. A uniform cell plus a matching
    fixed width sidesteps auto entirely, so the layout is deterministic: each flag owns an
    equal-pitch cell and the row reads evenly regardless of how auto behaves.

    The box keeps a wide one-line wordmark from towering over a compact two-line badge.
    All values are render pixels at FLAG_H, converted back to source pixels per file, so
    nothing is resampled - the ink is only re-canvased.
    """
    from PIL import Image

    cell_w = max_w + 2 * pad
    n_cat = 0
    for n in files:
        p = os.path.join(cat_dir, n)
        img = Image.open(p).convert("RGBA")
        bbox = img.getbbox()
        if bbox:
            img = img.crop(bbox)
        iw, ih = img.size
        a = iw / float(ih)

        ink_h = min(max_h, max_w / a)          # rendered ink height
        scale = ih / ink_h                     # source px per rendered px
        cw = int(round(cell_w * scale))
        ch = int(round(FLAG_H * scale))

        canvas = Image.new("RGBA", (max(cw, iw), max(ch, ih)), (0, 0, 0, 0))
        canvas.paste(img, ((canvas.size[0] - iw) // 2, (canvas.size[1] - ih) // 2))
        if not DRY:
            canvas.save(p, "PNG")
        n_cat += 1

    print("  %-9s %-12s %3d files -> ink fits %dx%d, uniform %dpx cell"
          % (os.path.basename(os.path.dirname(cat_dir)), os.path.basename(cat_dir),
             n_cat, max_w, max_h, cell_w))
    return n_cat


def normalize_to_bundle():
    """Pad imported icons onto the canvas aspect the SKIN'S OWN art uses, per category.

    The flags row is a horizontal grouplist with itemgap 0 and a fixed slot width per
    category (Includes_Flags.xml). Each texture draws left-aligned with <aspectratio>keep
    against a 36px height, so the leftover slot space IS the gap between flags. Even gaps
    therefore require the art to render at the width the slot was designed around.

    That target is NOT uniform across the row, and it is not guessed: it is read straight
    out of media/Textures.xbt, whose art is tuned per category to nearly fill its slot -
    resolution 1.64:1 (59px in an auto<=80 slot), videocodec 2.06:1 (74px in a 100 slot),
    hdr 2.71:1 (98px in a min-110 slot), and so on. Fuse art dropped in at its own aspect
    renders a different width and leaves a different gap, which is what threw the spacing
    out. Normalising both imported sets to the bundled aspect keeps every slot filled the
    way the skin intends, so colour, colourful and the stock white set all line up.

    Content is cropped to its alpha bbox then centred - no resampling, nothing cropped,
    idempotent on re-run.
    """
    from PIL import Image
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from xbt_list import median_aspect_by_category

    ref = median_aspect_by_category("flags/video/color/")
    if not ref:
        raise SystemExit("no reference aspects read from Textures.xbt")

    total = 0
    for dest_set in ["color", "colorful"]:
        root = os.path.join(DST, "video", dest_set)
        if not os.path.isdir(root):
            continue
        for cat in sorted(os.listdir(root)):
            cat_dir = os.path.join(root, cat)
            files = [n for n in os.listdir(cat_dir) if n.lower().endswith(".png")]
            if not files:
                continue

            # Measure this set's own ink shape for the category.
            inks = []
            for n in files:
                with Image.open(os.path.join(cat_dir, n)) as im:
                    b = im.convert("RGBA").getbbox()
                    if b and b[3] > b[1]:
                        inks.append((b[2] - b[0]) / float(b[3] - b[1]))
            inks.sort()
            ink = inks[len(inks) // 2] if inks else None

            box = FIT.get(cat)
            if box is None and dest_set == "colorful":
                box = FIT_COLORFUL.get(cat)
            if box is not None:
                total += fit_category(cat_dir, files, **box)
                continue

            aspect = ref.get(cat)
            note = "bundled"
            # If the imported art is much wider than the bundled badge, padding it to the
            # bundled aspect letterboxes it - the ink ends up half the height of its
            # neighbours. Fuse's resolution wordmarks (~3.3:1) against a 1.64:1 bundled
            # badge is exactly that case, so follow the art instead and widen the slot.
            if ink and aspect and ink > aspect * 1.5:
                aspect, note = ink, "ink (bundled %.2f too narrow)" % ref[cat]
            elif aspect is None:
                aspect, note = ink, "ink (no bundled reference)"
            if not aspect:
                continue

            n_cat = 0
            for n in files:
                p = os.path.join(cat_dir, n)
                img = Image.open(p).convert("RGBA")
                bbox = img.getbbox()
                if bbox:
                    img = img.crop(bbox)
                w, h = img.size
                if w / float(h) < aspect:
                    cw, ch = int(round(h * aspect)), h
                else:
                    cw, ch = w, int(round(w / aspect))
                # width="auto" + itemgap 0 means transparent margin inside the art is the
                # only thing separating one flag from the next, and art whose ink runs the
                # full canvas width would butt against its neighbour. Guarantee the gap.
                cw = max(cw, w + 2 * int(round(MIN_MARGIN * ch / FLAG_H)))
                canvas = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
                canvas.paste(img, ((cw - w) // 2, (ch - h) // 2))
                if not DRY:
                    canvas.save(p, "PNG")
                n_cat += 1
            total += n_cat
            print("  %-9s %-12s %3d files -> %.3f:1 %-30s (%.0fpx at height 36)"
                  % (dest_set, cat, n_cat, aspect, note, aspect * 36))
    print("  normalized %d files against Textures.xbt" % total)


print("[color]")
import_color("color")
print("\n[colorful: seed from color]")
import_color("colorful")
print("\n[colorful: overlay]")
import_colorful()
print("\n[ratings]")
import_ratings()

print("\n[normalize both sets to the bundled art in Textures.xbt]")
normalize_to_bundle()

print("\n[cell widths - these must match the '* Colourful' <width> values in Includes_Flags.xml]")
for c in sorted(CELLS):
    print("  %-12s %3dpx" % (c, CELLS[c]))

print("\n%s: %d copied, %d skipped -> %s" % ("DRY RUN" if DRY else "DONE", copied, skipped, DST))

# Not imported, and why:
#   mpaa      - Fuse "USA NC-17.png" vs Rounded "nc-17.png"/"bbfc_u_certificate_uk.png";
#               zero filename overlap. See 1080i/Includes_MPAA.xml.
#   language  - Rounded wants flags/lang/{32x32,80x80,dialog}/ with no color split.
#   channels  - Rounded draws one channel.png plus a text label, not per-count art.
#   ratings   - rtfresh/rtrotten/popcorn have no unambiguous mapping onto Rounded's
#               rottentomatoes/{hot,tomato,rt,good,notgood}.png; left on the bundled art.
#   status,trakt,root PNGs - no equivalent in this skin.
