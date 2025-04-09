import discord
from discord import app_commands
import json, os
from utils.vote_result_in_time import result_in_time
from utils.ResultView import ResultView

folder_path = "./Attachments"

async def setup(client, tree):

    @tree.command(name="vote_ajouter_image", description="Ajouter une image")
    @app_commands.checks.has_permissions(administrator=True)
    async def add_image(ctx, image: discord.Attachment):
        """
        Add an image for voting.

        Args:
            ctx: The context of the command.
            image (discord.Attachment): The image to be added.
        """
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("././secret_santa.json", "r") as file:
            dataSecret = json.load(file)

        # Make sure the folder exists; if not, create it
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

        # Save the attachment with its original filename
        file_path = os.path.join(
            folder_path,
            f"Photo_{dataSecret['next_image_id']}.{image.filename.split('.')[-1]}",
        )
        await image.save(file_path)

        image_id = dataSecret["next_image_id"]

        # Create a vote option for the added image
        view = ResultView(client)  # Pass the image ID to the view constructor
        client.add_view(view)
        view.timeout = None  # Set the timeout to None to make the view persistent

        embed = discord.Embed(
            title=f"Photo {image_id} :",
            description="Cliquez sur le bouton ci-dessous pour voter pour cette image.",
            color=discord.Color.red(),
        )
        embed.set_image(
            url=f"attachment://Photo_{image_id}.{image.filename.split('.')[-1]}"
        )

        message = await client.get_channel(ctx.channel_id).send(
            file=discord.File(
                os.path.join(
                    folder_path, f"Photo_{image_id}.{image.filename.split('.')[-1]}"
                )
            ),
            embed=embed,
            view=view,
        )

        dataSecret["images"].append(
            {
                "id": image_id,
                "file": f"Photo_{image_id}.{image.filename.split('.')[-1]}",
                "message_id": message.id,
            }
        )

        dataSecret["next_image_id"] += 1

        # Save the data to the JSON file
        with open("././secret_santa.json", "w") as file:
            json.dump(dataSecret, file)

        await result_in_time(client, ctx, True)
        await ctx.edit_original_response(content=f"L'image {image_id} a été ajoutée.")

if __name__ == '__main__':
    pass
