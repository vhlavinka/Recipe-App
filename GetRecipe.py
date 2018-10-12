import nltk
import requests
import json
import pprint
import re
import flask
from bs4 import BeautifulSoup



#print("Enter a recipe url")
#url = input()
#url = 'https://www.foodnetwork.com/recipes/tyler-florence/watermelon-gazpacho-recipe-1910394'
#url = 'https://www.delish.com/cooking/recipe-ideas/a22987076/crumbly-pumpkin-bread-recipe/'
#url = 'https://tasty.co/recipe/eggplant-potato-tomato-stew'
#url = 'https://www.pinchofyum.com/the-best-detox-crockpot-lentil-soup' # 403 error code, solved with headers WORKING
url = 'https://smittenkitchen.com/2018/08/layered-mocha-cheesecake/' # using application/json+oembed
#url = 'https://www.halfbakedharvest.com/apple-butter-bars/' # has firewall, solved with headers WORKING

# need to provide headers since some sites require for GET requests
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}

# send get request
r = requests.get(url, headers = headers)

# html of recipe page
soup = BeautifulSoup(r.text,'html5lib')

# store title of recipe
title = soup.title.string

# parse for JSON-LD
getJSON = soup.find("script", {"type" : "application/ld+json"})

if getJSON is not None:
    # if recipeIngredient not found in first block of script, then search next
    failsafe = 0;
    while "recipeIngredient" not in str(getJSON) and failsafe < 10:
        getJSON = getJSON.findNext("script", {"type": "application/ld+json"})
        failsafe = failsafe + 1 #provide a failsafe to avoid infinite loop. This occurs if there is no more application/ld_json tags

    # parse out tags
    getJSON = re.sub(r"<[^>]*>", "", getJSON.string)

    # create list
    list = getJSON

    # decode JSON
    list = json.loads(list)

    # extract recipe ingredient list

    recipeList = list["recipeIngredient"]

    # pull each item from dictionary
    print("Recipe: " + title)
    print("Ingredients :")
    for ele in recipeList:
        if ele.find("salt") == -1:  # here you can parse out staple ingredients like salt
            print(ele)


oEmbedURL = soup.find("link", rel="alternate", type="application/json+oembed", href = True)['href']

if getJSON is None and oEmbedURL is not None:

    apiRequest = requests.get(oEmbedURL)

    apiContents = apiRequest.json()
    apiContentsTitle = apiContents['title']
    apiContentsHtml = apiContents['html']

    apiSoup = BeautifulSoup(apiContentsHtml, 'html5lib')

    list = apiSoup.findAll("li", itemprop="recipeIngredient")

    print("Recipe :" + apiContentsTitle)
    print("Ingredients: ")
    for ele in list:
        print(ele.text)




