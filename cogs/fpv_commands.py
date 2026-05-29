import random

from discord.ext import commands


class FpvCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userid = 152656828193439744

    @commands.command()
    async def noprops(self, ctx):
        with open('resources/troubleshooting/noprops.txt', 'r') as f:
            noprops_content = f.read()
        await ctx.send(noprops_content)

    @commands.command()
    async def flip(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=7sSYwzVCJdA")

    @commands.command()
    async def flipout(self, ctx):
        await ctx.send("https://media0.giphy.com/media/AAIa8kYrPUcuQQejMN/giphy.gif?cid=5e2148864a8316e7d2a225196aa0b3b603e269f0133310b8&rid=giphy.gif&ct=g")

    @commands.command()
    async def impulserc(self, ctx):
        await ctx.send("https://github.com/ImpulseRC/ImpulseRC_Driver_Fixer/releases/download/v1_forever/ImpulseRC_Driver_Fixer.exe")

    @commands.command()
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def bardwell(self, ctx):
        with open('resources/bardwellgifs.txt', 'r') as f:
            gifs = [line.strip() for line in f if line.strip()]
        await ctx.send(random.choice(gifs))

    @bardwell.error
    async def bardwell_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"Slow down! Try `!bardwell` again in {error.retry_after:.0f}s.",
                delete_after=5,
            )
        else:
            raise error

async def setup(bot):
    await bot.add_cog(FpvCommands(bot))