import requests
import os
import subprocess
import aiohttp
import asyncio

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept': '/',
    'Accept-Language': 'en-US,en;q=0.5',
    # 'Accept-Encoding': 'gzip, deflate, br, zstd',
    'Referer': 'https://kick.com/alfie',
    'DNT': '1',
    'Sec-GPC': '1',
    'Connection': 'keep-alive',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

async def validate_response(response):
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse JSON data from the response
        json_data = response.json()
        return json_data
    else:
        # If error getting json data
        raise Exception('Error retrieving json data. Invalid Parameters or API Endpoint is down.')

async def download_clip(url):
    clip_id = url.split('_')[-1] # Extract the clip ID from the URL
    clip_api_url = f"https://kick.com/api/v2/clips/clip_{clip_id}"
    response = await validate_response(requests.get(clip_api_url, headers=headers)) 

    video_url = response['clip']['video_url'] # Extract the video URL from the JSON response
    if '.mp4' in video_url: # If the video URL is a direct link to the video
        return clip_id, video_url # Return the clip ID and the video URL
    
    video_partitions = requests.get(video_url) # Otherwise we have to extract the video partitions

    # Create a folder with the output_filename inside the 'clips' folder
    output_dir = os.path.join('clips', clip_id)
    if os.path.exists(output_dir): # If the folder already exists
        await asyncio.sleep(30)    # Wait a bit for the first process to finish uploading the video
        return clip_id, 'cached'   # Then return 'cached' to indicate that the video is cached
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    partitions_path = os.path.join(output_dir, f"{clip_id}.txt") # This file contains the list of partitions

    partitions = []
    if video_partitions.status_code != 200:
        raise Exception('Error retrieving video partitions')
    else:
        # Write content to the file 
        with open(partitions_path, 'wb') as file:
            file.write(video_partitions.content)
        with open(partitions_path , 'rt') as file:
            for line in file:
                # Remove trailing newline character
                line = line.rstrip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Add unique line to the array
                if line not in partitions:
                    partitions.append(line) # Append the partition to the list
    clip_prefix = response['clip']['thumbnail_url'].split('thumbnail.png')[0] # Extract the clip prefix
    clip_links = [f"{clip_prefix}{partition}" for partition in partitions]    # Assemble the clip links
    clip_filepath = await download_and_assemble(clip_links, output_dir, clip_id) # Download, assemble, and compress the clip
    return clip_id, clip_filepath


async def download_and_assemble(urls, output_dir, output_filename):
    # Download all segments and concatenate to a single .ts file
    concatenated_ts = os.path.join(output_dir, f"{output_filename}_concatenated.ts")

    with open(concatenated_ts, 'wb') as outfile:
        for url in urls:
            response = requests.get(url, stream=True)  # Download the video segment
            if response.status_code == 200:
                outfile.write(response.content)  # Write the video segment to the output file
                print(f"Appended: {url}")
            else:
                print(f"Failed to download: {url}")

    print(f"All segments assembled into: {concatenated_ts}")

    # Compress the .ts video and convert to .mp4 in a single command
    output_mp4 = os.path.join(output_dir, f"{output_filename}.mp4")
    compression_command = [
    'ffmpeg', '-i', concatenated_ts, '-vf', 'scale=854:480', '-c:v', 'h264_nvenc',
    '-rc', 'vbr_hq', '-cq:v', '25', '-qmin:v', '20', '-qmax:v', '30', '-profile:v', 'high', '-preset', 'llhp',
    '-b:v', '700k', '-max_muxing_queue_size', '9999',
    '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', output_mp4
]
    subprocess.run(compression_command)

    return output_mp4
