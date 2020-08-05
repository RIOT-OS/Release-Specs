import logging
import os
import re
import subprocess

from github import Github, GithubException


GITHUB_DOMAIN = "github.com"
API_URL = "https://api.%s" % GITHUB_DOMAIN
REPO_NAME = "RIOT-OS/Release-Specs"
GITHUBTOKEN_FILE = ".riotgithubtoken"


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
    m = re.search(r"test_spec(?P<spec>\d+)\.py::test_task(?P<task>\d+)",
                  nodeid)
    if m is None:
        logger.warning("Can not find task in {}".format(nodeid))
        return None
    return {k: int(v) for k, v in m.groupdict().items()}


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
                task_line = line
                return task_line, task
    return None, None


def make_comment(pytest_report, issue, task):
    comment = "### [{:02d}. {}]({})\n\n".format(
        task["spec"]["spec"],
        task["name"],
        task["url"]
    )
    run_url = None
    if "GITHUB_RUN_ID" in os.environ and \
       "GITHUB_REPOSITORY" in os.environ and \
       "GITHUB_SERVER_URL" in os.environ:
        run_url = "{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}/actions/runs/" \
                  "{GITHUB_RUN_ID}".format(**os.environ)
    comment += "<details><summary><strong>{}{}{}</strong></summary>\n\n" \
               .format(
                   '<a href="{}">'.format(run_url) if run_url else '',
                   pytest_report.outcome.upper(), '</a>' if run_url else ''
               )
    if pytest_report.longrepr:
        comment += "###### Failures\n\n"
        comment += "```\n"
        comment += str(pytest_report.longrepr)
        comment += "\n```\n\n"
    if pytest_report.sections:
        for title, body in pytest_report.sections:
            comment += "###### {}\n\n".format(title)
            comment += "```\n"
            comment += str(body)
            comment += "\n```\n\n"
    comment += "</details>"
    try:
        return issue.create_comment(comment)
    except GithubException as e:
        logger.error("Unable to comment: {}".format(e))
        return None


# pylint: disable=R0911,R0912
def update_issue(pytest_report):    # noqa: C901
    if pytest_report.when != 'call' or pytest_report.outcome == 'skipped':
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
    elif not task["done"]:
        comment = make_comment(pytest_report, issue, task)
        if comment:
            comment_url = comment.html_url
        else:
            comment_url = None
        if pytest_report.outcome == "passed":
            mark_task_done(github.get_user().login, comment_url, issue,
                           task_line, tested_task)
    else:
        logger.info("Task {spec}.{task} is already marked done in the "
                    "tracking issue".format(**tested_task))
