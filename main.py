import discord
from discord.ext import commands
from discord.utils import get
import logging
from dotenv import load_dotenv
import os
import asyncio
import datetime
import responses

load_dotenv()

token = os.getenv('DISCORD_TOKEN')


#handles logging
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

#creates instance of bot
bot = commands.Bot(command_prefix='-', intents=intents)

#load swear words
swears = ''
with open("censored.txt", 'r') as f:
    swears = f.read()

swears = swears.split('\n')



@bot.event
async def on_ready():
    print(f"{bot.user.name} is online")
    while True:
        #print("cleared")
        await asyncio.sleep(10)
        with open("spam.txt", "r+") as f:
            f.truncate(0)


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    text = message.content.split()
    
    #checks and removes content with censored words
    for words in swears:
        for word in text:
            if word.lower() == words.lower():
                await message.delete()
                await message.channel.send(f"Please refrain from using profanity {message.author.mention}")

    if 'http' in message.content:
        roles = message.author.roles
        role_names = [role.name for role in roles]

        if not 'Instructor' in role_names or not 'CS Team Member' in role_names:
            await message.delete()
            await message.channel.send(f"Links are not permitted to be sent {message.author.mention}")

    counter = 0
    with open("spam.txt", "r+") as f:
        for line in f:
            if (line.strip("\n") == str(message.author.id)):
                counter +=1

        f.writelines(f"{str(message.author.id)}\n")
        if counter > 5:
            #grab instance of member
            member = message.channel.guild.get_member(message.author.id)
            
            #time-out member
            await member.timeout(datetime.timedelta(minutes=5),reason="Spam")
            await message.channel.send(f"{message.author.mention} was muted for 5m.")

    await bot.process_commands(message)


@bot.command(brief='archives the current channel')
@commands.has_role("CS Team Member")
async def archive(ctx, *, message):
    guild = ctx.message.guild
    category_dict = {"preuni": "Archived [Pre University]", "bootcamp": "Archived [Bootcamp]"}

    channel = ctx.channel

    category_name = category_dict[message]
    category = discord.utils.get(guild.categories, name=category_name)

    await channel.edit(category=category)

    hidden_list = ["Bootcamp", "Plus", "Pre University", "Learner", "Ai and ML with python", 
                "AI: Building Brains with Deep Learning", "Build and Code your own Computer: Raspberry Pi",
                "Building your Dream App with AI", "Video Game Coding", "Game Design with Unreal",
                "Cyber Defender: Ethical Hacking", "Finance and Investment Management", "Mobile App Development",
                "Drone Engineering with Python"]
    
    for r in hidden_list:
            role = get(ctx.guild.roles, name=r)
            await channel.set_permissions(role, view_channel = False)
    


@archive.error
async def create_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to do that")
    else:
        await ctx.send("Incorrect usage\n\nusage: -archive `category`")


@bot.command(brief='Lists all compatible class names with -create')
@commands.has_role("Instructor")
async def class_names(ctx):
    await ctx.send("## Class names:\n\n```aiml\nraspberry_pi"
                   "\ncyber_defender\ngame_design\nvideo_game_coding\n"
                   "building_brains\ndream_app\nfinance\nmobile_app"
                   "\ndrone_engineering\nsoftware_dev\nproduct_management"
                   "\ngame_development```")

@bot.command(brief='Creates a new class channel', description="usage: -create  'category' (preuni/bootcamp)  'course name'  'instructor lastname'  'course code'\n\nuse -class_names to access all posssible class names")
@commands.has_role("Instructor")
async def create(ctx, *, message):
    guild = ctx.message.guild
    try:

        text = message.split()
        category_input = text[0]
        course = text[1]
        instructor = text[2]
        code = text[3]


        category_dict = {"preuni": "📘 | Class Channels [Pre University]", 
                        "bootcamp": "📕 | Class Channels [Bootcamp]"}
        

        channel_emoji_dict = {
            "aiml": "📡・", 
            "raspberry_pi": "💻・",
            "cyber_defender": "🔌・",
            "game_design": "🎮・",
            "video_game_coding": "🕹️・",
            "building_brains": "🧠・",
            "dream_app": "🖥️・",
            "finance": "💰・",
            "mobile_app": "📱・",
            "drone_engineering":"🚁・",
            "software_dev": "⌨️・",
            "product_management": "🧾・",
            "game_development": "🖱️・"
        }

        channel_name = f"{channel_emoji_dict[course]}{course}_{instructor}-{code}"

        category_name = category_dict[category_input]
        category = discord.utils.get(guild.categories, name=category_name)

        channel = await guild.create_text_channel(channel_name)
        await channel.edit(category=category)

        await channel.set_permissions(guild.default_role, view_channel = False)

        await ctx.reply("Managing permissions...")

        hidden_list = ["Bootcamp", "Plus", "Pre University", "Learner", "Ai and ML with python", 
                "AI: Building Brains with Deep Learning", "Build and Code your own Computer: Raspberry Pi",
                "Building your Dream App with AI", "Video Game Coding", "Game Design with Unreal",
                "Cyber Defender: Ethical Hacking", "Finance and Investment Management", "Mobile App Development",
                "Drone Engineering with Python"]
        
        access_list = ["Student Experience", "CS Team Member", "Teaching Assistant"]


        #sets permissions to hide new channel from student roles
        for r in hidden_list:
            role = get(ctx.guild.roles, name=r)
            await channel.set_permissions(role, view_channel = False)

        for r in access_list:
            role = get(ctx.guild.roles, name=r)
            await channel.set_permissions(role, view_channel= True)

        member = ctx.guild.get_member(ctx.author.id)
        overwrite = channel.overwrites_for(member)
        overwrite.view_channel = True
        overwrite.create_instant_invite = True
        await channel.set_permissions(member, overwrite=overwrite)
        await ctx.reply("Channel created successfully!")

        

    except Exception as e:
       await ctx.send(f"Incorrect usage\n\nusage: -create  `'category' (preuni/bootcamp)`  `'class name'`  `'instructor lastname'`  `'course code'`\n\nuse -class_names to access all posssible class names")
    
@create.error
async def create_error(ctx, error):
    if isinstance(error,commands.MissingRole):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to do that")
    else:
        await ctx.send(f"Incorrect usage\n\nusage: -create  `'category' (preuni/bootcamp)`  `'class name'`  `'instructor lastname'`  `'course code'`\n\nuse -class_names to access all posssible class names")

@bot.command(brief='Deletes the current channel')
@commands.has_role("CS Team Member")
async def delete(ctx):
    channel = ctx.channel
    await channel.delete()  

@delete.error
async def delete_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"Sorry {ctx.author.mention}, you do not have permission to do that")
    else:
        await ctx.send(f"Error occured: {error}")



@bot.command(brief='Returns an AI assisted answer [BETA]')
async def ask(ctx, *, message):
    if ctx.channel.name != "ask-ai":
        await ctx.reply("I can only answer questions in `#ask-ai`")
        return
    query = message
    async with ctx.channel.typing():
        response = responses.get_response(query)
    tail_text = "\n\nI am just an AI tool in its beta testing stage, if you are unsatisfied with my answer please do not hesitate to reach out to a staff member! Happy learning!"
    await ctx.reply(response.output_text + tail_text)


@ask.error
async def ask_error(ctx, error):
    await ctx.send("I was unfortunately unable to answer that question... please reword and try again!")

@bot.command(brief="Exits the program (will shut the bot off)")
@commands.has_role("Admin")
async def shutdown(ctx):
    await ctx.reply("Shutting down...")
    await asyncio.sleep(3)
    exit()

@shutdown.error
async def shutdown_error(ctx,error):
    if isinstance(error,commands.MissingRole):
        await ctx.reply("Insufficient permissions")

    else:
        print(f"Error: {error}") 
    

bot.run(token, log_handler=handler, log_level=logging.DEBUG)



