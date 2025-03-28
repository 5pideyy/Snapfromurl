from flask import Flask, request, render_template, jsonify
import requests
import re
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import socket

app = Flask(__name__)

blacklist = [
    "127.0.0.1",
    "0.0.0.0",
    "169.254.169.254",
    ""  
]

def blacklisted(url):
    try:
        parsed_url = urlparse(url)
        if parsed_url.scheme not in ["http", "https"]:
            return render_template("error.html", error="Invalid URL scheme"), 400
                

        host = parsed_url.hostname
        print("host",host)

    except:
        return True
    if host in blacklist:
        return True
    
    private_ip_patterns = [
        r"^127\..*",
        # r"\b(0|o|0o|q)177\b"  
        # r"^2130*",      
        # r"^10\..*",           
        # r"^172\.(1[6-9]|2[0-9]|3[0-1])\..*", 
        # r"^192\.168\..*",  
        # r"^169\.254\..*",
    ]
    
    for pattern in private_ip_patterns:
        if re.match(pattern, host):
            print("blocked")
            return True
    
    return False

def image_parser(res_text, url):
    soup = BeautifulSoup(res_text, 'html.parser')


    images = soup.find_all('img')

    img_data = [
        {
            'src': urljoin(url, img['src']),
            'alt': img.get('alt', '(No alt text)')
        }
        for img in images if 'src' in img.attrs
    ]

    print("img_data", img_data)

    if not img_data:
        return None

    return img_data

@app.route("/")
def home():
    return render_template('index.html')


@app.route('/images', methods=['POST'])
def images():
    try:
        url = request.form.get('url')

        if not url:
            return render_template("error.html",error="Missing url :("), 400

        if blacklisted(url):
            return render_template("error.html",error="URL is blacklisted (unsafe or restricted)"), 403

        ip = socket.gethostbyname(urlparse(url).hostname)
        print(ip)
        if ip in ["localhost", "0.0.0.0"]:
            return render_template("error.html",error="Blocked !! "), 403
        
        response = requests.get(url,allow_redirects=False)
        res_text=response.text
    
        img_urls = image_parser(res_text,url)
        if not img_urls:
            return render_template("error.html",error="No images found on the page :("), 404

        return render_template('images.html', url=url, images=img_urls)

    except Exception:
        error="An error occurred while fetching the URL. Please try again later."
        return render_template("error.html",error=error), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1234, debug=False)
