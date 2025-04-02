import discord
from discord import app_commands

async def setup(client, tree):
    @tree.command(name="ping", description="Donne la latence du bot !")
    async def ping(ctx):
        """
        Get the bot's latency.

        Args:
            ctx: The context of the command.
        """
        latency = round(client.latency * 1000)
        await ctx.response.send_message(
            content=f"Pong! Latence: {latency}ms", ephemeral=True
        )
if __name__ == '__main__':
    pass
