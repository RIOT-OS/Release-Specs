import logging
import os
import re
import subprocess

from bs4 import BeautifulSoup
from github import Github, GithubException


STICKY_COMMENT_COMMENT = "<!-- release-specs results {user} -->"
GITHUB_DOMAIN = "github.com"
API_URL = "https://api.%s" % GITHUB_DOMAIN
REPO_NAME = "RIOT-OS/Release-Specs"
GITHUBTOKEN_FILE = ".riotgithubtoken"
OUTCOME_EMOJIS = {
    "passed": "✔",
    "failed": "✖",
    "skipped": "🟡",
    "rerun": "🔁",
}


logger = logging.getLogger(__name__)
spec_comp = re.compile(
    r"- \[(?P<done>\s|x)\] \[(?P<name>(?P<spec>\d{2})-\S*)\]\((?P<url>[^)]+)\)"
)
task_comp = re.compile(
    r"- \[(?P<done>\s|x)\] "
    r"\[(?P<name>Task #(?P<task>\d{2})[^\]]*)\]\((?P<url>[^)]+)\)"
)


def get_rc():
    output = subprocess.check_output([
        "git", "-C", os.environ["RIOTBASE"], "log", "-1", "--oneline",
        "--decorate"
    ]).decode()
    m = re.search(r"tag:\s(?P<release>\d{4}.\d{2})-(?P<candidate>RC\d+)",
                  output)
    if m is None:
        logger.warning("Not a release candidate")
        logger.warning("  {}".format(output))
        return None
    return m.groupdict()


def get_task(nodeid):
    m = re.search(r"test_spec(?P<spec>\d+)\.py::test_task(?P<task>\d+)"
                  r"(\[(?P<params>[0-9a-zA-Z_-]+)\])",
                  nodeid)
    if m is None:
        logger.warning("Can not find task in {}".format(nodeid))
        return None
    return {k: int(v) if k != 'params' else v
            for k, v in m.groupdict().items()}


def get_user_name(github):
    return github.get_user().login


def get_access_token():
    try:
        with open(os.path.join(os.environ["HOME"], GITHUBTOKEN_FILE)) as tf:
            return tf.read().strip()
    except FileNotFoundError:
        logger.warning("~/{} not found".format(GITHUBTOKEN_FILE))
        return None


def get_github():
    access_token = get_access_token()
    if not access_token:
        return None
    return Github(access_token, base_url=API_URL)


def get_repo(github):
    try:
        return github.get_repo(REPO_NAME)
    except GithubException as e:
        logger.error("Unable to get {}: {}".format(REPO_NAME, e))
        return None


def get_rc_tracking_issue(repo, rc):
    issue = None
    try:
        for i in repo.get_issues(state="open"):
            if i.title == "Release {release} - {candidate}".format(**rc):
                issue = i
                break
        if issue is None:
            logger.error("No tracking issue found for {release}-{candidate}"
                         .format(**rc))
    except GithubException as e:
        logger.error("Unable to get repo's issues: {}".format(e))
    return issue


def mark_task_done(user, comment_url, issue, task_line, tested_task):
    new_task_line = task_line.replace("- [ ]", "- [x]")
    # trailing whitespace in case something was added after in the meantime
    if new_task_line != task_line:
        if comment_url:
            new_task_line += " @{} (see {}) ".format(user, comment_url)
        else:
            new_task_line += " @{} ".format(user)
    try:
        issue.update()      # reload body in case something changed
        new_body = issue.body.replace(task_line, new_task_line)
        issue.edit(body=new_body)
    except GithubException as e:
        logger.error("Unable to mark {}.{} in the tracking issue: {}"
                     .format(tested_task["spec"], tested_task["task"], e))


def find_task_text(issue_body, tested_task):
    spec = None
    for line in issue_body.splitlines():
        m = spec_comp.search(line)
        if m is not None:
            spec = m.groupdict()
            spec["spec"] = int(spec["spec"])
            spec["done"] = (spec["done"] == "x")
            continue
        if spec:
            m = task_comp.search(line)
            if m is not None and spec["spec"] == tested_task["spec"] and \
               int(m.group("task")) == tested_task["task"]:
                task = m.groupdict()
                task["spec"] = spec
                task["name"] = re.sub(r"#(\d+)", r"\1", task["name"])
                task["task"] = int(task["task"])
                task["done"] = (task["done"] == "x")
                if tested_task.get("params") is not None:
                    params = tested_task["params"]
                    # remove 'nodes0' param which is used for fixture
                    params = re.sub(r'nodes\d+', '', params)
                    # deduplicate dashes
                    params = re.sub(r'--+', '-', params)
                    params = params.strip('-')
                    if params:  # only add if there is anything left of params
                        task["params"] = params
                task_line = line
                return task_line, task
    return None, None


def find_previous_comment(github, issue):
    comment_comment = STICKY_COMMENT_COMMENT.format(user=get_user_name(github))
    for comment in issue.get_comments():
        if comment_comment in comment.body:
            return comment
    return None


def create_comment(github, issue):
    body = "<h1>Test Report</h1>\n\n"
    body += STICKY_COMMENT_COMMENT.format(user=get_user_name(github))
    body += """
<table>
  <thead>
    <tr><th></th><th>Task</th><th>Outcome</th></tr>
  </thead>
  <tbody>
  </tbody>
</table>
"""
    try:
        return issue.create_comment(body)
    except GithubException as e:
        logger.error("Unable to comment: {}".format(e))
        return None


def _generate_outcome_summary(pytest_report):
    run_url = None
    if "GITHUB_RUN_ID" in os.environ and \
       "GITHUB_REPOSITORY" in os.environ and \
       "GITHUB_SERVER_URL" in os.environ:
        run_url = "{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}/actions/runs/" \
                  "{GITHUB_RUN_ID}".format(**os.environ)
    return "<strong>{a_open}{outcome}{a_close}</strong>".format(
        a_open='<a href="{}">'.format(run_url) if run_url else '',
        outcome=pytest_report.outcome.upper(),
        a_close='</a>' if run_url else ''
    )


def get_tasks(comment, tbody, task):
    tasks = []
    task_already_exists = False
    for row in tbody.children:
        if row.name != 'tr':
            continue
        cells = list(row.find_all('td'))
        try:
            emoji = cells[0].decode_contents()
            task_cell = cells[1].find_all('a')[0]
            outcome = BeautifulSoup(
                ' '.join(str(t).strip() for t in cells[2].contents),
                'html.parser'
            )
        except IndexError:
            logger.error("Unexpected table format in %s:\n%s",
                         comment, row)
            continue
        task_title = task_cell.decode_contents().strip()
        try:
            task_url = task_cell['href']
        except KeyError:
            logger.error("Unexpected table format in %s:\n%s",
                         comment, task_cell)
            continue
        if task_title == task["title"].strip():
            task_already_exists = True
            emoji = task["emoji"]
            task_url = task["url"]
            outcome = task["outcome"]
        tasks.append((task_title, task_url, emoji, outcome))
    if not task_already_exists:
        tasks.append((task["title"].strip(), task["url"], task["emoji"],
                      task["outcome"]))
    tasks.sort()
    return tasks


def _update_soup(soup, tbody, tasks):
    tbody.clear()
    for task in tasks:
        tr = soup.new_tag("tr")
        tbody.append(tr)
        emoji_td = soup.new_tag("td")
        emoji_td.append(task[2])
        tr.append(emoji_td)
        task_td = soup.new_tag("td")
        task_a = soup.new_tag("a", href=task[1])
        task_a.string = task[0]
        task_td.append(task_a)
        tr.append(task_td)
        outcome_td = soup.new_tag("td")
        outcome_td.append(task[3])
        tr.append(outcome_td)


def _make_title(task):
    """
    >>> _make_title({'spec': {'spec': 4}, 'name': 'foobar'})
    '04. foobar'
    >>> _make_title({'spec': {'spec': 5}, 'name': 'snafu', 'params': 'params'})
    '05. snafu [params]'
    """
    title = "{:02d}. {}".format(task["spec"]["spec"], task["name"]).strip()
    if task.get("params") is not None:
        title += " [{}]".format(task["params"])
    return title


def update_comment(pytest_report, comment, task):
    soup = BeautifulSoup(comment.body, "html.parser")
    task["title"] = _make_title(task)
    task["outcome"] = BeautifulSoup(_generate_outcome_summary(pytest_report),
                                    "html.parser")
    task["emoji"] = OUTCOME_EMOJIS[pytest_report.outcome.lower()]
    tbody = soup.find('tbody')
    if tbody is None:
        logger.error("Unable to find table body in %s:\n%s",
                     comment, comment.body)
        return
    _update_soup(soup, tbody, get_tasks(comment, tbody, task))
    try:
        comment.edit(soup.prettify(formatter="html5"))
    except GithubException as e:
        logger.error("Unable to update comment: {}".format(e))


def make_comment(pytest_report, issue, task, github):
    comment = find_previous_comment(github, issue)
    if comment is None:
        comment = create_comment(github, issue)
    if comment is not None:
        update_comment(pytest_report, comment, task)
    return comment


# pylint: disable=R0911,R0912
def update_issue(pytest_report):    # noqa: C901
    if pytest_report.when not in ['call', 'setup'] or \
       (pytest_report.when == 'setup' and pytest_report.outcome != 'skipped'):
        return
    tested_task = get_task(pytest_report.nodeid)
    if not tested_task:
        return
    rc = get_rc()
    if not rc:
        return
    github = get_github()
    if not github:
        return
    repo = get_repo(github)
    if not repo:
        return
    issue = get_rc_tracking_issue(repo, rc)
    if not issue:
        return
    try:
        task_line, task = find_task_text(issue.body, tested_task)
    except GithubException as e:
        logger.error("Unable to get issue text of {}: {}"
                     .format(issue, e))
        return
    if not task_line or not task:
        logger.warning("Unable to find task {spec}.{task} in the "
                       "tracking issue".format(**tested_task))
    else:
        comment = make_comment(pytest_report, issue, task, github)
        if comment:
            comment_url = comment.html_url
        else:
            comment_url = None
        if not task["done"] and pytest_report.outcome == "passed":
            mark_task_done(get_user_name(github), comment_url, issue,
                           task_line, tested_task)
        elif task["done"]:
            logger.info("Task {spec}.{task} is already marked done in the "
                        "tracking issue".format(**tested_task))
