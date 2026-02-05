This is Betakontext/math-bird-game

A basic maths training game written in Python. It uses Pygame with Pygbag (Wasm) to integrate Python code into browsers. An additional UI is added on top, using an html wrapper overlay with Java Script for virtual numbpad and buttons, in case a mobile device gets detected.

You can download main.py to explore the actual state of the game offline f.e. out if IDLE or from command line, bash: python3 main.py

If you want to test it like on a mobile device, including the UI of virtual keys etc. download build/web/ folder, which contains favicon.png, index.html and math_bird.apk.
Start a local server inside the downloaded directory.
On Linux f.e. bash: python3 -m http.server 8000
Then open your browser and URL:
http://127.0.0.1:8000/index.html?forceMobile=1
The ?forceMobile=1 behind the URL to index, lets the app read the browser as mobile device and triggers the UI layer for mobile devices.

Feel free and participate to build up on that state, integrating further maths and or game options.

Fork, explore and have fun
https://dev.betakontext.de
dev@betakontext.de
