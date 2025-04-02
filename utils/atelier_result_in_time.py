import json
import discord

async def atelier_result_in_time(interaction, msg_delete: bool = False):
    """
    Display real-time workshop results.

    Args:
        interaction: The interaction object.
        msg_delete (bool): Whether to delete the previous result message.
    """
    with open("./participations.json", "r") as file:
        data = json.load(file)

    participations = data["participations"]
    participation_ids = [
        participation_id
        for participation_ids_list in participations.values()
        if participation_ids_list is not None
        for participation_id in participation_ids_list
    ]

    propositions_data = data["propositions"]

    embed = discord.Embed(
        title="Ateliers",
        description="Voici les participants actuellement enregistrées :",
        color=discord.Color.green(),
    )

    max_votes = 0
    for proposition in propositions_data:
        proposition_id = proposition["id"]
        proposition_titre = proposition["titre"]
        vote_count = participation_ids.count(proposition_id)
        if vote_count > max_votes:
            max_votes = vote_count
            proposition_max = proposition

        embed.add_field(
            name=f"Atelier : {proposition_titre}",
            value=f"- {vote_count} participant{'s' if vote_count > 1 else ''}{' - Places non disponibles' if vote_count >= data['max_inscrits'] else ''}",
            inline=False,
        )

    if max_votes > 0:
        if msg_delete or data["result_id"] == 0:
            if data["result_id"] != 0:
                channel = interaction.channel
                message = await channel.fetch_message(data["result_id"])
                await message.delete()

            message = await interaction.channel.send(embed=embed)

            data["result_id"] = message.id

            with open("./participations.json", "w") as file:
                json.dump(data, file)
        else:
            channel = interaction.channel
            message = await channel.fetch_message(data["result_id"])
            await message.edit(embed=embed)
