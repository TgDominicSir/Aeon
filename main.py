import os
import sys

# Add the current directory to sys.path so we can import the bot module
sys.path.append(os.getcwd())

if __name__ == "__main__":
    from bot import bot_loop
    # Import handlers and other initializations as done in __main__.py
    import bot.__main__
