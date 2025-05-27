# Install the required packages using pip in the terminal or command line:
# pip install Flask aiohttp beautifulsoup4 pandas base58
from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import hashlib
import base58
# Initialize Flask app
app = Flask(_name_)
BASE_URL = "https://hashkeys.space/71/"  # The URL to scrape from
VERSION_MAINNET = b'\x00'  # P2PKH version byte
# Function to generate a P2PKH Bitcoin address
def generate_p2pkh_address(public_key_hash):
    payload = VERSION_MAINNET + public_key_hash
    checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
    address = base58.b58encode(payload + checksum).decode()
    return address
# Function to scrape key hex and balances
def scrape_addresses():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.content, 'html.parser')
    addresses = []
    # Extract key hex and balance from table rows
    rows = soup.select('tbody tr')
    for row in rows:
        columns = row.find_all('td')
        if len(columns) >= 2:
            key_hex = columns[0].text.strip()  # First column: key hex
            balance = columns[1].text.strip()  # Second column: balance
            if float(balance) > 0:  # Only keep non-zero balances
                addresses.append((key_hex, balance))
    return addresses
@app.route('/', methods=['GET', 'POST'])
def home():
    found_address = None
    if request.method == 'POST':
        address_to_check = request.form.get('address')
        addresses = scrape_addresses()
        # Check if the entered address is in the scraped addresses
        for key_hex, balance in addresses:
            generated_address = generate_p2pkh_address(bytes.fromhex(key_hex))
            if generated_address == address_to_check:
                found_address = (key_hex, generated_address, balance)
                break
    # Filter the valid addresses 
    filtered_addresses = scrape_addresses()  # Update fresh list every time
    return render_template('index.html', found_address=found_address, filtered_addresses=filtered_addresses)
if _name_ == '_main_':
    app.run(host='0.0.0.0', port=5001, debug=True)
