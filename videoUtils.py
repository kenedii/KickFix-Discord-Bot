import requests
import os
import subprocess

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0',
    'Accept': '*/*',
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

def validate_response(response):  # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse JSON data from the response
            json_data = response.json()
            return json_data
        else:  # If error getting json data
            raise Exception('Error retrieving json data. Invalid Parameters or API Endpoint is down.')

def download_clip(url):
    clip_id = url.split('_')[-1]
    clip_api_url = f"https://kick.com/api/v2/clips/clip_{clip_id}"
    response = validate_response(requests.get(clip_api_url, headers=headers))
    video_url = response['clip']['video_url']
    video_partitions = requests.get(video_url)
    partitions = []
    if video_partitions.status_code != 200:
        raise Exception('Error retrieving video partitions')
    else:
         # Write content to the file (assuming response.content is the data)
        with open(f"{clip_id}.txt", 'wb') as file:
            file.write(video_partitions.content)
        with open(f"{clip_id}.txt" , 'rt') as file:
            for line in file:
                # Remove trailing newline character
                line = line.rstrip()
                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue
                # Add unique line to the array
                if line not in partitions:
                    partitions.append(line)
    clip_prefix = response['clip']['thumbnail_url'].split('thumbnail.png')[0]
    clip_links = [f"{clip_prefix}{partition}" for partition in partitions]
    clip_filepath = download_and_assemble(clip_links, clip_id)
    return clip_id, clip_filepath
         
def download_and_assemble(urls, output_filename):
    # Create the 'clips' folder if it doesn't exist
    if not os.path.exists('clips'):
        os.makedirs('clips')
    
    # Create a folder with the output_filename inside the 'clips' folder
    output_dir = os.path.join('clips', output_filename)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"{output_filename}.ts")
    
    with open(output_file, 'wb') as outfile:
        for url in urls:
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        outfile.write(chunk)
                print(f"Appended: {url}")
            else:
                print(f"Failed to download: {url}")
    
    print(f"All segments assembled into: {output_file}")

    # Convert the concatenated .ts file to .mp4
    output_file = os.path.join(output_dir, f"{output_filename}.mp4")
    command = ['ffmpeg', '-i', output_file, '-c', 'copy', output_file]
    subprocess.run(command)
    return output_file


