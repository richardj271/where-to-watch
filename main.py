import os

import requests
from simplejustwatchapi.justwatch import search

def call_baserow_api(token, table_id, command):

    response = requests.get(
        f"https://api.baserow.io/api/database/{command}/table/{table_id}/",
        headers={
            'Authorization': f'Token {token}'
        }
    )

    if response.status_code == 200:

        response_json = response.json()

        if 'next' in response_json:
            if response_json['next'] is not None or response_json['previous'] is not None:
                raise NotImplementedError("Paged results not yet supported.")
        
    else:

        print(f"Request failed with status code: {response.status_code}")
        raise RuntimeError()
    
    return response_json

def baserow_api_post(token, table_id, json):

    print(f"{json=}")

    response = requests.post(
        # Need user_field_names
        f"https://api.baserow.io/api/database/rows/table/{table_id}/?user_field_names=true",
        headers={
            'Authorization': f'Token {token}',
            "Content-Type": "application/json",
        },
        json=json,
    )

    # resp.raise_for_status()

    if response.status_code == 200:

        response_json = response.json()
        
    else:

        print(f"Request failed with status code: {response.status_code}")
        raise RuntimeError()
    
    return response_json

def baserow_api_patch(token, table_id, row_id, json):

    print(f"{json=}")

    response = requests.patch(
        # Need user_field_names
        f"https://api.baserow.io/api/database/rows/table/{table_id}/{row_id}/?user_field_names=true",
        headers={
            'Authorization': f'Token {token}',
            "Content-Type": "application/json",
        },
        json=json,
    )

    # resp.raise_for_status()

    if response.status_code == 200:

        response_json = response.json()
        
    else:

        print(f"Request failed with status code: {response.status_code}")
        raise RuntimeError()
    
    return response_json

def call_baserow_api_delete_row(token, table_id, row_id):

    response = requests.delete(
        f"https://api.baserow.io/api/database/rows/table/{table_id}/{row_id}/",
        headers={
            'Authorization': f'Token {token}'
        }
    )

    if response.status_code != 204:

        print(f"Request failed with status code: {response.status_code}")
        raise RuntimeError()
    
    return


def check_if_default_table(token, table_id):

    # Check we have only default fields
    response_json = call_baserow_api(token, table_id, 'fields')
    field_names = sorted([field['name'] for field in response_json])
    if field_names != ['Active', 'Name', 'Notes']:
        raise RuntimeError(':(')  # TODO Make this a custom error

    # Check rows...
    response_json = call_baserow_api(token, table_id, 'rows')
    results = response_json['results']

    # Check it's empty
    for row in results:
        for field_name, field_value in row.items():
            if field_name.startswith('field_'):
                if field_value not in ['', False]:
                    raise RuntimeError(':(')  # TODO Make this a custom error
    
    # Check two rows
    if len(results) != 2:
        raise RuntimeError(':(')
    
    return True


def delete_all_rows(token, table_id):

    response_json = call_baserow_api(token, table_id, 'rows')
    results = response_json['results']

    # Delete rows
    for row in results:
        print(row['id'])
        call_baserow_api_delete_row(token, table_id, row['id'])



def get_trakt_watchlist(trakt_client_id, user_id):

    def watchlist_json_rearrange(json_in):
        json_out = {
            # 'ID': json_in['id'],
            'Title': json_in['movie']['title'],
            'Year': str(json_in['movie']['year']),
            'IMDB ID': json_in['movie']['ids']['imdb'],
        }
        return json_out

    headers = {
        'Content-Type': 'application/json',
        'trakt-api-version': '2',
        'trakt-api-key': trakt_client_id,
    }

    type='movies'
    sort='added'

    # TODO Surprised I can just get this, is it public?
    r = requests.get(f'https://api.trakt.tv/users/{user_id}/watchlist/{type}/{sort}', headers=headers)

    watchlist_json = r.json()
    print(f"{len(watchlist_json)}")

    watchlist_json2 = []
    for watchlist_item in watchlist_json:
        watchlist_json2.append(
            watchlist_json_rearrange(watchlist_item)
        )

    return watchlist_json2

def add_watchlist_table(token, table_id, watchlist, update=False):
    for item in watchlist:
        if update:
            response_json = baserow_api_patch(token=token, table_id=table_id, json=item)
        else:
            response_json = baserow_api_post(token=token, table_id=table_id, json=item)
        
        print(response_json)

def find_film_on_justwatch(title, imdb_id):

    results = search(title, "GB", "en", 10, True)
    results_dict = {film.imdb_id: film for film in results if film.imdb_id is not None}

    try:
        film_info = results_dict[imdb_id]
    except KeyError:
        film_info = None

    return film_info

def find_films_on_justwatch(watchlist):
    
    watchlist2 = []
    for item in watchlist:
        justwatch_info = find_film_on_justwatch(item['Title'], item['IMDB ID'])

        if justwatch_info is None:

            justwatch_dict = {
                'URL': '',
                'Runtime /minutes': '',
                'Flatrate': [],
                'Rent': [],
            }

        else:

            justwatch_dict = {
                'URL': justwatch_info.url,
                'Runtime /minutes': justwatch_info.runtime_minutes,
                'Flatrate': ','.join([offer.name for offer in justwatch_info.offers if offer.monetization_type == 'FLATRATE']),
                'Rent': ','.join([offer.name for offer in justwatch_info.offers if offer.monetization_type == 'RENT']),
            }

        watchlist2.append(item | justwatch_dict)

    return watchlist2

# flatrates = []
# for _, row in df.iterrows():
#     offers = row['Offers']
#     print(set([offer.monetization_type for offer in offers]))

#     flatrate = [offer.name for offer in offers if offer.monetization_type == 'FLATRATE']
#     rent = [offer.name for offer in offers if offer.monetization_type == 'RENT']
    
#     print(flatrate)
#     # print(rent)

#     flatrates.append(flatrate)

# ##
    
# df['Flatrate'] = flatrates

if __name__ == '__main__':

    baserow_token = os.environ['BASEROW_TOKEN_WHERE_TO_WATCH']
    baserow_table_id = os.environ['BASEROW_FILMS_TABLE_ID']
    trakt_client_id = os.environ['TRAKT_CLIENT_ID_WHERE_TO_WATCH']
    trakt_user_id = os.environ['TRAKT_USER_ID']

    # is_default_table = check_if_default_table(token=baserow_token, table_id=baserow_table_id)
    # print(f"{is_default_table=}")

    # Don't actually always want to do this?
    delete_all_rows(token=baserow_token, table_id=baserow_table_id)

    # TODO Don't hardcode this
    watchlist = get_trakt_watchlist(trakt_client_id=trakt_client_id, user_id=trakt_user_id)

    # List of dicts with fields: Title, Year, IMDB ID
    print(f"{watchlist=}")

    # add_watchlist_table(token=baserow_token, table_id=baserow_table_id, watchlist=watchlist)

    watchlist2 = find_films_on_justwatch(watchlist)
    print(f"{watchlist2=}")

    # # NEEDS ROW ID
    # add_watchlist_table(token=baserow_token, table_id=baserow_table_id, watchlist=watchlist2, update=True)
    add_watchlist_table(token=baserow_token, table_id=baserow_table_id, watchlist=watchlist2)
