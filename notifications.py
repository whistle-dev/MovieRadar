import discord
from datetime import datetime, timezone
from PIL import Image, ImageDraw, ImageFont
import io


async def generate_ranking_image(rank):
    img = Image.new("RGBA", (150, 150), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype("arial.ttf", 80)
    text = f"#{rank}"
    textbbox = draw.textbbox((0, 0), text, font)
    textwidth = textbbox[2] - textbbox[0]
    textheight = textbbox[3] - textbbox[1]
    x = (img.width - textwidth) // 2
    y = (img.height - textheight) // 2
    draw.text((x, y), text, font=font, fill="grey")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


async def send_to_channel(new_movies, bot, channel_id):
    channel = bot.get_channel(channel_id)
    if channel:
        for movie in new_movies:
            rank = movie["rank"]
            ranking_image = await generate_ranking_image(rank)
            file = discord.File(ranking_image, filename="ranking.png")
            embed = discord.Embed(
                title=movie["title"],
                description=f'**Year:** {movie["year"]}\n**Length:** {movie["length"]}\n**Quality:** {movie["quality"]}',
                color=discord.Color.red(),
                timestamp=datetime.now(timezone.utc),
            )
            embed.set_image(url=movie["picture_url"])
            embed.url = movie["movie_url"]
            embed.set_thumbnail(url="attachment://ranking.png")
            embed.set_footer(text="MovieRadar", icon_url=bot.user.avatar.url)

            await channel.send(embed=embed, file=file)
