import requests
import os
import subprocess

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

def validate_response(response):
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse JSON data from the response
        json_data = response.json()
        return json_data
    else:
        # If error getting json data
        raise Exception('Error retrieving json data. Invalid Parameters or API Endpoint is down.')

def download_clip(url):
    clip_id = url.split('_')[-1]
    clip_api_url = f"https://kick.com/api/v2/clips/clip_{clip_id}"
    response = validate_response(requests.get(clip_api_url, headers=headers))

    video_url = response['clip']['video_url']
    if '.mp4' in video_url:
        return clip_id, video_url
    video_partitions = requests.get(video_url)

    # Create a folder with the output_filename inside the 'clips' folder
    output_dir = os.path.join('clips', clip_id)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    partitions_path = os.path.join(output_dir, f"{clip_id}.txt")

    partitions = []
    if video_partitions.status_code != 200:
        raise Exception('Error retrieving video partitions')
    else:
        # Write content to the file (assuming response.content is the data)
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
                    partitions.append(line)
    clip_prefix = response['clip']['thumbnail_url'].split('thumbnail.png')[0]
    clip_links = [f"{clip_prefix}{partition}" for partition in partitions]
    clip_filepath = download_and_assemble(clip_links, output_dir, clip_id)
    return clip_id, clip_filepath

def download_and_assemble(urls, output_dir, output_filename):
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
    output_mp4 = os.path.join(output_dir, f"{output_filename}.mp4")
    command = ['ffmpeg', '-i', output_file, '-c', 'copy', output_mp4]
    subprocess.run(command, text=False, capture_output=False)

    # Check the size of the output .mp4 file
    if os.path.exists(output_mp4):
        file_size_mb = os.path.getsize(output_mp4) / (1024 * 1024)  # in MB
        print(f"Output file size: {file_size_mb} MB")

        # If the file size exceeds 25MB, compress it
        if file_size_mb > 25:
            compressed_mp4 = os.path.join(output_dir, f"{output_filename}_compressed.mp4")
            compression_command = ['ffmpeg', '-i', output_mp4, '-vf', 'scale=-1:720', '-c:v', 'libx264', '-crf', '23', '-preset', 'medium', compressed_mp4]
            subprocess.run(compression_command, text=False, capture_output=False)
            
            # Check the size of the compressed file
            compressed_size_mb = os.path.getsize(compressed_mp4) / (1024 * 1024)
            print(f"Compressed file size: {compressed_size_mb} MB")
            
            # Use compressed file if it's smaller than original, otherwise keep original
            if compressed_size_mb < file_size_mb:
                os.remove(output_mp4)  # Remove the original large file
                return compressed_mp4
            else:
                return output_mp4
    return output_mp4
