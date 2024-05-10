# Bundle the program into a binary.
pyinstaller main.py --onefile \
--add-data pomodoro.conf:pomodoro.conf \
--add-data start.mp3:start.mp3 \
--add-data done.mp3:done.mp3

# Create a directory for the new build, and copy over needed files.
mkdir linux-build
cp dist/main linux-build/pomodoro
cp start.mp3 linux-build/start.mp3
cp done.mp3 linux-build/done.mp3
cp pomodoro.conf linux-build/pomodoro.conf