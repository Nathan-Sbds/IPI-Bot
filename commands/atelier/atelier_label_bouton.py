import discord
from discord import app_commands
import json
from utils.AtelierView import AtelierView

async def setup(client, tree):
    @tree.command(
        name="atelier_label_bouton",
        description="Modifier le texte du bouton (ne doit pas depasser 80 caractères)",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_modify_button_label(ctx, button_label: str):
        """
        Modify the button label.

        Args:
            ctx: The context of the command.
            button_label (str): The new button label.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)
        if len(button_label) > 80:
            await ctx.response.send_message(
                content="Le texte du bouton ne peut pas dépasser 80 caractères.",
                ephemeral=True,
            )
            return

        data["button_label"] = button_label

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        for view in client.persistent_views:
            if isinstance(view, AtelierView):
                view.children[0].label = data["button_label"]

        for propositions in data["propositions"]:
            proposition_id = propositions["id"]
            view = AtelierView(client)
            view.children[0].label = data["button_label"]
            message_id = int(propositions["message_id"])
            channel_id = int(propositions["channel_id"])
            channel = client.get_channel(channel_id)

            if channel:
                message = await channel.fetch_message(message_id)
                await message.edit(
                    view=view, content=message.content, embed=message.embeds[0]
                )
                client.add_view(view, message_id=int(propositions["message_id"]))

        await ctx.response.send_message(
            content=f"Le texte du bouton est maintenant {button_label}", ephemeral=True
        )
if __name__ == '__main__':
    pass
