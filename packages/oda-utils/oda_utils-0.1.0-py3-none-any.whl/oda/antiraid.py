import discord
from discord.ext import commands

def detect_raid(whitelist: list[int], log_channel_id: int):
    class AntiRaid(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.Cog.listener()
        async def on_member_join(self, member: discord.Member):
            if not member.bot:
                return

            guild = member.guild
            try:
                entry = None
                async for log in guild.audit_logs(limit=5, action=discord.AuditLogAction.bot_add):
                    if log.target.id == member.id:
                        entry = log
                        break

                if not entry:
                    return

                author = entry.user
                if author.id in whitelist:
                    return

                try:
                    roles_to_remove = [role for role in author.roles if role.name != "@everyone"]
                    await author.remove_roles(*roles_to_remove, reason="AntiRaid - Bot no autorizado")
                except Exception as e:
                    print(f"[AntiRaid] No se pudieron quitar roles a {author}: {e}")

                try:
                    await member.ban(reason="AntiRaid - Bot no autorizado")
                except Exception as e:
                    print(f"[AntiRaid] No se pudo banear al bot {member}: {e}")

                embed = discord.Embed(
                    title="<a:siren:1401291154078564433> Anti-Raid Activado <a:siren:1401291154078564433>",
                    description="**Se ha detectado un bot no autorizado.**",
                    color=discord.Color.red()
                )
                embed.add_field(name="<:usuarios:1401570272745750673> Usuario que lo agregó", value=f"{author.mention} (`{author.id}`)", inline=False)
                embed.add_field(name="<:bot:1401291178518909210> Bot detectado", value=f"{member.mention} (`{member.id}`)", inline=False)
                embed.set_footer(text=guild.name)
                embed.timestamp = discord.utils.utcnow()

                canal_logs = guild.get_channel(log_channel_id)
                if canal_logs:
                    await canal_logs.send(embed=embed)

                try:
                    dm_embed = discord.Embed(
                        title="<a:758027033761677444:1401291110579572746> Tu bot fue eliminado",
                        description=f"Agregaste un bot no autorizado a **{guild.name}**. Fue **baneado automáticamente** y tus roles fueron removidos.",
                        color=discord.Color.orange()
                    )
                    dm_embed.add_field(name="Bot que agregaste", value=f"{member.name} (`{member.id}`)", inline=False)
                    dm_embed.set_footer(text="Sistema AntiRaid - Contacta al staff si fue un error")
                    dm_embed.timestamp = discord.utils.utcnow()

                    await author.send(embed=dm_embed)
                except Exception as e:
                    print(f"[AntiRaid] No se pudo enviar DM a {author}: {e}")

            except Exception as e:
                print(f"[AntiRaid] Error general: {e}")

    async def setup(bot):
        await bot.add_cog(AntiRaid(bot))

    return setup
