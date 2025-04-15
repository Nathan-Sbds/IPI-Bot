import discord
from discord import app_commands
import json
from PIL import Image

async def setup(client, tree):
    @tree.command(name="vote_resultats", description="Afficher les résultats")
    @app_commands.checks.has_permissions(administrator=True)
    async def show_results(ctx):
        """
        Show the voting results.

        Args:
            ctx: The context of the command.
        """
        await ctx.response.send_message(content="J'y travaille...", ephemeral=True)

        with open("././secret_santa.json", "r") as file:
            dataSecret = json.load(file)

        # Get the results
        votes = dataSecret["votes"]
        image_ids = [int(vote_id) for vote_id in votes.values()]
        image_data = [image for image in dataSecret["images"]]

        # Create an embed to display the results
        embed_detail = discord.Embed(
            title="Résultat du Vote",
            description="Voici les résultats détaillées du vote :",
            color=discord.Color.green(),
        )

        img1_vote = -1
        img1_name = ""
        img2_vote = -1
        img2_name = ""
        img3_vote = -1
        img3_name = ""

        for image in image_data:
            image_id = image["id"]
            image_filename = image["file"]
            vote_count = image_ids.count(image_id)
            if vote_count > img3_vote:
                img3_vote = vote_count
                img3_name = image_filename
                if vote_count > img2_vote:
                    img3_vote, img2_vote = img2_vote, img3_vote
                    img3_name, img2_name = img2_name, img3_name
                    if vote_count > img1_vote:
                        img2_vote, img1_vote = img1_vote, img2_vote
                        img2_name, img1_name = img1_name, img2_name

            embed_detail.add_field(
                name=f"Photo {image_id}:",
                value=f"{vote_count} vote{'s' if vote_count > 1 else ''}",
                inline=False,
            )

        if img1_vote > 0:
            image_fond = Image.open("././Img/Podium.png").convert("RGBA")
            couronne = Image.open("././Img/Couronne.png").convert("RGBA")

            # Ouvrir les trois images à coller
            if img1_name != "":
                image1 = Image.open(f"././Attachments/{img3_name}").convert("RGBA")
            else:
                image1 = Image.open(f"././Img/Null.png").convert("RGBA")

            if img2_name != "":
                image2 = Image.open(f"././Attachments/{img2_name}").convert("RGBA")
            else:
                image2 = Image.open(f"././Img/Null.png").convert("RGBA")

            if img3_name != "":
                image3 = Image.open(f"././Attachments/{img1_name}").convert("RGBA")
            else:
                image3 = Image.open(f"././Img/Null.png").convert("RGBA")

            # Redimensionner les trois images à une largeur de 545 tout en maintenant les proportions
            largeur_souhaitee = 545
            hauteur_souhaitee1 = (largeur_souhaitee * image1.height) // image1.width
            hauteur_souhaitee2 = (largeur_souhaitee * image2.height) // image2.width
            hauteur_souhaitee3 = (largeur_souhaitee * image3.height) // image3.width

            image1 = image1.resize((largeur_souhaitee, hauteur_souhaitee1))
            image2 = image2.resize((largeur_souhaitee, hauteur_souhaitee2))
            image3 = image3.resize((largeur_souhaitee, hauteur_souhaitee3))

            # Coller les trois images sur l'image de fond aux positions spécifiées
            position1 = (333, 1979 - image1.height)
            position2 = (1699, 1867 - image2.height)
            position3 = (1009, 1587 - image3.height)
            positionc = (1337, 1587 - image3.height - 114)

            image_fond.paste(image1, position1, image1)
            image_fond.paste(image2, position2, image2)
            image_fond.paste(image3, position3, image3)
            image_fond.paste(couronne, positionc, couronne)

            image_fond.save("././Img/result_podium.png")

            # Envoie l'embed avec les fichiers locaux sur le canal où la commande a été utilisée
            embed = discord.Embed(
                title="Le Podium", description="Et le grand gagant est...", color=0xFFD700
            )  # Couleur dorée

            embed.set_image(url=f"attachment://result_podium.png")

            await client.get_channel(ctx.channel_id).send(
                embed=embed, file=discord.File("././Img/result_podium.png")
            )
            await client.get_channel(ctx.channel_id).send(embed=embed_detail)
            await ctx.edit_original_response(
                content=f"Les résultats ont été postés dans le channel <#{ctx.channel_id}>.",
            )
        else:
            await ctx.edit_original_response(
                content="Il n'y a pas de résultats à afficher."
            )

if __name__ == '__main__':
    pass
