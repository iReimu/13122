import requests
from datetime import date


country = 1
version = '5.131'
token = 'vk1.a.2uccwV6kWU53fqZHJizOJTkgNhilejrow5HW_J7X8do5QF11Ap5_js4uNoaM5Fmq6q4M8tN_HWoItykzKzgnzW5FBDQ0zfYRnBzOS5UQLRiwtg8PxU1mbTUU7CRfELBlgpgRa8uuwq3wPFiSB7Se0_bSLnqVNITCubnzMFnIri9u9vfJA-AVa0AMHyAZASUH'
count = 999
has_photo = 1
online = 0
all_users = []
count_users = 0


def make_request(sex, city, age_from, age_to):
    current_year = date.today().year
    print(f'making request with: {sex} {city} {age_from} {age_to}')
    for i in range(age_from, age_to + 1):
        age = current_year - i
        r = requests.get('https://api.vk.com/method/users.search',
                         params={
                             'offset': 1,
                             'count': 1000,
                             'access_token': token,
                             'v': version,
                             'country': country,
                             'city': city,
                             'sex': sex,
                             'has_photo': has_photo,
                             'birth_year': age,
                             'sort': 1,
                             'online': online,
                             'fields': 'personal, quotes, about, activities, books, domain, games, movies, music, online, photo_400_orig, education, status, relation'
                         })
        all_users.extend(r.json()['response']['items'])
    return all_users

