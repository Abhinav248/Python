#!/router/bin/python3


try:
    import time
    import requests
    import argparse
except Exception as e:
    print ("Failed to import the required modules", e, flush=True)


if __name__ == '__main__':

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--OS", dest = 'OS', help = "OPERATING SYSTEM", required = True)
    parser.add_argument("--tracker_id", dest = 'tracker_id', help = "tracker id", required = True)
    parser.add_argument("--user_id", dest = 'user_id', help = "user id", required = True)
    parser.add_argument("--retry_count", dest='retry_count', help="No of retry if response status fails.")
    parser.add_argument("--retry_interval", dest='retry_interval', help="Sleep time in seconds")
    options, args = parser.parse_known_args()
    os = options.OS
    t_id = options.tracker_id
    u_id = options.user_id
    retry = options.retry_count or 5
    interval = options.retry_interval or 300
    url = 'https://aaaaa.vvvvv.com/getDetails/'
    url += os + '/' + t_id + '?userid=' + u_id
    try:
        count = 0
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                print ("Success\n")
                break
            print ("Failure\n")
            if count == int(retry):
                break
            time.sleep(int(interval))
            print ("Retrying... after %s seconds." %(interval))
            count += 1
    except Exception as e:
        print ("Failed to get response\n", e, flush=True)
