from parse.swift import proxy_server

__author__ = 'Pace Francesco'


def parse_lines(raw_lines, start_timestamp, end_timestamp):
    proxy_lines = []
    parsed_data = {
        "proxy-server": {}
    }
    for raw_line in raw_lines:
        split_log = raw_line.split(' ')
        if "proxy-server:" in split_log[:5]:
            parsed_line = proxy_server.parse_line(split_log[5:])
            # start and end timestamps are in millisecond precision
            # parsed_line["timestamp"] is in second precision
            if len(parsed_line) != 0 and (start_timestamp / 1000.0) < parsed_line["timestamp"] < (end_timestamp / 1000.0):
                proxy_lines.append(parsed_line)

    parsed_data["proxy-server"] = proxy_server.correlate(proxy_lines)

    return parsed_data
