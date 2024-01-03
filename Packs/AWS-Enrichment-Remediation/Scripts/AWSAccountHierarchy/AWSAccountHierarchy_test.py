import demistomock as demisto  # noqa: F401
import pytest
from CommonServerPython import CommandResults


def test_lookup_func(mocker):
    """Tests lookup helper function.

        Given:
            - Mocked arguments
        When:
            - Sending args to lookup helper function.
        Then:
            - Checks the output of the helper function with the expected output.
    """
    from AWSAccountHierarchy import lookup
    folder_lookup = [{'Type': 1, 'Contents': {'AWS.Organizations.Root(val.Id && val.Id == obj.Id)': [{'Arn': 'arn:aws:organizations::111111111111:root/o-2222222222/r-3333', 'Id': 'r-3333', 'Name': 'Root'}]}}]

    mocker.patch.object(demisto, "executeCommand", return_value=folder_lookup)
    args = {"parent_obj": "r-3333", "level": 2, "instance_to_use": "fake-instance-name"}
    result = lookup(**args)
    assert result == ('stop', {'id': 'r-3333', 'level': '2', "name": "Root", 'arn': 'arn:aws:organizations::111111111111:root/o-2222222222/r-3333'})


def test_aws_account_heirarchy_command(mocker):
    """Tests aws_account_heirarchy function.

        Given:
            - Mocked arguments
        When:
            - Sending args to aws_account_heirarchy function.
        Then:
            - Checks the output of the function with the expected output.
    """
    from AWSAccountHierarchy import aws_account_heirarchy

    def executeCommand(name, args):
        if name == "aws-org-account-list":
            return [{'Type': 1, 'Contents': {'Name': "master-account", 'Id': '111111111111', 'Arn': "arn:aws:organizations::111111111111:root/o-2222222222/111111111111"}, 'Metadata': {'instance': 'fake-instance-name'}}]
        elif name == "aws-org-parent-list":
            return [{'Type': 1, 'Contents': {'Id': 'r-3333'}}]
        elif name == "aws-org-root-list":
            return [{'Type': 1, 'Contents': {'AWS.Organizations.Root(val.Id && val.Id == obj.Id)': [{'Arn': 'arn:aws:organizations::111111111111:root/o-2222222222/r-3333', 'Id': 'r-3333', 'Name': 'Root'}]}}]

    mocker.patch.object(demisto, "executeCommand", side_effect=executeCommand)
    args = {"account_id": "111111111111"}
    result = aws_account_heirarchy(args)
    expected_hierachy = [{'id': '111111111111', 'level': 'account', 'name': 'master-account', 'arn': "arn:aws:organizations::111111111111:root/o-2222222222/111111111111"}, {'id': 'r-3333', 'level': '1', 'name': 'Root', 'arn': 'arn:aws:organizations::111111111111:root/o-2222222222/r-3333'}]
    expected_result = CommandResults(outputs_prefix='AWSHierarchy',
                                     outputs_key_field='level',
                                     outputs=expected_hierachy)
    assert result.outputs == expected_result.outputs
    #assert result.readable_output == 2


def test_aws_account_heirarchy_command_no_account(mocker):
    """Tests aws_account_heirarchy function.

        Given:
            - Null mocked arguments
        When:
            - Sending args to aws_account_heirarchy function.
        Then:
            - Checks the output of the function with the expected output.
    """
    from AWSAccountHierarchy import aws_account_heirarchy

    def executeCommand(name, args):
        if name == "aws-org-account-list":
            return [{'Type': 4, 'Contents': {'bad command'}}]

    mocker.patch.object(demisto, "executeCommand", side_effect=executeCommand)
    args = {"account_id": "111111111111"}
    result = aws_account_heirarchy(args)
    expected_result = CommandResults(readable_output = "could not find specified account info")

    assert result.readable_output == expected_result.readable_output

