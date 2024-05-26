import pytest


import json
from freezegun import freeze_time
import demistomock as demisto


URL = "https://openphish.com/feed.txt"


def util_load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.loads(f.read())


def util_load_txt(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def mock_client():
    """
    Create a mock client for testing.
    """
    from FeedGitHub import Client

    return Client(
        base_url="example.com",
        verify=False,
        proxy=False,
        owner="",
        repo="",
        headers={},
    )


def test_get_base_head_commits_sha(mocker):
    pass


def test_extract_commits(mocker):
    pass


def test_get_content_files_from_repo(mocker):
    """
    Given:
     - A list of relevant files to fetch content from.
     - Parameters specifying the feed type and extensions to fetch.
     - A mock response for the content files from the repository.
    When:
     - Calling get_content_files_from_repo to fetch the content of the relevant files.
    Then:
     - Returns the content of the relevant files matching the expected results.
    """
    from FeedGitHub import get_content_files_from_repo

    client = mock_client()
    params = {"feedType": "IOCs", "extensions_to_fetch": ["txt"]}
    relevant_files = util_load_json("test_data/relevant-files.json")
    return_data = util_load_json("test_data/content_files_from_repo.json")
    mocker.patch.object(client, "_http_request", return_value=return_data)
    content_files = get_content_files_from_repo(client, relevant_files, params)
    assert content_files == util_load_json("test_data/get_content-files-from-repo-result.json")


def test_get_commit_files(mocker):
    """
    Given:
     - A base commit SHA, a head commit SHA, and a flag indicating if it is the first fetch.
     - A mock response for the list of all commit files between the base and head commits.
    When:
     - Calling get_commits_files to retrieve the relevant files and the current repo head SHA.
    Then:
     - Returns the list of relevant files and the current repo head SHA matching the expected results.
    """
    from FeedGitHub import get_commits_files

    client = mock_client()
    base = "ad3e0503765479e9ee09bac5dee726eb918b9ebd"
    head = "9a611449423b9992c126c20e47c5de4f58fc1c0e"
    is_first_fetch = True
    all_commits_files = util_load_json("test_data/all-commit-files-res.json")
    current_repo_head_sha = "ad3e0503765479e9ee09bac5dee726eb918b9ebd"
    mocker.patch.object(client, "get_files_between_commits", return_value=(all_commits_files, current_repo_head_sha))
    relevant_files, current_repo_head_sha = get_commits_files(client, base, head, is_first_fetch)
    assert relevant_files == util_load_json("test_data/relevant-files.json")


def test_filter_out_files_by_status():
    """
    Given:
     - A list of dictionaries representing commit files, each containing a status and a raw_url.
    When:
     - Filtering out files by their status using the filter_out_files_by_status function.
    Then:
     - Returns a list of URLs for files that are added or modified.
    """
    from FeedGitHub import filter_out_files_by_status

    commits_files = [
        {"status": "added", "raw_url": "http://example.com/file1"},
        {"status": "modified", "raw_url": "http://example.com/file2"},
        {"status": "removed", "raw_url": "http://example.com/file3"},
        {"status": "renamed", "raw_url": "http://example.com/file4"},
        {"status": "added", "raw_url": "http://example.com/file5"},
    ]

    expected_output = ["http://example.com/file1", "http://example.com/file2", "http://example.com/file5"]
    actual_output = filter_out_files_by_status(commits_files)
    assert actual_output == expected_output, f"Expected {expected_output}, but got {actual_output}"


def test_split_yara_rules():
    """
    Test the split_yara_rules function.
    Given:
    - Yara rule sets from 'test_data/test-split-yara-critical-rule.yar' and 'test_data/test-split-yara-1.yar'.
    - Expected split result from 'test_data/split-critical-yara-rule-res.json'.
    When:
    - split_yara_rules is called on both Yara rule sets.
    Then:
    - The number of rules from 'test_data/test-split-yara-1.yar' is 6.
    - The split result of 'test_data/test-split-yara-critical-rule.yar' matches the expected result.
    """
    from FeedGitHub import split_yara_rules

    aaa = util_load_txt("test_data/test-split-yara-critical-rule.yar")
    bbb = split_yara_rules(aaa)
    yara_content = util_load_txt("test_data/test-split-yara-1.yar")
    yara_rules = split_yara_rules(yara_content)
    assert len(yara_rules) == 6
    assert bbb == util_load_json("test_data/split-critical-yara-rule-res.json")


@freeze_time("2024-05-12T15:30:49.330015")
def test_parse_and_map_yara_content(mocker):
    """
    Given:
     - YARA rule files as input from different sources.
     rule-1 = classic yara rule
     rule-2 = broken yara rule
     rule-3 = yara rule has a unique structure that contains curly brackets inside the rule strings field
     list_rules_input = Several different rules from a single file
    When:
     - Parsing and mapping YARA content using the parse_and_map_yara_content function.
    Then:
     - Returns the parsed YARA rules in JSON format matching the expected results.
    """
    from FeedGitHub import parse_and_map_yara_content

    mocker.patch.object(demisto, "error")
    rule_1_input = {"example.com": util_load_txt("test_data/yara-rule-1.yar")}
    rule_2_input = {"example.com": util_load_txt("test_data/yara-rule-2.yar")}
    rule_3_input = {"example.com": util_load_txt("test_data/yara-rule-3.yar")}
    list_rules_input = {"example.com": util_load_txt("test_data/test-split-yara-1.yar")}
    parsed_rule1 = parse_and_map_yara_content(rule_1_input)
    parsed_rule2 = parse_and_map_yara_content(rule_2_input)
    parsed_rule3 = parse_and_map_yara_content(rule_3_input)
    list_parsed_rules = parse_and_map_yara_content(list_rules_input)

    assert parsed_rule1 == util_load_json("test_data/yara-rule-1-res.json")
    assert parsed_rule2 == util_load_json("test_data/yara-rule-2-res.json")
    assert parsed_rule3 == util_load_json("test_data/yara-rule-3-res.json")
    assert list_parsed_rules == util_load_json("test_data/list-parsed-rules-res.json")


@freeze_time("2024-05-12T15:30:49.330015")
def test_extract_text_indicators():
    """
    Given:
     - A dictionary containing file paths and their respective contents with IOC indicators.
     - Parameters specifying the repository owner and name.
    When:
     - Calling extract_text_indicators to extract IOC indicators from the file contents.
    Then:
     - Returns the extracted IOC indicators matching the expected results.
    """
    from FeedGitHub import extract_text_indicators

    ioc_indicators_input = {"example.com": util_load_txt("test_data/test-ioc-indicators.txt")}
    params = {"owner": "example.owner", "repo": "example.repo"}
    res_indicators = extract_text_indicators(ioc_indicators_input, params)
    assert res_indicators == util_load_json("test_data/iocs-res.json")


def test_get_stix_indicators():
    """
    Given:
        - Output of the STIX feed API
    When:
        - When calling the 'get_stix_indicators' method
    Then:
        - Returns a list of the STIX indicators parsed from "STIX2XSOARParser client"
    """
    from FeedGitHub import get_stix_indicators

    stix_indicators_input = util_load_json("test_data/taxii_test.json")
    res_indicators = get_stix_indicators(stix_indicators_input)
    assert res_indicators == util_load_json("test_data/taxii_test_res.json")


def test_negative_limit(mocker):
    """
    Given:
        - A negative limit.
    When:
        - Calling get_indicators.
    Then:
        - Ensure ValueError is raised with the right message.
    """
    mocker.patch.object(demisto, "error")
    from FeedGitHub import get_indicators_command

    args = {"limit": "-1"}
    client = mock_client()

    with pytest.raises(ValueError) as ve:
        get_indicators_command(client, {}, args)
    assert ve.value.args[0] == "get_indicators_command return with error. \n\nError massage: Limit must be a positive number."


def test_fetch_indicators(mocker):
    """
    Given:
     - A mock client and parameters specifying the fetch time frame.
     - Mocked responses for base and head commit SHAs, and indicators.
    When:
     - Calling fetch_indicators to retrieve indicators from the GitHub feed.
    Then:
     - Returns the list of indicators matching the expected results.
    """
    import FeedGitHub

    client = mock_client()
    mocker.patch.object(demisto, "debug")
    mocker.patch.object(demisto, "setLastRun")
    params = {"fetch_since": "15 days ago"}
    mocker.patch.object(client, "get_commits_between_dates", return_value="046a799ebe004e1bff686d6b774387b3bdb3d1ce")
    mocker.patch.object(
        FeedGitHub,
        "get_indicators",
        return_value=(util_load_json("test_data/iterator-test.json"), "9a611449423b9992c126c20e47c5de4f58fc1c0e"),
    )
    results = FeedGitHub.fetch_indicators(client, None, params)
    assert results == util_load_json("test_data/fetch-indicators-res.json")


@freeze_time("2024-05-20T11:05:36.984413")
def test_get_indicators_command(mocker):
    """
    Given:
     - A mock client and parameters to retrieve indicators from the GitHub feed.
     - Mocked responses for base and head commit SHAs, and indicators.
    When:
     - Calling get_indicators_command to retrieve and format indicators.
    Then:
     - Returns the human-readable output matching the expected results.
    """

    import FeedGitHub
    from CommonServerPython import tableToMarkdown

    client = mock_client()
    # args = {"limit": "6", "since": "15 days ago", "until": "now"}
    mocker.patch.object(demisto, "debug")
    mocker.patch.object(demisto, "error")
    mocker.patch.object(
        client,
        "get_commits_between_dates",
        return_value=[
            "9a611449423b9992c126c20e47c5de4f58fc1c0e",
            "aabaf42225cb4d18e338bc5c8c934f25be814704",
            "046a799ebe004e1bff686d6b774387b3bdb3d1ce",
        ],
    )
    mocker.patch.object(FeedGitHub, "get_indicators", return_value=(util_load_json("test_data/iterator-test.json"), None))
    results = FeedGitHub.get_indicators_command(client, params={}, args={"limit": ""})
    hr_indicators = util_load_json("test_data/hr-indicators.json")
    human_readable = tableToMarkdown("Indicators from GitHubFeed:", hr_indicators, headers=["Type", "Value"], removeNull=True)
    assert results.readable_output == human_readable
