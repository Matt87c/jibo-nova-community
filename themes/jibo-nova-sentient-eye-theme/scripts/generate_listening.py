"""Generate a deterministic blue listening eye from this theme's idle PNG.

Only the inner iris is illuminated. Preserve the alpha silhouette so the
selected NOVA Sentient Eye/Orb geometry and background are unchanged.
This build tool is not shipped inside the BEacon theme ZIP.
"""
from io import BytesIO
from PIL import Image, ImageDraw, ImageFilter


def generate_listening_png(source_png):
    with Image.open(BytesIO(source_png)) as image:
        if image.format != 'PNG' or image.width != image.height:
            raise ValueError('Expected square source-eye PNG')
        original = image.convert('RGBA')

    side = original.width
    center = side // 2

    ambient = Image.new('RGBA', original.size, (0, 0, 0, 0))
    ambient_mask = Image.new('L', original.size, 0)
    draw = ImageDraw.Draw(ambient_mask)
    radius = round(side * 0.305)
    draw.ellipse((center-radius, center-radius, center+radius, center+radius), fill=70)
    ambient_mask = ambient_mask.filter(ImageFilter.GaussianBlur(max(2, round(side * 0.025))))
    ambient.paste((4, 99, 255, 0), (0, 0, side, side))
    ambient.putalpha(ambient_mask)

    halo = Image.new('RGBA', original.size, (0, 0, 0, 0))
    line = ImageDraw.Draw(halo)
    radius = round(side * 0.223)
    width = max(5, round(side * 0.014))
    bbox = (center-radius, center-radius, center+radius, center+radius)
    line.ellipse(bbox, outline=(14, 174, 255, 210), width=width)
    diffused = halo.filter(ImageFilter.GaussianBlur(max(3, round(side * 0.028))))

    result = Image.alpha_composite(original, ambient)
    result = Image.alpha_composite(result, diffused)
    result = Image.alpha_composite(result, halo)
    result.putalpha(original.getchannel('A'))
    output = BytesIO()
    result.save(output, format='PNG', optimize=True)
    return output.getvalue()
