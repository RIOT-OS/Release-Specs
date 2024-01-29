import logging
import re
import subprocess

import pytest

from bs4 import BeautifulSoup

import testutils.github

from .test_git import config_repo

# pylint: disable=too-many-lines


@pytest.mark.parametrize(
    "output,expected",
    [
        (b"foobar", None),
        (b"tag: 2042.06-RC13", {"release": "2042.06", "candidate": "RC13"}),
    ],
)
def test_check_rc(monkeypatch, caplog, output, expected):
    monkeypatch.setattr(subprocess, "check_output", lambda *args, **kwargs: output)
    with caplog.at_level(logging.WARNING):
        assert testutils.github.get_rc() == expected
    if expected is None:
        assert "Not a release candidate" in caplog.text
    else:
        assert "Not a release candidate" not in caplog.text


def test_check_rc_error(monkeypatch, caplog):
    def mock_log(*args, **kwargs):
        raise testutils.github.GitError(returncode=42, cmd="don't panic")

    monkeypatch.setattr(testutils.github.Git, "log", mock_log)
    with caplog.at_level(logging.ERROR):
        assert testutils.github.get_rc() is None
    assert "don't panic" in caplog.text
    assert '42' in caplog.text


@pytest.mark.parametrize(
    "nodeid,expected",
    [
        ("foobar", None),
        (
            "03-single-hop-ipv6-icmp/test_spec87.py::test_task642[nodes0]",
            {"spec": 87, "task": 642, "params": "nodes0"},
        ),
    ],
)
def test_get_task(caplog, nodeid, expected):
    with caplog.at_level(logging.WARNING):
        assert testutils.github.get_task(nodeid) == expected
    if expected is None:
        assert "Can not find task" in caplog.text
    else:
        assert "Can not find task" not in caplog.text


@pytest.mark.parametrize("access_token,expected", [(None, None), ("abcdefg", "GitHub")])
def test_get_github(monkeypatch, access_token, expected):
    monkeypatch.setattr(
        testutils.github, "get_access_token", lambda *args, **kwargs: access_token
    )
    monkeypatch.setattr(testutils.github, "Github", lambda *args, **kwargs: "GitHub")
    assert testutils.github.get_github() == expected


def test_get_repo():
    # pylint: disable=R0903
    class MockGithub:
        # pylint: disable=W0613
        def get_repo(self, name):
            return "I am repo"

    assert testutils.github.get_repo(MockGithub()) == "I am repo"


def test_get_repo_error(caplog):
    # pylint: disable=R0903
    class MockGithub:
        # pylint: disable=W0613
        def get_repo(self, name):
            raise testutils.github.GithubException(404, "I am not repo", None)

    with caplog.at_level(logging.ERROR):
        assert not testutils.github.get_repo(MockGithub())
    assert re.search('Unable to get .*: 404.*I am not repo', caplog.text)


@pytest.mark.parametrize(
    "issue_titles,rc,expected_idx",
    [
        (
            ["Release 2456.13 - RC74", "Broken", "foobar"],
            {"release": "2456.13", "candidate": "RC74"},
            0,
        ),
        (
            ["Broken", "Release 2456.13 - RC74", "foobar"],
            {"release": "2456.13", "candidate": "RC74"},
            1,
        ),
        (
            ["Broken", "Release 2456.13 - RC74", "foobar"],
            {"release": "2456.14", "candidate": "RC74"},
            None,
        ),
        (
            ["Broken", "Release 2456.13 - RC74", "foobar"],
            {"release": "2456.13", "candidate": "RC69"},
            None,
        ),
        (
            ["Broken", "snafu", "foobar"],
            {"release": "2456.13", "candidate": "RC74"},
            None,
        ),
    ],
)
def test_get_rc_tracking_issue(caplog, issue_titles, rc, expected_idx):
    # pylint: disable=R0903
    class MockIssue:
        def __init__(self, title):
            self.title = title

    # pylint: disable=R0903
    class MockRepo:
        def __init__(self, issues):
            self.issues = issues

        # pylint: disable=W0613
        def get_issues(self, *args, **kwargs):
            for issue in self.issues:
                yield issue

    issues = [MockIssue(title) for title in issue_titles]
    repo = MockRepo(issues)
    with caplog.at_level(logging.ERROR):
        res = testutils.github.get_rc_tracking_issue(repo, rc)
    if expected_idx is None:
        assert res is None
        assert "No tracking issue found" in caplog.text
    else:
        assert res == issues[expected_idx]


def test_get_rc_tracking_issue_error(caplog):
    # pylint: disable=R0903
    class MockRepo:
        # pylint: disable=W0613
        def get_issues(self, *args, **kwargs):
            raise testutils.github.GithubException(403, "You don't get issues", None)

    rc = {"release": "2456.13", "candidate": "RC74"}
    repo = MockRepo()
    with caplog.at_level(logging.ERROR):
        res = testutils.github.get_rc_tracking_issue(repo, rc)
        assert res is None
    assert re.search(
        "Unable to get repo's issues: 403.*You don't get issues", caplog.text
    )


@pytest.mark.parametrize(
    "body,comment_url,task_line,user,expected",
    [
        ("- [ ] foobar", None, "- [ ] foobar", "hello", "- [x] foobar @hello "),
        ("- [x] foobar", None, "- [ ] foobar", "hello", "- [x] foobar"),
        ("- [x] foobar", None, "- [x] foobar", "hello", "- [x] foobar"),
        ("- [ ] foobar", None, "- [x] foobar", "hello", "- [ ] foobar"),
        (
            "- [ ] foobar",
            "url",
            "- [ ] foobar",
            "hello",
            "- [x] foobar @hello (see url) ",
        ),
        ("- [x] foobar", "url", "- [ ] foobar", "hello", "- [x] foobar"),
        ("- [x] foobar", "url", "- [x] foobar", "hello", "- [x] foobar"),
        ("- [ ] foobar", "url", "- [x] foobar", "hello", "- [ ] foobar"),
    ],
)
def test_mark_task_done(body, comment_url, task_line, user, expected):
    class MockIssue:
        def __init__(self, body):
            self._body = body

        @property
        def body(self):
            return self._body

        # pylint: disable=W0613
        def edit(self, body, *args, **kwargs):
            self._body = body

        def update(self):
            pass

    issue = MockIssue(body)
    testutils.github.mark_task_done(
        user, comment_url, issue, task_line, {"spec": 16, "task": 500}
    )
    assert issue.body == expected


@pytest.mark.parametrize("raiser", ["update", "edit"])
def test_mark_task_done_error1(caplog, raiser):
    class MockIssue:
        def __init__(self, body):
            self.body = body

        # pylint: disable=W0613
        def edit(self, body, *args, **kwargs):
            self.body = body

        def update(self):
            pass

    # pylint: disable=W0613
    def _raise(*args, **kwargs):
        raise testutils.github.GithubException(404, "This went wrong", None)

    issue = MockIssue(" - [ ] foobar")
    setattr(issue, raiser, _raise)
    with caplog.at_level(logging.ERROR):
        testutils.github.mark_task_done(
            "hello", None, issue, " - [x] foobar", {"spec": 16, "task": 500}
        )
    assert "Unable to mark 16.500 in the tracking issue" in caplog.text


def test_mark_task_done_error2(caplog):
    class MockIssue:
        def __init__(self, body):
            self._body = body

        @property
        def body(self):
            raise testutils.github.GithubException(404, "This went wrong", None)

        # pylint: disable=W0613
        def edit(self, body, *args, **kwargs):
            self._body = body

        def update(self):
            pass

    issue = MockIssue(" - [ ] foobar")
    with caplog.at_level(logging.ERROR):
        testutils.github.mark_task_done(
            "hello", None, issue, " - [x] foobar", {"spec": 16, "task": 500}
        )
    assert "Unable to mark 16.500 in the tracking issue" in caplog.text


def test_find_task_text1():
    issue_body = """
        - [x] [03-fantasy](coap://what?) (this is just for you ;-))
      - [ ] [Task #02 We don't want this](out)
    - [ ] [05-this-is-us](http://example.org) ))))) sonic
      - [ ] [Task #02 Let's not make this complicated](This-isn't-even-a-URL))
    """
    task_line, task = testutils.github.find_task_text(
        issue_body, {"spec": 5, "task": 2}
    )
    assert (
        "- [ ] [Task #02 Let's not make this complicated]"
        "(This-isn't-even-a-URL)" in task_line
    )
    assert len(task) == 5
    assert task["task"] == 2
    assert not task["done"]
    assert task["name"] == "Task 02 Let's not make this complicated"
    assert task["url"] == "This-isn't-even-a-URL"
    assert len(task["spec"]) == 4
    assert task["spec"]["spec"] == 5
    assert not task["spec"]["done"]
    assert task["spec"]["name"] == "05-this-is-us"
    assert task["spec"]["url"] == "http://example.org"


def test_find_task_text2():
    issue_body = """
        - [x] [03-fantasy](coap://what?) (this is just for you ;-))
      - [ ] [Task #02 We don't want this](out)
    - [x] [05-this-is-us](http://example.org) ))))) sonic
      - [x] [Task #02 Let's not make this complicated](This-isn't-even-a-URL))
    """
    task_line, task = testutils.github.find_task_text(
        issue_body, {"spec": 5, "task": 2, "params": "nodes0"}
    )
    assert (
        "- [x] [Task #02 Let's not make this complicated]"
        "(This-isn't-even-a-URL)" in task_line
    )
    assert len(task) == 5
    assert task["done"]
    assert len(task["spec"]) == 4
    assert task["spec"]["done"]


def test_find_task_text3():
    issue_body = """
        - [x] [03-fantasy](coap://what?) (this is just for you ;-))
      - [ ] [Task #02 We don't want this](out)
    - [x] [05-this-is-us](http://example.org) ))))) sonic
      - [x] [Task #02 Let's not make this complicated](This-isn't-even-a-URL))
    """
    task_line, task = testutils.github.find_task_text(
        issue_body, {"spec": 5, "task": 2, "params": "nodes0-foobar"}
    )
    assert (
        "- [x] [Task #02 Let's not make this complicated]"
        "(This-isn't-even-a-URL)" in task_line
    )
    assert len(task) == 6
    assert task["params"] == "foobar"
    assert task["done"]
    assert len(task["spec"]) == 4
    assert task["spec"]["done"]


def test_find_task_text4():
    issue_body = "foobar"
    task_line, task = testutils.github.find_task_text(
        issue_body, {"spec": 5, "task": 2}
    )
    assert task_line is None
    assert task is None


class MockComment:
    def __eq__(self, other):
        return self._body == other.body

    def __init__(self, body):
        self._body = body

    def __str__(self):
        return self._body

    @property
    def body(self):
        return self._body

    def edit(self, body):
        self._body = body


def _github(user_class=None):
    # pylint: disable=R0903
    class MockUser:
        @property
        def login(self):
            return "user"

    # pylint: disable=R0903
    class MockGithub:
        def get_user(self):
            if user_class is None:
                return MockUser()
            return user_class()

    return MockGithub()


@pytest.mark.parametrize(
    'comments, exp',
    [
        ([], None),
        ([MockComment("test")], None),
        (
            [MockComment(testutils.github.STICKY_COMMENT_COMMENT.format(user="user"))],
            MockComment(testutils.github.STICKY_COMMENT_COMMENT.format(user="user")),
        ),
    ],
)
def test_find_previous_comment(comments, exp):
    class MockIssue:  # pylint: disable=R0903
        def get_comments(self):
            return comments

    assert testutils.github.find_previous_comment(_github(), MockIssue()) == exp


def test_create_comment(monkeypatch, caplog):
    class MockIssue:  # pylint: disable=R0903
        def __init__(self):
            self.comment = None

        def create_comment(self, comment):
            self.comment = MockComment(comment)
            return self.comment

    # isolate from test environment
    monkeypatch.setattr(testutils.github.os, "environ", {})
    with caplog.at_level(logging.ERROR):
        comment = testutils.github.create_comment(_github(), MockIssue())
    assert caplog.text == ""
    assert comment is not None
    assert (
        comment.body
        == "<h1>Test Report</h1>\n\n"
        + testutils.github.STICKY_COMMENT_COMMENT.format(user="user")
        + """
<table>
  <thead>
    <tr><th></th><th>Task</th><th>Outcome</th></tr>
  </thead>
  <tbody>
  </tbody>
</table>
"""
    )


def test_create_comment_error(caplog):
    class MockIssue:  # pylint: disable=R0903
        def create_comment(self, comment):
            raise testutils.github.GithubException(300, "Nope", None)

    with caplog.at_level(logging.ERROR):
        comment = testutils.github.create_comment(_github(), MockIssue())
    assert 'Unable to comment: ' in caplog.text
    assert comment is None


# SimpleBeautifulSoup
class SBS4(BeautifulSoup):  # pylint: disable=W0223
    def __init__(self, soup):
        super().__init__(soup, "html.parser")


@pytest.mark.parametrize(
    "tbody,task,exp,exp_errs",
    [
        (
            "",
            {
                "title": " foobar",
                "url": "http://example.org",
                "emoji": ":-)",
                "outcome": SBS4("blafoo"),
            },
            [("foobar", "http://example.org", ":-)", SBS4("blafoo"))],
            None,
        ),
        (
            "<tr></tr>",
            {
                "title": " foobar",
                "url": "http://example.org",
                "emoji": ":-)",
                "outcome": SBS4("blafoo"),
            },
            [("foobar", "http://example.org", ":-)", SBS4("blafoo"))],
            ["Unexpected table format in "],
        ),
        (
            "<tr><td>:-(</td><td>test</td><td>snafoo</td></tr>",
            {
                "title": " foobar",
                "url": "http://example.org",
                "emoji": ":-)",
                "outcome": SBS4("blafoo"),
            },
            [
                ("foobar", "http://example.org", ":-)", SBS4("blafoo")),
            ],
            ["Unexpected table format in "],
        ),
        (
            "<tr><td>:-(</td><td><a>test</a></td><td>snafoo</td></tr>",
            {
                "title": " foobar",
                "url": "http://example.org",
                "emoji": ":-)",
                "outcome": SBS4("blafoo"),
            },
            [
                ("foobar", "http://example.org", ":-)", SBS4("blafoo")),
            ],
            ["Unexpected table format in "],
        ),
        (
            "<tr><td>:-(</td><td><a href='https://example.org/2'>test</a></td>"
            + "<td>snafoo</td></tr>",
            {
                "title": " foobar",
                "url": "http://example.org",
                "emoji": ":-)",
                "outcome": SBS4("blafoo"),
            },
            [
                ("foobar", "http://example.org", ":-)", SBS4("blafoo")),
                ("test", "https://example.org/2", ":-(", SBS4("snafoo")),
            ],
            None,
        ),
        (
            "<tr><td>:-(</td><td><a href='https://example.org/2'>foobar</a>"
            + "</td><td>snafoo</td></tr>",
            {
                "title": " foobar",
                "url": "http://example.org",
                "emoji": ":-)",
                "outcome": SBS4("blafoo"),
            },
            [
                ("foobar", "http://example.org", ":-)", SBS4("blafoo")),
            ],
            None,
        ),
    ],
)
def test_get_tasks(caplog, tbody, task, exp, exp_errs):
    tbody = SBS4(f'<table><tbody>{tbody}</tbody></table>').find('tbody')
    with caplog.at_level(logging.ERROR):
        tasks = testutils.github.get_tasks(MockComment("foobar"), tbody, task)
    assert exp == tasks
    if exp_errs:
        for exp_err in exp_errs:
            assert exp_err in caplog.text
    else:
        assert caplog.text == ""


def _get_mock_report(outcome, longrepr=None, sections=None, when=None):
    class MockReport:
        @property
        def longrepr(self):
            return longrepr

        @property
        def outcome(self):
            return outcome

        @property
        def nodeid(self):
            return "foobar"

        @property
        def sections(self):
            return sections

        @property
        def when(self):
            return when

    return MockReport()


@pytest.mark.parametrize(
    'comment_body,env,gist_id,exp_body,exp_errs',
    [
        (
            "<tbody></tbody>",
            {},
            None,
            """<tbody>
 <tr>
  <td>
   ✔
  </td>
  <td>
   <a href="http://example.org">
    01. foobar
   </a>
  </td>
  <td>
   <strong>
    PASSED
   </strong>
  </td>
 </tr>
</tbody>""",
            None,
        ),
        (
            "<table></table>",
            {},
            None,
            "<table></table>",
            "Unable to find table body in ",
        ),
        (
            "<h1>The title</h1><tbody></tbody>",
            {},
            None,
            """<h1>
 The title
</h1>
<tbody>
 <tr>
  <td>
   ✔
  </td>
  <td>
   <a href="http://example.org">
    01. foobar
   </a>
  </td>
  <td>
   <strong>
    PASSED
   </strong>
  </td>
 </tr>
</tbody>""",
            None,
        ),
        (
            "<h1>The title</h1><tbody></tbody>",
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
            None,
            """<h1>
 <a href="https://example.org/test/foobar/actions/runs/1275479086">
  The title
 </a>
</h1>
<tbody>
 <tr>
  <td>
   ✔
  </td>
  <td>
   <a href="http://example.org">
    01. foobar
   </a>
  </td>
  <td>
   <strong>
    PASSED
   </strong>
  </td>
 </tr>
</tbody>""",
            None,
        ),
        (
            "<tbody></tbody>",
            {},
            '663209485c1e2a39fb8fb4ab9fcd51ac',
            """<!-- gist-id:663209485c1e2a39fb8fb4ab9fcd51ac -->
<tbody>
 <tr>
  <td>
   ✔
  </td>
  <td>
   <a href="http://example.org">
    01. foobar
   </a>
  </td>
  <td>
   <strong>
    PASSED
   </strong>
  </td>
 </tr>
</tbody>""",
            None,
        ),
    ],
)
def test_update_comment(
    monkeypatch, caplog, comment_body, env, gist_id, exp_body, exp_errs
):
    # pylint: disable=R0913
    # patch environment variables to not include run URL when run in Github
    # Action
    monkeypatch.setattr(testutils.github.os, "environ", env)
    comment = MockComment(comment_body)
    with caplog.at_level(logging.ERROR):
        task = {'spec': {'spec': 1}, 'name': 'foobar', 'url': 'http://example.org'}
        if gist_id is not None:
            task['gist_id'] = gist_id
        testutils.github.update_comment(_get_mock_report("passed"), comment, task)
    assert comment.body.strip() == exp_body.strip()
    if exp_errs:
        for exp_err in exp_errs:
            assert exp_err in caplog.text
    else:
        assert caplog.text == ""


def test_gist_file_url():
    assert (
        testutils.github.gist_file_url("https://example.org", "ab_cd..ef.txt", "foobar")
        == "https://example.org/foobar#ab_cd-ef-txt"
    )


def test_github_file_url():
    assert (
        testutils.github.github_file_url(
            "https://github.com", "ab_cd..ef.txt", "foobar"
        )
        == "https://github.com/blob/foobar/ab_cd..ef.txt"
    )


def test_github_file_url_non_github_url():
    assert (
        testutils.github.github_file_url(
            "https://example.org", "ab_cd..ef.txt", "foobar"
        )
        is None
    )


@pytest.mark.parametrize(
    'repo_exists,content,staging_changed',
    [
        (True, {}, False),
        (False, {}, False),
        (True, {'test.txt': 'foobar'}, True),
        (True, {'test.txt': 'foobar', 'abcd.txt': 'snafu'}, False),
    ],
)
def test_upload_result_content(
    tmp_path, monkeypatch, repo_exists, content, staging_changed
):
    pulled = False

    def mock_pull(self):  # pylint: disable=unused-argument
        nonlocal pulled
        pulled = True

    repo = testutils.github.Git(tmp_path)
    repo.cmd("init")
    config_repo(repo)

    monkeypatch.setattr(testutils.github.Git, 'exists', lambda self: repo_exists)
    monkeypatch.setattr(testutils.github.Git, 'pull', mock_pull)
    monkeypatch.setattr(testutils.github.Git, 'clone', lambda *args, **kwargs: repo)
    monkeypatch.setattr(testutils.github.Git, 'push', lambda self: None)
    monkeypatch.setattr(
        testutils.github.Git, 'staging_changed', lambda self: staging_changed
    )
    monkeypatch.setattr(testutils.github.Git, 'head_sha', 'abcdef')

    assert (
        testutils.github.upload_result_content(
            _github(), repo, 'https://example.org', content
        )
        == 'abcdef'
    )
    assert repo_exists or not pulled
    if content and staging_changed:
        for filename in content:
            output = repo.log('--format=%H', '--name-only', '--', filename)
            assert filename in output
            assert (tmp_path / filename).exists()
            with (tmp_path / filename).open() as f:
                assert f.read() == content[filename]
        assert len(repo.log('--oneline').strip().split('\n')) == len(content)
    else:
        with pytest.raises(testutils.git.GitError):
            repo.log()


def test_upload_result_content_error(monkeypatch, caplog, tmp_path):
    def mock_exists(self):
        raise testutils.github.GitError(returncode=42, cmd=["exists"])

    monkeypatch.setattr(testutils.github.Git, 'exists', mock_exists)
    with caplog.at_level(logging.ERROR):
        testutils.github.upload_result_content(
            _github(), testutils.git.Git(tmp_path), "https://examples.org", []
        )
    assert "42" in caplog.text
    assert "exists" in caplog.text


def test_update_comment_edit_error(monkeypatch, caplog):
    class MockCommentEditError(MockComment):
        def edit(self, body):
            raise testutils.github.GithubException(300, "Nope", None)

    # isolate test environment
    monkeypatch.setattr(testutils.github.os, "environ", {})
    comment_body = "<tbody><tr><td>foobar</td></tr></tbody>"
    comment = MockCommentEditError(comment_body)
    with caplog.at_level(logging.ERROR):
        testutils.github.update_comment(
            _get_mock_report("passed"),
            comment,
            {'spec': {'spec': 1}, 'name': 'foobar', 'url': 'http://example.org'},
        )
    assert "Unable to update comment: " in caplog.text
    assert comment.body == comment_body


@pytest.mark.parametrize(
    'gist_ids,gist_id,in_comment,error_get,error_create',
    [
        (['b217693d', '99fb3395'], 'b217693d', False, False, False),
        (['b217693d', '99fb3395'], 'b217693d', False, False, True),
        (['b217693d', '99fb3395'], 'b217693d', False, True, False),
        (['b217693d', '99fb3395'], 'b217693d', True, True, False),
        (['b217693d', '99fb3395'], 'b217693d', True, False, True),
        (['b217693d', '99fb3395'], 'b28c49fb', True, True, False),
        (['b217693d', '99fb3395'], 'b28c49fb', True, False, True),
    ],
)
def test_get_results_gist(  # noqa: C901
    caplog,
    tmp_path,
    gist_ids,
    gist_id,
    in_comment,
    error_get,
    error_create,
):
    # pylint: disable=too-few-public-methods,too-many-arguments
    # pylint: disable=unused-argument
    class MockGist:
        def __init__(self, identifier):
            self._id = identifier

        @property
        def id(self):
            return self._id

        @property
        def html_url(self):
            return f'https://example.org/{self._id}'

    class MockGistUser:
        def get_gists(self):
            if error_get:
                raise testutils.github.GithubException(300, "Nope", None)
            return [MockGist(g) for g in gist_ids]

        def create_gist(self, *args, **kwargs):
            if error_create:
                raise testutils.github.GithubException(400, "Nope", None)
            return MockGist(gist_id)

    with caplog.at_level(logging.ERROR):
        res = testutils.github.get_results_gist(
            MockComment(
                testutils.github.GIST_ID_COMMENT_FMT.format(gist_id=gist_id)
                if in_comment
                else ''
            ),
            _github(MockGistUser),
            {'release': '2021.05', 'candidate': 'RC6'},
            tmp_path,
            {},
        )
    assert len(res) == 3
    if in_comment and gist_id in gist_ids:
        if error_get:
            assert '300' in caplog.text
            assert 'Nope' in caplog.text
            assert all(r is None for r in res)
        else:
            assert res[0].repodir == str(tmp_path / gist_id)
            assert res[1] == MockGist(gist_id).html_url
            assert res[2] is None
            assert caplog.text == ''
    else:
        if gist_id not in gist_ids and error_get:
            assert '300' in caplog.text
            assert 'Nope' in caplog.text
            assert all(r is None for r in res)
        elif error_create:
            assert '400' in caplog.text
            assert 'Nope' in caplog.text
            assert all(r is None for r in res)
        else:
            assert res[0].repodir == str(tmp_path / gist_id)
            assert res[1] == MockGist(gist_id).html_url
            assert res[2] == gist_id
            assert caplog.text == ''


@pytest.mark.parametrize(
    "params,outcome,longrepr,sections",
    [
        (None, 'skipped', 'blafoo', [('test', 'abcdef')]),
        (None, 'passed', 'blafoo', [('test', 'abcdef')]),
        ('test-arg', 'failed', 'blafoo', []),
        ('test-arg', 'failed', 'blafoo', None),
        (None, 'passed', None, [('test', 'abcdef')]),
    ],
)
def test_generate_outcome_content(params, outcome, longrepr, sections):
    report = _get_mock_report(outcome, longrepr=longrepr, sections=sections)
    task = {'spec': {'spec': 3}, 'task': 1, 'name': 'foobar', 'params': params}
    content = testutils.github.generate_outcome_content(report, task)
    if outcome in ['passed', 'failed']:
        assert len(content) == 1
        filename = list(content)[0]
        if params:
            assert filename == f'task_03.01.{params}_result.md'
            assert params.lower() in content[filename].lower()
        else:
            assert filename == 'task_03.01_result.md'
        assert outcome.lower() in content[filename].lower()
        if longrepr:
            assert longrepr in content[filename]
        if sections:
            for title, body in sections:
                assert title in content[filename]
                assert body in content[filename]
    else:
        assert not content


@pytest.mark.parametrize(
    "env,content_generated,gist_created,head,outcome_url",
    [
        ({}, False, False, None, None),
        ({}, True, False, None, None),
        ({}, True, True, None, None),
        (
            {'RESULT_OUTPUT_DIR': '../', 'RESULT_OUTPUT_URL': 'https://example.org'},
            True,
            False,
            None,
            None,
        ),
        (
            {'RESULT_OUTPUT_DIR': '../', 'RESULT_OUTPUT_URL': 'https://example.org'},
            True,
            True,
            None,
            None,
        ),
        ({}, True, True, 'the_head', None),
        (
            {'RESULT_OUTPUT_DIR': '../', 'RESULT_OUTPUT_URL': 'https://example.org'},
            True,
            True,
            'the_head',
            None,
        ),
        ({}, True, True, None, 'https://example.org/the_id'),
        (
            {'RESULT_OUTPUT_DIR': '../', 'RESULT_OUTPUT_URL': 'https://example.org'},
            True,
            True,
            None,
            'https://example.org/the_id',
        ),
        ({}, True, True, 'the_head', 'https://example.org/the_id'),
        (
            {'RESULT_OUTPUT_DIR': '../', 'RESULT_OUTPUT_URL': 'https://example.org'},
            True,
            True,
            'the_head',
            'https://example.org/the_id',
        ),
    ],
)
def test_upload_results(
    monkeypatch, caplog, env, content_generated, gist_created, head, outcome_url
):
    # pylint: disable=too-many-arguments
    monkeypatch.setattr(
        testutils.github,
        "generate_outcome_content",
        lambda *args, **kwargs: {"test.txt": "foobar"} if content_generated else None,
    )
    monkeypatch.setattr(testutils.github.os, "environ", env)
    monkeypatch.setattr(
        testutils.github, "github_file_url", lambda *args, **kwargs: outcome_url
    )
    monkeypatch.setattr(
        testutils.github, "gist_file_url", lambda *args, **kwargs: outcome_url
    )
    monkeypatch.setattr(
        testutils.github,
        "get_results_gist",
        lambda *args, **kwargs: (
            (testutils.github.Git('.'), "", "the_gist_id")
            if gist_created
            else (None, None, None)
        ),
    )
    monkeypatch.setattr(
        testutils.github, "upload_result_content", lambda *args, **kwargs: head
    )
    task = {}
    with caplog.at_level(logging.INFO):
        testutils.github.upload_results(
            _get_mock_report("passed"), MockComment(''), task, _github(), {}, './'
        )
    if not content_generated:
        assert "No result content for " in caplog.text
        assert not task
        return
    if len(env) == 0:
        if gist_created:
            assert task["gist_id"] == "the_gist_id"
        else:
            assert "No suitable repo for result upload" in caplog.text
            assert "gist_id" not in task or task["gist_id"] is None
            return
    elif 'RESULT_OUTPUT_DIR' in env and 'RESULT_OUTPUT_URL' in env:
        assert "gist_id" not in task
    if head and outcome_url:
        assert task["outcome_url"] == outcome_url
    else:
        assert "outcome_url" not in task


@pytest.mark.parametrize(
    "outcome,longrepr,sections,task,env",
    [
        (
            "passed",
            None,
            [("foobar", "blafoo"), ("snafu", "ruined!")],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {},
        ),
        (
            "failed",
            "Foos rho dah",
            [("foobar", "blafoo")],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {},
        ),
        (
            "failed",
            None,
            None,
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {},
        ),
        (
            "failed",
            None,
            [],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {},
        ),
        (
            "passed",
            None,
            [("foobar", "blafoo"), ("snafu", "ruined!")],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
        ),
        (
            "skipped",
            ("test", 5, "not loaded"),
            [("foobar", "blafoo")],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
        ),
        (
            "failed",
            "Foos rho dah",
            [("foobar", "blafoo")],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
        ),
        (
            "skipped",
            ("test", 5, "not loaded"),
            None,
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
        ),
        (
            "failed",
            None,
            None,
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
        ),
        (
            "failed",
            None,
            [],
            {"spec": {"spec": 5}, "task": 1, "name": "Lorem", "url": "t::test"},
            {
                "GITHUB_RUN_ID": "1275479086",
                "GITHUB_REPOSITORY": "test/foobar",
                "GITHUB_SERVER_URL": "https://example.org",
            },
        ),
    ],
)
# pylint: disable=R0913
def test_make_comment(monkeypatch, tmpdir, outcome, longrepr, sections, task, env):
    class MockIssue:
        def __init__(self):
            self.comment = None

        def create_comment(self, comment):
            self.comment = MockComment(comment)
            return self.comment

        def get_comments(self):
            if self.comment:
                return [self.comment]
            return []

    # pylint: disable=R0903
    monkeypatch.setattr(testutils.github.os, "environ", env)
    monkeypatch.setattr(testutils.github, "upload_results", lambda *args: None)
    report = _get_mock_report(outcome, longrepr=longrepr, sections=sections)
    issue = MockIssue()
    rc = {"release": "2021.05", "candidate": "RC7"}
    assert (
        testutils.github.make_comment(report, issue, task, _github(), rc, tmpdir)
        is not None
    )
    assert f"{task['spec']['spec']:02}" in issue.comment.body
    assert task["name"] in issue.comment.body
    assert task["url"] in issue.comment.body
    for key in env:
        assert env[key] in issue.comment.body
    assert outcome.upper() in issue.comment.body


@pytest.mark.parametrize(
    "outcome,longrepr,sections,task",
    [
        (
            "passed",
            None,
            [("foobar", "blafoo"), ("snafu", "ruined!")],
            {"spec": {"spec": 5}, "name": "Lorem", "url": "t::test"},
        ),
        (
            "failed",
            "Foos rho dah",
            [("foobar", "blafoo")],
            {"spec": {"spec": 5}, "name": "Lorem", "url": "t::test"},
        ),
        (
            "failed",
            None,
            None,
            {"spec": {"spec": 5}, "name": "Lorem", "url": "t::test"},
        ),
        ("failed", None, [], {"spec": {"spec": 5}, "name": "Lorem", "url": "t::test"}),
    ],
)
# pylint: disable=R0913
def test_make_comment_error(
    monkeypatch, tmpdir, caplog, outcome, longrepr, sections, task
):
    # pylint: disable=R0903
    class MockIssue:
        def __init__(self):
            self.comment = None

        # pylint: disable=W0613
        def create_comment(self, comment):
            raise testutils.github.GithubException(300, "Nope", None)

    monkeypatch.setattr(testutils.github.os, "environ", {})
    monkeypatch.setattr(testutils.github, "find_previous_comment", lambda *args: None)
    report = _get_mock_report(outcome, longrepr, sections)
    issue = MockIssue()
    rc = {"release": "2021.05", "candidate": "RC7"}
    with caplog.at_level(logging.ERROR):
        assert (
            testutils.github.make_comment(report, issue, task, _github(), rc, tmpdir)
            is None
        )
    assert "Unable to comment:" in caplog.text


def _mock_update_issue():
    # pylint: disable=R0903
    class MockIssue:
        @property
        def body(self):
            return "Mock text"

        def __str__(self):
            return "Mock issue"

    return MockIssue()


@pytest.mark.parametrize(
    "when,outcome,tested_task,rc,github,repo,issue,task,log,comment_error,"
    "exp_marked",
    [
        # configure monkeypatched functions progressively to get further and
        # further in update_issue()
        (
            "setup",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "skipped",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "passed",
            None,
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            None,
            _github(),
            "Repo",
            _mock_update_issue(),
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            None,
            "Repo",
            _mock_update_issue(),
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            None,
            _mock_update_issue(),
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            None,
            ("blafoo", {"done": False, "url": "t::test"}),
            None,
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            (None, {"done": False, "url": "t::test"}),
            "Unable to find task 1.1 in the tracking issue",
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("blafoo", None),
            "Unable to find task 1.1 in the tracking issue",
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            (None, None),
            "Unable to find task 1.1 in the tracking issue",
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            None,  # Fire GithubException
            "Unable to get issue text of Mock issue",
            False,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("foobar", {"done": True, "url": "t::test"}),
            "Task 1.1 is already marked done in the tracking issue",
            False,
            False,
        ),
        (
            "call",
            "failed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("foobar", {"done": False, "url": "t::test"}),
            # not marked task as failed
            None,
            False,
            False,
        ),
        (
            "call",
            "failed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("foobar", {"done": False, "url": "t::test"}),
            # comment failed and not marked task as failed
            None,
            True,
            False,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("foobar", {"done": False, "url": "t::test"}),
            # marked as task passed
            None,
            False,
            True,
        ),
        (
            "call",
            "passed",
            {"spec": 1, "task": 1},
            {"release": "2020.07", "candidate": "RC1"},
            _github(),
            "Repo",
            _mock_update_issue(),
            ("foobar", {"done": False, "url": "t::test"}),
            # comment failed and marked as task passed
            None,
            True,
            True,
        ),
    ],
)
# pylint: disable=R0913,R0914
def test_update_issue(
    monkeypatch,
    caplog,
    tmpdir,
    when,
    outcome,
    tested_task,
    rc,
    github,
    repo,
    issue,
    task,
    log,
    comment_error,
    exp_marked,
):
    # pylint: disable=R0903,W0621
    class MockComment:
        @property
        def html_url(self):
            return "t::test"

    task_marked_done = False
    # monkeypatch ALL the functions with parameter values!
    monkeypatch.setattr(
        testutils.github, "get_task", lambda *args, **kwargs: tested_task
    )
    monkeypatch.setattr(testutils.github, "get_rc", lambda *args, **kwargs: rc)
    monkeypatch.setattr(testutils.github, "get_github", lambda *args, **kwargs: github)
    monkeypatch.setattr(testutils.github, "get_repo", lambda *args, **kwargs: repo)
    monkeypatch.setattr(
        testutils.github, "get_rc_tracking_issue", lambda *args, **kwargs: issue
    )
    if task is None:
        # pylint: disable=W0613
        def _raise(*args, **kwargs):
            raise testutils.github.GithubException(420, "Fail!", None)

        monkeypatch.setattr(testutils.github, "find_task_text", _raise)
    else:
        monkeypatch.setattr(
            testutils.github, "find_task_text", lambda *args, **kwargs: task
        )

    # pylint: disable=W0613
    def comment(*args, **kwargs):
        if comment_error:
            return None
        return MockComment()

    # pylint: disable=W0613
    def mark(*args, **kwargs):
        nonlocal task_marked_done
        task_marked_done = True

    monkeypatch.setattr(testutils.github, "make_comment", comment)
    monkeypatch.setattr(testutils.github, "mark_task_done", mark)

    report = _get_mock_report(outcome, when=when)
    with caplog.at_level(logging.INFO):
        testutils.github.update_issue(report, tmpdir)
    if log:
        assert log in caplog.text
    else:
        assert not caplog.text
    assert task_marked_done == exp_marked
