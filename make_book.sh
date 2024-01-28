#! /bin/sh
start http://localhost:5000/
sleep 10
python images.py
python svg_rl.py
