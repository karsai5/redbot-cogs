from .mycog import SplitwiseCog


async def setup(bot):
    await bot.add_cog(SplitwiseCog(bot))
