import os
import requests
from dotenv import load_dotenv
import datetime


def check_response(response):
    response = response.json()
    if 'response' in response.json():
        vk_response = response['response']
        return vk_response
    else:
        raise requests.HTTPError(response['error']['error_msg'])


def get_payload(vk_token, offset):
    payload = {
        'access_token': vk_token,
        'v': '5.103',
        'count': 100,
        'offset': offset,
    }
    return payload


def fetch_posts(vk_token, vk_group_name):
    url = 'https://api.vk.com/method/wall.get'
    offset = 0
    count_posts = 100
    posts_ids = []
    while offset < count_posts:
        extra_payload = {'domain': vk_group_name, 'filter': 'owner'}
        payload = get_payload(vk_token, offset)
        payload.update(extra_payload)
        response = requests.post(url=url, data=payload)
        vk_response = check_response(response)
        offset += 100
        count_posts = vk_response['count']
        post_items = vk_response['items']
        post_ids = [post_items[post_number]['id'] for post_number, item in enumerate(post_items)]
        posts_ids.extend(post_ids)
    return posts_ids


def get_group_id(vk_token, vk_group_name):
    url = 'https://api.vk.com/method/groups.getById'
    params = {
        'group_id': vk_group_name,
        'access_token': vk_token,
        'v': '5.103'
    }
    response = requests.get(url=url, params=params)
    vk_response = check_response(response)
    return f"-{vk_response[0]['id']}"


def get_commetns(vk_token, post_id, group_id):
    url = 'https://api.vk.com/method/wall.getComments'
    offset = 0
    comments_count = 100
    comments = []
    while offset < comments_count:
        extra_payload = {'owner_id': group_id,'post_id': post_id}
        payload = get_payload(vk_token, offset)
        payload.update(extra_payload)
        response = requests.post(url=url, data=payload)
        vk_response = check_response(response)
        offset += 100
        comments_count = vk_response['count']
        items_count = len(vk_response['items'])
        if items_count > 0:
            for comment_number in range(items_count):
                comments.append(vk_response['items'][comment_number])
    return comments


def fetch_comments_period(comments, period=1209600):
    last_comments = {}
    now = datetime.datetime.now().strftime('%s')
    for comment in comments:
        if comment.get('text'):
            date = comment['date']
            timedelta = int(now) - date
            if period < timedelta:
                last_comments[comment['id']] = comment['text']
    return last_comments


def fetch_comments_ids(last_comments, group_id):
    filter_comments = []
    for user_id in last_comments.keys():
        if user_id != group_id:
            filter_comments.append(user_id)
    return set(filter_comments)


def fetch_all_likes(vk_token, group_id, post_id):
    url = 'https://api.vk.com/method/likes.getList'
    offset = 0
    likes = []
    count_likes = 100
    while offset < count_likes:
        extra_payload = {'type': 'post', 'owner_id': group_id,'item_id': post_id}
        payload = get_payload(vk_token, offset)
        payload.update(extra_payload)
        response = requests.post(url=url, data=payload)
        vk_response = check_response(response)
        offset += 100
        count_likes = vk_response['count']
        likes.extend(vk_response['items'])
    return set(likes)


def run_vk():
    load_dotenv()
    vk_token = os.getenv('VK_TOKEN')
    vk_group_name = os.getenv('VK_GROUP_NAME')
    vk_posts_amount = os.getenv('VK_POSTS_AMOUNT')

    group_id = get_group_id(vk_token, vk_group_name)

    posts = fetch_posts(vk_token,vk_group_name)[:vk_posts_amount]
    core_audience = []
    for post_id in posts:
        comments = get_commetns(vk_token, post_id, group_id)
        last_comments = fetch_comments_period(comments)
        comments = fetch_comments_ids(last_comments, group_id)
        likes = fetch_all_likes(vk_token, group_id, post_id)
        core_audience.append(comments.difference(likes))
    print(core_audience)


if __name__ == '__main__':
    run_vk()
