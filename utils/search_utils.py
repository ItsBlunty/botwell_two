import discord
from googleapiclient import discovery

search_results = {}

def search_channel(query, channel_id, api_key):
    try:
        youtube = discovery.build('youtube', 'v3', developerKey=api_key)

        request = youtube.search().list(
            part='snippet',
            q=query,
            channelId=channel_id,
            type='video',
            maxResults=30
        )

        response = request.execute()
        return response
    except Exception as e:
        print(f"YouTube API error: {str(e)}")
        return None

def format_video_results(results, start_index):

    embed = discord.Embed(color=discord.Color.dark_purple())

    if len(results['items']) < start_index + 3:
        return None

    if results['items']:
        video = results['items'][start_index]
        video2 = results['items'][start_index + 1]
        video3 = results['items'][start_index + 2]
        videoname = video['snippet']['title']
        videoname2 = video2['snippet']['title']
        videoname3 = video3['snippet']['title']
        video_id = video['id']['videoId']
        video_id2 = video2['id']['videoId']
        video_id3 = video3['id']['videoId']
        url = f'https://www.youtube.com/watch?v={video_id}'
        url2 = f'https://www.youtube.com/watch?v={video_id2}'
        url3 = f'https://www.youtube.com/watch?v={video_id3}'

        embed.add_field(name="", value="For more results, respond `!more`\nTo show a specific result, respond `!result 2`\nPlease report any issues to <@152656828193439744>", inline=False)
        embed.add_field(name="Result 1", value="[" + videoname + "](" + url + ")", inline=True)
        embed.add_field(name="Result 2", value="[" + videoname2 + "](" + url2 + ")", inline=True)
        embed.add_field(name="Result 3", value="[" + videoname3 + "](" + url3 + ")", inline=True)
    
    return embed

