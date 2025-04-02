import discord
from discord import app_commands
import json

async def result_in_time(client, ctx, msg_delete: bool = False):
    """
    Display real-time voting results.

    Args:
        ctx: The context of the command.
        msg_delete (bool): Whether to delete the previous result message.
    """
    with open("./secret_santa.json", "r") as file:
        dataSecret = json.load(file)

    # Get the results
    votes = dataSecret["votes"]
    image_ids = [int(vote_id) for vote_id in votes.values()]
    image_data = [image for image in dataSecret["images"]]

    # Create an embed to display the results
    embed = discord.Embed(
        title="Résultat en temps réel du Vote",
        description="Voici les résultats actuels du vote :",
        color=discord.Color.green(),
    )

    max_votes = 0
    for image in image_data:
        image_id = image["id"]
        image_filename = image["file"]
        vote_count = image_ids.count(image_id)
        if vote_count > max_votes:
            max_votes = vote_count
            image_max = image

        embed.add_field(
            name=f"Photo {image_id}:",
            value=f"{vote_count} vote{'s' if vote_count > 1 else ''}",
            inline=False,
        )

    if max_votes > 0:
        if msg_delete or dataSecret["result_id"] == 0:
            if dataSecret["result_id"] != 0:
                channel = client.get_channel(ctx.channel_id)
                message = await channel.fetch_message(dataSecret["result_id"])
                await message.delete()

            message = await client.get_channel(ctx.channel_id).send(embed=embed)

            dataSecret["result_id"] = message.id

            with open("./secret_santa.json", "w") as file:
                json.dump(dataSecret, file)
        else:
            channel = client.get_channel(ctx.channel_id)
            message = await channel.fetch_message(dataSecret["result_id"])
            await message.edit(embed=embed)