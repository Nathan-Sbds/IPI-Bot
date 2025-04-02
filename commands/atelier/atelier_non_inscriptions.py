import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_non_inscriptions",
        description="Afficher les personnes ne s'etant pas inscrits",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_non_inscrit(ctx):
        """
        Show the people who have not registered.

        Args:
            ctx: The context of the command.
        """
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("././participations.json", "r") as file:
            data = json.load(file)

        roles_id = data["roles"]
        roles = []
        for role_id in roles_id:
            roles.append(ctx.guild.get_role(role_id))

        for role in roles:
            non_participants = []
            for member in role.members:
                member_id = str(member.id)
                if member_id not in data["participations"]:
                    non_participants.append({f"{member_id}": 0})

                elif len(data["participations"][member_id]) < data["max_inscription"]:
                    non_participants.append(
                        {f"{member_id}": len(data["participations"][member_id])}
                    )

            non_participant_text = f"Les personnes n'ayant pas participer suffisamment de fois de la promo {role.name} sont : \nNom de la personne (Nombre d'atelier auquel il/elle est inscrit)\n\n"
            for member_data in non_participants:
                for member_id, participation_time in member_data.items():
                    non_participant_text += f"- **{ctx.guild.get_member(int(member_id)).display_name}** ({participation_time})\n"

            if len(non_participant_text) != 0:
                user = client.get_user(ctx.user.id)
                await user.send(content=non_participant_text)
            else:
                await ctx.edit_original_response(
                    content=f"Toutes les personnes de la promo {role.name} ont votés {data['max_inscription']} fois"
                )

        await ctx.edit_original_response(
            content="Les personnes n'ayant pas participer suffisamment de fois ont été envoyés en message privé"
        )

if __name__ == '__main__':
    pass
