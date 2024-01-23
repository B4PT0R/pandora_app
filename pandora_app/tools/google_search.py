import os
_root_=os.path.dirname(os.path.abspath(__file__))
import sys
if not sys.path[0]==_root_:
    sys.path.insert(0,_root_)
def root_join(*args):
    return os.path.join(_root_,*args)

from googleapiclient.discovery import build
from dotenv import load_dotenv
load_dotenv(_root_)


def google_search(api_key,cse_id,query, num=5, type='web'):
    service = build("customsearch", "v1", developerKey=api_key)
    ns = num // 10
    r = num % 10
    results = []
    if not ns == 0:
        for i in range(ns):
            args_dict = {
                'cx': cse_id,
                'q': query,
                'num': 10,
                'start': 1 + i * 10
            }
            if type == 'image':
                args_dict['searchType'] = 'image'
            res = service.cse().list(**args_dict).execute()
            for item in res['items']:
                results.append({
                    'title': item['title'],
                    'description': item['snippet'] if item.get('snippet') else "",
                    'url': item['link']
                })
    if not r == 0:
        args_dict = {
            'cx': cse_id,
            'q': query,
            'num': r,
            'start': 1 + ns * 10
        }
        if type == 'image':
            args_dict['searchType'] = 'image'
        res = service.cse().list(**args_dict).execute()
        for item in res['items']:
            results.append({
                'title': item['title'],
                'description': item['snippet'] if item.get('snippet') else "",
                'url': item['link']
            })

    return results

def init_google_search(api_key,cse_id):
    def g_search(query, num=5, type='web'):
        return google_search(api_key,cse_id,query, num=num, type=type)
    return g_search

