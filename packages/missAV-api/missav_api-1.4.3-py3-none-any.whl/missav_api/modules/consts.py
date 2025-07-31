import re

HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Referer": "https://www.missav.ws",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36"
}


regex_title = re.compile(r'<h1 class="text-base lg:text-lg text-nord6">(.*?)</h1>')
regex_video_code = re.compile(r'<span class="font-medium">(.*?)</span>')
regex_publish_date = re.compile(r'class="font-medium">(.*?)</time>')
regex_thumbnail = re.compile(r'og:image" content="(.*?)cover-n.jpg')
regex_m3u8_js = re.compile(r"'m3u8(.*?)video")