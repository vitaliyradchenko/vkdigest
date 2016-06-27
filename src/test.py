# -*- coding: utf-8 -*-
from urllib2 import urlopen
from requests.utils import quote
import json
from settings import wall_token, user_id, video_token
from datetime import datetime, date

class Wall(object):
    def __init__(self, id, wall_tok, video_tok):
        self.user_id = id
        self.token = wall_tok
        self.video_token = video_tok

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
        print data
        #if return_n:
        #    return data['response'][0]
        #return data['response']

    def check_date(self, date_from, date_to):
        n = self.get_posts()[0]
        n_start_bool = True
        n_start = n
        n_end_bool = True
        n_end = 1

        for i in range(n // 100 + 1):

            data = self.get_posts(offset=i*100, count=100)
            for j in range(1, 101):
                if (datetime.fromtimestamp(data[j]['date']) < date_to) and n_end_bool:
                    n_end = j - 1
                    n_end_bool = False

                if (datetime.fromtimestamp(data[j]['date']) < date_from) and n_start_bool:
                    n_start = j - 1
                    return n_end, n_start
        return n_end, n_start

    def check_owner(self, item):
        if item['attachments'][0][item['attachments'][0]['type']]['owner_id'] == self.user_id:
            return 'own'
        return 'repost'

    def create_dict(self, item):
        d = {'date': str(datetime.fromtimestamp(item['date'])), 'type': self.check_owner(item), 'attachment': {}}
        post_type = item['attachments'][0]['type']
        if d['type'] == 'own':
            d['attachment']['text'] = item['attachment'][post_type]['text']
            d['attachment'][post_type] = item['attachment'][post_type]['src_big'].replace("\\", "")
        else:
            d['attachment']['own'], d['attachment']['repost'] = {}, {}
            d['attachment']['repost']['text'] = item['text']
            d['attachment']['repost']['id'] = item['copy_owner_id']
            d['attachment']['repost']['date'] = item['copy_post_date']
            d['attachment']['repost']['attachments'] = []
            for i in item['attachments']:
                if i['type'] == 'photo':
                    d['attachment']['repost']['attachments'].append({
                        i['type']: i[i['type']]['src_big'].replace("\\", "")})
                if i['type'] == 'video':
                    print self.get_video(item['media']['item_id'], item['media']['owner_id'])

            d['attachment']['own']['text'] = item['copy_text']
        return d

    def save_posts(self, date_from=datetime(2000, 1, 1), date_to=date.today()):
        n1, n2 = self.check_date(date_from, date_to)
        data = self.get_posts(offset=n1, count=n2-n1)[1:]
        posts = []
        for i in data:
            posts.append(self.create_dict(i))
        return posts

    def get_group_name(self, group_id):
        request = urlopen(
            'https://api.vk.com/method/groups.getById?group_ids=' + str(group_id).replace('-','') + '&fields=description'+
            '&access_token=' + self.token)
        data = eval(request.read())
        data = json.loads(json.dumps(data))

        return data['response'][0]['name']

    def get_video(self, video_id, video_owner):
        request = urlopen(
            'https://api.vk.com/method/video.get?videos=' + str(video_owner) + '_' + str(video_id) +
            '&access_token=' + self.video_token)
        data = eval(request.read())
        data = json.loads(json.dumps(data))
        return data

    def beautiful_print(self, post):
        if post['type'] == 'repost':
            print '=================================================='
            print 'Date:', post['date']
            print 'Type:', post['type']
            if post['attachment']['own']['text'] != u'':
                print 'Own text:', post['attachment']['own']['text']
            print 'REPOSTED PART:'
            print 'Original post date is', datetime.fromtimestamp(post['attachment']['repost']['date'])
            print 'This post was created by', self.get_group_name(post['attachment']['repost']['id'])
            if post['attachment']['repost']['text'] != u'':
                text = post['attachment']['repost']['text'].split('<br>')
                for i in text:
                    print i
            for i, item in enumerate(post['attachment']['repost']['attachments']):
                print str(i+1) + ')', item.keys()[0], ':', item.values()[0]
        else:
            print '=================================================='
            print 'Date:', post['date']
            print 'Type:', post['type']
            if post['attachment']['text'] != u'':
                text = post['attachment']['text'].split('<br>')
                for i in text:
                    print i
            for i, item in enumerate(post['attachment']['attachments']):
                print str(i + 1) + ')', item.keys()[0], ':', item.values()[0]

w = Wall(user_id, wall_token, video_token)
posts = w.save_posts(date_from=datetime(2016, 1, 1), date_to=datetime(2016, 11, 14, 14))
print posts