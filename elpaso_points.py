import csv
import json
import requests

f_name = "./streetcar_survey_responses.csv"

#find a way to automate retrieval
jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo1LCJ1c2VybmFtZSI6ImJyYmF0dEBobnRiLmNvbSIsImV4cCI6MTYyODM0OTAzNCwiZW1haWwiOiJicmJhdHRAaG50Yi5jb20ifQ.W1G_zF6vy5kREVdjLQjRKL8y9yId2Ntd6f36VqQ_D2I"
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

headers = ['home_x', 'home_y', 'work_x', 'work_y', 'school_x', 'school_y', 'play_x', 'play_y', 'other_x', 'other_y', 'ex2_x', 'ex2_y', 'ex5_x', 'ex5_y']
to_csv = []

points_csv = []
points_csv.append(['home_x', 'home_y', 'work_x', 'work_y', 'school_x', 'school_y', 'play_x', 'play_y', 'other_x', 'other_y', 'ex2_x', 'ex2_y', 'ex5_x', 'ex5_y'])

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
    other_x = ''
    other_y = ''
    coords_w_type = response['response_json']['coordinatesWithType']
    for coords in coords_w_type:
        if 'type' in coords:
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
        else:
            other_x = coords['x']
            other_y = coords['y']
    ex2 = response['response_json']['EX2']
    ex5 = response['response_json']['EX5']
    for entry in ex2:
        ex2_x = entry['x']
        ex2_y = entry['y']
    for entry in ex5:
        ex5_x = entry['x']
        ex5_y = entry['y']
    response_list = [""] * len(headers) # create placeholders
    response_list[headers.index('home_x')] = home_x
    response_list[headers.index('home_y')] = home_y
    response_list[headers.index('work_x')] = work_x
    response_list[headers.index('work_y')] = work_y
    response_list[headers.index('school_x')] = school_x
    response_list[headers.index('school_y')] = school_y
    response_list[headers.index('play_x')] = play_x
    response_list[headers.index('play_y')] = play_y
    response_list[headers.index('other_x')] = other_x
    response_list[headers.index('other_y')] = other_y
    response_list[headers.index('ex2_x')] = ex2_x
    response_list[headers.index('ex2_y')] = ex2_y
    response_list[headers.index('ex5_x')] = ex5_x
    response_list[headers.index('ex5_y')] = ex5_y
    points_csv.append(response_list)

with open('elpaso_points.csv', mode='w', newline="", encoding='utf-8') as sce_file:
    sce_writer = csv.writer(sce_file, delimiter=';')
    sce_writer.writerows(points_csv)

