default:
    @just -l

export:
    uv export > requirements.txt

run:
    ~/Code/python/ShuiyuanAnnualReport/.venv/bin/python ~/Code/python/ShuiyuanAnnualReport/main.py 

get-emoji:
    ~/Code/python/ShuiyuanAnnualReport/.venv/bin/python ~/Code/python/ShuiyuanAnnualReport/get_custom_emoji.py

clean:
    fd -t d -g -I "**pycache**" -x rm -r {}
