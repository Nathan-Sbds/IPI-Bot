import discord
from discord import app_commands
import os
import re
import urllib.request
import logging
from utils.send_mail import send_mail

async def setup(client, tree):

    @tree.command(
        name="assigner_role",
        description="Donne le role ciblé a toutes les personnes dans le fichier .csv",
    )
    @app_commands.checks.has_permissions(manage_roles=True)
    @app_commands.describe(
        fichier="Fichier contenant les nom et prenom dans deux colonnes séparées",
        supprimer="Faut-il supprimer les personnes ayant le role actuellement ?",
        role="Role a donner aux personnes presentes dans le fichier",
        role2="Second rôle a donner",
        role3="Second rôle a donner",
    )
    async def assign_role(
        ctx,
        fichier: discord.Attachment,
        supprimer: bool,
        role: discord.Role,
        role2: discord.Role = None,
        role3: discord.Role = None,
    ):
        """
        Assign a role to all people in the CSV file.

        Args:
            ctx: The context of the command.
            fichier (discord.Attachment): The CSV file containing names.
            supprimer (bool): Whether to remove the role from current members.
            role (discord.Role): The role to assign.
            role2 (discord.Role, optional): The second role to assign.
            role3 (discord.Role, optional): The third role to assign.
        """
        try:
            await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

            if supprimer == True:
                OldMemberID = [m.id for m in role.members]
                OldMember = [m.display_name for m in role.members]
                for member in OldMemberID:
                    await ctx.guild.get_member(member).remove_roles(role)

                OldMemberTxt = ", ".join(OldMember)

            member_list = []

            for member in ctx.guild.members:
                member_list.append(member.display_name.replace(" ", "").lower())
                member_list.append(member.id)

            try:
                all_file = []
                for row in urllib.request.urlopen(
                    urllib.request.Request(
                        url=str(fichier), headers={"User-Agent": "Mozilla/5.0"}
                    )
                ):
                    element_list = []
                    for element in re.split(",|\n|\r|;|\ufeff", row.decode("utf-8")):
                        if element != "":
                            element_list.append(element)

                    all_file.append(element_list)

                not_found = []
                for element_list in all_file:
                    try:
                        element_list[1]
                        if (
                            (str(element_list[0]) + str(element_list[1]))
                            .replace(" ", "")
                            .lower()
                            in member_list
                        ) or (
                            (str(element_list[1]) + str(element_list[0]))
                            .replace(" ", "")
                            .lower()
                            in member_list
                        ):
                            try:
                                await ctx.guild.get_member(
                                    member_list[
                                        member_list.index(
                                            (str(element_list[0]) + str(element_list[1]))
                                            .replace(" ", "")
                                            .lower()
                                        )
                                        + 1
                                    ]
                                ).add_roles(role)
                                if role2 != None:
                                    await ctx.guild.get_member(
                                        member_list[
                                            member_list.index(
                                                (
                                                    str(element_list[0])
                                                    + str(element_list[1])
                                                )
                                                .replace(" ", "")
                                                .lower()
                                            )
                                            + 1
                                        ]
                                    ).add_roles(role2)
                                if role3 != None:
                                    await ctx.guild.get_member(
                                        member_list[
                                            member_list.index(
                                                (
                                                    str(element_list[0])
                                                    + str(element_list[1])
                                                )
                                                .replace(" ", "")
                                                .lower()
                                            )
                                            + 1
                                        ]
                                    ).add_roles(role3)

                            except:
                                await ctx.guild.get_member(
                                    member_list[
                                        member_list.index(
                                            (str(element_list[1]) + str(element_list[0]))
                                            .replace(" ", "")
                                            .lower()
                                        )
                                        + 1
                                    ]
                                ).add_roles(role)
                                if role2 != None:
                                    await ctx.guild.get_member(
                                        member_list[
                                            member_list.index(
                                                (
                                                    str(element_list[1])
                                                    + str(element_list[0])
                                                )
                                                .replace(" ", "")
                                                .lower()
                                            )
                                            + 1
                                        ]
                                    ).add_roles(role2)
                                if role3 != None:
                                    await ctx.guild.get_member(
                                        member_list[
                                            member_list.index(
                                                (
                                                    str(element_list[1])
                                                    + str(element_list[0])
                                                )
                                                .replace(" ", "")
                                                .lower()
                                            )
                                            + 1
                                        ]
                                    ).add_roles(role3)

                        else:
                            not_found.append(
                                str(element_list[0]) + " " + str(element_list[1])
                            )

                    except IndexError:
                        pass

                not_found = ", ".join(not_found)
                NewMenberTxt = ", ".join([f"<@{m.id}>" for m in role.members])

                too_much = False
                if len(not_found + NewMenberTxt) > 1900:
                    too_much = True

                if supprimer == True:
                    if too_much == False:
                        await ctx.edit_original_response(
                            content=(
                                f"Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                            )
                        )
                        user = client.get_user(ctx.user.id)
                        await user.send(
                            content=(
                                f"Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                            )
                        )
                    else:
                        user = client.get_user(ctx.user.id)
                        with open("message.txt", "w", encoding="utf-8") as file:
                            file.write(
                                f"Role supprimé à : {OldMemberTxt}\n\nRole donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                            )
                        await ctx.edit_original_response(
                            content=(
                                "Le message est trop long, je vous l'ai envoyé en message privé !"
                            )
                        )
                        await user.send(file=discord.File("message.txt"))
                        os.remove("message.txt")
                else:
                    if too_much == False:
                        await ctx.edit_original_response(
                            content=(
                                f"Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                            )
                        )
                        user = client.get_user(ctx.user.id)
                        await ctx.edit_original_response(
                            content=(
                                f"Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                            )
                        )
                    else:
                        user = client.get_user(ctx.user.id)
                        with open("message.txt", "w", encoding="utf-8") as file:
                            file.write(
                                f"Role donné à : {NewMenberTxt}\n\nPersonnes non trouvée(s) : {not_found}"
                            )
                        await user.send(file=discord.File("message.txt"))
                        os.remove("message.txt")

            except Exception as e:
                send_mail(e, "assign_role")
                print(e)
                await ctx.edit_original_response(content=("Fichier illisible (.csv)"))
        except Exception as e:
            logging.error(f'Error in command "assign_role": {e}', exc_info=True)
            send_mail(e, "assign_role")
            await ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande."
            )
            return
