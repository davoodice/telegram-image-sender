import os
import asyncio
import shutil
from telegram import Bot
from telegram.error import RetryAfter, TimedOut

#v1.2

# ANSI escape codes for colors
RESET = "\033[0m"
BOLD = "\033[1m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"

# Function to load configuration from a file
def load_config(config_file='config.txt'):
    config = {}
    with open(config_file, 'r') as f:
        for line in f:
            key, value = line.strip().split('=')
            config[key] = value
    return config

# Load configuration
config = load_config()

TOKEN = config['TOKEN']
CHANNEL_ID = config['CHANNEL_ID']
IMAGE_FOLDER = config['IMAGE_FOLDER']
SENT_IMAGE_FOLDER = config['SENT_IMAGE_FOLDER']
DELAY = int(config['DELAY'])

# Create the sent images folder if it doesn't exist
os.makedirs(SENT_IMAGE_FOLDER, exist_ok=True)

async def main():
    # Create Bot object
    bot = Bot(token=TOKEN)

    # Get the list of image files
    image_files = [f for f in os.listdir(IMAGE_FOLDER) if os.path.isfile(os.path.join(IMAGE_FOLDER, f))]
    total_images = len(image_files)

    # Send images with a delay
    for index, image in enumerate(image_files, start=1):
        image_path = os.path.join(IMAGE_FOLDER, image)
        print(f"{BOLD}{CYAN}Processing file: {image}{RESET}")

        while True:
            try:
                with open(image_path, 'rb') as photo:
                    print(f"{BOLD}{BLUE}Sending image: {image}{RESET}")
                    await bot.send_photo(chat_id=CHANNEL_ID, photo=photo)
                print(f"{BOLD}{GREEN}Image sent successfully: {image}{RESET}")

                # Move the image to the sent folder after successful sending
                shutil.move(image_path, os.path.join(SENT_IMAGE_FOLDER, image))
                print(f"{BOLD}{MAGENTA}Moved image to sent folder: {image}{RESET}")
                break  # Exit the retry loop since the image was sent successfully

            except RetryAfter as e:
                print(f"{BOLD}{RED}Flood control exceeded. Retrying in {e.retry_after} seconds for image: {image}...{RESET}")
                await asyncio.sleep(e.retry_after)

            except TimedOut:
                print(f"{BOLD}{RED}Request timed out. Retrying in 15 seconds for image: {image}...{RESET}")
                await asyncio.sleep(15)  # Wait 15 seconds before retrying

        # Calculate and display remaining images
        remaining_images = total_images - index
        print(f"{BOLD}{YELLOW}Waiting for {DELAY} seconds before processing the next image...{RESET}")
        print(f"{BOLD}{CYAN}Remaining images in folder: {remaining_images}{RESET}\n")
        
        await asyncio.sleep(DELAY)
        
        # Add space between operation cycles
        print(f"{BOLD}{CYAN}---------------------------------------{RESET}\n")

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
