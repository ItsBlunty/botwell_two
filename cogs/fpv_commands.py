from discord.ext import commands


class FpvCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userid = 152656828193439744

    @commands.command(aliases=['ts'])
    async def troubleshooting(self, ctx, query=None):
        if query is None:
            await ctx.send("Reply with one of the following after !ts\n\n!ts noprops: quick explanation of why your motors spin up on their own without props")
        elif query == "noprops":
            with open('resources/troubleshooting/noprops.txt', 'r') as f:
                noprops_content = f.read()
            await ctx.send(noprops_content)

    @commands.command()
    async def flip(self, ctx):
        await ctx.send("https://www.youtube.com/watch?v=7sSYwzVCJdA")

    @commands.command()
    async def impulserc(self, ctx):
        await ctx.send("https://github.com/ImpulseRC/ImpulseRC_Driver_Fixer/releases/download/v1_forever/ImpulseRC_Driver_Fixer.exe")

async def setup(bot):
    await bot.add_cog(FpvCommands(bot))