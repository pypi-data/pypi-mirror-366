from http import HTTPStatus

from aioresponses import aioresponses
from yarl import URL


class EVDutyServerForTest:
    base_url = 'https://api.evduty.net'

    def __init__(self):
        self.server = aioresponses()

    def __enter__(self):
        self.server.__enter__()
        return self

    def __exit__(self, *args):
        self.server.__exit__(*args)

    def prepare_login_response(self, body=None, status=HTTPStatus.OK, repeat=True):
        self.server.post(
            url=f'{self.base_url}/v1/account/login',
            status=status,
            payload=body or {'accessToken': 'token', 'expiresIn': 43200},
            repeat=repeat,
        )

    def prepare_stations_response(self, body=None, status=HTTPStatus.OK, repeat=True):
        self.server.get(
            url=f'{self.base_url}/v1/account/stations',
            status=status,
            payload=body or [],
            repeat=repeat,
        )

    def prepare_terminal_details_response(self, body):
        self.server.get(
            url=f'{self.base_url}/v1/account/stations/station_id/terminals/terminal_id',
            status=HTTPStatus.OK,
            payload=body,
            repeat=True,
        )

    def prepare_put_terminal_details(self):
        self.server.put(f'{self.base_url}/v1/account/stations/station_id/terminals/terminal_id')

    def prepare_session_response(self, body):
        self.server.get(
            url=f'{self.base_url}/v1/account/stations/station_id/terminals/terminal_id/session',
            status=HTTPStatus.OK,
            payload=body,
            repeat=True,
        )

    def assert_called_with(self, url, method, *args, **kwargs):
        self.server.assert_called_with(f'{self.base_url}{url}', method, *args, **kwargs)

    def assert_called_n_times_with(self, times, url, method, headers, json):
        key = (method, URL(f'{self.base_url}{url}'))
        assert len(self.server.requests[key]) == times
        self.assert_called_with(url, method, headers=headers, json=json)
