from libs import *
#get_api_return_codes, get_all_api_return_codes, get_first_api_return_code, get_last_api_return_code
def main():
    logfilename = 'Http.log'
    api_url = 'https://api.com/http/v1/data/events'
    print(f"=== Info about calls of {api_url} ===\n"
      f"[1] All return codes: {get_all_api_return_codes(logfilename, api_url)}\n"
      f"[2] First return code: {get_first_api_return_code(logfilename, api_url)}\n"
      f"[3] Last return code: {get_last_api_return_code(logfilename, api_url)}")

    print(f"=== Optional usage of function to get info about calls of {api_url} ===\n"
      f"[1] All return codes: {get_api_return_codes(logfilename, api_url)}\n"
      f"[2] First return code: {get_api_return_codes(logfilename, api_url, target='first')}\n"
      f"[3] Last return code: {get_api_return_codes(logfilename, api_url, target='last')}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()