#!/bin/bash
killall python
cd /home/ec2-user
export BACKEND_API=http://modul-LoadB-19X7K43CY3SUI-1487929617.us-east-1.elb.amazonaws.com
pip install -r requirements.txt
nohup python app.py &>/dev/null &
