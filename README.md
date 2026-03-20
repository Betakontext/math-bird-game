# MATH-BIRD-GAME

A basic maths training game written in Python, using Pygame with Pygbag (Wasm) to integrate Python code into browsers. An additional UI Layer is added on top, using an html wrapper overlay with Java Script for virtual numbpad and buttons, in case a mobile device gets detected.
______________
Online version: https://dev.betakontext.de/math-bird-game
______________
You can download main.py to explore the actual state of the game offline f.e. out if Python via IDLE or from command line, bash: python3 main.py
If you want to test it simulating a mobile device, including the UI of virtual keys etc. download build/web/ folder, which contains favicon.png, index.html and math_bird.apk.

Start a local server inside the downloaded directory.

	python3 -m http.server 8000

Then open http://localhost:8000/ in your browser.
ctrl+c in the terminal closes the server.

Use /index-html?forceMobile=1 to read the browser as mobile device and trigger the UI, on JS overlay layer for mobile devices.
______________

Feel free to build up on that state to integrate further maths and-or game options.

Guideline to use pygbag and rebuild the apk f.e. on linux:

Install python3-venv:

	sudo apt update
	sudo apt install -y python3-venv python3-full

Create venv (in project folder)

	python3 -m venv .venv

Activate venv:

	source .venv/bin/activate

Check:

	python -V
	pip -V

Install Pygbag in venv:

	pip install -U pip setuptools wheel
	pip install pygbag

Build:

	python -m pygbag --build .

Overlay: Extension of build/web/index.html vornehmen:

	python patch-build.py

For lokal test	switch to build/web:

	python3 -m http.server 8000

Open in browser:

	http://localhost:8000/

To test the overlay (only visible on mobile devices) on desktop:

		URL… 	?forceMobile=1
		F.e.:	https://URL/index.html?forceMobile=1


Fork and explore.

The project is build with AI assistance and under MIT licence.
CONTACT: Christoph Medicus | dev@betakontext.de
