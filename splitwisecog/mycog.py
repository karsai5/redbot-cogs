from redbot.core import commands
from splitwise import Splitwise

CONSUMER_KEY = ""
CONSUMER_SECRET = ""
API_KEY = ""


class SplitwiseCog(commands.Cog):
    """This cog interacts with Splitwise API"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sw(self, ctx):
        """This command will fetch the groups from Splitwise, and show any outstanding debts"""
        async with ctx.typing():
            s_obj = Splitwise(CONSUMER_KEY, CONSUMER_SECRET, api_key=API_KEY)
            groups = s_obj.getGroups()
            # msg = ""
            # for g in groups:
            #     msg += f"{g.getName()} `{g.getId()}`\n"
            # await ctx.send(msg)

            msg = ""
            group = s_obj.getGroup(20621529)
            group_members = {}
            for m in group.getMembers():
                group_members[m.getId()] = m
            debts = group.getSimplifiedDebts()

            msg += f"Group: {group.getName()}\n"
            if len(debts) > 0:
                msg += "Debts:\n"
                for d in debts:
                    msg += f"{group_members[d.getFromUser()].getFirstName()} owes {group_members[d.getToUser()].getFirstName()} {d.getAmount()}\n"
            else:
                msg += "No debts\n"
            await ctx.send(msg)
            # Your code will go here
