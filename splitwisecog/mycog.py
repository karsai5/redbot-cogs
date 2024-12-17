from redbot.core import Config, commands
from splitwise import Splitwise

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
API_KEY = ""


class SplitwiseCog(commands.Cog):
    """This cog interacts with Splitwise API"""

    def __init__(self, bot):
        self.config = Config.get_conf(
            self, identifier=1234567890, force_registration=True
        )

        self.config.register_guild(
            group_id=0,
            api_key=API_KEY,
        )

        self.bot = bot

    @commands.command()
    async def sw_apikey(self, ctx, api_key: str):
        """Set the API key for Splitwise"""
        await self.config.guild(ctx.guild).api_key.set(api_key)
        await ctx.send("API key set")

    @commands.command()
    async def sw_set_group(self, ctx, group_id: int):
        """Set the group ID for Splitwise"""
        await self.config.guild(ctx.guild).group_id.set(group_id)
        await ctx.send("Group ID set")

    @commands.command()
    async def sw_list_groups(self, ctx):
        """List the groups in Splitwise"""
        async with ctx.typing():
            tokens = await self.bot.get_shared_api_tokens("splitwise")
            api_key = await self.config.guild(ctx.guild).api_key()

            s_obj = Splitwise(
                tokens["consumer_key"], tokens["consumer_secret"], api_key=api_key
            )
            groups = s_obj.getGroups()
            msg = ""
            for g in groups:
                msg += f"{g.getName()} `{g.getId()}`\n"
            await ctx.send(msg)

    @commands.command()
    async def sw(self, ctx):
        """This command will show any outstanding debts for the selected group"""
        async with ctx.typing():
            tokens = await self.bot.get_shared_api_tokens("splitwise")
            # consumer_key = await self.config.consumer_key()
            # consumer_secret = await self.config.consumer_secret()
            api_key = await self.config.guild(ctx.guild).api_key()

            print(tokens)
            print(api_key)

            s_obj = Splitwise(
                tokens["consumer_key"], tokens["consumer_secret"], api_key=api_key
            )

            group_id = await self.config.guild(ctx.guild).group_id()


            try:
                group = s_obj.getGroup(group_id)


                group_members = {}
                for m in group.getMembers():
                    group_members[m.getId()] = m
                debts = group.getSimplifiedDebts()

                msg = ""
                msg += f"Group: {group.getName()}\n"
                if len(debts) > 0:
                    msg += "Debts:\n"
                    for d in debts:
                        msg += f"{group_members[d.getFromUser()].getFirstName()} owes {group_members[d.getToUser()].getFirstName()} {d.getAmount()}\n"
                else:
                    msg += "No debts\n"
                await ctx.send(msg)
            except Exception as e:
                await ctx.send(f"Could not talk to splitwise, got the following error: {e}")
