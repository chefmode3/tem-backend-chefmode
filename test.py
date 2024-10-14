# import http.client
#
# conn = http.client.HTTPSConnection("youtube-downloader31.p.rapidapi.com")
#
# headers = {
#     'x-rapidapi-key': "f2d1322fc9mshd04f3762ac0793ep11069cjsn4e55258922af",
#     'x-rapidapi-host': "youtube-downloader31.p.rapidapi.com"
# }
#
# conn.request("GET", "/video.php?url=https://www.youtube.com/shorts/GysRbezYyJY", headers=headers)
#
# res = conn.getresponse()
# data = res.read()
#
# print(data.decode("utf-8"))

import http.client

conn = http.client.HTTPSConnection("youtube-media-downloader.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "f2d1322fc9mshd04f3762ac0793ep11069cjsn4e55258922af",
    'x-rapidapi-host': "youtube-media-downloader.p.rapidapi.com"
}

conn.request("GET", "/v2/video/details?videoId=GysRbezYyJY", headers=headers)

res = conn.getresponse()
data = res.read()

print(data.decode("utf-8"))