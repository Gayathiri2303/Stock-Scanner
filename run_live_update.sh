#!/bin/bash
cd /home2/thekidsw/gayathiriportfolio.xyz/stockscanner
/home2/thekidsw/virtualenv/gayathiriportfolio.xyz/stockscanner/3.10/bin/python update_stocks_live.py >> stock_updater.log 2>&1
