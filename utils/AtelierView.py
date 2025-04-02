import sys
import os
import discord
from discord import app_commands
import json
from utils.atelier_get_participation_count import atelier_get_participation_count
from utils.atelier_get_role_count import atelier_get_role_count
from utils.atelier_result_in_time import atelier_result_in_time
from utils.AtelierConfirmView import MyViewAtelierConfirm

with open("./participations.json", "r") as file:
    data = json.load(file)

class AtelierView(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client

    @discord.ui.button(
        label=data["button_label"], style=discord.ButtonStyle.red, custom_id="button"
    )
    async def button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the workshop button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        with open("./participations.json", "r") as file:
            data = json.load(file)

        if data["active"]:
            user_id = str(interaction.user.id)
            user_participations = data["participations"].get(user_id, [])

            if not isinstance(user_participations, list):
                user_participations = []

            if len(user_participations) < data["max_inscription"]:
                for proposition in data["propositions"]:
                    if proposition["message_id"] == interaction.message.id:
                        if proposition["id"] not in user_participations:
                            for role in interaction.user.roles:
                                if role.id in data["roles"]:
                                    if (
                                        atelier_get_participation_count(
                                            proposition["id"]
                                        )
                                        < data["max_inscrits"]
                                    ):
                                        for role_member in atelier_get_role_count(
                                            interaction, proposition["id"]
                                        ):
                                            if (
                                                atelier_get_role_count(
                                                    interaction, proposition["id"]
                                                )[role_member]
                                                >= data["max_inscrits_promo"]
                                                and interaction.user.id == role_member
                                            ):
                                                await interaction.response.send_message(
                                                    f"Le nombre maximum d'inscrits de votre promo a été atteint.",
                                                    ephemeral=True,
                                                )
                                                return

                                        confirmview = MyViewAtelierConfirm(
                                            interaction, interaction.user
                                        )
                                        self.client.add_view(confirmview)

                                        await interaction.response.send_message(
                                            f"Souhaitez-vous valider votre inscription à l'atelier {proposition['titre']} ? Vous ne pourrez pas vous désinscrire après. (https://discord.com/channels/{interaction.guild.id}/{interaction.channel_id}/{interaction.message.id})",
                                            view=confirmview,
                                            ephemeral=True,
                                        )

                                        return

                                    else:
                                        await interaction.response.send_message(
                                            "Le nombre d'inscrit autorisé a été atteint.",
                                            ephemeral=True,
                                        )
                                        return
                            await interaction.response.send_message(
                                "Vos rôles ne vous permettent pas de vous inscrire à cet atelier.",
                                ephemeral=True,
                            )

                        else:
                            await interaction.response.send_message(
                                "Vous avez déjà voté pour cette proposition.",
                                ephemeral=True,
                            )
                            return

                with open("./participations.json", "w") as file:
                    json.dump(data, file)

                await atelier_result_in_time(interaction)
            else:
                await interaction.response.send_message(
                    f"Vous avez déjà voté pour {data['max_inscription']} proposition{'s' if int(data['max_inscription'])>1 else ''}. Vous ne pouvez pas voter davantage.",
                    ephemeral=True,
                )
        else:
            await interaction.response.send_message(
                "L'inscription n'est pas encore ouverte, mais vous pouvez prendre connaissance des ateliers proposés. Réessayez un peu plus tard.",
                ephemeral=True,
            )

if __name__ == "__main__":
    print("This script is part of the IPI-Bot package and should not be run directly.")
