import requests 
from bs4 import BeautifulSoup
import lxml

url=input("Enter the url :- ")
head={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36sss"}

res=requests.get(url,headers=head)
soup=BeautifulSoup(res.content,"lxml")
print(soup)

all_urls=[]
usl_contain_base_url=[]
links=soup.find_all("a")

for i in links:
    all_urls.append(i['href'])
    if url in i["href"]:
        usl_contain_base_url.append(url)
print(usl_contain_base_url)
print(all_urls)

