import discord
from discord.ext import tasks, commands
import praw
import random
import os
from dotenv import load_dotenv
from flask import Flask
from threading import Thread

# Load secrets from .env
load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID")
REDDIT_SECRET = os.getenv("REDDIT_SECRET")
REDDIT_USER_AGENT = "cursed-news-bot"

# Discord bot setup
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Reddit API setup
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

# Subreddits to pull from
subreddits = [
    "nottheonion", "IllegallySmolCats", "aww","technicallythetruth", "unexpected","cats","LilGrabbies","shitposting","femboy","relationship_advice","nicegus","nicegirls","atetheonion","creepypms","iamverysmart","sadcringe"
]

# Web server to keep Replit alive
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()



@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    post_news.start()

@tasks.loop(seconds=120)
async def post_news():
    try:
        subreddit = reddit.subreddit(random.choice(subreddits))
        posts = list(subreddit.hot(limit=25))
        random.shuffle(posts)

        for post in posts:
            

            # Images
            if post.url.endswith((".jpg", ".png", ".gif", ".jpeg", ".webp")):
                await send_post(post)
                break

            # Reddit-hosted videos
            elif "v.redd.it" in post.url:
                if post.media and "reddit_video" in post.media:
                    video_url = post.media["reddit_video"]["fallback_url"]
                    await send_post(post, video_url)
                    break

            # YouTube or other video links
            elif "youtube.com" in post.url or "youtu.be" in post.url:
                await send_post(post)
                break

    except Exception as e:
        print(f"Error posting: {e}")

async def send_post(post, override_url=None):
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        await channel.send(f"**{post.title}**\n{override_url or post.url}")
keep_alive()
bot.run(DISCORD_TOKEN)
