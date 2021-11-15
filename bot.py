import requests
import urllib

def qingyunke(msg):
    url = 'http://api.qingyunke.com/api.php?key=free&appid=0&msg={}'.format(
        urllib.parse.quote(msg))
    html = requests.get(url)
    re = str(html.json()["content"])
    re = re.replace("菲菲", "老公")
    re = re.replace("北辰宇", "老公")
    return re
