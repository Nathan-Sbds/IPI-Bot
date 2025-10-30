import discord
import logging
from typing import List


def _sanitize_prefix(prefix: str) -> str:
    return prefix.replace(" ", "-").lower()


def _filter_channels_by_type(category: discord.CategoryChannel, type_channel: int):
    if type_channel == 0:
        return [channel for channel in category.channels if isinstance(channel, discord.VoiceChannel)]
    return [channel for channel in category.channels if isinstance(channel, discord.TextChannel)]


def _format_channel_mentions(channels: List[discord.abc.GuildChannel]) -> str:
    if not channels:
        return "Aucun channel"
    return "\n".join(f"- <#{channel.id}>" for channel in channels)


class ConfirmDeleteChannelsView(discord.ui.View):
    def __init__(self, ctx: discord.Interaction, channels: List[discord.abc.GuildChannel], category: discord.CategoryChannel, command_source: str):
        super().__init__(timeout=60)
        self.ctx = ctx
        self.channels = channels
        self.category = category
        self.command_source = command_source
        self.channel_names = {
            getattr(channel, "id", idx): getattr(channel, "name", "Nom inconnu")
            for idx, channel in enumerate(channels)
        }

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.ctx.user.id:
            await interaction.response.send_message(
                "Seule la personne ayant lancé la commande peut confirmer cette suppression.",
                ephemeral=True,
            )
            return False
        return True

    def _disable_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    @discord.ui.button(label="Valider", style=discord.ButtonStyle.danger)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        deleted = []
        failed = []

        for channel in self.channels:
            channel_id = getattr(channel, "id", None)
            channel_name = self.channel_names.get(channel_id, getattr(channel, "name", "Nom inconnu"))
            try:
                await channel.delete(
                    reason=(
                        f"Suppression via {self.command_source} demandée par {self.ctx.user} (ID: {self.ctx.user.id})"
                    )
                )
                deleted.append(channel_name)
            except Exception as error:  # pragma: no cover - logging path
                logging.error(
                    f"Error while deleting channel {channel_name} in confirm view: {error}",
                    exc_info=True,
                )
                failed.append(channel_name)

        deleted_summary = ", ".join(deleted) if deleted else "aucun"
        failed_summary = ", ".join(failed) if failed else None

        message_lines = [
            f"Suppression terminée pour la catégorie {self.category.name}.",
            f"Channels supprimés : {deleted_summary}.",
        ]

        if failed_summary:
            message_lines.append(
                f"Impossible de supprimer : {failed_summary}. Ils peuvent avoir déjà été supprimés ou une erreur est survenue."
            )

        self._disable_buttons()
        await self.ctx.edit_original_response(
            content="\n".join(message_lines),
            view=None,
        )

    @discord.ui.button(label="Annuler", style=discord.ButtonStyle.secondary)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self._disable_buttons()
        await interaction.response.edit_message(
            content=(
                "Suppression annulée. Aucun channel n'a été supprimé."
            ),
            view=None,
        )


class CategorySelectDeleteChannel(discord.ui.View):
    def __init__(self, categories_select, ctx, type_channel, prefix):
        super().__init__()
        self.add_item(
            CategoryDropdownDeleteChannel(
                categories_select,
                ctx,
                type_channel,
                prefix,
            )
        )


class CategoryDropdownDeleteChannel(discord.ui.Select):
    def __init__(self, categories_select, ctx, type_channel, prefix):
        options = [
            discord.SelectOption(label=category.name.replace("=", ""), value=category.name)
            for category in categories_select
        ]
        self.ctx = ctx
        self.type_channel = type_channel
        self.prefix = prefix
        super().__init__(placeholder="Choisissez une catégorie...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_object = discord.utils.get(self.ctx.guild.categories, name=self.values[0])
        try:
            await self.ctx.edit_original_response(content="J'y travaille...", view=None)

            if category_object is None:
                await self.ctx.edit_original_response(
                    content="La catégorie sélectionnée est introuvable.",
                )
                return

            sanitized_prefix = _sanitize_prefix(self.prefix)
            channels = _filter_channels_by_type(category_object, self.type_channel)
            matched_channel = next(
                (channel for channel in channels if channel.name.lower().startswith(sanitized_prefix)),
                None,
            )

            if matched_channel is None:
                await self.ctx.edit_original_response(
                    content=(
                        f"Aucun channel commençant par '{sanitized_prefix}' n'a été trouvé dans la catégorie {category_object.name}."
                    ),
                )
                return

            channel_mentions = _format_channel_mentions([matched_channel])
            await self.ctx.edit_original_response(
                content=(
                    "Les channels suivants seront supprimés :\n"
                    f"{channel_mentions}\n\n"
                    "Confirmez-vous la suppression ?"
                ),
                view=ConfirmDeleteChannelsView(
                    ctx=self.ctx,
                    channels=[matched_channel],
                    category=category_object,
                    command_source="/supprimer_channel_prefix",
                ),
            )
        except Exception as e:
            logging.error(f'Error in command "delete_channel_prefix": {e}', exc_info=True)
            await self.ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande.",
            )
            return


class CategorySelectDeleteMultipleChannel(discord.ui.View):
    def __init__(self, categories_select, ctx, type_channel, prefix, nb_channel):
        super().__init__()
        self.add_item(
            CategoryDropdownDeleteMultipleChannel(
                categories_select,
                ctx,
                type_channel,
                prefix,
                nb_channel,
            )
        )


class CategoryDropdownDeleteMultipleChannel(discord.ui.Select):
    def __init__(self, categories_select, ctx, type_channel, prefix, nb_channel):
        options = [
            discord.SelectOption(label=category.name.replace("=", ""), value=category.name)
            for category in categories_select
        ]
        self.ctx = ctx
        self.type_channel = type_channel
        self.prefix = prefix
        self.nb_channel = nb_channel
        super().__init__(placeholder="Choisissez une catégorie...", options=options)

    async def callback(self, interaction: discord.Interaction):
        category_object = discord.utils.get(self.ctx.guild.categories, name=self.values[0])
        try:
            await self.ctx.edit_original_response(content="J'y travaille...", view=None)

            if category_object is None:
                await self.ctx.edit_original_response(
                    content="La catégorie sélectionnée est introuvable.",
                )
                return

            sanitized_prefix = _sanitize_prefix(self.prefix)
            channels = _filter_channels_by_type(category_object, self.type_channel)
            matched_channels = [
                channel for channel in channels if channel.name.lower().startswith(sanitized_prefix)
            ][: self.nb_channel]

            if not matched_channels:
                await self.ctx.edit_original_response(
                    content=(
                        f"Aucun channel commençant par '{sanitized_prefix}' n'a été trouvé dans la catégorie {category_object.name}."
                    ),
                )
                return

            channel_mentions = _format_channel_mentions(matched_channels)
            await self.ctx.edit_original_response(
                content=(
                    "Les channels suivants seront supprimés :\n"
                    f"{channel_mentions}\n\n"
                    "Confirmez-vous la suppression ?"
                ),
                view=ConfirmDeleteChannelsView(
                    ctx=self.ctx,
                    channels=matched_channels,
                    category=category_object,
                    command_source="/supprimer_multiple_channels_prefix",
                ),
            )
        except Exception as e:
            logging.error(f'Error in command "delete_multiple_channel_prefix": {e}', exc_info=True)
            await self.ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande.",
            )
            return
