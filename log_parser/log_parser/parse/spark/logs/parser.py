from datetime import datetime

__author__ = 'Pace Francesco'

REQUEST_METHOD = ["HEAD", "GET", "POST", "PUT", "COPY", "DELETE"]


def parse_lines(filepath):
    with open(filepath) as log_file:
        lines = log_file.readlines()
    parsed_lines = []
    for line in lines:
        split_line = line.split(' ')
        if len(split_line) > 4:
            _date = split_line[0]
            _time = split_line[1]
            _level = split_line[2]
            _class = split_line[3].strip(':')
            _message = split_line[4:]
            try:
                # We check if the two field of the line are the date and time, if not, we discard the line
                parsed_lines.append({
                    'dateTime': datetime.strptime(_date + ' ' + _time, '%d/%m/%y %X'),
                    'level': _level,
                    'class': _class,
                    'message': _message
                })
            except ValueError:
                pass

    return parsed_lines


def extract_http_requests(parsed_lines):
    def lookup(line, word):
        if line['class'] == "org.apache.hadoop.fs.swift.http.SwiftRestClient":
            return 1 if line['message'][0] == word else 0
        else:
            res = line['message'].count(word)
            if res > 1:
                print("# ERROR! Line contains multiple record of the searched word (%s)".format(word))
            else:
                return res

    requests = {}
    for line in parsed_lines:
        for method in REQUEST_METHOD:
            if method not in requests:
                requests[method] = 0

            requests[method] += lookup(line, method)

    return requests

