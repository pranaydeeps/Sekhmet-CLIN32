from lib2to3.pgen2 import token
import requests
from bs4 import BeautifulSoup
import tqdm
import csv

STARTING_KEYPHRASE ='heart_failure'
TARGET_LANGUAGE = 'fr'
DEPTH = 2
BILINGUAL_DICT = []
TOKENS = []
BASE_URL = 'https://en.wikipedia.org'

def check_len(link):
    # response = requests.get(link)
    # soup = BeautifulSoup(response.content, 'html.parser')
    # length = len(" ".join(t.strip() for t in soup.find_all(text=True)))
    # return length
    return 0

def get_page(link, mwe=False):
    if link in TOKENS:
        return None
    response = requests.get(url=link)
    soup = BeautifulSoup(response.content, 'html.parser')
    for div in soup.find_all("div", {'class':'reflist'}): 
        div.decompose()
    title = soup.find_all(id="firstHeading")[0].text

    length = len(" ".join(t.strip() for t in soup.find_all(text=True)))
    try:
        tgt_link = soup.find_all("li", {"class" :"interwiki-{}".format(TARGET_LANGUAGE)})[0].a.attrs["href"]
    except:
        return None
    tgt_title = tgt_link.split('/')[-1]
    tgt_title.replace('_',' ')
    if mwe==True:
        if len(tgt_title.split())>1:
            return None
    tgt_length = check_len(tgt_link)
    links = [ x for x in soup.find_all("div",id="bodyContent")[0].find_all("a")]
    branches = []
    for link in links:
        try:
            temp = link.attrs['href']
            if temp.startswith('/wiki/') and '.' not in temp and ':' not in temp:
                branches.append(BASE_URL + temp)
        except Exception as e:
            pass
    TOKENS.append(link)
    return title, length, tgt_title, tgt_length, list(set(branches))

def cycle(branches, save_every=200):
    new_branches = []
    for i, branch in tqdm.tqdm(enumerate(list(set(branches)))):
        output = get_page(branch, mwe=False)
        if output!=None:
            BILINGUAL_DICT.append(output[:-1])
            new_branches+=output[-1]
        if i%save_every==0:
            with open('{}_{}.csv'.format(STARTING_KEYPHRASE, TARGET_LANGUAGE), 'w') as f:
                write = csv.writer(f)
                write.writerows(BILINGUAL_DICT)
    return list(set(new_branches))


BILINGUAL_DICT.append(['source','wiki_sanity_source','target','wiki_sanity_target'])

_ = get_page('https://en.wikipedia.org/wiki/{}'.format(STARTING_KEYPHRASE), mwe=False)
branches = _[-1]
BILINGUAL_DICT.append(_[:-1])

while(DEPTH>0):
    DEPTH-=1
    print('AT DEPTH : {}'.format(DEPTH))
    branches = cycle(branches)
    with open('{}_{}.csv'.format(STARTING_KEYPHRASE, TARGET_LANGUAGE), 'w') as f:
        write = csv.writer(f)
        write.writerows(BILINGUAL_DICT)
