import requests


tesr_url = 'https://www.mzitu.com/1515'

a = requests.get(tesr_url).content

print(a)