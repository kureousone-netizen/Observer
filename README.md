The script uses a lot of built-in modules like sys, logging, time, and the like, but the real-time observation is something that is sadly, 
quite lacking in the Python standard library, but be of good cheer, as that's your one and ONLY dependency!

It can be installed with the command:

```pip install watchdog```

From there, you'd do well to run it from the terminal, giving it your target folder as the argument to sys.argv[1] (basically, the argument that comes after python or python3). For example, you'd write:

```python organizer.py "C:\example\folder"``` 
for Windows and
```python3 organizer.py /home/example/folder```
for MacOs and Linux

If you don't do that, however, don't fear! The script will default to a simple input prompt (if you don't want to run it from the terminal). Just provide it the folder you want to watch, and it will
work just as well. Ideally, you should look to how you can run it as a background task, but due to the respective differences you may encounter from system to system, I'll leave that to the more 
adventurous among us to figure out! :D

You can view this [demo](https://www.linkedin.com/feed/update/urn:li:activity:7486376651149250560/), if you're curious about how it works
