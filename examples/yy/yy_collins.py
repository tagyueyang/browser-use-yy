import os
import asyncio
import subprocess
import time
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from browser_use import Agent, Browser, BrowserConfig
from playwright.async_api import async_playwright
## install playwright: pip install playwright
## clone https://github.com/browser-use/browser-use, go through basic setup in the git repo, study example will be a great help
## kill all edge >> taskkill /IM msedge.exe /F
## cmd: "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --remote-debugging-port=9223 --no-first-run --no-default-browser-check
## powershell: Start-Process "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" -ArgumentList "--remote-debugging-port=9223", "--no-first-run", "--no-default-browser-check"

# Kill existing Edge processes
subprocess.run(["taskkill", "/IM", "msedge.exe", "/F"], capture_output=True)

# Start Edge with remote debugging
edge_path = '"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"'
powershell_cmd = f'Start-Process {edge_path} -ArgumentList "--remote-debugging-port=9223", "--no-first-run", "--no-default-browser-check"'
subprocess.run(["powershell", "-Command", powershell_cmd])

# Wait a moment for Edge to start
time.sleep(3)  # Give Edge time to start up

# Load environment variables
load_dotenv(verbose=True)  # Added verbose=True for debugging

# Get API key and convert to SecretStr
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError("OPENAI_API_KEY not found in .env")

# Get remote debugging port (default to 9223)
debugging_port = os.getenv("REMOTE_DEBUGGING_PORT", "9223")
websocket_url = f"ws://127.0.0.1:{debugging_port}/devtools/browser/"

sign_in_email = os.getenv("DMN_SIGNIN_EMAIL")
sign_in_password = os.getenv("DMN_SIGNIN_PWD")

# Initialize LLM 
llm = ChatOpenAI(
	model='gpt-4o',
	temperature=0.0,
)

async def main():
    async with async_playwright():
        try:
            # Connect to existing Edge browser via WebSocket
            browser = Browser(
                config=BrowserConfig(
                    browser_binary_path='C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
                    wss_url=websocket_url,
                    cdp_url="http://localhost:9223"
                )
            )
            json_body = {
				"booking_custom_field": "CoffeeTest",
                "notification_email": "yytest@test.com",
                "new_booking_source": "CoffeeSource",
                "selected_booking_source": "CoffeeSource"
            }
            # Initialize Agent with task
            agent = Agent(
                task=f''' \
                1. Go to https://identity-playpen.designmynight.com/
                2. Sign in with email "{sign_in_email}" and password "{sign_in_password}"
                3. Click on "Access Collins" image 
                4. On the top navigation bar, go to Settings > Organisation
                5. On the left menu, go to "Group details", enter "{json_body['notification_email']}" under Notification email
                6. On the left menu, go to "Bookings"
                7. look for input with "Booking custom field" and type "{json_body['booking_custom_field']}"
                8. Look for input with "ADD ANOTHER" and type "{json_body['new_booking_source']}"
				9. Click on "Source for bookings from your website" dropdown and select "{json_body['selected_booking_source']}" then send "escape" key to close dropdown menu"
                ''',
                llm=llm,
                browser=browser
            )

            print("Agent initialized, starting task...")
            await agent.run(max_steps=20)

        except Exception as e:
            print(f"Error: {e}")
            raise

if __name__ == '__main__':
    asyncio.run(main())
