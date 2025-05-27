from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
from bs4 import BeautifulSoup
import hashlib
import base58
app = FastAPI()
templates = Jinja2Templates(directory="templates")  # Templates folder
BASE_URL = "https://hashkeys.space/71/"
VERSION_MAINNET = b'\x00'
def generate_p2pkh_address(public_key_hash):
    payload = VERSION_MAINNET + public_key_hash
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    address = base58.b58encode(payload + checksum).decode()
    return address
def scrape_addresses():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    addresses = []
    rows = soup.select('tbody tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) >= 2:
            key_hex = columns[0].text.strip()
            balance = columns[1].text.strip()
            if float(balance) > 0:
                addresses.append((key_hex, balance))
    return addresses
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    filtered_addresses = scrape_addresses()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "filtered_addresses": filtered_addresses}
    )
@app.post("/", response_class=HTMLResponse)
async def check_address(request: Request, address: str = Form(...)):
    found_address = None
    addresses = scrape_addresses()
    for key_hex, balance in addresses:
        generated_address = generate_p2pkh_address(bytes.fromhex(key_hex))
        if generated_address == address:
            found_address = (key_hex, generated_address, balance)
            break
    filtered_addresses = scrape_addresses()
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "found_address": found_address, "filtered_addresses": filtered_addresses}
    )
if _name_ == "_main_":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
