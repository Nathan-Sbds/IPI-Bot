import discord
from discord import app_commands
import json
from utils.vote_result_in_time import result_in_time

class ResultView(discord.ui.View):
    def __init__(self, client):
        super().__init__(timeout=None)

        self.client = client

    @discord.ui.button(
        label="Voter", style=discord.ButtonStyle.red, custom_id=f"vote_button"
    )
    async def button_callback(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        """
        Callback for the vote button.

        Args:
            interaction (discord.Interaction): The interaction object.
            button (discord.ui.Button): The button that was clicked.
        """
        with open("./secret_santa.json", "r") as file:
            dataSecret = json.load(file)

        user_id = str(interaction.user.id)

        if user_id in dataSecret["votes"]:
            del dataSecret["votes"][user_id]

        for image in dataSecret["images"]:
            if image["message_id"] == interaction.message.id:
                dataSecret["votes"][user_id] = image["id"]
                selected_image = image["id"]
                break

        # Save the data to the JSON file
        with open("./secret_santa.json", "w") as file:
            json.dump(dataSecret, file)

        await interaction.response.send_message(
            f"Vous avez voté pour l'image {selected_image}.", ephemeral=True
        )

        await result_in_time(self.client, interaction)
