import asyncio
from playwright.async_api import async_playwright
import requests

PLATFORM_URL = "https://aglewebcommerce.com/login"
ENGINE_URL = "http://localhost:8000/api/process-task"

async def run_bot():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()

        # Step 1: Login
        await page.goto(PLATFORM_URL)
        await page.fill('input[name="email"]', "YOUR_EMAIL")
        await page.fill('input[name="password"]', "YOUR_PASSWORD")
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/dashboard")
        print("[+] Logged into AGLE Web Commerce successfully.")

        # Step 2: Task Polling Loop
        while True:
            await page.goto("https://aglewebcommerce.com/available-tasks")
            claim_buttons = await page.query_selector_all('.claim-task-btn')
            
            if claim_buttons:
                print("[!] Task detected! Claiming...")
                await claim_buttons[0].click()
                await page.wait_for_selector('#editor-workspace')

                audio_elem = await page.query_selector('audio source')
                audio_url = await audio_elem.get_attribute('src')
                
                audio_data = requests.get(audio_url).content
                with open("temp_task.mp3", "wb") as f:
                    f.write(audio_data)

                res = requests.post(ENGINE_URL, json={
                    "task_id": "task_auto_1",
                    "audio_path": "temp_task.mp3",
                    "is_verbatim": False
                }).json()

                processed_text = res.get("formatted_transcript")

                await page.fill('#transcript-editor', processed_text)
                await page.click('#submit-task-btn')
                print("[✔] Task completed and submitted automatically.")

            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(run_bot())
      
