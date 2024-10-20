# Unlimited Views

Get unlimited views on YouTube with this script! Simply place your satisfying or car footage (or any video) in `footage.mp4` in the same directory. The script will generate voice audio from Reddit. You can change the subreddit in the code on line 104 and edit the number of videos to make on line 109. Although it only makes 30 for some reason and it says it made 28, so that might not work, anyway — it’s not fancy AI TTS with CUDA, but it gets the job done.

**Note:** On line 112, the script changes to the number of threads your CPU has or 1 even. If you get an error about ffmpeg, don't worry about it; it should still do it without ffmpeg.

## WARNING ⚠️

### Beware of PC Strain
- This script requires a significant amount of disk space.
- It is power-hungry and you'll need at least **16GB of RAM**.
- The script utilizes multithreading and will max out your CPU usage. It even maxed out my 24-thread i7.

**Important:** Do not attempt to perform other heavy tasks while this script is running.
