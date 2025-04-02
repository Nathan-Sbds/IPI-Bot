import discord
import json
from utils.atelier_result_in_time import atelier_result_in_time

class MyViewAtelierConfirm(discord.ui.View):
    def __init__(self, interactionMaster: discord.Interaction, author):
        super().__init__(timeout=None)
        self.interactionMaster = interactionMaster
        self.author = author

    proposition_id = None

    @discord.ui.button(
        label="Oui", style=discord.ButtonStyle.green, custom_id="confirm"
    )
    async def confirm_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the confirm button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        if interaction.user.id == self.author.id:
            user_id = str(interaction.user.id)

            with open("./participations.json", "r") as file:
                data = json.load(file)

            if data["active"]:
                message_id = int(
                    interaction.message.content.split("https://discord.com/channels/")[
                        1
                    ].split("/")[2][:-1]
                )

                for proposition in data["propositions"]:
                    if proposition["message_id"] == message_id:
                        proposition_id = proposition["id"]
                if user_id not in data["participations"]:
                    data["participations"][user_id] = []

                if proposition_id not in data["participations"].get(user_id, []):
                    data["participations"][user_id].append(proposition_id)

                    with open("./participations.json", "w") as file:
                        json.dump(data, file)

                    if len(data["participations"][user_id]) >= int(
                        data["max_inscription"]
                    ):
                        non_inscrit_role = discord.utils.get(
                            interaction.guild.roles, name="Non Inscrit"
                        )

                        if non_inscrit_role:
                            member = interaction.guild.get_member(int(user_id))
                            if non_inscrit_role in member.roles:
                                await member.remove_roles(non_inscrit_role)

                    if (
                        data["max_inscription"] - len(data["participations"][user_id])
                        == 0
                    ):
                        for proposition in data["propositions"]:
                            if proposition["id"] == proposition_id:
                                nb_atelier_restant = data["max_inscription"] - len(
                                    data["participations"][user_id]
                                )
                                await interaction.response.edit_message(
                                    content=f"Vous avez confirmé votre inscription à l'atelier {proposition['titre']}.\nVous ne pouvez pas vous inscrire à un autre atelier. Merci de votre inscription.",
                                    view=None,
                                )
                                await atelier_result_in_time(interaction)
                                return

                    else:
                        for proposition in data["propositions"]:
                            if proposition["id"] == proposition_id:
                                nb_atelier_restant = data["max_inscription"] - len(
                                    data["participations"][user_id]
                                )
                                await interaction.response.edit_message(
                                    content=f"Vous avez confirmé votre inscription à l'atelier {proposition['titre']}.\nVous pouvez vous inscrire à {nb_atelier_restant} autre{'s' if nb_atelier_restant > 1 else ''} atelier{'s' if nb_atelier_restant > 1 else ''}.",
                                    view=None,
                                )
                                await atelier_result_in_time(interaction)
                else:
                    await interaction.response.send_message(
                        "Vous avez déjà voté pour cette proposition.", ephemeral=True
                    )

    @discord.ui.button(label="Non", style=discord.ButtonStyle.red, custom_id="cancel")
    async def cancel_button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the cancel button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        await interaction.response.edit_message(
            content="Votre inscription a été annulée.", view=None
        )
