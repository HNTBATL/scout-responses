import csv
import json
import requests

f_name = "./streetcar_survey_responses.csv"

#find a way to automate retrieval
jwt = "JWT eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjo0LCJ1c2VybmFtZSI6ImJyYmF0dEBobnRiLmNvbSIsImV4cCI6MTYzNDc2MzE3OSwiZW1haWwiOiJicmJhdHRAaG50Yi5jb20ifQ.D8JoxLmFga3ux3ZQp2jEbV485piBHj7RiaTD8Ztvl3M"

survey_id = 2
survey_json = requests.post(f"https://scout-lai10-api.scoutfeedback.com/api/surveyJSON/{survey_id}", headers={"authorization": jwt})
survey_responses_json = requests.post("https://scout-lai10-api.scoutfeedback.com/api/responseJSON", headers={"authorization": jwt})
stakeholders_json = requests.post("https://scout-lai10-api.scoutfeedback.com/api/stakeholders", headers={"authorization": jwt})

try:
    survey_json = requests.post(f"https://scout-lai10-api.scoutfeedback.com/api/surveyJSON/{survey_id}", headers={"authorization": jwt})
    survey_json.raise_for_status()
except requests.exceptions.HTTPError as err:
    print('RESPONSE ERROR: ', err)

survey = json.loads(survey_json.text)
survey_responses = json.loads(survey_responses_json.text)
stakeholders = json.loads(stakeholders_json.text)

survey_questions = [question for question in survey['survey_json']['pages'][0]['elements']]
survey_responses = [r for r in survey_responses if r['survey'] == survey_id]

print(len(survey_responses))

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

headers = list(set(headers)) + ["comment_location"] + ['stakeholder_id']

to_csv = []
to_csv.append([header_title_dict.get(header, 'NOTITLE') for header in headers])

for response in survey_responses:
    comment_location = response['comment_location']
    response_list = [""] * len(headers) # create placeholders
    response_list[headers.index('comment_location')] = comment_location
    for question, answer in response['response_json'].items():
        response_list[headers.index(question)] = answer
    to_csv.append(response_list)

with open('sce_responses.csv', mode='w', newline="", encoding='utf-8') as sce_file:
    sce_writer = csv.writer(sce_file, delimiter=';')
    sce_writer.writerows(to_csv)