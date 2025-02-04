from discord.ext import commands, tasks
from googleapiclient import discovery
import os
import pickle
from pathlib import Path
from datetime import datetime, timezone

class NewVideoHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.video_cache = {}
        self.channel_id = 'UCX3eufnI7A2I7IkKHZn8KSQ'
        self.uploads_playlist_id = 'UU' + self.channel_id[2:]
        self.load_video_cache()
        self.check_for_new_videos.start()

    def load_video_cache(self):
        try:
            if Path('video_cache.pkl').exists():
                with open('video_cache.pkl', 'rb') as f:
                    self.video_cache = pickle.load(f)
                print(f"Video cache loaded: {len(self.video_cache)} videos")
        except Exception as e:
            print(f"Error loading video cache: {e}")
            self.video_cache = {}

    def save_video_cache(self):
        try:
            with open('video_cache.pkl', 'wb') as f:
                pickle.dump(self.video_cache, f)
        except Exception as e:
            print(f"Error saving video cache: {e}")

    async def initialize_cache(self):
        """Initialize cache with the last 50 videos"""
        try:
            youtube = discovery.build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
            
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=self.uploads_playlist_id,
                maxResults=50
            )
            
            response = request.execute()
            
            for item in response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                published_at = datetime.strptime(
                    item['snippet']['publishedAt'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
                
                self.video_cache[video_id] = {
                    'title': item['snippet']['title'],
                    'published_at': published_at
                }
            
            self.save_video_cache()
            print(f"Cache initialized with {len(self.video_cache)} videos")
            
        except Exception as e:
            print(f"Error initializing cache: {e}")

    @tasks.loop(minutes=30)
    async def check_for_new_videos(self):
        try:
            youtube = discovery.build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
            
            request = youtube.playlistItems().list(
                part='snippet',
                playlistId=self.uploads_playlist_id,
                maxResults=5
            )
            
            response = request.execute()
            
            if not response['items']:
                return
                
            for item in response['items']:
                video_id = item['snippet']['resourceId']['videoId']
                published_at = datetime.strptime(
                    item['snippet']['publishedAt'], 
                    '%Y-%m-%dT%H:%M:%SZ'
                ).replace(tzinfo=timezone.utc)
                
                if video_id not in self.video_cache:
                    print(f"New video found: {item['snippet']['title']} ({published_at})")
                    self.video_cache[video_id] = {
                        'title': item['snippet']['title'],
                        'published_at': published_at
                    }
                    self.save_video_cache()
                    
                    channel = self.bot.get_channel(int(os.getenv('VIDEO_CHANNEL')))
                    if channel:
                        video_title = item['snippet']['title']
                        video_url = f'https://www.youtube.com/watch?v={video_id}'
                        await channel.send(f"**New Video!**\n{video_title}\n{video_url}")
                    
        except Exception as e:
            print(f"Error checking for new videos: {e}")

    @check_for_new_videos.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()
        if not self.video_cache:
            await self.initialize_cache()

    def get_sorted_videos(self):
        """Return videos sorted by publish date, newest first"""
        return sorted(
            [(vid_id, data) for vid_id, data in self.video_cache.items()],
            key=lambda x: x[1]['published_at'],
            reverse=True
        )

async def setup(bot):
    await bot.add_cog(NewVideoHandler(bot))
