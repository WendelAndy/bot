import discord
from discord import app_commands
from discord.ext import commands

id_do_servidor = 1049014169787170877
id_cargo_atendente = 1072328466562830398
token_bot = ""

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="en", label="English", emoji="🇺🇸"),
            discord.SelectOption(value="pt", label="Português", emoji="🇧🇷"),
            discord.SelectOption(value="es", label="Español", emoji="🇪🇸"),
        ]
        super().__init__(
            placeholder="Select a language...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_language"
        )

    async def callback(self, interaction: discord.Interaction):
        language = self.values[0]
        if language == "en":
            await interaction.response.send_message("Click below to open a ticket", ephemeral=True, view=CreateTicket())
        elif language == "pt":
            await interaction.response.send_message("Clique abaixo para abrir um ticket", ephemeral=True, view=CreateTicket())
        elif language == "es":
            await interaction.response.send_message("Haz clic a continuación para abrir un ticket", ephemeral=True, view=CreateTicket())


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Dropdown())


class CreateTicket(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=300)
        self.value = None

    @discord.ui.button(label="Open Ticket", style=discord.ButtonStyle.blurple, emoji="➕")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        self.stop()

        ticket = None
        for thread in interaction.channel.threads:
            if f"{interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.response.send_message(ephemeral=True, content="You already have an ongoing ticket!")
                    return

        async for thread in interaction.channel.archived_threads(private=True):
            if f"{interaction.message.interaction.user.id}" in thread.name:
                if thread.archived:
                    ticket = thread
                else:
                    await interaction.edit_original_message(content="You already have an ongoing ticket!", view=None)
                    return
        
        if ticket is not None:
            await ticket.edit(archived=False, locked=False)
            await ticket.edit(name=f"{interaction.message.interaction.user.name} ({interaction.message.interaction.user.id})", auto_archive_duration=10080, invitable=False)
        else:
            ticket = await interaction.channel.create_thread(name=f"{interaction.user.name} ({interaction.user.id})",auto_archive_duration=10080)
            await ticket.edit(invitable=False)

        language = self.children[0]
        translations = {
            "en": {
                "ticket_created": f"I have created a ticket for you! {ticket.mention}",
                "ticket_message": f"📩  **|** {interaction.user.mention} ticket created! Please provide all the relevant information about your issue and wait for an attendant to respond.\n\nOnce your issue is resolved, you can use `/closeticket` to close the ticket!"
            },
            "pt": {
                "ticket_created": f"Criei um ticket para você! {ticket.mention}",
                "ticket_message": f"📩  **|** {interaction.user.mention} ticket criado! Envie todas as informações possíveis sobre seu caso e aguarde até que um atendente responda.\n\nApós a sua questão ser sanada, você pode usar `/fecharticket` para encerrar o atendimento!"
            },
            "es": {
                "ticket_created": f"He creado un ticket para ti! {ticket.mention}",
                "ticket_message": f"📩  **|** {interaction.user.mention} ticket creado! Por favor, proporcione toda la información relevante sobre tu problema y espera a que un asistente responda.\n\nUna vez que se resuelva tu problema, puedes usar `/fecharticket` para cerrar el ticket."
            }
        }

        ticket_created_text = translations[language]["ticket_created"]
        ticket_message_text = translations[language]["ticket_message"]

        await interaction.response.send_message(ephemeral=True, content=ticket_created_text)
        await ticket.send(ticket_message_text)


class client(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False #Nós usamos isso para o bot não sincronizar os comandos mais de uma vez

    async def setup_hook(self) -> None:
        self.add_view(DropdownView())

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced: #Checar se os comandos slash foram sincronizados 
            await tree.sync(guild = discord.Object(id=id_do_servidor)) # Você também pode deixar o id do servidor em branco para aplicar em todos servidores, mas isso fará com que demore de 1~24 horas para funcionar.
            self.synced = True
        print(f"Entramos como {self.user}.")


aclient = client()

tree = app_commands.CommandTree(aclient)

@tree.command(guild = discord.Object(id=id_do_servidor), name = 'setup', description='Setup')
@commands.has_permissions(manage_guild=True)
async def setup(interaction: discord.Interaction):
    await interaction.response.send_message("Mensagem do painel", view=DropdownView()) 


@tree.command(guild = discord.Object(id=id_do_servidor), name="fecharticket", description='Feche um atendimento atual.')
async def _fecharticket(interaction: discord.Interaction):
    mod = interaction.guild.get_role(id_cargo_atendente)
    if str(interaction.user.id) in interaction.channel.name or mod in interaction.author.roles:
        await interaction.response.send_message(f"O ticket foi arquivado por {interaction.user.mention}, obrigado por entrar em contato!")
        await interaction.channel.edit(archived=True, locked=True)
    else:
        await interaction.response.send_message("Isso não pode ser feito aqui...")

aclient.run("")
