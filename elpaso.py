import csv
import json
import requests
from jwt_tokens import jwt

print(jwt)

f_name = "./streetcar_survey_responses.csv"

#find a way to automate retrieval
api_url = "https://txdot-api.scoutfeedback.com/api"

survey_id = 1
survey_json = requests.post(f"https://txdot-api.scoutfeedback.com/api/surveyJSON/{survey_id}", headers={"authorization": jwt})
survey_responses_json = requests.post("https://txdot-api.scoutfeedback.com/api/responseJSON", headers={"authorization": jwt})
stakeholders_json = requests.post("https://txdot-api.scoutfeedback.com/api/stakeholders", headers={"authorization": jwt})

survey = json.loads(survey_json.text)
survey_responses = json.loads(survey_responses_json.text)
stakeholders = json.loads(stakeholders_json.text)

survey_responses = [r for r in survey_responses if r['survey'] == survey_id]

survey_count = len(survey_responses)

print(survey_count)

headers = []
for response in survey_responses:
    response_list = [""] * len(headers) # create placeholders
    for answer in response['response_json']:
        headers.append(answer)

headers = list(set(headers)) + ["comment_location"] + ['first_name'] + ['last_name'] + ['zip_code']

to_csv = []

trip_from_csv = []
trip_from_csv.append(['first_name', 'last_name', 'zip', 'x', 'y'])

trip_to_csv = []
trip_to_csv.append(['first_name', 'last_name', 'zip', 'x', 'y'])

def pull_points(pnt_list):
    xy_coords = {}
    from_coords = []
    to_coords = []
    for key in pnt_list:
        if key == 'starting_from':
            for pnt in pnt_list[key]:
                from_coords.append([pnt['x'], pnt['y']])
        if key == 'going_to':
            for pnt in pnt_list[key]:
                to_coords.append([pnt['x'], pnt['y']])
    xy_coords['starting_from'] = from_coords
    xy_coords['going_to'] = to_coords
    return xy_coords

# print('#################################### START PRINT ######################################')
# print(survey_responses[0]['response_json']['EX2'])
# print('#################################### END PRINT ########################################')
for response in survey_responses:
    ex2_x = ''
    ex2_y = ''
    ex5_x = ''
    ex5_y = ''
    home_x = ''
    home_y = ''
    work_x = ''
    work_y = ''
    school_x = ''
    school_y = ''
    play_x = ''
    play_y = ''
    print('########################################################################################################')
    coords_w_type = response['response_json']['coordinatesWithType']
    for coords in coords_w_type:
        if 'type' in coords:
            print('COORDS: ', coords)
            if coords['type'] == 'home':
                home_x = coords['x']
                home_y = coords['y']
            if coords['type'] == 'work':
                work_x = coords['x']
                work_y = coords['y']
            if coords['type'] == 'school':
                school_x = coords['x']
                school_y = coords['y']
            if coords['type'] == 'play':
                play_x = coords['x']
                play_y = coords['y']
    ex2 = response['response_json']['EX2']
    ex5 = response['response_json']['EX5']
    for entry in ex2:
        ex2_x = entry['x']
        ex2_y = entry['y']
    for entry in ex5:
        ex5_x = entry['x']
        ex5_y = entry['y']
    # print('RESPONSE: ', ex2_x, ex2_y, ex5_x, ex5_y)
    # print(response['response_json'])
    comment_location = response['comment_location']
    xy_coords = pull_points(comment_location)
    coords_from = xy_coords['starting_from']
    coords_to = xy_coords['going_to']
    survey_taker_id = response['survey_taker_id']
    stakeholder = [sh for sh in stakeholders if sh['pk'] == survey_taker_id][0]
    stakeholder_first_name = stakeholder['first_name'].split('-')[0]
    stakeholder_last_name = stakeholder['last_name'].split('-')[0]
    stakeholder_zip_code = stakeholder['postal_code']
    response_list = [""] * len(headers) # create placeholders
    # response_list[headers.index('comment_location')] = comment_location
    # response_list[headers.index('first_name')] = stakeholder_first_name
    # response_list[headers.index('last_name')] = stakeholder_last_name
    # response_list[headers.index('zip_code')] = stakeholder_zip_code
    response_list['home_x'] = home_x
    response_list['home_y'] = home_y

    # to_csv.append(home_x, home_y, work_x, work_y, school_x, school_y, play_x, play_y, ex2_x, ex2_y, ex5_x, ex5_y)
    to_csv.append(response_list)

with open('elpaso_responses.csv', mode='w', newline="", encoding='utf-8') as sce_file:
    sce_writer = csv.writer(sce_file, delimiter=';')
    sce_writer.writerows(to_csv)

