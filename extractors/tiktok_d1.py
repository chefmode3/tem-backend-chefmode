# import asyncio
# import mycdp
# from seleniumbase.undetected import cdp_driver
# import time
# import requests
#
# async def listenMEDIA(page):
#     media_requests = []
#     async def handler(evt):
#         if evt.type_ is mycdp.network.ResourceType.MEDIA:
#             media_url = evt.response.url
#             if "tiktok.com/video" in media_url:
#                 print(f"[DEBUG] TikTok video URL captured: {media_url}")
#                 media_requests.append({
#                     "url": media_url,
#                     "request_id": evt.request_id,
#                     "timestamp": time.time()
#                 })
#     page.add_handler(mycdp.network.ResponseReceived, handler)
#     return media_requests
#
# async def get_media_url_and_cookies(video_url: str):
#     driver = await cdp_driver.cdp_util.start_async()
#     tab = await driver.get("about:blank")
#
#     try:
#         media_requests = await listenMEDIA(tab)
#         await tab.get(video_url)
#
#         saved_cookies = await tab.send(mycdp.network.get_cookies())
#         await asyncio.sleep(10)
#
#         if media_requests:
#             captured_url = media_requests[0]["url"]
#             print(f"Media URL: {captured_url}")
#             print("Cookies:", saved_cookies)
#             # await driver.close()
#             return captured_url, saved_cookies
#
#     except Exception as e:
#         print(f"[ERROR] Error: {str(e)}")
#         # await driver.close()
#     return None, None
#
# def download_video(media_url, cookies):
#     try:
#         cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
#         response = requests.get(media_url, cookies=cookies_dict)
#
#         if response.status_code == 200:
#             filename = f'tiktok_video_{int(time.time())}.mp4'
#             with open(filename, 'wb') as f:
#                 f.write(response.content)
#             print(f"Video downloaded: {filename}")
#         else:
#             print(f"Download failed: Status code {response.status_code}")
#
#     except Exception as e:
#         print(f"[ERROR] Download error: {str(e)}")
#
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