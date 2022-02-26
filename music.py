import discord
from discord.ext import commands
import youtube_dl
import asyncio

queues = {}
queueNames = {}

class music(commands.Cog):
  def __init__(self, client):
      self.client = client
      infos = None

  
  def check_queue(self,ctx, id):
    if queues[id] != []:
      voice = ctx.guild.voice_client
      source = queues[id].pop(0)
      name = queueNames[id].pop(0)
      voice.play(source)
      embed = discord.Embed(title = "", description = f"Now playing {name} [{ctx.author.mention }]", colour = 0xEAD787)      
      #channel = ctx.author.voice.channel
      self.client.loop.create_task(ctx.send(embed = embed))  

  @commands.command()
  async def join(self,ctx):
      if ctx.author.voice is None:
        embed = discord.Embed(title = "", description = "You're not in a VC! Join a VC to play music.", colour = discord.Colour.red(), delete_after=5)        
        await ctx.send(embed = embed)
      if ctx.voice_client is None:
        voice_channel = ctx.author.voice.channel
        self.queue = {}
        await voice_channel.connect()
      else:
          voice_channel = ctx.author.voice.channel
          await ctx.voice_client.move_to(voice_channel)

  @commands.command()
  async def play(self,ctx,*url):
    
      if ctx.author.voice is None:
          await ctx.send("You're not in a voice channel!")
      voice_channel = ctx.author.voice.channel
      if ctx.voice_client is None:
          await voice_channel.connect()
      else:
          await ctx.voice_client.move_to(voice_channel)
      FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
      YDL_OPTIONS = {'format':"bestaudio"}
      vc = ctx.voice_client
      if(url):
        print(url)
        ctx.voice_client.stop()
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
          if("youtube.com" in url or "youtu" in url):
            info = ydl.extract_info(url, download=False)
            linkdes = url
            info = self.info
            
          else:
            keywords = ""
            for i in url:
              keywords += i
            keyword = ydl.extract_info(f"ytsearch:{url}", download=False)
            url2 = keyword['entries'][0]['webpage_url']
            info = ydl.extract_info(url2, download=False)
            linkdes = url2
            global infos
            infos = info
          url3 = info['formats'][0]['url']
          video_title = info.get('title', None)
          
          source = await discord.FFmpegOpusAudio.from_probe(url3, **FFMPEG_OPTIONS)
          guild_id = ctx.message.guild.id
          vc.play(source, after=lambda x=None: self.check_queue(ctx, ctx.message.guild.id))
          embed = discord.Embed(title = "", description = f"Now playing [{video_title}]({linkdes}) [{ctx.author.mention }]", colour = 0xEAD787)        
          await ctx.send(embed = embed)
      else:
        vc.resume()

  @commands.command()
  async def queue(self,ctx, *url):
    YDL_OPTIONS = {'format':"bestaudio"}
    FFMPEG_OPTIONS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    guild_id = ctx.message.guild.id
    if(url):
        with youtube_dl.YoutubeDL(YDL_OPTIONS) as ydl:
            if("youtube.com" in url):
              info = ydl.extract_info(url, download=False)
              linkdes = url
              info = self.info
            else:
              keywords = ""
              for i in url:
                keywords += i
              keyword = ydl.extract_info(f"ytsearch:{url}", download=False)
              url2 = keyword['entries'][0]['webpage_url']
              info = ydl.extract_info(url2, download=False)
              linkdes = url2
              global infos
              infos = info
            url3 = info['formats'][0]['url']
            video_title = info.get('title', None)
            
            source = await discord.FFmpegOpusAudio.from_probe(url3, **FFMPEG_OPTIONS)
            if guild_id in queues and guild_id in queueNames:
              queues[guild_id].append(source)
              queueNames[guild_id].append(video_title)
            else:
              queues[guild_id] = [source]
              queueNames[guild_id] = [video_title]
            
            embed = discord.Embed(title = "", description = f"Queued [{video_title}]({linkdes}) [{ctx.author.mention }]", colour = 0x18191C)        
            await ctx.send(embed = embed)
    else:
      liste = "**Queue**  \n \n"
      try:
        if len(queues[guild_id]) == 0:
            embed = discord.Embed(title = "", description = "No songs in queue!", colour = discord.Colour.red())
            await ctx.send(embed = embed)
        else:
          for i in range(len(queues[guild_id])):
              liste += (str(i+1) + ". " + str(queueNames[guild_id][i]) + " \n ")
          embed = discord.Embed(title = "", description = ''.join(liste), colour = 0x18191C)
          await ctx.send(embed = embed)
      except:
        embed = discord.Embed(title = "", description = "No songs in queue!", colour = discord.Colour.red())
        await ctx.send(embed = embed)


  @commands.command()
  async def remove(self,ctx, num):
    if(num):
      try:
        guild_id = ctx.message.guild.id
        queues[guild_id].pop(int(num) - 1)
        queueNames[guild_id].pop(int(num) - 1)
        await ctx.message.add_reaction('👌')
      except:
        embed = discord.Embed(title = "", description = "Song selected for removal doesn't exist! Try again.", colour = discord.Colour.red())
        await ctx.send(embed = embed, delete_after=5)

  @commands.command()
  async def removeRange(self,ctx, first, second):
      firstn = int(first)
      secondn = int(second)
      try:
        while firstn <= secondn:
          guild_id = ctx.message.guild.id
          queues[guild_id].remove(queues[guild_id][int(first) - 1])
          queueNames[guild_id].remove(queueNames[guild_id][int(first) - 1])
          firstn += 1
        await ctx.message.add_reaction('👌')
      except:
        embed = discord.Embed(title = "", description = "Range was not specificied or numbers provided out of range. Try again.", colour = discord.Colour.red())
        await ctx.send(embed = embed, delete_after=5)

  @commands.command()
  async def clear(self,ctx, *url):
    guild_id = ctx.message.guild.id
    queues[guild_id].clear()
    queueNames[guild_id].clear()
    await ctx.message.add_reaction('👌')
  
  @commands.command()
  async def skip(self,ctx, *url):
    ctx.voice_client.stop()
    self.check_queue(ctx, ctx.message.guild.id)
    await ctx.message.add_reaction('👌')
  

    
  @commands.command()
  async def lyrics(self,ctx):
    global infos
    video_title = infos.get('lyrics', None)
    print(infos)
    await ctx.send(video_title)

  @commands.command()
  async def leave(self,ctx):
    try:
      await ctx.voice_client.disconnect()
      await ctx.message.add_reaction('👋')
    except:
      embed = discord.Embed(title = "", description = "I'm not currently in a VC.", colour = discord.Colour.red())        
      await ctx.send(embed = embed, delete_after=5)

  @commands.command()
  async def die(self,ctx):
    try:
      await ctx.voice_client.disconnect()
      await ctx.message.add_reaction('👋')
    except:
      embed = discord.Embed(title = "", description = "I'm not currently in a VC.", colour = discord.Colour.red())        
      await ctx.send(embed = embed, delete_after=5)

  @commands.command()
  async def disconnect(self,ctx):
    try:
      await ctx.voice_client.disconnect()
      await ctx.message.add_reaction('👋')
    except:
      embed = discord.Embed(title = "", description = "I'm not currently in a VC.", colour = discord.Colour.red())        
      await ctx.send(embed = embed, delete_after=5)
    

  
  
  @commands.command()
  async def pause(self,ctx):
    try:
      await ctx.voice_client.pause()
    except:
      await ctx.message.add_reaction('👌')
  
  @commands.command()
  async def stop(self,ctx):
    try:
      await ctx.voice_client.pause()
    except:
      await ctx.message.add_reaction('👌')
  
  @commands.command()
  async def resume(self,ctx):
    try:
      await ctx.voice_client.resume()
    except:
      await ctx.message.add_reaction('👌')

  @commands.command()
  async def help(self, ctx):
    list_msg ="__**LalSound Help Menu**__"
    result = "\n"
    embed = discord.Embed(
      title =  list_msg,
      description = ''.join(result),
      colour = discord.Colour.blue()
    )        

    embed.add_field(name="\n__**Purpose:**__", value="Play music in Discord VCs.", inline = False)    
    embed.add_field(name="Open Source Code", value="[Here](https://github.com/Tarun1877220/Discord-Music-Bot)")
    embed.add_field(name="\n__**Summoning The Bot:**__", value=f"-Use the command - to summon the bot\n -default prefix is - and cannot be changed as of now*\n\n", inline = False)    

    embed.add_field(name="__**Commands:**__", value="\n > -play [insert song name] - plays a song selected(not used for queuing) \n > -join - summons bot to join channel \n > -die/leave/disconnect - removes bot from channel \n > -pause/stop - pauses music \n > -play/resume - resumes the current song \n > -queue [song name] - adds song to queue or displays queue if no parameteres are given \n > -clear - clears the queue \n > -skip - skips over song current song to next one in queue \n > remove [num] - removes a song from queue \n > -removeRange[int x, int y] - removes a range of songs(not by index)", inline = False)
    await ctx.channel.send(embed = embed)

def setup(client):
  client.add_cog(music(client))

  '''
  if guild_id in queues:
    if (len(queues[guild_id]) > 0):
      if guild_id in queues and guild_id in queueNames:
        queues[guild_id].append(source)
        queueNames[guild_id].append(video_title)
      else:
        queues[guild_id] = [source]
        queueNames[guild_id] = [video_title]
      embed = discord.Embed(title = "", description = f"Queued [{video_title}]({linkdes}) [{ctx.author.mention }]", colour = discord.Colour.light_grey())        
    await ctx.send(embed = embed)
  else:
    queues[guild_id] = [source]
    queueNames[guild_id] = [video_title]
    vc.play(source, after=lambda x=None: self.check_queue(ctx, ctx.message.guild.id))
    embed = discord.Embed(title = "", description = f"Now playing [{video_title}]({linkdes}) [{ctx.author.mention }]", colour = discord.Colour.light_grey())        
    await ctx.send(embed = embed)
'''