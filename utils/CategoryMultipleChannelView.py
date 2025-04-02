import discord
import logging

class CategorySelectMultipleChannel(discord.ui.View):
    def __init__(self, categories_select, ctx, type_channel, name, nb_channel):
        super().__init__()
        self.add_item(CategoryDropdownMultipleChannel(categories_select, ctx, type_channel, name, nb_channel))

class CategoryDropdownMultipleChannel(discord.ui.Select):
    def __init__(self, categories_select, ctx, type_channel, name, nb_channel):
        options = [
            discord.SelectOption(label=category.name.replace("=",""), value=category.name) for category in categories_select
        ]
        self.ctx = ctx
        self.type_channel = type_channel
        self.name = name
        self.nb_channel = nb_channel
        super().__init__(placeholder="Choisissez une catégorie...", options=options)


    async def callback(self, interaction: discord.Interaction):
        category_object = discord.utils.get(
                self.ctx.guild.categories, name=self.values[0]
            )
        try:
            self.ctx.edit_original_response(content="J'y travaille...")
            server = self.ctx.guild
            pedago = discord.utils.get(self.ctx.guild.roles, name="Team Pedago IPI")
            creator = discord.utils.get(self.ctx.guild.members, id=self.ctx.user.id)

            for i in range(self.nb_channel):
                if self.type_channel == 0:
                    await server.create_voice_channel(
                        name=self.name.lower()+"-"+str(i+1), category=category_object
                    )
                else:
                    await server.create_text_channel(
                        name=self.name.lower()+"-"+str(i+1), category=category_object
                    )

                await discord.utils.get(
                    self.ctx.guild.channels, name=self.name.lower()+"-"+str(i+1)
                ).set_permissions(
                    target=pedago,
                    read_messages=True,
                    send_messages=True,
                    connect=True,
                    speak=True,
                )

                await discord.utils.get(
                    self.ctx.guild.channels, name=self.name.lower()+"-"+str(i+1)
                ).set_permissions(
                    target=creator,
                    read_messages=True,
                    send_messages=True,
                    connect=True,
                    speak=True,
                )

            await self.ctx.edit_original_response(
                content=(
                    f"Les channels ont été créés !"
                ), view=None
            )
        except Exception as e:
            logging.error(f'Error in command "create_channel": {e}', exc_info=True)
            print(e, "create_channel")
            await self.ctx.edit_original_response(
                content="Une erreur s'est produite lors de l'exécution de la commande.", view=None
            )
            return