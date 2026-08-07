from PIL import Image, ImageDraw
import os

out_dir = r"E:\skin.arctic.zephyr.rounded\media\common"
os.makedirs(out_dir, exist_ok=True)


def make_ring(size, stroke, radius, filename, outer_inset=0):
    mask = Image.new("L", (size, size), 0)
    draw = ImageDraw.Draw(mask)
    o = outer_inset
    draw.rounded_rectangle(
        [o, o, size - 1 - o, size - 1 - o],
        radius=max(0, radius - o),
        fill=255,
    )
    inset = o + stroke
    inner_r = max(0, radius - inset)
    draw.rounded_rectangle(
        [inset, inset, size - 1 - inset, size - 1 - inset],
        radius=inner_r,
        fill=0,
    )
    img = Image.new("RGBA", (size, size), (255, 255, 255, 255))
    img.putalpha(mask)
    path = os.path.join(out_dir, filename)
    img.save(path, "PNG")
    print("wrote", path, "stroke", stroke, "outer_inset", outer_inset)


# Ring on the texture edge (flush when pad matches poster pad_image=10)
make_ring(64, 3, 14, "selectbox_thin.png", outer_inset=0)
print("done")
