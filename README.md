ssh -L 11434:127.0.0.1:11434 student@10.249.84.213
Keep this terminal open while you use the Ollama server.

This makes localhost:11434 on your Mac point to the Pi's Ollama server.

Set the environment variable
In a new terminal on your Mac, run:

export OLLAMA_HOST=http://localhost:11434




Run a model from the Pi
Now you can call the Ollama model on your Pi:

ollama run tinyllama "Hello via Pi server!"ß
