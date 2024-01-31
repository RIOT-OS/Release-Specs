import logging
import os
import re
import urllib.parse

from bs4 import BeautifulSoup
from github import Auth, Github, GithubException, InputFileContent

from testutils.git import Git, GitError


STICKY_COMMENT_COMMENT = "<!-- release-specs results {user} -->"
GIST_ID_COMMENT_FMT = "<!-- gist-id:{gist_id} -->"
GIST_ID_COMMENT_PATTERN = GIST_ID_COMMENT_FMT.format(gist_id="(?P<gist_id>[0-9a-f]+)")
GIT_QUIET = True
GITHUB_DOMAIN = "github.com"
API_URL = f"https://api.{GITHUB_DOMAIN}"
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
    try:
        output = Git(os.environ["RIOTBASE"]).log("-1", "--oneline", "--decorate")
    except GitError as exc:
        logger.error(exc)
        return None
    m = re.search(r"tag:\s(?P<release>\d{4}.\d{2})-(?P<candidate>RC\d+)", output)
    if m is None:
        logger.warning("Not a release candidate")
        logger.warning(f"  {output}")
        return None
    return m.groupdict()


def get_task(nodeid):
    m = re.search(
        r"test_spec(?P<spec>\d+)\.py::test_task(?P<task>\d+)"
        r"(\[(?P<params>[0-9a-zA-Z_-]+)\])",
        nodeid,
    )
    if m is None:
        logger.warning(f"Can not find task in {nodeid}")
        return None
    return {k: int(v) if k != 'params' else v for k, v in m.groupdict().items()}


def get_user_name(github):
    return github.get_user().login


def get_access_token():
    try:
        with open(
            os.path.join(os.environ["HOME"], GITHUBTOKEN_FILE), encoding='utf-8'
        ) as tf:
            return tf.read().strip()
    except FileNotFoundError:
        logger.warning(f"~/{GITHUBTOKEN_FILE} not found")
        return None


def get_github():
    access_token = get_access_token()
    if not access_token:
        return None
    return Github(auth=Auth.Token(access_token), base_url=API_URL)


def get_repo(github):
    try:
        return github.get_repo(REPO_NAME)
    except GithubException as e:
        logger.error(f"Unable to get {REPO_NAME}: {e}")
        return None


def get_rc_tracking_issue(repo, rc):
    issue = None
    try:
        for i in repo.get_issues(state="open"):
            # pylint: disable=C0209
            if i.title == "Release {release} - {candidate}".format(**rc):
                issue = i
                break
        if issue is None:
            # pylint: disable=C0209
            logger.error(
                "No tracking issue found for {release}-{candidate}".format(**rc)
            )
    except GithubException as e:
        logger.error(f"Unable to get repo's issues: {e}")
    return issue


def mark_task_done(user, comment_url, issue, task_line, tested_task):
    new_task_line = task_line.replace("- [ ]", "- [x]")
    # trailing whitespace in case something was added after in the meantime
    if new_task_line != task_line:
        if comment_url:
            new_task_line += f" @{user} (see {comment_url}) "
        else:
            new_task_line += f" @{user} "
    try:
        issue.update()  # reload body in case something changed
        new_body = issue.body.replace(task_line, new_task_line)
        issue.edit(body=new_body)
    except GithubException as e:
        spec = tested_task['spec']
        spec_task = tested_task['task']
        logger.error(
            f"Unable to mark {spec}.{spec_task} " f"in the tracking issue: {e}"
        )


def find_task_text(issue_body, tested_task):
    spec = None
    for line in issue_body.splitlines():
        m = spec_comp.search(line)
        if m is not None:
            spec = m.groupdict()
            spec["spec"] = int(spec["spec"])
            spec["done"] = spec["done"] == "x"
            continue
        if spec:
            m = task_comp.search(line)
            if (
                m is not None
                and spec["spec"] == tested_task["spec"]
                and int(m.group("task")) == tested_task["task"]
            ):
                task = m.groupdict()
                task["spec"] = spec
                task["name"] = re.sub(r"#(\d+)", r"\1", task["name"])
                task["task"] = int(task["task"])
                task["done"] = task["done"] == "x"
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
    run_url = None
    if (
        "GITHUB_RUN_ID" in os.environ
        and "GITHUB_REPOSITORY" in os.environ
        and "GITHUB_SERVER_URL" in os.environ
    ):
        # pylint: disable=C0209
        run_url = (
            "{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}/actions/runs/"
            "{GITHUB_RUN_ID}".format(**os.environ)
        )

    # pylint: disable=C0209
    body = "<h1>{a_open}Test Report{a_close}</h1>\n\n".format(
        a_open='<a href="{}">'.format(run_url) if run_url else '',
        a_close='</a>' if run_url else '',
    )
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
        logger.error(f"Unable to comment: {e}")
        return None


def _generate_outcome_summary(pytest_report, task):
    # pylint: disable=C0209
    return "<strong>{a_open}{outcome}{a_close}</strong>".format(
        a_open=(
            '<a href="{}">'.format(task["outcome_url"]) if "outcome_url" in task else ''
        ),
        outcome=pytest_report.outcome.upper(),
        a_close='</a>' if "outcome_url" in task else '',
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
                ' '.join(str(t).strip() for t in cells[2].contents), 'html.parser'
            )
        except IndexError:
            logger.error("Unexpected table format in %s:\n%s", comment, row)
            continue
        task_title = task_cell.decode_contents().strip()
        try:
            task_url = task_cell['href']
        except KeyError:
            logger.error("Unexpected table format in %s:\n%s", comment, task_cell)
            continue
        if task_title == task["title"].strip():
            task_already_exists = True
            emoji = task["emoji"]
            task_url = task["url"]
            outcome = task["outcome"]
        tasks.append((task_title, task_url, emoji, outcome))
    if not task_already_exists:
        tasks.append(
            (task["title"].strip(), task["url"], task["emoji"], task["outcome"])
        )
    tasks.sort()
    return tasks


def _update_soup(soup, tbody, tasks):
    if (
        "GITHUB_RUN_ID" in os.environ
        and "GITHUB_REPOSITORY" in os.environ
        and "GITHUB_SERVER_URL" in os.environ
    ):
        title = soup.find("h1")
        if title:
            run_a = title.find("a")
            # pylint: disable=C0209
            url = (
                "{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}/"
                "actions/runs/{GITHUB_RUN_ID}".format(**os.environ)
            )
            if run_a:
                run_a["href"] = url
            else:
                content = ' '.join(str(t).strip() for t in title.contents)
                title.clear()
                title.append(
                    BeautifulSoup(f'<a href="{url}">' + content + '</a>', 'html.parser')
                )
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
    title = f"{task['spec']['spec']:02d}. {task['name']}".strip()
    if task.get("params") is not None:
        title += f" [{task['params']}]"
    return title


def update_comment(pytest_report, comment, task):
    soup = BeautifulSoup(comment.body, "html.parser")
    if "gist_id" in task:
        soup.insert(
            0,
            BeautifulSoup(
                GIST_ID_COMMENT_FMT.format(gist_id=task["gist_id"]), "html.parser"
            ),
        )
    task["title"] = _make_title(task)
    task["outcome"] = BeautifulSoup(
        _generate_outcome_summary(pytest_report, task), "html.parser"
    )
    task["emoji"] = OUTCOME_EMOJIS[pytest_report.outcome.lower()]
    tbody = soup.find('tbody')
    if tbody is None:
        logger.error("Unable to find table body in %s:\n%s", comment, comment.body)
        return
    _update_soup(soup, tbody, get_tasks(comment, tbody, task))
    try:
        comment.edit(soup.prettify(formatter="html5"))
    except GithubException as e:
        logger.error(f"Unable to update comment: {e}")


def generate_outcome_content(pytest_report, task):
    params = task.get('params')
    # pylint: disable=C0209
    filename = 'task_{spec:02d}.{task:02d}{params}_result.md'.format(
        spec=task['spec']['spec'],
        task=task['task'],
        params='.{}'.format(params) if params else '',
    )
    content = ""
    if pytest_report.outcome in ['passed', 'failed']:
        content += f'# {task["spec"]["spec"]:02d}. {task["name"]} ['
        if task.get('params'):
            content += task['params'] + '] ['
        content += pytest_report.outcome.upper()
        content += ']\n'
        if pytest_report.longrepr:
            content += "## Failures\n\n"
            content += "```\n"
            content += str(pytest_report.longrepr)
            content += "\n```\n\n"
        if pytest_report.sections:
            for title, body in pytest_report.sections:
                content += f"## {title}\n\n"
                content += "```\n"
                content += str(body)
                content += "\n```\n\n"
    if content:
        return {filename: content}
    return {}


def gist_file_url(gist_url, filename, ref=''):
    file_slug = re.sub('[^0-9A-Za-z_]+', '-', filename)
    return f'{gist_url}/{ref}#{file_slug}'


def github_file_url(repo_url, filepath, ref='main'):
    if GITHUB_DOMAIN not in repo_url:
        return None
    return f'{repo_url}/blob/{ref}/{filepath}'


def upload_result_content(github, repo, repo_url, new_content):
    try:
        if repo.exists():
            repo.pull()
        else:
            pull_url = list(urllib.parse.urlsplit(repo_url))
            # add user credentials to URL to be able to push to HTTPS
            username = get_user_name(github)
            pull_url[1] = f'{username}:{get_access_token()}@{pull_url[1]}'
            repo = Git.clone(
                urllib.parse.urlunsplit(pull_url), repo.repodir, quiet=GIT_QUIET
            )
        for filename in new_content:
            with open(
                os.path.join(repo.repodir, filename), 'w', encoding='utf-8'
            ) as file:
                file.write(new_content[filename])
            repo.add(filename)
            if repo.staging_changed():
                repo.commit('-m', f'Add {filename}')
        repo.push()
        return repo.head_sha
    except GitError as exc:
        logger.error(exc)
        return None


def get_results_gist(comment, github, rc, tmpdir, content):
    github_user = github.get_user()
    gist_match = re.search(GIST_ID_COMMENT_PATTERN, comment.body)
    if gist_match is not None:
        gist_id = gist_match.group('gist_id')
        try:
            for gist in github_user.get_gists():
                if gist.id == gist_id:
                    return (
                        Git(os.path.join(tmpdir, gist.id), quiet=GIT_QUIET),
                        gist.html_url,
                        None,
                    )
        except GithubException as exc:
            logger.error(exc)
            return None, None, None
    # no gist found so try to create one.
    try:
        gist = github_user.create_gist(
            public=False,
            files={k: InputFileContent(content=content[k]) for k in content},
            description='Automated test results for RIOT '
            f'{rc["release"]}-{rc["candidate"]}',
        )
    except GithubException as exc:
        logger.error(exc)
        return None, None, None
    # add return gist ID so it can be added to comment to later find it.
    return (Git(os.path.join(tmpdir, gist.id), quiet=GIT_QUIET), gist.html_url, gist.id)


def upload_results(pytest_report, comment, task, github, rc, tmpdir):
    # pylint: disable=too-many-arguments
    content = generate_outcome_content(pytest_report, task)
    if not content:
        logger.info("No result content for %s", pytest_report)
        return
    if "RESULT_OUTPUT_DIR" in os.environ and "RESULT_OUTPUT_URL" in os.environ:
        repo = Git(os.environ['RESULT_OUTPUT_DIR'], quiet=GIT_QUIET)
        repo_url = os.environ['RESULT_OUTPUT_URL']
        url_func = github_file_url
    else:
        repo, repo_url, task['gist_id'] = get_results_gist(
            comment, github, rc, tmpdir, content
        )
        if repo is None:
            logger.info("No suitable repo for result upload")
            return
        url_func = gist_file_url
    head = upload_result_content(github, repo, repo_url, content)
    if head:
        outcome_url = url_func(repo_url, list(content.keys())[0], head)
        if outcome_url:
            task['outcome_url'] = outcome_url


def make_comment(pytest_report, issue, task, github, rc, tmpdir):
    # pylint: disable=too-many-arguments
    comment = find_previous_comment(github, issue)
    if comment is None:
        comment = create_comment(github, issue)
    if comment is not None:
        upload_results(pytest_report, comment, task, github, rc, tmpdir)
        update_comment(pytest_report, comment, task)
    return comment


# pylint: disable=R0911,R0912
def update_issue(pytest_report, tmpdir):  # noqa: C901
    if pytest_report.when not in ['call', 'setup'] or (
        pytest_report.when == 'setup' and pytest_report.outcome != 'skipped'
    ):
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
        logger.error(f"Unable to get issue text of {issue}: {e}")
        return
    if not task_line or not task:
        # pylint: disable=C0209
        logger.warning(
            "Unable to find task {spec}.{task} in the "
            "tracking issue".format(**tested_task)
        )
    else:
        comment = make_comment(pytest_report, issue, task, github, rc, tmpdir)
        if comment:
            comment_url = comment.html_url
        else:
            comment_url = None
        if not task["done"] and pytest_report.outcome == "passed":
            mark_task_done(
                get_user_name(github), comment_url, issue, task_line, tested_task
            )
        elif task["done"]:
            # pylint: disable=C0209
            logger.info(
                "Task {spec}.{task} is already marked done in the "
                "tracking issue".format(**tested_task)
            )
