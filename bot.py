from logic import DB_Map
import discord
from discord.ext import commands
from matplotlib.colors import is_color_like
from config import TOKEN

manager = DB_Map("database.db")
manager.create_user_table()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

@bot.event
async def on_ready():
    print(" Bot berhasil dijalankan")

@bot.command()
async def start(ctx: commands.Context):
    await ctx.send(f"Halo, {ctx.author.name}. Gunakan `!help_me` untuk melihat perintah yang tersedia.")

@bot.command()
async def help_me(ctx: commands.Context):
    await ctx.send(
        "**Daftar Perintah:**\n"
        "`!start` - Mulai bot\n"
        "`!help_me` - Lihat semua perintah\n"
        "`!set_color <warna>` - Atur warna penanda kota kamu\n"
        "`!show_city <nama_kota>` - Tampilkan kota di peta\n"
        "`!remember_city <nama_kota>` - Simpan kota favorit\n"
        "`!show_my_cities` - Tampilkan semua kota favoritmu"
    )

@bot.command()
async def set_color(ctx: commands.Context, *, color=""):
    if not is_color_like(color):
        await ctx.send("❌ Warna tidak valid. Gunakan nama seperti `blue`, `green`, atau hex code seperti `#ff0000`.")
        return
    manager.set_user_color(ctx.author.id, color)
    await ctx.send(f"✅ Warna penanda kamu telah diatur ke: `{color}`")

@bot.command()
async def show_city(ctx: commands.Context, *, city_name=""):
    if not city_name:
        await ctx.send("❌ Masukkan nama kota setelah perintah.")
        return
    manager.create_graph(f'{ctx.author.id}.png', [city_name], ctx.author.id)
    await ctx.send(file=discord.File(f'{ctx.author.id}.png'))

@bot.command()
async def remember_city(ctx: commands.Context, *, city_name=""):
    if manager.add_city(ctx.author.id, city_name):
        await ctx.send(f"✅ Kota `{city_name}` berhasil disimpan.")
    else:
        await ctx.send("❌ Kota tidak ditemukan. Pastikan nama kota sesuai dan dalam bahasa Inggris.")

@bot.command()
async def show_my_cities(ctx: commands.Context):
    cities = manager.select_cities(ctx.author.id)
    if cities:
        path = f'{ctx.author.id}_cities.png'
        manager.create_graph(path, cities, ctx.author.id)
        await ctx.send(file=discord.File(path))
    else:
        await ctx.send("🚫 Kamu belum menyimpan kota apa pun.")

if __name__ == "__main__":
    bot.run(TOKEN)
