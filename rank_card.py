
import io
from PIL import Image, ImageDraw, ImageFont

async def generate_rank_card(user, xp, level):
    img = Image.new("RGB", (600, 150), color=(54, 57, 63))
    draw = ImageDraw.Draw(img)

    font = ImageFont.load_default()
    draw.text((20, 20), f"User: {user.name}", font=font, fill=(255, 255, 255))
    draw.text((20, 50), f"Level: {level}", font=font, fill=(255, 255, 0))
    draw.text((20, 80), f"XP: {xp}", font=font, fill=(0, 255, 255))

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
