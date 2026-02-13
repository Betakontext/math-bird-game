This is a basic maths training game written in Python. It uses Pygame with Pygbag (Wasm) to integrate Python code into browsers. An additional UI is added on top, using an html wrapper overlay with Java Script for virtual numbpad and buttons, in case a mobile device gets detected.
---------------
Online version: https://dev.betakontext.de/math-bird-game
---------------
You can download main.py to explore the actual state of the game offline f.e. out if Python via IDLE or from command line, bash: python3 main.py
If you want to test it simulating a mobile device, including the UI of virtual keys etc. download build/web/ folder, which contains favicon.png, index.html and math_bird.apk.
Start a local server inside the downloaded directory.
bash: python3 -m http.server 8000
Then open http://localhost:8000/ in your browser.
ctrl+c in the terminal closes the server.
Try /index-html?forceMobile=1 to read the browser as mobile device and trigger the UI, on JS overlay layer for mobile devices.
---------------

The project is build with AI assistance and under MIT licence.
Fork and feel free to build up on that state, integrating further maths and/or game options.

CONTACT: Christoph Medicus | dev@betakontext.de
