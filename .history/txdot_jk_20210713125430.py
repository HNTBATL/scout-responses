import csv
import json
import requests

f_name = "./streetcar_survey_responses.csv"

#find a way to automate retrieval
jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6ImJyYmF0dEBobnRiLmNvbSIsImV4cCI6MTYyODM0OTAzNCwiZW1haWwiOiJicmJhdHRAaG50Yi5jb20ifQ.W1G_zF6vy5kREVdjLQjRKL8y9yId2Ntd6f36VqQ_D2I"

survey_id = 12
survey_json = requests.post(f"https://staging-api.scoutfeedback.com/api/surveyJSON/{survey_id}", headers={"authorization": jwt})
survey_responses_json = requests.post("https://staging-api.scoutfeedback.com/api/responseJSON", headers={"authorization": jwt})
stakeholders_json = requests.post("https://staging-api.scoutfeedback.com/api/stakeholders", headers={"authorization": jwt})

survey = json.loads(survey_json.text)
survey_responses = json.loads(survey_responses_json.text)
stakeholders = json.loads(stakeholders_json.text)

survey_questions = [question for question in survey['survey_json']['pages'][0]['elements']]
survey_responses = [r for r in survey_responses if r['survey'] == survey_id]

survey_count = len(survey_responses)

print(survey_count)
# print(survey_responses[0])
# print(stakeholders[0])

def create_questions_dict(survey_questions):
    questions = {}
    for question in survey_questions:
        is_panel_type = question.get('type', False)
        print(is_panel_type)
        if is_panel_type == 'panel':            
            for q in question["elements"]:
                questions[q['name']] = q.get('title', 'NOTITLE')
        else:
            questions[question['name']] = question.get('title', 'NOTITLE')
    return questions

header_title_dict = create_questions_dict(survey_questions)
headers = [q for q in create_questions_dict(survey_questions).keys()]

headers = []
for response in survey_responses:
    response_list = [""] * len(headers) # create placeholders
    for answer in response['response_json']:
        headers.append(answer)

headers = list(set(headers)) + ["comment_location"] + ['first_name'] + ['last_name'] + ['zip_code']

to_csv = []
to_csv.append([header_title_dict.get(header, 'NOTITLE') for header in headers])

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

for response in survey_responses:
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
    response_list[headers.index('comment_location')] = comment_location
    response_list[headers.index('first_name')] = stakeholder_first_name
    response_list[headers.index('last_name')] = stakeholder_last_name
    response_list[headers.index('zip_code')] = stakeholder_zip_code
    if coords_from != None:
        for x, y in coords_from:
            trip_from_csv.append((stakeholder_first_name, stakeholder_last_name, stakeholder_zip_code, x, y))
    if coords_to != None:
        for x, y in coords_to:
            trip_to_csv.append((stakeholder_first_name, stakeholder_last_name, stakeholder_zip_code, x, y))
    for question, answer in response['response_json'].items():
        response_list[headers.index(question)] = answer
    to_csv.append(response_list)

with open('txdot_responses.csv', mode='w', newline="", encoding='utf-8') as sce_file:
    sce_writer = csv.writer(sce_file, delimiter=';')
    sce_writer.writerows(to_csv)

with open('txdo_trip_from.csv', mode='w', newline="", encoding='utf-8') as sce_safety_file:
    sce_safety_writer = csv.writer(sce_safety_file, delimiter=',')
    sce_safety_writer.writerows(trip_from_csv)

with open('txdot_trip_to.csv', mode='w', newline="", encoding='utf-8') as sce_safety_file:
    sce_safety_writer = csv.writer(sce_safety_file, delimiter=',')
    sce_safety_writer.writerows(trip_to_csv)
