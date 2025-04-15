import discord
from discord import app_commands
import json, os

folder_path = "././Attachments"

async def setup(client, tree):
    @tree.command(
        name="vote_supprimer", description="Supprimer toutes les données et votes"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def clear_all(ctx):
        """
        Clear all voting data and votes.

        Args:
            ctx: The context of the command.
        """
        global dataSecret
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        for image in dataSecret["images"]:
            channel = client.get_channel(ctx.channel_id)
            message = await channel.fetch_message(image["message_id"])
            await message.delete()
        if dataSecret["result_id"] != 0:
            message = await channel.fetch_message(dataSecret["result_id"])
            await message.delete()

        dataSecret = {"votes": {}, "images": [], "next_image_id": 1, "result_id": 0}

        # Save the data to the JSON file
        with open("././secret_santa.json", "w") as file:
            json.dump(dataSecret, file)

        for file in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
            except Exception as e:
                print(e)

        await ctx.edit_original_response(content="Toutes les données ont été supprimées")

if __name__ == '__main__':
    pass
