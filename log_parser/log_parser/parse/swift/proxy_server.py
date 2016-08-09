from urllib import unquote
from urlparse import urlparse

from datetime import datetime

from parse.swift.utils import split_path, LISTING_PARAMS, month_map

__author__ = 'Pace Francesco'


def parse_line(raw_log):
    """given a raw access log line, return a dict of the good parts
    :param raw_log:
    """
    d = {
        'server': 'proxy-server'
    }
    try:
        log_source = None
        split_log = raw_log
        (client_ip,
         lb_ip,
         timestamp,
         method,
         request,
         http_version,
         code,
         referrer,
         user_agent,
         auth_token,
         bytes_in,
         bytes_out,
         etag,
         trans_id,
         headers,
         processing_time) = (unquote(x) for x in split_log[:16])
        if len(split_log) > 16:
            log_source = split_log[16]
    except ValueError:
        # print("Bad line data: %s'" % repr(raw_log))
        return {}
    try:
        parsed_url = urlparse(request)
        request = parsed_url.path
        query = parsed_url.query
        (version, account, container_name, object_name) = \
            split_path(request, 2, 4, True)
    except ValueError, e:
        print("Invalid path: %(error)s from data: %(log)s" %
              {'error': e, 'log': repr(raw_log)})
        return {}
    if version != 'v1':
        # "In the wild" places this can be caught are with auth systems
        # that use the same endpoint as the rest of the Swift API (eg
        # tempauth or swauth). But if the Swift API ever does change, this
        # protects that too.
        print('Unexpected Swift version string: found "%s" expected "v1"' % version)
        return {}
    if query != "":
        args = query.split('&')
        d['query'] = query
        # Count each query argument. This is used later to aggregate
        # the number of format, prefix, etc. queries.
        for q in args:
            if '=' in q:
                k, v = q.split('=', 1)
            else:
                k = q
            # Certain keys will get summmed in stats reporting
            # (format, path, delimiter, etc.). Save a "1" here
            # to indicate that this request is 1 request for
            # its respective key.
            if k in LISTING_PARAMS:
                d[k] = 1
    d['client_ip'] = client_ip
    d['lb_ip'] = lb_ip
    d['method'] = method
    d['request'] = request
    d['http_version'] = http_version
    d['code'] = code
    d['referrer'] = referrer
    d['user_agent'] = user_agent
    d['auth_token'] = auth_token
    d['bytes_in'] = bytes_in
    d['bytes_out'] = bytes_out
    d['etag'] = etag
    d['trans_id'] = trans_id
    d['processing_time'] = processing_time
    day, month, year, hour, minute, second = timestamp.split('/')
    timestamp = (datetime(year=int(year), month=int(month_map.index(month)),
                          day=int(day), hour=int(hour), minute=int(minute), second=int(second)) -
                 datetime(1970, 1, 1)).total_seconds()
    d['day'] = day
    month = ('%02s' % month_map.index(month)).replace(' ', '0')
    d['month'] = month
    d['year'] = year
    d['hour'] = hour
    d['minute'] = minute
    d['second'] = second
    d['timestamp'] = timestamp
    d['tz'] = '+0000'
    d['account'] = account
    d['container_name'] = container_name
    d['object_name'] = object_name
    d['bytes_out'] = int(d['bytes_out'].replace('-', '0'))
    d['bytes_in'] = int(d['bytes_in'].replace('-', '0'))
    d['code'] = int(d['code'])
    d['log_source'] = log_source
    return d


def correlate(parsed_lines):
    parsed_data = {
        "Request": {}
    }
    for line in parsed_lines:
        # if 'client_ip' not in line:
        #     continue
        # if line['client_ip'] == '-' or line['client_ip'] == 'localhost' or line['client_ip'] == '127.0.0.1':
        #     continue

        # if 'log_source' not in line:
        #     continue
        if line['log_source'] != '-':
            continue

        if line['method'] not in parsed_data["Request"]:
            parsed_data["Request"][line['method']] = {
                'total': 0,
                'code': {}
            }
        parsed_data["Request"][line['method']]['total'] += 1

        if line['code'] not in parsed_data["Request"][line['method']]['code']:
            parsed_data["Request"][line['method']]['code'][line['code']] = 0
        parsed_data["Request"][line['method']]['code'][line['code']] += 1

    return parsed_data
