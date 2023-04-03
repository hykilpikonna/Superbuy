# Superbuy

My scripts relating to the Superbuy delivery service.

This repo includes: 

1. A script to automatically add Taobao orders to Superbuy
2. Analysis of superbuy order data to rank the best shipping methods

**COPYRIGHT NOTICE**: Superbuy owns all rights to the data in this repo. If you are a Superbuy employee and would like me to remove this repo, please contact me.

## Analysis

The analysis can be found in the jupyter notebook [analysis.ipynb](analysis.ipynb).

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
