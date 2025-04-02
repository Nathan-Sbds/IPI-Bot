import discord
import logging
from discord import app_commands
from utils.send_mail import send_mail

async def setup(client, tree):
    @tree.command(
        name="transferer_role",
        description="Transfere un role a toutes les personnes ayant un autre role",
    )
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.describe(
        ancien_role="Les personnes ayant ce role vont recevoir le nouveau",
        nouveau_role="Role a donner",
        supprimer="Faut-il supprimer le role actuel utilisé pour transferer ? (oui /non)",
    )
    async def transfert_role(
        ctx, ancien_role: discord.Role, nouveau_role: discord.Role, supprimer: bool
    ):
        """
        Transfer a role to all people who have another role.

        Args:
            ctx: The context of the command.
            ancien_role (discord.Role): The role that people currently have.
            nouveau_role (discord.Role): The role to assign.
            supprimer (bool): Whether to remove the current role used for transfer.
        """
        try:
            await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

            OldMemberID = [m.id for m in ancien_role.members]
            OldMember = [f"<@{m.id}>" for m in ancien_role.members]
            OldMemberTxt = [m.display_name for m in ancien_role.members]
            NewRoleMember = [m.id for m in nouveau_role.members]
            OldMemberTxtMention = ", ".join(OldMember)
            OldMemberTxtNoMention = ", ".join(OldMemberTxt)

            if supprimer == True:
                for member in OldMemberID:
                    await ctx.guild.get_member(member).remove_roles(ancien_role)

            for member in OldMemberID:
                await ctx.guild.get_member(member).add_roles(nouveau_role)

            NewMenberTxtMention = ", ".join(
                [f"<@{m.id}>" for m in nouveau_role.members if m.id not in NewRoleMember]
            )
            NewMenberTxt = ", ".join(
                [m.display_name for m in nouveau_role.members if m.id not in NewRoleMember]
            )
            if supprimer == True:
                await ctx.edit_original_response(
                    content=(
                        f"Role supprimer à : {OldMemberTxtMention}\n\nRole donné à : {NewMenberTxtMention}"
                    )
                )
                user = client.get_user(ctx.user.id)
                await user.send(
                    content=(
                        f"Role supprimer à : {OldMemberTxtNoMention}\n\nRole donné à : {NewMenberTxt}"
                    )
                )

            else:
                await ctx.edit_original_response(
                    content=(f"Role donné à : {NewMenberTxtMention}")
                )
                user = client.get_user(ctx.user.id)
                await user.send(content=(f"Role donné à : {NewMenberTxt}"))
        except Exception as e:
            logging.error(f'Error in command "transfert_role": {e}', exc_info=True)
            send_mail(e, "transfert_role")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return
        
if __name__ == "__main__":
    pass