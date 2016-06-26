from urllib2 import urlopen
from requests.utils import quote
import json
from settings import token, user_id
from datetime import datetime, date
import pprint
# import time
import urllib


class Wall(object):
    def __init__(self, id, tok):
        self.user_id = id
        self.token = tok

    def write_message(self, mes):
        request = urlopen('https://api.vk.com/method/wall.post?owner_id=' + str(self.user_id) + '&message=' + quote(mes, safe='') +
                          '&access_token=' + self.token)
        data = eval(request.read())
        data = json.loads(json.dumps(data))

        return data['response']['post_id']

    def delete_message(self, post_id):
        request = urlopen('https://api.vk.com/method/wall.delete?owner_id=' + str(self.user_id) + '&post_id=' + str(post_id) +
                          '&access_token=' + self.token)

        data = eval(request.read())
        data = json.loads(json.dumps(data))

        return data

    def pin_post(self, post_id):
        request = urlopen(
            'https://api.vk.com/method/wall.pin?owner_id=' + str(self.user_id) + '&post_id=' + str(post_id) +
            '&access_token=' + self.token)

        data = eval(request.read())
        data = json.loads(json.dumps(data))

        return data

    def unpin_post(self, post_id):
        request = urlopen(
            'https://api.vk.com/method/wall.unpin?owner_id=' + str(self.user_id) + '&post_id=' + str(post_id) +
            '&access_token=' + self.token)

        data = eval(request.read())
        data = json.loads(json.dumps(data))

        return data

    def get_posts(self, domain=None, offset=0, count=1, filter='all', extended=0, return_n=False):
        if domain is not None:
            request = urlopen(
                'https://api.vk.com/method/wall.get?owner_id=' + str(self.user_id) + '&domain=' + domain + '&offset=' +
                    str(offset) + '&count=' + str(count) + '&filter=' + str(filter) + '&extended=' + str(extended) +
                '&access_token=' + self.token)

            data = eval(request.read())
            data = json.loads(json.dumps(data))
        else:
            request = urlopen(
                'https://api.vk.com/method/wall.get?owner_id=' + str(self.user_id) + '&offset=' +
                str(offset) + '&count=' + str(count) + '&filter=' + str(filter) + '&extended=' + str(extended) +
                '&access_token=' + self.token)

            data = eval(request.read())
            data = json.loads(json.dumps(data))
        if return_n:
            return data['response'][0]
        return data['response']

    def check_date(self, date_from, date_to):
        n = self.get_posts()['response'][0]
        n_start_bool = True
        n_start = n
        n_end_bool = True
        n_end = 1

        for i in range(n // 100 + 1):

            data = self.get_posts(offset=i*100, count=100)['response']
            for j in range(1, 101):
                if (datetime.fromtimestamp(data[j]['date']) < date_to) and n_end_bool:
                    n_end = j
                    n_end_bool = False

                if (datetime.fromtimestamp(data[j]['date']) < date_from) and n_start_bool:
                    n_start = j - 1
                    return n_end, n_start
        return n_end, n_start

    def save_posts(self, date_from=datetime(2000, 1, 1), date_to=date.today()):
        n1, n2 = self.check_date(date_from, date_to)
        data = self.get_posts(offset=n1, count=n2-n1+1)
        return data


w = Wall(user_id, token)
#pprint.pprint(w.get_posts(count=1)['response'][1])
#pprint.pprint(w.get_posts(count=5)['response'][5]['attachment']['video']['title'])
#print(datetime.fromtimestamp(w.get_posts(count=14)['response'][14]['date']))
# w.save_posts(n)
print w.save_posts(date_from=datetime(2015, 1, 1), date_to=datetime(2015, 5, 1))
