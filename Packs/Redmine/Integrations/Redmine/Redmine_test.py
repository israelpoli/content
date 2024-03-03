import pytest
from Redmine import Client
from requests.models import Response

@pytest.fixture
def redmine_client(url: str = 'url', verify_certificate: bool = True, proxy: bool = False, auth=('username', 'password')):
    return Client(url, verify_certificate, proxy, auth=auth)


''' COMMAND FUNCTIONS TESTS '''

def test_create_issue_command_without_file(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-create command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import create_issue_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'status_id': '1', 'priority_id': '1', 'subject': 'newSubject', 'project_id': '1'}
    create_issue_command(redmine_client, args=args)
    http_request.assert_called_with('POST', '/issues.json', params={'status_id': '1', 'priority_id': '1', 'project_id': '1'},
                                    json_data={'issue': {'subject': 'newSubject'}}, headers={'Content-Type': 'application/json'})


def test_create_issue_command_with_file(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-create command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import create_issue_command
    create_file_token_request_mock = mocker.patch.object(redmine_client, 'create_file_token_request')
    create_file_token_request_mock.return_value = {'upload': {'token': 'token123'}}
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'file_entry_id': '9@klmlqm', 'status_id': '1', 'priority_id': '1', 'subject': 'newSubject', 'project_id': '1'}
    create_issue_command(redmine_client, args=args)
    create_file_token_request_mock.assert_called_with({}, '9@klmlqm')
    http_request.assert_called_with('POST', '/issues.json',
                                    params={'status_id': '1', 'priority_id': '1', 'project_id': '1'},
                                    json_data={'issue': {'subject': 'newSubject', 'uploads': [{'token': 'token123'}]}},
                                    headers={'Content-Type': 'application/json'})

def test_create_issue_command_missing_status_id(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-create command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import create_issue_command
    from CommonServerPython import DemistoException
    args = {}
    with pytest.raises(DemistoException) as e:
        create_issue_command(redmine_client, args)
    assert e.value.message == 'One or more required arguments not specified: status_id, priority_id, subject, project_id'
    
def test_create_issue_command_failed_to_create_file_token(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-create command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import create_issue_command
    create_file_token_request_mock = mocker.patch.object(redmine_client, 'create_file_token_request')
    from CommonServerPython import DemistoException
    args = {'project_id': '2','status_id': '1', 'priority_id': '1', 'subject': 'newSubject', 'file_entry_id':'9@klmlqm'}
    create_file_token_request_mock.return_value = {}
    with pytest.raises(DemistoException) as e:
        create_issue_command(redmine_client, args)
    assert str(e.value) == "Could not upload file with entry id 9@klmlqm"
    
def test_update_issue_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed without list id
    When:
        - redmine-issue-update command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import update_issue_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'issue_id': '1', 'subject': 'changeFromCode', 'tracker_id': '1', 'watcher_user_ids': '[1]'}
    update_issue_command(redmine_client, args=args)
    http_request.assert_called_with('PUT', '/issues/1.json', json_data={'issue': {'subject': 'changeFromCode',
                                                                                  'tracker_id': '1', 'watcher_user_ids': '[1]'}}, headers={'Content-Type': 'application/json'})

def test_update_issue_command_no_issue_id(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-delete command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import update_issue_command
    from CommonServerPython import DemistoException
    args = {}
    with pytest.raises(DemistoException) as e:
        update_issue_command(redmine_client, args)
    assert e.value.message == "Issue_id is missing in order to update this issue"
    
def test_update_issue_command_with_file(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed without list id
    When:
        - redmine-issue-update command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import update_issue_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    create_file_token_request_mock = mocker.patch.object(redmine_client, 'create_file_token_request')
    create_file_token_request_mock.return_value = {'upload': {'token': 'token123'}}
    args = {'entry_id': 'a.png', 'issue_id': '1', 'subject': 'changeFromCode', 'tracker_id': '1', 'watcher_user_ids': '[1]'}
    update_issue_command(redmine_client, args=args)
    create_file_token_request_mock.assert_called_with({}, 'a.png')
    http_request.assert_called_with('PUT', '/issues/1.json', json_data={'issue': {'subject': 'changeFromCode',
                                    'tracker_id': '1', 'watcher_user_ids': '[1]', 'uploads':
                                                                                  [{'token': 'token123', 'file_name': '', 'description': '',
                                                                                   'content_type': ''}]}}, headers={'Content-Type': 'application/json'})

def test_get_issues_list_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed with asset id
    When:
        - redmine-issue-list command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import get_issues_list_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'sort': 'priority:desc', 'limit': '1'}
    get_issues_list_command(redmine_client, args)
    http_request.assert_called_with('GET', '/issues.json', params={'offset': 0, 'limit': '1', 'sort': 'priority:desc'},
                                    headers={})

def test_get_issue_by_id_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed without asset id
    When:
        - redmine-issue-show command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import get_issue_by_id_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'issue_id': '1', 'include': 'watchers,attachments'}
    get_issue_by_id_command(redmine_client, args)
    http_request.assert_called_with('GET', '/issues/1.json', params={'include': 'watchers,attachments'},
                                    headers={'Content-Type': 'application/json'})

def test_get_issue_by_id_command_no_issue_id(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-delete command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import get_issue_by_id_command
    from CommonServerPython import DemistoException
    args = {}
    with pytest.raises(DemistoException) as e:
        get_issue_by_id_command(redmine_client, args)
    assert e.value.message == "Issue_id is missing in order to get this issue"

def test_delete_issue_by_id_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-delete command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import delete_issue_by_id_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'issue_id': '41'}
    delete_issue_by_id_command(redmine_client, args)
    http_request.assert_called_with('DELETE', '/issues/41.json', headers={'Content-Type': 'application/json'}, 
                                    empty_valid_codes=[200, 204, 201], return_empty_response=True)

def test_delete_issue_by_id_command_no_issue_id(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-delete command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import delete_issue_by_id_command
    from CommonServerPython import DemistoException
    args = {}
    with pytest.raises(DemistoException) as e:
        delete_issue_by_id_command(redmine_client, args)
    assert e.value.message == "Issue_id is missing in order to delete"

def test_add_issue_watcher_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-add command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import add_issue_watcher_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'issue_id': '1', 'watcher_id': '1'}
    add_issue_watcher_command(redmine_client, args)
    http_request.assert_called_with('POST', '/issues/1/watchers.json', params={'user_id': '1'},
                                    headers={'Content-Type': 'application/json'},
                                    empty_valid_codes=[200, 204, 201], return_empty_response=True)

def test_add_issue_watcher_command_no_watcher(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-add command is executed
    Then:
        - No watcher id raises a DemistoException
    """
    from Redmine import add_issue_watcher_command
    from CommonServerPython import DemistoException
    args = {'issue_id': '1'}
    with pytest.raises(DemistoException) as e:
        add_issue_watcher_command(redmine_client, args)
    assert e.value.message == "watcher_id is missing in order to add this watcher to the issue"

def test_add_issue_watcher_command_no_issue_id(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-add command is executed
    Then:
        - No issue id raises a DemistoException
    """
    from Redmine import add_issue_watcher_command
    from CommonServerPython import DemistoException
    args = {'watcher_id': '1'}
    with pytest.raises(DemistoException) as e:
        add_issue_watcher_command(redmine_client, args)
    assert e.value.message == "Issue_id is missing in order to add a watcher to this issue"
def test_remove_issue_watcher_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-remove command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import remove_issue_watcher_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'issue_id': '1', 'watcher_id': '1'}
    remove_issue_watcher_command(redmine_client, args)
    http_request.assert_called_with('DELETE', '/issues/1/watchers/1.json', headers={'Content-Type': 'application/json'},
                                    empty_valid_codes=[200, 204, 201], return_empty_response=True)
    
def test_remove_issue_watcher_command_no_watcher(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-remove command is executed
    Then:
        - No watcher id raises a DemistoException
    """
    from Redmine import remove_issue_watcher_command
    from CommonServerPython import DemistoException
    args = {'issue_id': '1'}
    with pytest.raises(DemistoException) as e:
        remove_issue_watcher_command(redmine_client, args)
    assert e.value.message == "watcher_id is missing in order to remove watcher from this issue"

def test_remove_issue_watcher_command_no_issue_id(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-remove command is executed
    Then:
        - No issue id raises a DemistoException
    """
    from Redmine import remove_issue_watcher_command
    from CommonServerPython import DemistoException
    args = {'watcher_id': '1'}
    with pytest.raises(DemistoException) as e:
        remove_issue_watcher_command(redmine_client, args)
    assert e.value.message == "Issue_id is missing in order to remove watcher from this issue"
    
def test_get_project_list_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-project-list command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import get_project_list_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    args = {'include': 'time_entry_activities'}
    get_project_list_command(redmine_client, args)
    http_request.assert_called_with('GET', '/projects.json', params={'include': 'time_entry_activities'}, headers={})

def test_get_project_list_command_include_not_in_predefined_values(redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-issue-watcher-remove command is executed
    Then:
        - No issue id raises a DemistoException
    """
    from Redmine import get_project_list_command
    from CommonServerPython import DemistoException
    args = {'include': 'time_entry_activities,jissue_categories'}
    with pytest.raises(DemistoException) as e:
        get_project_list_command(redmine_client, args)
    assert e.value.message == "The 'include' argument should only contain values from trackers/issue_categories/enabled_modules/time_entry_activities/issue_custom_fields, separated by commas. These values are not in options ['jissue_categories']"


def test_get_custom_fields_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-custom-field-list command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import get_custom_fields_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    get_custom_fields_command(redmine_client, {})
    http_request.assert_called_with('GET', '/custom_fields.json', headers={})
    
def test_get_users_command(mocker, redmine_client):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-user-id-list command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import get_users_command
    http_request = mocker.patch.object(redmine_client, '_http_request')
    get_users_command(redmine_client, {'status': 'Active'})
    http_request.assert_called_with('GET', 'users.json', headers= {}, params= {'status': '1'})

''' HELPER FUNCTIONS TESTS '''

@pytest.mark.parametrize('page_size, page_number, expected_output',
                         [(1, 10, '#### Showing 1 results from page 10:\n')])
def test_create_paging_header(page_size, page_number, expected_output):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-user-id-list command is executed
    Then:
        - The http request is called with the right arguments
    """
    from Redmine import create_paging_header
    assert create_paging_header(page_size, page_number) == expected_output
    
@pytest.mark.parametrize('args, expected_output',
                         [({'page_number':'2','page_size':'20'}, '20, 20, #### Showing 20 results from page 2:\n')])
def test_adjust_paging_to_request(args, expected_output):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - redmine-user-id-list command is executed
    Then:
        - The http request is called with the right arguments
    """
    expected_output = expected_output.split(', ')
    from Redmine import adjust_paging_to_request
    assert adjust_paging_to_request(args) == (int(expected_output[0]), int(expected_output[1]), expected_output[2])
    
@pytest.mark.parametrize('header_name, expected_output',
                         [('id', '#### Showing 1 results from page 10:\n')])
def test_map_header(header_name, expected_output):
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - map header command is executed
    Then:
        - The header is being converted
    """
    from Redmine import map_header
    assert map_header(header_name) == 'ID'

def test_convert_args_to_request_format():
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - adjust_name_to_id_in_dict command is executed
    Then:
        - The key or value is being converted
    """
    from Redmine import convert_args_to_request_format
    convert_args_to_request_format({'watcher_user_ids':'1,2,3'})
    
def test_error_handler():
    """
    Given:
        - All relevant arguments for the command that is executed
    When:
        - error_handler command is executed
    Then:
        - The key or value is being converted
    """
    from Redmine import error_handler
    from CommonServerPython import DemistoException
    response_data = {
        "status_code": 404,
        "reason": "Not Found"
    }
    mock_response = Response()
    mock_response.__dict__.update(response_data)
    with pytest.raises(DemistoException) as e:
        error_handler(mock_response)
    assert e.value.message == "Redmine - Error in API call 404 - Not Found; ID does not exist."