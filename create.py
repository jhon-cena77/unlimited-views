import requests
from bs4 import BeautifulSoup
from gtts import gTTS
from mutagen.mp3 import MP3
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip
import concurrent.futures
import threading
import os

# Step 1: Fetch posts from Reddit
def fetch_posts(subreddit, limit=50):
    url = f"https://old.reddit.com/r/{subreddit}/hot/"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        posts = []

        for post in soup.find_all('div', class_='thing', limit=limit):
            title = post.find('a', class_='title').text
            selftext = post.find('div', class_='expando').text if post.find('div', class_='expando') else ''
            content = f"{title}\n{selftext}"
            posts.append(content)

        return posts
    else:
        print(f"Failed to fetch posts: {response.status_code}")
        return []

# Step 2: Create TTS and check its length using mutagen
def text_to_speech(text, filename):
    tts = gTTS(text=text, lang='en')
    tts.save(filename)
    
    # Use mutagen to measure duration of the TTS output
    audio = MP3(filename)
    duration = audio.info.length  # Get duration in seconds
    return duration

# Step 3: Adjust video to match TTS duration and overlay TTS
def adjust_and_overlay_video(input_video, tts_audio, output_video, tts_duration, video_start):
    video = VideoFileClip(input_video)

    # Check if remaining footage is less than TTS duration, loop if necessary
    video_duration = video.duration
    video_end = video_start + tts_duration

    if video_end > video_duration:
        # We need to loop the footage
        video = video.subclip(video_start, video_duration)  # Use remaining footage
        remaining_duration = tts_duration - (video_duration - video_start)
        video_loop = VideoFileClip(input_video).subclip(0, remaining_duration)  # Loop from start
        video = video.concat([video, video_loop])
    else:
        # If the video is long enough, just trim to match TTS duration
        video = video.subclip(video_start, video_end)

    # Reduce video volume to 25%
    video = video.volumex(0.25)

    # Load the TTS audio
    tts = AudioFileClip(tts_audio)

    # Overlay the TTS audio onto the video
    final_audio = CompositeAudioClip([video.audio, tts])
    final_video = video.set_audio(final_audio)

    # Write the final video
    final_video.write_videofile(output_video, codec='libx264')

    # Return the point where the video stopped
    return video_end % video_duration  # If we looped, return the point after the loop

# Create a lock for thread-safe access to video_start
video_start_lock = threading.Lock()
video_start = 0  # Global variable to track video start position

# Function to process each post
def process_post(post, index, input_video, output_prefix):
    global video_start  # Declare video_start as global
    tts_filename = f"tts_audio_{index}.mp3"
    duration = text_to_speech(post, tts_filename)

    if duration < 58:
        print(f"TTS duration: {duration} seconds. Proceeding with this post.")

        # Generate the output filename
        output_video = f"{output_prefix}{index}.mp4"

        # Use the lock to safely read and update video_start
        with video_start_lock:
            current_video_start = video_start
            video_start += duration  # Increment the video start for the next thread

        # Adjust video and overlay TTS based on TTS duration
        adjust_and_overlay_video(input_video, tts_filename, output_video, duration, current_video_start)

        print(f"Final video saved as {output_video}")
    else:
        print(f"TTS duration: {duration} seconds. Skipping this post.")

def main():
    subreddit = "askreddit"
    input_video = "footage.mp4"
    output_prefix = "output"

    # Fetch posts from subreddit
    posts = fetch_posts(subreddit, limit=100)

    # Use a ThreadPoolExecutor to manage concurrent threads
    with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
        # Prepare futures for the TTS and video processing
        futures = {executor.submit(process_post, post, i + 1, input_video, output_prefix): i + 1 for i, post in enumerate(posts)}

        for future in concurrent.futures.as_completed(futures):
            index = futures[future]
            try:
                future.result()  # We can also collect the result if needed
            except Exception as e:
                print(f"Post {index} generated an exception: {e}")

if __name__ == "__main__":
    main()