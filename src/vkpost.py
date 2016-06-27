# -*- coding: utf-8 -*-
from urllib2 import urlopen
from requests.utils import quote
import json
from settings import token, user_id
from datetime import datetime, date
import pprint
import time
import urllib


class Wall(object):
    def __init__(self, u_id, tok):
        self.user_id = u_id
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
        try:
            return data['response']
        except:
            time.sleep(0.2)
            return self.get_posts(offset=offset, count=count)

    def check_date(self, date_from, date_to):
        n = self.get_posts()[0]
        n_start = n
        n_end_bool = True
        n_end = 1

        for i in range(n // 100 + 1):

            data = self.get_posts(offset=i*100, count=100)
            for j in range(1, 101):
                if (datetime.fromtimestamp(data[j]['date']) < date_to) and n_end_bool:
                    n_end = j - 1 + i*100
                    n_end_bool = False

                if datetime.fromtimestamp(data[j]['date']) < date_from:
                    n_start = j - 1 + i*100
                    return n_end, n_start
        return n_end, n_start

    def check_owner(self, item):
        try:
            if item['from_id'] != self.user_id:
                return 'friends_post'
            elif ('attachments' not in item.keys()) or ('copy_owner_id' not in item.keys()):
                return 'own'
            elif 'copy_owner_id' in item.keys():
                return 'repost'
            elif item['attachments'][0][item['attachments'][0]['type']]['owner_id'] == self.user_id:
                return 'own'
            return 'repost'
        except:
            print 'ERROR'
            print item

    def attachment(self, data):
        if data['type'] == 'photo':
            return {data['type']: data[data['type']]['src_big'].replace("\\", "")}
        elif data['type'] == 'video':
            link, title = self.get_video(data[data['type']]['vid'], data[data['type']]['owner_id'])
            if title == False:
                return {data['type']: link}
            return {data['type']: {'title': title, 'link': link}}
        elif data['type'] == 'page':
            return {data['type']: {'url': data[data['type']]['view_url'].replace("\\", ""),
                                   'title': data[data['type']]['title']}}
        elif data['type'] == 'link':
            return {data['type']: {'url': data[data['type']]['url'].replace("\\", ""),
                                   'title': data[data['type']]['title']}}
        elif data['type'] == 'audio':
            return {data['type']: {'url': data[data['type']]['url'].replace("\\", ""),
                                   'artist': data[data['type']]['artist'],
                                   'title': data[data['type']]['title']}}
        elif data['type'] == 'doc':
            return {data['type']: {'url': data[data['type']]['url'].replace("\\", ""),
                                   'title': data[data['type']]['title']}}
        elif data['type'] == 'photos_list':
            d = {}
            for i, j in enumerate(data['photo_list']):
                d[i] = j['src_big']
            return {data['type']: d}
        elif data['type'] == 'poll':
            return {data['type']: {'title': data[data['type']]['question']}}
        print 'Error'
        return 'Error'

    def create_dict(self, item):
        d = {'date': str(datetime.fromtimestamp(item['date'])), 'type': self.check_owner(item), 'attachment': {}}

        if d['type'] == 'own':
            d['text'] = item['text']
            if 'attachments' in item.keys():
                d['attachment'] = []
                for i in item['attachments']:
                    d['attachment'].append(self.attachment(i))

        elif d['type'] == 'friends_post':
            d['text'] = item['text']
            d['from_id'] = item['from_id']
            if 'attachments' in item.keys():
                d['attachment'] = []
                for i in item['attachments']:
                    d['attachment'].append(self.attachment(i))
        else:
            d['attachment']['own'], d['attachment']['repost'] = {}, {}
            d['attachment']['repost']['text'] = item['text']
            d['attachment']['repost']['id'] = item['copy_owner_id']
            d['attachment']['repost']['date'] = item['copy_post_date']
            d['attachment']['repost']['attachments'] = []
            for i in item['attachments']:
                d['attachment']['repost']['attachments'].append(self.attachment(i))
            if 'copy_text' in item.keys():
                d['attachment']['own']['text'] = item['copy_text']
        return d

    def save_posts(self, date_from=datetime(2000, 1, 1), date_to=date.today()):
        n1, n2 = self.check_date(date_from, date_to)
        posts = []
        for i in range((n2-n1) // 100 + 1):
            data = self.get_posts(offset=n1, count=100 if n2-n1 > 100 else n2-n1)[1:]
            for i in data:
                posts.append(self.create_dict(i))
            n1 += 100
        return posts

    def get_group_name(self, group_id):
        request = urlopen(
            'https://api.vk.com/method/groups.getById?group_ids=' + str(group_id).replace('-', '') +
            '&fields=description' + '&access_token=' + self.token)
        data = eval(request.read())
        data = json.loads(json.dumps(data))

        try:
            return data['response'][0]['name']
        except:
            time.sleep(0.2)
            return self.get_group_name(group_id)

    def get_video(self, video_id, video_owner):
        request = urlopen(
            'https://api.vk.com/method/video.get?videos=' + str(video_owner) + '_' + str(video_id) +
            '&access_token=' + self.token)
        data = eval(request.read())
        data = json.loads(json.dumps(data))
        try:
            return data['response'][1]['player'].replace("\\", ""), data['response'][1]['title']
        except:
            if 'response' in data.keys() and (data['response'] == [0]):
                return 'Video was deleted', False
            elif data['error']['error_code'] == 6:
                time.sleep(0.2)
                return self.get_video(video_id, video_owner)
            else:
                print 'ERROR VIDEO'

    def beautiful_print(self, post):
        if post['type'] == 'repost':
            print '=================================================='
            print 'Date:', post['date']
            print 'Type:', post['type']
            try:
                if post['attachment']['own']['text'] != u'':
                    text = post['attachment']['own']['text'].split('<br>')
                    print 'Own text:'
                    for i in text:
                        print i
            except:
                print post
            print 'REPOSTED PART:'
            print 'Original post date is', datetime.fromtimestamp(post['attachment']['repost']['date'])
            print 'This post was created by', self.get_group_name(post['attachment']['repost']['id'])
            if post['attachment']['repost']['text'] != u'':
                text = post['attachment']['repost']['text'].split('<br>')
                for i in text:
                    print i
            for i, item in enumerate(post['attachment']['repost']['attachments']):
                try:
                    if isinstance(item.values()[0],dict):
                        print str(i + 1) + ')', item.keys()[0], ':'
                        for j, k in item.values()[0].iteritems():
                            print j, ':', k
                    else:
                        print str(i + 1) + ')', item.keys()[0], ':', item.values()[0]
                except:
                    print item
        else:
            print '=================================================='
            print 'Date:', post['date']
            print 'Type:', post['type']
            if 'from_id' in post.keys():
                print post['from_id'], 'posted on your wall.'
            if post['text'] != u'':
                text = post['text'].split('<br>')
                for i in text:
                    print i
            for i, item in enumerate(post['attachment']):
                if isinstance(item.values()[0], dict):
                    print str(i + 1) + ')', item.keys()[0], ':'
                    for j, k in item.values()[0].iteritems():
                        print j, ':', k
                else:
                    print str(i + 1) + ')', item.keys()[0], ':', item.values()[0]


w = Wall(user_id, token)
posts = w.save_posts(date_from=datetime(2014, 1, 1), date_to=datetime(2016, 11, 14, 14))
print(len(posts))
for i in posts:
    w.beautiful_print(i)

#print w.get_posts(offset=1, count=3)

