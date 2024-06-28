import random, string, sys
import requests

import vobject

import time

import json

def __post_request(url, json_data):

    api_url = f"{api_host}/{url}"
    headers = {'X-API-Key': api_key, 'Content-type': 'application/json'}

    req = requests.post(api_url, headers=headers, json=json_data)

    # samoilov 06.02.2024 check if response is not empty
    if req.content != b'':
        rsp = req.json()
    else:
        req.close()
        return

    req.close()

    if isinstance(rsp, list):
        rsp = rsp[0]

    if not "type" in rsp or not "msg" in rsp:
        sys.exit(f"API {url}: got response without type or msg from Mailcow API")

    if rsp['type'] != 'success':
        sys.exit(f"API {url}: {rsp['type']} - {rsp['msg']}")



def add_user(email, name, quota, active):
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=20))
    json_data = {
        'local_part':email.split('@')[0],
        'domain':email.split('@')[1],
        'name':name,
        'password':password,
        'password2':password,
        "quota": quota,
        "active": 1 if active else 0
    }
    try:
        __post_request('api/v1/add/mailbox', json_data)
    except Exception:
        print(Exception)
        pass

def edit_user(email, active=None, name=None, quota=None, avatar=None, description=None):
    attr = {}

     # vcard create
    vcard = vobject.vCard()

    o = vcard.add('email')
    o.type_param = 'INTERNET'
    o.value = email

    if (active is not None):
        attr['active'] = 1 if active else 0
    if (name is not None):
        #name = email
        attr['name'] = name
        o = vcard.add('fn')
        o.value = name
    if (quota is not None):
        attr['quota'] = quota
    json_data = {
        'items': [email],
        'attr': attr
    }
    try:
        __post_request('api/v1/edit/mailbox', json_data)
    except Exception:
        print(Exception)
        pass

    # custom attr
    attr = {'attribute': [], 'value': []}



    if (description is not None):
        attr['attribute'].append('description')
        attr['value'].append(description)
        o = vcard.add('title')
        o.value = description

    if (avatar is not None):
        attr['attribute'].append(ava_attr)
        attr['value'].append(avatar.decode("utf-8"))
        o = vcard.add('photo')
        o.value = avatar.decode("utf-8")

    try:
        vcard = vcard.serialize()
        attr['attribute'].append('vcard')
        attr['value'].append(vcard)

        if attr is not {}:
            json_data = {
                    'items': [email],
                    'attr': attr
            }

            __post_request('api/v1/edit/mailbox/custom-attribute', json_data)
    except Exception:
        print(Exception)
        pass

def __delete_user(email):
    json_data = [email]
    try:
        __post_request('api/v1/delete/mailbox', json_data)
    except Exception:
        print(Exception)
        pass

def check_user(email):

    url = f"{api_host}/api/v1/get/mailbox/{email}"
    headers = {'X-API-Key': api_key, 'Content-type': 'application/json'}
    req = requests.get(url, headers=headers)
    rsp = req.json()
    req.close()


    if not isinstance(rsp, dict):
        sys.exit("API get/mailbox: got response of a wrong type")


    if (not rsp):
        return (False, False, None, None, None)

    if 'active_int' not in rsp and rsp['type'] == 'error':
        sys.exit(f"API {url}: {rsp['type']} - {rsp['msg']}")

    return (True, bool(rsp['active_int']), rsp['name'], rsp['quota'], rsp['custom_attributes'])
