import argparse
from os import readlink
from bs4 import BeautifulSoup as bs
import bs4
import os.path
import pathlib
import json
from subprocess import *

def jarWrapper(*args):
    process = Popen(['java', '-cp']+list(args), stdout=PIPE, stderr=PIPE)
    ret = []
    while process.poll() is None:
        line = process.stdout.readline()
        if line != '' and line.endswith(b'\n'):
            ret.append(line[:-1])
    stdout, stderr = process.communicate()
    ret += stdout.split(b'\n')
    if stderr != '':
        ret += stderr.split(b'\n')
    ret.remove(b'')
    return ret


def readXml(cacheFile, sectionalContent):
    ## get the current file path
    with open(cacheFile) as f:
        responseData = f.read()
    bs_content = bs(responseData, "lxml")
    title = bs_content.find("article-title").contents[0]
    sectionalContent["title"] = title
    abstract = bs_content.find("abstract").contents[1]
    sectionalContent["abstract"] = str(abstract).replace("<p>", "")
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

# def storeJson(sectionalContent, resultName):
#     with open(resultName, "w") as file:
#         json.dump(sectionalContent, file)


def sectionDevider(input):

    ## check if the responseCache have it or not
    currentPath = pathlib.Path(__file__)
    inputPath = pathlib.Path(input)
    cacheName = str(input).split('/')[-1].split('.')[0] + '.cermxml'
    # resultName = "cerine" + str(input).split('/')[-1].split('.')[0] + '.json'
    cacheFile = os.path.join(inputPath.parents[0], cacheName)
    # resultFile = os.path.join(currentPath.parents[0], "responseCache", resultName)

    sectionalContent = {}
    if(os.path.isfile(cacheFile)):
        readXml(cacheFile, sectionalContent)

    else:
        args = ['cermine-impl-1.13-jar-with-dependencies.jar', 'pl.edu.icm.cermine.ContentExtractor', '-path', inputPath.parents[0] ] # Any number of args to be passed to the jar file
        jarWrapper(*args)

        # headers = {
        #     'Content-Type': 'application/binary',
        # }
        # data = open(input, 'rb').read()
        # response =  requests.post('http://cermine.ceon.pl/extract.do', headers=headers, data=data)
        # with open(cacheFile, "w") as f:
        #     f.write(response.text)
        # readXml(cacheFile, sectionalContent)
        readXml(cacheFile, sectionalContent)

    # storeJson(sectionalContent, resultFile)
    return sectionalContent
