import asyncio
import json
import re
from wreq import Client, Emulation

def extract_video_data(html_content):
    """
    Finds the ytInitialData JSON inside the HTML and extracts 
    titles and URLs from all videoRenderer objects.
    """
    # 1. Use regex to find the `ytInitialData` variable which contains the JSON
    match = re.search(r'var ytInitialData = (\{.*?\});</script>', html_content)
    if not match:
        print("Could not find video data in the page.")
        return []

    # 2. Parse the JSON string into a Python dictionary
    # This automatically converts things like \u0026 into &
    raw_json = match.group(1)
    try:
        data = json.loads(raw_json)
    except json.JSONDecodeError:
        print("Error parsing the JSON data.")
        return []

    extracted_videos = []

    # 3. Create a recursive function to find all "videoRenderer" blocks inside the massive JSON
    def find_videos(obj):
        if isinstance(obj, dict):
            if 'videoRenderer' in obj:
                renderer = obj['videoRenderer']
                video_id = renderer.get('videoId')
                
                # Safely navigate the nested title dictionary
                try:
                    title = renderer['title']['runs'][0]['text']
                except (KeyError, IndexError):
                    title = "Unknown Title"
                
                # If we found a valid video ID, construct the full URL and save it
                if video_id:
                    extracted_videos.append({
                        'title': title,
                        'url': f'https://www.youtube.com/watch?v={video_id}'
                    })
            
            # Continue searching deeper into the dictionary
            for value in obj.values():
                find_videos(value)
                
        elif isinstance(obj, list):
            # Continue searching if it's a list
            for item in obj:
                find_videos(item)

    # Start the search
    find_videos(data)
    
    return extracted_videos

async def main():
    client = Client(emulation=Emulation.Safari26)
    url = "https://www.youtube.com/@devinahermawan/videos"
    
    print(f"Fetching {url}...")
    resp = await client.get(url)
    html_content = await resp.text()
    
    print("Extracting video titles and URLs...\n")
    videos = extract_video_data(html_content)
    
    # 4. Print the final results and optionally save them to a file
    with open("parsed_videos.txt", "w", encoding="utf-8") as f:
        for idx, video in enumerate(videos, start=1):
            output_line = f"{idx}. {video['title']}\n   {video['url']}\n"
            print(output_line.strip())
            f.write(output_line + "\n")
            
    print(f"\nSuccessfully extracted {len(videos)} videos and saved to parsed_videos.txt")

if __name__ == "__main__":
    asyncio.run(main())