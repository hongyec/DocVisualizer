import argparse
import requests
from bs4 import BeautifulSoup as bs
import bs4
import os.path
import pathlib
import json

def readXml(cacheFile, sectionalContent):
    ## get the current file path
    print(cacheFile)
    with open(cacheFile) as f:
        responseData = f.read()
    bs_content = bs(responseData, "lxml")
    title = bs_content.find("article-title").contents[0]
    sectionalContent["title"] = title
    sections = bs_content.findAll("sec")
    for section in sections:
        title = section.find("title").contents[0]
        body = ""
        for p in section.findAll("p"):
            for content in p.contents:
                if isinstance(content, bs4.element.NavigableString):
                    body+=str(content)
        sectionalContent[title]=body
    return sectionalContent

def storeJson(sectionalContent, resultName):
    with open(resultName, "w") as file:
        json.dump(sectionalContent, file)


def sectionDevider(input):

    ## check if the responseCache have it or not
    currentPath = pathlib.Path(__file__)
    cacheName = "cerine" + str(input).split('/')[-1].split('.')[0] + '.xml'
    resultName = "cerine" + str(input).split('/')[-1].split('.')[0] + '.json'
    cacheFile = os.path.join(currentPath.parents[0], "responseCache", cacheName)
    resultFile = os.path.join(currentPath.parents[0], "responseCache", resultName)

    print(cacheFile)

    sectionalContent = {}
    if(os.path.isfile(cacheFile)):
        readXml(cacheFile, sectionalContent)

    else:
        headers = {
            'Content-Type': 'application/binary',
        }
        data = open('targetFolder/SOSP.pdf', 'rb').read()
        response =  requests.post('http://cermine.ceon.pl/extract.do', headers=headers, data=data)
        with open(cacheName, "w") as f:
            f.write(response.text)
        readXml(cacheName, sectionalContent)

    storeJson(sectionalContent, resultFile)
    return sectionalContent
