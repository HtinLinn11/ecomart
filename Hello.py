# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger
import google.generativeai as genai
import http.client
import re

LOGGER = get_logger(__name__)

genai.configure(api_key="AIzaSyDFFDSsV8H2hncAlNiRxxu7auqxsBIsDy0")
model = genai.GenerativeModel('gemini-pro')
ms = st.session_state

APIKeys = {"APIKey1": "1d02052b51msh6dee74f2642bb67p1ab876jsn345ba5f417d8", "APIKey2": "c6b2556f55msh39fc0fd1df0801ep14bfd8jsnd987d64b7277", "APIKey3": "6442f2a758mshb645a6362702efcp1cb3fajsn40ce767cb6d5", "APIKey4": "4a10d4e4d5mshfbd8cd7450cc2c7p1e7032jsndbfb762af901"}
chat = None
responded = False
greeting_message = 'Your Thailand Trip Planner Powered by AI. Simplify your travels across Thailand with personalized itineraries crafted just for you. Discover the best of Thailand effortlessly with Next Thai.'

if 'AIModel' not in ms:
    chat = model.start_chat(history=[])
    chat.send_message("nyello")
    ms['AIModel'] = chat
else:
    chat = ms['AIModel']

if 'replyText' not in ms:
    ms['replyText'] = greeting_message

if ms['replyText'] == greeting_message:
    responded = False
else: 
    responded = True

if "themes" not in ms: 
    ms.themes = {"current_theme": "dark",
                    "refreshed": True,
                    }

def run():
    
    global replyText, responded

    st.set_page_config(
        page_title="Eco Mart",
        page_icon="👋",
        layout="wide"
    )

    st.markdown("# Customize Your Journey Here!")
    st.subheader("Your Dream Trip with Next Thai.")

    st.sidebar.header("Customize Your Journey Here!")
    
    APIKey = APIKeys[st.sidebar.selectbox(
    'API Key for RapidAPI',
    ("APIKey1", "APIKey2", "APIKey3", "APIKey4"))]

    searchItem = st.sidebar.text_input('Search Item', 'Lamp')

    price = st.sidebar.number_input('Maximum Price in Bhat', min_value = 0, value = 0, step = 50)

    #store = st.sidebar.selectbox(
    #'Online Shops',
    #("All", "Amazon", "Lazada", "Shopee"))

    store = "Amazon"

    additionalInfo = st.sidebar.text_input('Additional Product Info', 'Suggest for Campers')
  
    if st.sidebar.button('Suggest Eco Friendly Products'):
        with st.spinner('Fetching ESG Compliant Products...'):
            findProducts(APIKey, searchItem, price, store, additionalInfo)
    else:
        pass
    st.markdown(st.session_state['replyText'])

def esg_module(data, additionalInfo, searchItem):
    global chat, replyText
    response = chat.send_message("What are the traits that require "+searchItem+" to be eco-friendly?")
    reply("From the data in the json list: "+data+" choose 5 that from the names help with eco-friendliness, the 'Reason for Eco Friendliness' and the 'Rating'. Include the 'URL for Product Image' first which will have a ! at the front and put the link in the brackets, example: '![Alt Text](https://media.giphy.com/media/vFKqnCdLPNOKc/giphy.gif)', and 'Product Name' as well as the 'Link to Product'. Prioritize items that fulfil the requirement:"+additionalInfo+". Write this as you would write down a markdown code for html table with the image at the first element and their sizes around 150px and a put each element into separate lines. so the order will be in header 'Product Image', 'name','reasons','rating','link'")
    return

def reply(prompt):
    global chat, replyText
    st.session_state['replyText'] = chat.send_message(prompt).text
    return

def list_to_string(lst, delimiter=', '):
    return delimiter.join(lst)

def findProducts(APIKey, searchItem, price, store, additionalInfo):
    
    global responded, replyText
    
    responded = True

    prompt = ""
    
    if store == "Shopee" or store == "All":
      #Shoppe
      conn = http.client.HTTPSConnection("shopee-e-commerce-data.p.rapidapi.com")

      headers = {
          'X-RapidAPI-Key': APIKey,
          'X-RapidAPI-Host': "shopee-e-commerce-data.p.rapidapi.com"
      }
      priceText = ""
      if price != 0:
        priceText = "&price_end="+str(price)

      conn.request("GET", "/shopee/search/items/v2?site=th&keyword="+str(searchItem)+"&page=1&pageSize=1"+str(priceText), headers=headers)

      res = conn.getresponse()
      data = res.read()

      prompt += "\nShopee: "
      prompt += str(data.decode("utf-8"))

    if store == "Lazada" or store == "All":
    #Lazada
      conn = http.client.HTTPSConnection("lazada-api.p.rapidapi.com")

      headers = {
          'X-RapidAPI-Key': "1d02052b51msh6dee74f2642bb67p1ab876jsn345ba5f417d8",
          'X-RapidAPI-Host': "lazada-api.p.rapidapi.com"
      }
      priceText = ""
      if price != 0:
        priceText = "&endPrice="+str(price)

      conn.request("GET", "/lazada/search/items?keywords="+str(searchItem)+"&site=th&page=1&sort=sales"+str(priceText), headers=headers)

      res = conn.getresponse()
      data = res.read()
      prompt += "\nLazada: "
      prompt += str(data.decode("utf-8"))

    if store == "Amazon" or store == "All":
    #Amazon
      conn = http.client.HTTPSConnection("real-time-amazon-data.p.rapidapi.com")

      headers = {
          'X-RapidAPI-Key': APIKey,
          'X-RapidAPI-Host': "real-time-amazon-data.p.rapidapi.com"
      }
      priceText = ""
      if price != 0:
        priceText = "&max_price="+str(price)

      conn.request("GET", "/search?query="+str(searchItem)+"&page=1&country=SG&category_id=aps"+str(priceText), headers=headers)

      res = conn.getresponse()
      data = res.read()
      prompt += "\nAmazon: "
      prompt += str(data.decode("utf-8"))

    print(prompt)
    esg_module(prompt, additionalInfo, searchItem)
    #reply(prompt + "Choose five products, with at least one from each website, that is environmentally sustainable from the title of the product and show a list containing their names, their image urls, their product urls, and why they are environmentally sustainable. Only respond in english."+additionalInfo)
    return

def ChangeTheme():
  previous_theme = ms.themes["current_theme"]
  tdict = ms.themes["light"] if ms.themes["current_theme"] == "light" else ms.themes["dark"]
  for vkey, vval in tdict.items(): 
    if vkey.startswith("theme"): st._config.set_option(vkey, vval)

  ms.themes["refreshed"] = False
  if previous_theme == "dark": ms.themes["current_theme"] = "light"
  elif previous_theme == "light": ms.themes["current_theme"] = "dark"

if __name__ == "__main__":
    run()


