import asyncio
import mycdp
from seleniumbase.undetected import cdp_driver
import time

async def listenMEDIA(page):
    media_requests = []
    
    async def handler(evt):
        if evt.type_ is mycdp.network.ResourceType.MEDIA:
            media_url = evt.response.url
            print(f"\n[DEBUG] Media URL detected: {media_url}")
            if "tiktok.com/video" in media_url:
                print(f"[DEBUG] TikTok video URL captured: {media_url}")
                media_requests.append({
                    "url": media_url,
                    "request_id": evt.request_id,
                    "timestamp": time.time()
                })
    
    page.add_handler(mycdp.network.ResponseReceived, handler)
    return media_requests

async def get_tiktok_video(video_url: str):
    driver = await cdp_driver.cdp_util.start_async()
    tab = await driver.get("about:blank")
    
    try:
        # Setup media request listener
        media_requests = await listenMEDIA(tab)
        
        # Navigate to TikTok video
        await tab.get(video_url)
        
        # Wait for video to load
        wait_time = 10
        await asyncio.sleep(wait_time)
        
        # Process captured media requests
        for request in media_requests:
            media_url = request["url"]
            print(f"[DEBUG] Processing media URL: {media_url}")
            await tab.get(media_url)
            
            while True:
                await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[INFO] Received keyboard interrupt, closing browser...")
    except Exception as e:
        print(f"[ERROR] Main process error: {str(e)}")

if __name__ == "__main__":
    video_url = "https://www.tiktok.com/@heresyourbite/video/7379061623429942558?lang=en"
    try:
        asyncio.run(get_tiktok_video(video_url))
    except KeyboardInterrupt:
        print("\n[INFO] Program terminated by user")