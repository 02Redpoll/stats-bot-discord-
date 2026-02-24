import discord
from discord.ext import tasks
import a2s
import asyncio

# Discord токен (вставьте сюда)
TOKEN = 'ваш_токен_бота'

# Настройки игрового сервера
SERVER_IP = '127.0.0.1'        # IP вашего сервера
SERVER_PORT = 28083             # Порт сервера

# ID вашего Discord сервера (вставьте сюда)
ALLOWED_GUILD_ID = 123456789012345678

# Карусель эмодзи (можно изменить под свои)
EMOJI_CAROUSEL = ['⚡', '🔥', '💫', '🍃', '🌊', '❄️', '🌱', '☀️', '🌙', '⭐', '🎮']
current_emoji_index = 0

intents = discord.Intents.none()
intents.guilds = True

class StatusBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.last_online = 0
        self.is_ready = False  
    
    async def setup_hook(self):
        self.update_status.start()
        self.rotate_emojis.start()
    
    @tasks.loop(seconds=15)
    async def rotate_emojis(self):
        global current_emoji_index
        current_emoji_index = (current_emoji_index + 1) % len(EMOJI_CAROUSEL)
    
    @tasks.loop(seconds=5)
    async def update_status(self):
        
        if not self.is_ready or self.is_closed():
            return
        
        try:
            players = await asyncio.to_thread(a2s.players, ADDRESS, timeout=3.0)
            online_count = len(players)
            self.last_online = online_count
            
            current_emoji = EMOJI_CAROUSEL[current_emoji_index]
            status_text = f"{current_emoji} сейчас играет {online_count}/100 игроков"
            
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=status_text
                )
            )
            
        except Exception:
            current_emoji = EMOJI_CAROUSEL[current_emoji_index]
            if self.last_online > 0:
                status_text = f"{current_emoji} сейчас играет {self.last_online}/100 игроков?"
            else:
                status_text = f"{current_emoji} сервер оффлайн"
            
            await self.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.playing,
                    name=status_text
                ),
                status=discord.Status.idle
            )

bot = StatusBot()

@bot.event
async def on_ready():
    print(f'✅ Бот {bot.user} запущен')
    
    guild = bot.get_guild(ALLOWED_GUILD_ID)
    if guild:
        print(f'✅ На сервере: {guild.name}')
    else:
        print(f'❌ Бот не на сервере ID: {ALLOWED_GUILD_ID}')
    
    bot.is_ready = True  

@bot.event
async def on_guild_join(guild):
    if guild.id != ALLOWED_GUILD_ID:
        print(f'❌ Чужой сервер: {guild.name}')
        await guild.leave()

if __name__ == "__main__":
    bot.run(TOKEN)