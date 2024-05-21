import uuid
import demistomock as demisto
from CommonServerPython import *
import urllib3
from typing import Any
import base64


MAX_EVENTS = 500
# Disable insecure warnings
urllib3.disable_warnings()

''' CONSTANTS '''

DATE_FORMAT = '%Y-%m-%dT%H:%M:%SZ'
VENDOR = 'Druva'
PRODUCT = 'Druva'

''' CLIENT CLASS '''


class Client(BaseClient):
    """Client class to interact with the service API

    This Client implements API calls, and does not contain any Demisto logic.
    Should only do requests and return data.
    It inherits from BaseClient defined in CommonServer Python.
    Most calls use _http_request() that handles proxy, SSL verification, etc.
    For this HelloWorld implementation, no special attributes defined
    """

    def update_headers(self, base_64_string):
        base_64_string = base_64_string.decode("utf-8")
        headers = {"Content-Type": "application/x-www-form-urlencoded", 'Authorization': f'Basic {base_64_string}'}
        data = {'grant_type': 'client_credentials', 'scope': 'read'}
        response = self._http_request(method='POST', url_suffix='/token', headers=headers, data=data, resp_type='response')
        response_json = response.json()
        access_token = response_json.get('access_token')
        headers = {'Authorization': f'Bearer {access_token}'}
        self._headers = headers

    def search_events(self, tracker: Optional[str]) -> dict:
        """
        Searches for Druva events.

        Args:
            tracker: pointer to the last event we got last time

        Returns:
            List[Dict]: List of events
        """

        data = {'tracker': tracker} if tracker else {}
        headers = {'Authorization': self._headers.get('Authorization'), 'accept': 'application/json'}
        response = self._http_request(method='GET', url_suffix='/insync/eventmanagement/v2/events', headers=headers, data=data)
        return response


def test_module(client: Client) -> str:
    """
    Tests API connectivity and authentication
    When 'ok' is returned it indicates the integration works like it is supposed to and connection to the service is
    successful.
    Raises exceptions if something goes wrong.

    Args:
        client (Client): Druva client to use.

    Returns:
        str: 'ok' if test passed, anything else will raise an exception and will fail the test.
    """

    try:
        client.search_events()
    except Exception as e:
        if 'Forbidden' in str(e):
            return 'Authorization Error: make sure API Key is correctly set'
        else:
            raise e
    return 'ok'


def get_events(client: Client, tracker: Optional[str]) -> tuple[List[dict], str]:
    """
    Gets events from Druva API in one batch (max 500), if tracker is given, events will be returned from here.
    Args:
        client: Druva client to use.
        tracker: A pointer to the last event we received.

    Returns:
        Druva's events and tracker
    """

    response = client.search_events(tracker)
    return response.get('events'), response.get('tracker')


def fetch_events(client: Client, last_run: dict[str, int],
                 first_fetch_time, alert_status: str | None, max_events_per_fetch: int
                 ) -> tuple[Dict, List[Dict]]:
    """
    Args:
        client (Client): HelloWorld client to use.
        last_run (dict): A dict with a key containing the latest event created time we got from last fetch.
        first_fetch_time: If last_run is None (first time we are fetching), it contains the timestamp in
            milliseconds on when to start fetching events.
        alert_status (str): status of the alert to search for. Options are: 'ACTIVE' or 'CLOSED'.
        max_events_per_fetch (int): number of events per fetch
    Returns:
        dict: Next run dictionary containing the timestamp that will be used in ``last_run`` on the next fetch.
        list: List of events that will be created in XSIAM.
    """
    prev_id = last_run.get('prev_id', None)
    if not prev_id:
        prev_id = 0

    events = client.search_events(
        prev_id=prev_id,
        alert_status=alert_status,
        limit=max_events_per_fetch,
        from_date=first_fetch_time,
    )
    demisto.debug(f'Fetched event with id: {prev_id + 1}.')

    # Save the next_run as a dict with the last_fetch key to be stored
    next_run = {'prev_id': prev_id + 1}
    demisto.debug(f'Setting next run {next_run}.')
    return next_run, events


''' MAIN FUNCTION '''


def add_time_to_events(events: List[Dict] | None):
    """
    Adds the _time key to the events.
    Args:
        events: List[Dict] - list of events to add the _time key to.
    Returns:
        list: The events with the _time key.
    """
    if events:
        for event in events:
            create_time = arg_to_datetime(arg=event.get('timestamp'))
            event['_time'] = create_time.strftime(DATE_FORMAT) if create_time else None


def main() -> None:  # pragma: no cover
    """
    main function, parses params and runs command functions
    """

    params = demisto.params()
    args = demisto.args()
    command = demisto.command()
    proxy = params.get('proxy') == 'false'
    verify_certificate = not params.get('insecure', False)

    druva_client_id = params["credentials"]["identifier"]
    druva_secret_key = params["credentials"]["password"]
    druva_base_url = params.get('url')
    str_to_encode = f'{druva_client_id}:{druva_secret_key}'
    base_64_string = base64.b64encode(str_to_encode.encode())

    demisto.debug(f'Command being called is {command}')
    try:
        client = Client(
            base_url=druva_base_url,
            verify=verify_certificate,
            headers=None,
            proxy=proxy)

        client.update_headers(base_64_string)

        if command == 'test-module':
            # This is the call made when pressing the integration Test button.
            return_results(test_module(client))

        elif command == 'druva-get-events':
            should_push_events = argToBoolean(args.pop('should_push_events'))
            events, tracker = get_events(client, args.get('tracker'))
            return_results(
                CommandResults(readable_output=tableToMarkdown(f"{VENDOR} Events:", events))
            )
            if should_push_events:
                add_time_to_events(events)
                send_events_to_xsiam(
                    events,
                    vendor=VENDOR,
                    product=PRODUCT
                )

        # elif command == 'fetch-events':
        #     last_run = demisto.getLastRun()
        #     next_run, events = fetch_events(
        #         client=client,
        #         last_run=last_run,
        #         first_fetch_time=first_fetch_time,
        #         alert_status=alert_status,
        #         max_events_per_fetch=max_events_per_fetch,
        #     )
        #
        #     add_time_to_events(events)
        #     send_events_to_xsiam(
        #         events,
        #         vendor=VENDOR,
        #         product=PRODUCT
        #     )
        #     demisto.setLastRun(next_run)


    # Log exceptions and return errors
    except Exception as e:
        return_error(f'Failed to execute {command} command.\nError:\n{str(e)}')


''' ENTRY POINT '''

if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()
