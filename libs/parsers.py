import re


class HttpLogLineParser(object):
    row_regex = "^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}) " \
        "(?P<pid>\d{1,5}) (?P<log_level>[A-Z]+) (?P<session_id>\d+): (?P<session_data>.*)$"

    def parse(self, log_line):
        '''
        will return parsed data in case it is reflects to used regexp

        :param row: Line of the log file
        :return: parsed data or None
        '''
        result = re.match(self.row_regex, log_line)
        return None if result is None else result.groupdict()


class HttpSession(object):
    _regexps = [
        r'^HttpRequest::URL - (?P<api_url>.*)$',
        r'^HttpRequest::receiveResponse succeed\. StatusCode:(?P<status_code>\d{3}), '
        'ContentLength:(?P<content_length>\d+), StreamLength=(?P<stream_length>\d+)$'
    ]

    def __init__(self, id=None):
        self._id = id
        self._history = []

    def process(self, prepared_data):
        self._history.append(prepared_data)
        # TODO: set start and stop session ts via setter
        for regex in self._regexps:
            result = re.match(regex, prepared_data.get("session_data"))
            if result is not None:
                result = result.groupdict()
                for session_attribute, attribute_value in result.items():
                    # print(self._id, session_attribute, attribute_value)  # TODO: logging
                    # TODO: check if attribute is already exists --> it can be in case we have duplicated session id
                    self.__setattr__(session_attribute, attribute_value)
                return


class HttpLogParser(object):
    def __init__(self, log_file: str, line_parser=HttpLogLineParser):
        self._sessions = {}
        self._sessions_history = []
        self._line_parser = line_parser()
        self.logfile = log_file
        self.__process_logfile()

    def __process_logfile(self):
        with open(self.logfile, "r") as log:
            for line in log.readlines():
                self._process(line)

    def _process(self, line):
        """
        Process prepared data
        :param prepared_data: dict with specific information about session
        :return: None
        """

        prepared_data = self._line_parser.parse(line)
        if prepared_data is None: return

        session_id = prepared_data.get("session_id", None)
        # stop processing data in case it was not prepared
        if session_id is None: return
        # print(prepared_data)
        # if len(self._sessions_history) == 0 or self._sessions_history[-1] != session_id:
        #     print(session_id)

        # update sessions_history if it is required
        # TODO: time based order
        if session_id not in self._sessions_history:
            self._sessions_history.append(session_id)

        session = self._sessions.get(session_id, HttpSession(id=session_id))
        session.process(prepared_data)

        self._sessions[session_id] = session

    def _get_all_session_ids_for_url(self, api):
        target_sessions = []
        for session_id in self._sessions_history:
            session = self._sessions.get(session_id)
            if session.api_url == api:
                target_sessions.append(session_id)

        return target_sessions

    def get_all_api_return_codes(self, api):
        '''
        Return all return codes for calls of specified api

        :param api: target api
        :return: list of all return codes
        '''
        return [self._sessions.get(session_id).status_code for session_id in self._get_all_session_ids_for_url(api)]

    def get_first_api_return_code(self, api):
        '''
        Return only first return code for calls of specified api

        :param api: target api
        :return: return code or None
        '''
        all_return_codes = self.get_all_api_return_codes(api)
        return None if len(all_return_codes) == 0 else all_return_codes[0]

    def get_last_api_return_code(self, api):
        '''
        Return only last return code for calls of specified api

        :param api: target api
        :return: return code or None
        '''
        all_return_codes = self.get_all_api_return_codes(api)
        return None if len(all_return_codes) == 0 else all_return_codes[-1]

def get_all_api_return_codes(log_file: str, api: str):
    return get_api_return_codes(log_file=log_file, api=api)

def get_first_api_return_code(log_file: str, api: str):
    return get_api_return_codes(log_file=log_file, api=api, target='first')

def get_last_api_return_code(log_file: str, api: str):
    return get_api_return_codes(log_file=log_file, api=api, target='last')

def get_api_return_codes(log_file: str, api: str, target:str = 'all'):
    parser = HttpLogParser(log_file=log_file)
    return {
        'all': parser.get_all_api_return_codes,
        'first': parser.get_first_api_return_code,
        'last': parser.get_last_api_return_code
    }[target](api=api)
