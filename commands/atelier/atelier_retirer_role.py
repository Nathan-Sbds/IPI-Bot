import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_retirer_role",
        description="Supprimer un/des rôle ayant la possibilité d'utiliser le module atelier",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_remove_role(
        ctx,
        role1: discord.Role,
        role2: discord.Role = None,
        role3: discord.Role = None,
        role4: discord.Role = None,
        role5: discord.Role = None,
        role6: discord.Role = None,
        role7: discord.Role = None,
        role8: discord.Role = None,
        role9: discord.Role = None,
        role10: discord.Role = None,
    ):
        """
        Remove roles from the list of roles that can use the workshop module.

        Args:
            ctx: The context of the command.
            role1 (discord.Role): The first role to remove.
            role2 (discord.Role, optional): The second role to remove.
            role3 (discord.Role, optional): The third role to remove.
            role4 (discord.Role, optional): The fourth role to remove.
            role5 (discord.Role, optional): The fifth role to remove.
            role6 (discord.Role, optional): The sixth role to remove.
            role7 (discord.Role, optional): The seventh role to remove.
            role8 (discord.Role, optional): The eighth role to remove.
            role9 (discord.Role, optional): The ninth role to remove.
            role10 (discord.Role, optional): The tenth role to remove.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        members = []
        data["roles"].remove(role1.id)
        multiple = False
        for member in role1.members:
            members.append(member)

        if role2 is not None:
            data["roles"].remove(role2.id)
            multiple = True
            for member in role2.members:
                members.append(member)
        if role3 is not None:
            data["roles"].remove(role3.id)
            multiple = True
            for member in role3.members:
                members.append(member)
        if role4 is not None:
            data["roles"].remove(role4.id)
            multiple = True
            for member in role4.members:
                members.append(member)
        if role5 is not None:
            data["roles"].remove(role5.id)
            multiple = True
            for member in role5.members:
                members.append(member)
        if role6 is not None:
            data["roles"].remove(role6.id)
            multiple = True
            for member in role6.members:
                members.append(member)
        if role7 is not None:
            data["roles"].remove(role7.id)
            multiple = True
            for member in role7.members:
                members.append(member)
        if role8 is not None:
            data["roles"].remove(role8.id)
            multiple = True
            for member in role8.members:
                members.append(member)
        if role9 is not None:
            data["roles"].remove(role9.id)
            multiple = True
            for member in role9.members:
                members.append(member)
        if role10 is not None:
            data["roles"].remove(role10.id)
            multiple = True
            for member in role10.members:
                members.append(member)

        non_inscrit_role = discord.utils.get(ctx.guild.roles, name="Non Inscrit")

        if non_inscrit_role:
            for member in members:
                if non_inscrit_role in member.roles:
                    await member.remove_roles(non_inscrit_role)

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.edit_original_response(
            content=f"Le{'s' if multiple else ''} rôle{'s' if multiple else ''} {role1.name}{f', {role2.name}' if role2 is not None else ''}{f', {role3.name}' if role3 is not None else ''}{f', {role4.name}' if role4 is not None else ''}{f', {role5.name}' if role5 is not None else ''}{f', {role6.name}' if role6 is not None else ''}{f', {role7.name}' if role7 is not None else ''}{f', {role8.name}' if role8 is not None else ''}{f', {role9.name}' if role9 is not None else ''}{f', {role10.name}' if role10 is not None else ''} ont été supprimés des rôles autorisés à participer",
        )
if __name__ == '__main__':
    pass
