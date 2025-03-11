from fastapi import FastAPI, Request, Body
from pydantic import BaseModel
from time import time
import httpx
import asyncio
import json
import imaplib
import email
from imap_tools import MailBox, AND
from email.header import decode_header
import base64
import re
import retailcrm
import yadisk
import aiofiles

disk_client = yadisk.AsyncClient(token="y0__xChi-z7Bxjj8DUgmuvkvxKrZeWiG8ZMqvScgztqL-Mze3zFDg")

app = FastAPI()
#url = 'https://mdevelopeur.retailcrm.ru/api/v5/'
url = 'https://laminat77.retailcrm.ru'
apikey = 'bma1wovaLnCuJrayUpzUecTIcpdHnw7X'
#apikey = 'nHY0H7zd7UWwcEiwN0EbwhXz2eGY9o9G'
retail_client = retailcrm.v5(url, apikey)
headers = {
  'X-API-KEY' : apikey
}

#password = "zrAUqnFWgD14Ygkq13VK"
#username = "kworktestbox@mail.ru"
password = "r4ZuvyWydYMktHuTn3uJ"
username = "novers495@mail.ru"
imap_server = "imap.mail.ru"

async def upload_file(client, file):
    print(await client.check_token())

    # Get disk information
    print(await client.get_disk_info())

async def main(client):
    #await upload_file(disk_client)
    messages = await get_mail(username, password, imap_server)
    for msg in messages : 
        #response = retail_client.files_upload([])
        for a in msg["attachments"]:
            print(a.filename)
            #response = await disk_client.upload(b'111', '/file.txt')# + #a.filename)
            #print(response)
        result = await post_order(retail_client, msg["first_name"], msg["last_name"], msg["email"], msg["subject"], msg["text"], msg["html"])#, msg["attachments"])
        return result    

async def post_order(client, first_name, last_name, email, subject, text, html):
    print('posting...')
    try: 
       filter = {'email': email}
       customers = client.customers(filter).get_response()["customers"]#[0]["id"]           
    except Exception as e:
        print('exception: ', e)
        return e
    try: 
        print('posting....')
        order = {'firstName': first_name, 'lastName': last_name, 'email': email, 'customerComment': text}
        if len(customers) > 0:
            order["customer"] = { 'id': customers[0]["id"]}
        result = client.order_create(order)
    except Exception as e:
        print('exception: ', e)
    
    print(customers)
    print('result: ', result)
    return result 

async def get_mail(username, password, imap_server):
    array = []
    print('connecting to imap server...')
    with MailBox(imap_server).login(username, password) as mailbox:
        print('fetching...')
        for msg in mailbox.fetch(AND(seen=False)):
            attachments = []
            for a in msg.attachments:
                print(a.filename)
                #print(a.payload)
                attachments.append(a)
            print(len(attachments))
            name = re.search('(.*) <' + msg.from_ + '>', msg.from_values.full).group(1).split(' ')
            print(name)
            lastName = name[-1]
            name.pop(-1)
            firstName = ' '.join(name)
            print(firstName, lastName)
            data = {"email": msg.from_, "first_name": firstName, "last_name": lastName, "subject": msg.subject, "text": msg.text, "html": msg.html, "attachments": attachments}
            print(data["email"])
            print(msg.date, msg.from_, msg.subject, msg.from_values,name, len(msg.text or msg.html))
            array.append(data)
        return array

async def task():
    async with httpx.AsyncClient() as client:
        tasks = [main(client) for i in range(1)]
        result = await asyncio.gather(*tasks)
        return result

@app.get('/api')
async def api():
    #start = time()
    output = await task()
    #print("time: ", time() - start)
    return output
