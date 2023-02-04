# Superbuy

Automatically add Taobao orders to Superbuy


## Usage Guide

### Installation

1. Clone/download this repo
2. Install Tampermonkey on your default browser
3. Create a new userscript, copy-and-paste the content of `taobao.js`
4. Install python>=3.9 (tested on 3.11)
5. `pip install -r requirements.txt`
6. Fill in your email and password in `auth.toml`

### Usage

1. Login to taobao
2. `python mobile.py` will open a browser tab and close it after it syncs all orders

Note: If you have manually-added orders before using this script, you can change the `MIN_DATE` variable in `mobile.py` to the date of the first order you want to sync.
