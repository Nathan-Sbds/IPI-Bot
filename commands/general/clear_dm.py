import discord
from discord import app_commands

async def setup(client, tree):
    @tree.command(
        name="clear_dm",
        description="Supprime les messages envoyés par le bot en message privé. Utilisable en message privé uniquement.",
    )
    async def clear_messages(ctx):
        """
        Clear messages sent by the bot in private messages.

        Args:
            ctx: The context of the command.
        """
        if not isinstance(ctx.channel, discord.DMChannel):
            await ctx.response.send_message(
                content="Cette commande n'est disponible qu'en messages privés.",
                ephemeral=True,
            )
        else:
            await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
            async for msg in ctx.channel.history(limit=None):
                if msg.author == client.user:
                    await msg.delete()
            await ctx.edit_original_response(content="Et voila !")

if __name__ == '__main__':
    pass
