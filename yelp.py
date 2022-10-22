import requests
import json

business_id = 'NkP2RxMxJdX5tYL22gsHSA'

API_KEY = 'Gm2_Eqv8w2kpyhMqFYBJns1p2KNRtG5NY_LtrK6TDt_DtqVm2zqpL8LM4yzqLV-VTyI0ja8c5fpN73nC31aXCoaJWNuMc2YoUZv2MrtvGVbM4dR4Tg4TTYkxVU9PY3Yx'
END_POINT = 'https://api.yelp.com/v3/businesses/search'
HEADERS = {'Authorization': 'bearer %s' % API_KEY}

offset = 0
arr = []
count = 0
dic = {}

while offset != 500:
    PARAMETERS = {
        'term': 'Mexican',
        'location': 'NYC',
        'limit': 50,
        'offset': offset
    }
    response = requests.get(url=END_POINT, params=PARAMETERS, headers=HEADERS)
    business_data = response.json()
    for biz in business_data['businesses']:
        dic['id'] = biz['id']
        dic['name'] = biz['name']
        dic['rating'] = biz['rating']
        dic['review_count'] = biz['review_count']
        dic['address'] = biz['location']['display_address'][0]
        dic['zip_code'] = biz['location']['zip_code']
        dic['coordinate'] = (biz['coordinates']['latitude'],
                             biz['coordinates']['longitude'])
        arr.append(dic)
        dic = {}
        # arr.append(f"id: {biz['id']}, name: {biz['name']}, rating: {biz['rating']}, review_count: {biz['review_count']}, address: {biz['location']['display_address'][0]}, zip_code: {biz['location']['zip_code']}, coordinates: {biz['coordinates']['latitude'], biz['coordinates']['longitude']}")
    offset += 50

# Serializing json
json_object = json.dumps(arr, indent=4)
f = open("mexican-restaurant.json", "w")
f.write(str(json_object))
f.close()
