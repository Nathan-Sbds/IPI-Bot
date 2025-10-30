import discord
import logging

class CategorySelectUniqueChannel(discord.ui.View):
    def __init__(self, categories_select, ctx, type_channel, name, limite_utilisateurs, bitrate):
        super().__init__()
        self.add_item(
            CategoryDropdownUniqueChannel(
                categories_select,
                ctx,
                type_channel,
                name,
                limite_utilisateurs,
                bitrate,
            )
        )

class CategoryDropdownUniqueChannel(discord.ui.Select):
    def __init__(self, categories_select, ctx, type_channel, name, limite_utilisateurs, bitrate):
        options = [
            discord.SelectOption(label=category.name.replace("=",""), value=category.name) for category in categories_select
        ]
        self.ctx = ctx
        self.type_channel = type_channel
        self.name = name
        self.limite_utilisateurs = limite_utilisateurs
        self.bitrate = bitrate
        super().__init__(placeholder="Choisissez une catégorie...", options=options)


    async def callback(self, interaction: discord.Interaction):
        category_object = discord.utils.get(
                self.ctx.guild.categories, name=self.values[0]
            )
        try:
            await self.ctx.edit_original_response(content="J'y travaille...")

            server = self.ctx.guild
            default_role = server.default_role
            bitrate_limit = server.bitrate_limit
            requested_bitrate = min(self.bitrate * 1000, bitrate_limit)
            user_limit = self.limite_utilisateurs if self.limite_utilisateurs is not None else 0

            if self.type_channel == 0:
                channel = await server.create_voice_channel(
                    name=self.name.lower(),
                    category=category_object,
                    user_limit=user_limit,
                    bitrate=requested_bitrate,
                )
            else:
                channel = await server.create_text_channel(
                    name=self.name.lower(), category=category_object
                )

            await channel.edit(sync_permissions=True)

            if category_object.permissions_for(default_role).view_channel:
                deny_kwargs = {"view_channel": False}
                if isinstance(channel, discord.VoiceChannel):
                    deny_kwargs.update({"connect": False, "speak": False})
                else:
                    deny_kwargs.update({"read_messages": False})

                await channel.set_permissions(default_role, **deny_kwargs)

            await self.ctx.edit_original_response(
                content=(
                    f"Channel {self.name.lower()} créé !"
                ), view=None
            )
        except Exception as e:
            logging.error(f'Error in command "create_channel": {e}', exc_info=True)
            print(e, "create_channel")
            await self.ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande.", view=None
            )
            return