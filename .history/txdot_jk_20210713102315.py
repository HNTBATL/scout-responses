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

print(len(survey_responses))
# print(survey_responses[0])
# print(stakeholders[0])

def create_questions_dict(survey_questions):
    questions = {}
    for question in survey_questions:
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

type_csv = []
type_csv.append(['first_name', 'last_name', 'zip', 'home_x', 'home_y', 'work_x', 'work_y', 'meet_x', 'meet_y', 'play_x', 'play_y'])

def pull_type_points(pnt_list):
    xy_coords = {}
    for pnt in pnt_list:
        lwp_type = pnt.get('type', None)
        if lwp_type:
            xy_coords[lwp_type] = (pnt['x'], pnt['y'])
        else:
            pass
    return xy_coords

for response in survey_responses:
    comment_location = response['comment_location'] # yields array
    type_coords = pull_type_points(comment_location)
    # print(type_coords)
    survey_taker_id = response['survey_taker_id']
    stakeholder = [sh for sh in stakeholders if sh['pk'] == survey_taker_id][0]
    stakeholder_first_name = stakeholder['first_name']
    stakeholder_last_name = stakeholder['last_name']
    stakeholder_zip_code = stakeholder['postal_code']
    response_list = [""] * len(headers) # create placeholders
    response_list[headers.index('comment_location')] = comment_location
    response_list[headers.index('first_name')] = stakeholder_first_name
    response_list[headers.index('last_name')] = stakeholder_last_name
    response_list[headers.index('zip_code')] = stakeholder_zip_code
    going_to_x, going_to_y = type_coords.get('going_to', (0, 0))
    starting_from_x, starting_from_y = type_coords.get('starting_from', (0, 0))
    type_csv.append((stakeholder_first_name, stakeholder_last_name, stakeholder_zip_code, going_to_x, going_to_y, starting_from_x, starting_from_y))
    for question, answer in response['response_json'].items():
        response_list[headers.index(question)] = answer
    to_csv.append(response_list)


# with open('sce_spatial.csv', mode='w', newline="", encoding='utf-8') as sce_spatial:
#     sce_spatial_writer = csv.writer(sce_spatial, delimiter=';')
    # sce_spatial_writer.writerows(to_csv)

with open('sce_responses.csv', mode='w', newline="", encoding='utf-8') as sce_file:
    sce_writer = csv.writer(sce_file, delimiter=';')
    sce_writer.writerows(to_csv)

with open('sce_type.csv', mode='w', newline="", encoding='utf-8') as sce_type_file:
    sce_type_writer = csv.writer(sce_type_file, delimiter=',')
    sce_type_writer.writerows(type_csv)