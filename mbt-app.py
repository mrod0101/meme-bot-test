import os, requests
from flask import Flask, request
from github import Github, GithubIntegration

app = Flask(__name__)

app_id = '226987'

with open(os.path.normpath(os.path.expanduser(r'~\kfiles\meme-bot-test.2022-08-09.private-key.pem')), 'r') as cert_f:
    app_key = cert_f.read()

    git_integration = GithubIntegration(app_id, app_key)


@app.route("/", methods=['POST'])
def bot():
    p = request.json


    # check is Github PR creation event
    if not all(k in p.keys() for k in ['action', 'pull_request']) and \
            p['action'] == 'opened':
        return 'ok'

    owner = p['repository']['owner']['login']
    repo_name = p['repository']['name']

    #get permission as bot
    git_connection = Github(
        login_or_token=git_integration.get_access_token(
            git_integration.get_installation(owner, repo_name).id).token)

    repo = git_connection.get_repo(f'{owner}/{repo_name}')

    issue = repo.get_issue(number=p['pull_request']['number'])

    # call meme-api to get a random meme
    response = requests.get(url='https://meme-api.herokuapp.com/gimme')
    if response.status_code != 200:
        return 'ok'

    meme_url = response.json()['preview']['-1']

    issue.create_comment(f"![Alt Text]({meme_url})")
    return 'ok'

if __name__ == "__main__":
    # deepcode ignore RunWithDebugTrue: not accessible by third party
    app.run(debug=True, port=5000) #nosec
