# this will define the APIs
import os
import glob
import json
from apis.blockchain import Blockchain
import requests
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import asyncpg
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
import platform
from fastapi import HTTPException
import copy

load_dotenv()
shared_secret = os.getenv("SECRETPASS")
# peers = [os.getenv("PEER1"),os.getenv("PEER2")]
peers=[]
bc = Blockchain()
keys = ["0","0"]
def check_pass(pasw):
    global shared_secret
    if pasw == shared_secret:
        return True
    return False

activity = [0 for _ in range(60)]

st_activity = 0
temp=0

def addact():
    global temp
    global st_activity
    try:
        st_activity+=1
    except UnboundLocalError:
        print("Initializing Activity")
        temp=0
        st_activity=0


def minutetime():
    global temp
    global st_activity
    try:
        temp=st_activity
        activity.append(st_activity)
        activity.pop(0)
    except UnboundLocalError:
        print("Please initialize your node by calling the / API")

scheduler = BackgroundScheduler()
scheduler.add_job(minutetime, 'interval', minutes=1)
scheduler.start()

def initiate():
    global keys
    addact()
    keys[0], keys[1] = generate_key_pair()
    return {"Connection status":"Successful"}

def ret_keypair():
    global keys
    addact()
    return keys[0], keys[1]

async def change():
    global bc
    addact()
    if platform.system() == 'Windows':
        list_of_files = glob.glob('C:/Program Files/PostgreSQL/*/data/log/*')
    elif platform.system() == 'Linux':
        list_of_files = glob.glob('/var/log/postgresql/*')
    else:
        raise HTTPException(status_code=401, detail="Unidentified OS")

    sample = max(list_of_files, key=os.path.getctime)
    with open(sample, "rb") as file:
        try:
            file.seek(-2, os.SEEK_END)
            while file.read(1) != b'\n':
                file.seek(-2, os.SEEK_CUR)
        except OSError:
            file.seek(0)
        last_line = file.readline().decode()
    block = bc.create_block(last_line)
    print(block)
    # responses=  []
    # data = {
    #     "block":block,
    #     "size":len(bc.chain)
    # }
    # for ip in peers:
    #     response = requests.post("http://"+ip+":8000/remotechange", json=data)
    #     responses.append(response)
    return {"new block":block}

async def connect_to_db():
    addact()
    conn = await asyncpg.connect(
        user=os.getenv("USERN"),
        password=os.getenv("PASSWORD"),
        host=os.getenv("HOST"),
        port=os.getenv("PORT"),
        database=os.getenv("DB")
    )
    return conn

def ret_db_name():
    addact()
    return os.getenv("DB")

def generate_key_pair():
    addact()
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048
    )
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode('utf-8')
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode('utf-8')
    return public_pem, private_pem


async def makechange(json_data):
    req=json.loads(json_data)
    size = req["size"]
    block = req["block"]
    addact()
    conn = await connect_to_db()
    if size>len(bc.chain):
        bc.chain.append(block)
        statement = block["data"]["message"][11:]
        response = await conn.execute(statement)
    else:
        return {'response':"already have data"}
    return {'new_block':response}

def query_blocks():
    addact()
    last_five = bc.return_last_five(bc.chain)
    filtered = []
    filt_buf = {"message":"", "timestamp":""}
    for object in last_five:
        filt_buf["timestamp"]=object["timestamp"]
        filt_buf["message"]=object["data"]["message"].split(':',1)[-1]
        filtered.append(copy.deepcopy(filt_buf))
    return filtered

def return_peers():
    addact()
    return {"peers":peers}

def get_total_traffic():
    return {"minute":activity}

def get_dynamic_traffic():
    return {"second":[st_activity,temp]}