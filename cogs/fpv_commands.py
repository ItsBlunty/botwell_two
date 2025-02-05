from discord.ext import commands


class FpvCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.userid = 152656828193439744

    @commands.command(aliases=['ts'])
    async def troubleshooting(self, ctx, query=None):
        if query is None:   
            await ctx.send("Reply with one of the following after !ts\n\n!ts flip: guide for fixing a flipping quadcopter\n!ts impulserc: link to impulserc driver fixer\n!ts noprops: quick explanation of why your motors spin up on their own without props")
        elif query == "flip" or query == "flip on arm" or query == "flip on takeoff" or query == "flip out":
            with open('resources/troubleshooting/flip.txt', 'r') as f:
                flip_content = f.read()
            await ctx.send(flip_content)
        elif query == "impulserc" or query == "driver fixer" or query == "driverfixer" or query == "impulsercdriverfixer":
            with open('resources/troubleshooting/impulserc.txt', 'r') as f:
                impulserc_content = f.read()
            await ctx.send(impulserc_content)
        elif query == "noprops":
            with open('resources/troubleshooting/noprops.txt', 'r') as f:
                noprops_content = f.read()
            await ctx.send(noprops_content)

async def setup(bot):
    await bot.add_cog(FpvCommands(bot))