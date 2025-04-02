import discord
import json

def atelier_get_role_count(ctx: discord.Interaction, proposition_id: int):
    """
    Get the count of roles for a proposition.

    Args:
        ctx (discord.Interaction): The interaction object.
        proposition_id (int): The ID of the proposition.

    Returns:
        dict: A dictionary with role IDs as keys and counts as values.
    """
    with open("./participations.json", "r") as file:
        data = json.load(file)

    roles_id = data["roles"]
    roles = []
    for role_id in roles_id:
        roles.append(ctx.guild.get_role(role_id))

    role_counter = {}
    for role in roles:
        for member in role.members:
            member_id = str(member.id)
            if str(member.id) in data["participations"]:
                if proposition_id in data["participations"][str(member.id)]:
                    if role.id not in role_counter:
                        role_counter[role.id] = 0
                    role_counter[role.id] += 1

    return role_counter