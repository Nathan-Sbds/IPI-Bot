import discord
import logging
from discord import app_commands
from utils.send_mail import send_mail

async def setup(client, tree):
    @tree.command(
        name="supprimer_role",
        description="Supprime le role a toutes les personnes ayant ce role",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        role="Role a retirere aux personnes",
        role_condition="Retirer le role seulement aux personnes ayant ce role",
    )
    async def supprime_role(ctx, role: discord.Role, role_condition: discord.Role = None):
        """
        Remove a role from all people who have it.

        Args:
            ctx: The context of the command.
            role (discord.Role): The role to remove.
            role_condition (discord.Role, optional): The role condition to check.
        """
        try:
            await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
            if role_condition != None:
                MembersMention = ", ".join(
                    [f"<@{m.id}>" for m in role.members if m in role_condition.members]
                )
                Members = ", ".join(
                    [m.display_name for m in role.members if m in role_condition.members]
                )
                [
                    await m.remove_roles(role)
                    for m in role.members
                    if m in role_condition.members
                ]
            else:
                MembersMention = ", ".join([f"<@{m.id}>" for m in role.members])
                Members = ", ".join([m.display_name for m in role.members])
                [await m.remove_roles(role) for m in role.members]

            await ctx.edit_original_response(
                content=(f"Role supprimé pour : {MembersMention}")
            )
            user = client.get_user(ctx.user.id)
            await user.send(content=(f"Role supprimé pour : {Members}"))

        except Exception as e:
            logging.error(f'Error in command "supprime_role": {e}', exc_info=True)
            send_mail(e, "supprime_role")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return
