import discord
from discord import ui
from redbot.core import Config, commands
from splitwise import Splitwise


class SplitwiseCog(commands.Cog):
    """This cog interacts with Splitwise API"""

    def __init__(self, bot):
        self.config = Config.get_conf(
            self, identifier=1234567890, force_registration=True
        )

        self.config.register_guild(
            group_id=0,
            api_key="",
        )

        self.bot = bot

    async def setup_splitwise(self, ctx):
        """Setup splitwise"""
        tokens = await self.bot.get_shared_api_tokens("splitwise")
        api_key = await self.config.guild(ctx.guild).api_key()

        if (
            not tokens
            or "consumer_key" not in tokens
            or "consumer_secret" not in tokens
        ):
            raise ValueError("The Splitwise API tokens are not set")
        if not api_key:
            raise ValueError("The Splitwise API key is not set")

        return Splitwise(
            tokens["consumer_key"], tokens["consumer_secret"], api_key=api_key
        )

    @commands.command()
    async def sw_apikey(self, ctx, api_key: str):
        """Set the API key for Splitwise"""
        await self.config.guild(ctx.guild).api_key.set(api_key)
        await ctx.send("API key set")

    @commands.command()
    async def sw_set_group(self, ctx):
        """List the groups in Splitwise"""
        async with ctx.typing():
            try:
                splitwise = await self.setup_splitwise(ctx)

                groups = splitwise.getGroups()
                msg = ""
                for g in groups:
                    msg += f"{g.getName()} `{g.getId()}`\n"
                view = GroupSelectorView(ctx, self.config, groups)
                await ctx.send(
                    "Pick a group to set as a default for this discord:", view=view
                )
            except Exception as e:
                await ctx.send(
                    f"Could not talk to splitwise, got the following error: {e}"
                )
                raise e

    @commands.command()
    async def sw(self, ctx):
        """This command will show any outstanding debts for the selected group"""
        async with ctx.typing():

            splitwise = await self.setup_splitwise(ctx)

            group_id = await self.config.guild(ctx.guild).group_id()

            try:
                group = splitwise.getGroup(group_id)

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
                await ctx.send(
                    f"Could not talk to splitwise, got the following error: {e}"
                )


class GroupSelectorView(discord.ui.View):
    def __init__(self, ctx, config, groups):
        super().__init__()
        self.ctx = ctx

        self.add_item(GroupSelector(ctx, config, groups))


class GroupSelector(discord.ui.Select):
    def __init__(self, ctx, config, groups):
        super().__init__()
        self.ctx = ctx
        self.config = config

        options = []
        for g in groups:
            options.append(
                discord.SelectOption(
                    label=g.getName(), value=str(g.getId()), description=g.getId()
                )
            )

        self.placeholder = "Pick which group to use"
        self.min_values = 1
        self.max_values = 1
        self.options = options

    async def callback(self, interaction: discord.Interaction):
        selected_option = self.values[0]
        await self.config.guild(self.ctx.guild).group_id.set(selected_option)
        await interaction.response.send_message(f"Group set to: {selected_option}")
