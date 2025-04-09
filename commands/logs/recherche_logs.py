import discord
from discord import app_commands
from datetime import datetime

async def setup(client, tree):
    @tree.command(name="recherche_logs", description="Rechercher des messages dans les logs")
    @app_commands.checks.has_any_role(
        "Team Pedago IPI",
        "Team Entreprise IPI",
        "Team Communication IPI",
        "Directrice IPI",
        "Admin Serveur",
    )
    @app_commands.describe(
        membre="Membre à rechercher",
        date_debut="Date de début de la recherche (JJ/MM/AAAA HH:MM)",
        date_fin="Date de fin de la recherche (JJ/MM/AAAA HH:MM)",
    )
    async def search_logs(ctx: discord.Interaction, membre: discord.Member, date_debut: str, date_fin: str):
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)
        
        channel = discord.utils.get(ctx.guild.text_channels, name="logs")
        if not channel:
            await ctx.edit_original_response(content="Le channel 'logs' n'existe pas.")
            return

        try:
            start_dt = datetime.strptime(date_debut, "%d/%m/%Y %H:%M")
            end_dt = datetime.strptime(date_fin, "%d/%m/%Y %H:%M")
        except ValueError:
            await ctx.edit_original_response(content="Format de date invalide. Utilisez le format `JJ/MM/AAAA HH:MM`.")
            return
        
        if start_dt >= end_dt:
            await ctx.edit_original_response(content="La date de début doit être antérieure à la date de fin.")
            return

        found_messages = []
        nb_messages = 0

        await ctx.edit_original_response(content="Recupération des messages en cours. Cela peut prendre un certain temps...")

        async for message in channel.history(after=start_dt, before=end_dt, limit=10000):
            nb_messages += 1

        index = 0
        last_percentage = 0

        if nb_messages == 0:
            await ctx.edit_original_response(content="Aucun message trouvé dans la période spécifiée.")
            return
        else:
            frequency = round(1000 / nb_messages)
        if frequency == 0:
            frequency = 1

        async for message in channel.history(after=start_dt, before=end_dt, limit=10000):
            index+=1
            percentage = round((index / nb_messages) * 100)
            if percentage != last_percentage and percentage % frequency == 0:
                await ctx.edit_original_response(content=f"Analyse des messages en cours : {percentage}%")
                last_percentage = percentage
            if len(message.embeds) > 0:
                if message.embeds[0].author and membre.name == message.embeds[0].author.name:
                    found_messages.append(message.embeds[0])

        def get_embed_length(embed: discord.Embed) -> int:
            total = 0
            if embed.title:
                total += len(embed.title)
            if embed.description:
                total += len(embed.description)
            if embed.footer and embed.footer.text:
                total += len(embed.footer.text)
            if embed.fields:
                for field in embed.fields:
                    total += len(field.name) + len(field.value)
            return total

        if found_messages:
            pages = []
            current_page = []
            current_length = 0
            limite_caracteres = 5500
            max_embeds = 10

            for embed in found_messages:
                embed_length = get_embed_length(embed)
                if (current_length + embed_length > limite_caracteres and current_page) or (len(current_page) >= max_embeds):
                    pages.append(current_page)
                    current_page = [embed]
                    current_length = embed_length
                else:
                    current_page.append(embed)
                    current_length += embed_length
            if current_page:
                pages.append(current_page)
            
            current_page_index = 0

            class PaginationView(discord.ui.View):
                def __init__(self, pages):
                    super().__init__(timeout=None)
                    self.pages = pages
                    self.current_page = 0
                    self.update_buttons()

                @discord.ui.button(label="Précédent", style=discord.ButtonStyle.primary)
                async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page > 0:
                        self.current_page -= 1
                        self.update_buttons()
                        await interaction.response.edit_message(embeds=self.pages[self.current_page], view=self)

                @discord.ui.button(label="Suivant", style=discord.ButtonStyle.primary)
                async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
                    if self.current_page < len(self.pages) - 1:
                        self.current_page += 1
                        self.update_buttons()
                        await interaction.response.edit_message(embeds=self.pages[self.current_page], view=self)

                def update_buttons(self):
                    self.children[0].disabled = self.current_page == 0
                    self.children[1].disabled = self.current_page == len(self.pages) - 1

            view = PaginationView(pages)
            await ctx.edit_original_response(
                content=f"Messages concernant <@{membre.id}> entre **{date_debut}** et **{date_fin}**:",
                embeds=pages[current_page_index],
                view=view
            )
        else:
            await ctx.edit_original_response(content=f"Aucun message concernant <@{membre.id}> n'a été trouvé entre **{date_debut}** et **{date_fin}**.")

        with open("./bot_errors.log", "w") as file:
            file.write(len(found_messages))


if __name__ == '__main__':
    pass
