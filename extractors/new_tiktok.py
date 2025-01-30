import asyncio
import mycdp
from seleniumbase.undetected import cdp_driver
import time
import requests

from utils.common import save_video_to_file


async def listenMEDIA(page):
    media_requests = []
    async def handler(evt):
        if evt.type_ is mycdp.network.ResourceType.MEDIA:
            media_url = evt.response.url
            if "tiktok.com/video" in media_url:
                print(f"[DEBUG] TikTok video URL captured: {media_url}")
                media_requests.append({
                    "url": media_url,
                    "request_id": evt.request_id,
                    "timestamp": time.time()
                })
    page.add_handler(mycdp.network.ResponseReceived, handler)
    return media_requests
async def get_media_url_and_cookies(video_url: str):
    driver = await cdp_driver.cdp_util.start_async(headless=True)
    tab = await driver.get("about:blank")
    media_requests = await listenMEDIA(tab)
    await tab.get(video_url)
    saved_cookies = await tab.send(mycdp.network.get_cookies())
    await asyncio.sleep(10)
    if media_requests:
        captured_url = media_requests[0]["url"]
        print(f"Media URL: {captured_url}")
        print("Cookies:", saved_cookies)
        return captured_url, saved_cookies
    return None, None


def download_video(media_url, cookies):
    try:
        cookies_dict = {cookie.name: cookie.value for cookie in cookies}
        response = requests.get(media_url, cookies=cookies_dict)
        if response.status_code == 200:
            return save_video_to_file(response.content)
        else:
            return None
    except Exception as e:
        print(f"[ERROR] Download error: {str(e)}")
    return None

def download_video_new_tiktok(video_url, max_retries=0):
    MAX_Try = 3
    # Run the async function to get media URL and cookies
    media_url, cookies = asyncio.run(get_media_url_and_cookies(video_url))

    if media_url and cookies:
        # if media_url and cookies:
        return download_video(media_url, cookies)
    else:
        if max_retries < MAX_Try:
            print(f"[INFO] Retrying download: {max_retries + 1}")
            return download_video_new_tiktok(video_url, max_retries + 1)
        print("[ERROR] Unable to get media URL and cookies.")

        return None

# async def main():
#     video_url = "https://www.tiktok.com/@heresyourbite/video/7379061623429942558?lang=en"
#     media_url, cookies = await get_media_url_and_cookies(video_url)
#     if media_url and cookies:
#         download_video(media_url, cookies)
#
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("\n[INFO] Program terminated by user")