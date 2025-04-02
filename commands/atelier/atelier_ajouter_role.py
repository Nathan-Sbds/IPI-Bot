import discord
from discord import app_commands
import json

async def setup(client, tree):
    @tree.command(
        name="atelier_ajouter_role",
        description="Ajouter un rôle a la liste des roles pouvant utiliser le module atelier",
    )
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    async def atelier_add_role(
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
        Add roles to the list of roles that can use the workshop module.

        Args:
            ctx: The context of the command.
            role1 (discord.Role): The first role to add.
            role2 (discord.Role, optional): The second role to add.
            role3 (discord.Role, optional): The third role to add.
            role4 (discord.Role, optional): The fourth role to add.
            role5 (discord.Role, optional): The fifth role to add.
            role6 (discord.Role, optional): The sixth role to add.
            role7 (discord.Role, optional): The seventh role to add.
            role8 (discord.Role, optional): The eighth role to add.
            role9 (discord.Role, optional): The ninth role to add.
            role10 (discord.Role, optional): The tenth role to add.
        """
        with open("././participations.json", "r") as file:
            data = json.load(file)

        await ctx.response.send_message(content="J'y travaille..", ephemeral=True)
        members = []
        data["roles"].append(role1.id)
        for member in role1.members:
            members.append(member)
        multiple = False
        if role2 is not None:
            data["roles"].append(role2.id)
            multiple = True
            for member in role2.members:
                members.append(member)
        if role3 is not None:
            data["roles"].append(role3.id)
            multiple = True
            for member in role3.members:
                members.append(member)
        if role4 is not None:
            data["roles"].append(role4.id)
            multiple = True
            for member in role4.members:
                members.append(member)
        if role5 is not None:
            data["roles"].append(role5.id)
            multiple = True
            for member in role5.members:
                members.append(member)
        if role6 is not None:
            data["roles"].append(role6.id)
            multiple = True
            for member in role6.members:
                members.append(member)
        if role7 is not None:
            data["roles"].append(role7.id)
            multiple = True
            for member in role7.members:
                members.append(member)
        if role8 is not None:
            data["roles"].append(role8.id)
            multiple = True
            for member in role8.members:
                members.append(member)
        if role9 is not None:
            data["roles"].append(role9.id)
            multiple = True
            for member in role9.members:
                members.append(member)
        if role10 is not None:
            data["roles"].append(role10.id)
            multiple = True
            for member in role10.members:
                members.append(member)

        non_inscrit_role = discord.utils.get(ctx.guild.roles, name="Non Inscrit")

        if not non_inscrit_role:
            non_inscrit_role = await ctx.guild.create_role(
                name="Non Inscrit", color=discord.Color(0xFFFF00)
            )
        for member in members:
            if non_inscrit_role not in member.roles:
                await member.add_roles(non_inscrit_role)

        with open("././participations.json", "w") as file:
            json.dump(data, file)

        await ctx.edit_original_response(
            content=f"Le{'s' if multiple else ''} rôle{'s' if multiple else ''} {role1.name}{f', {role2.name}' if role2 is not None else ''}{f', {role3.name}' if role3 is not None else ''}{f', {role4.name}' if role4 is not None else ''}{f', {role5.name}' if role5 is not None else ''}{f', {role6.name}' if role6 is not None else ''}{f', {role7.name}' if role7 is not None else ''}{f', {role8.name}' if role8 is not None else ''}{f', {role9.name}' if role9 is not None else ''}{f', {role10.name}' if role10 is not None else ''} {'ont' if multiple else 'a'} été ajouté{'s' if multiple else ''} aux rôles autorisés à participer",
        )
if __name__ == '__main__':
    pass
