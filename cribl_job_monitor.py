#!/usr/bin/python

import requests
import json
import os
import sys
import argparse
import getpass

#############################
# I don't care about insecure certs
# (maybe you do, comment out if so)
requests.urllib3.disable_warnings(requests.urllib3.exceptions.InsecureRequestWarning)

#############################
# where we login to get a bearer token
auth_uri = '/api/v1/auth/login'
cloud_token_url = 'https://login.cribl.cloud/oauth/token'

#############################
# prompt for password if one is not supplied
class Password:
    # if password is provided, use it. otherwise prompt
    DEFAULT = 'Prompt if not specified'

    def __init__(self, value):
        if value == self.DEFAULT:
            value = getpass.getpass('Password: ')
        self.value = value

    def __str__(self):
        return self.value

# Check if the TOKEN environment variable exists
def get_token_from_env():
    return os.getenv('CRIBL_AUTH_TOKEN')

#############################
# parse the command args
def parse_args():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-D', '--debug', help='Extra output',action='store_true')
    parser.add_argument('-l', '--leader', help='Leader URL, http(s)://leader:port',required=True)
    parser.add_argument('-g', '--group', type=str, help="Target worker group", required=False)
    parser.add_argument('-u', '--username', help='API token id (cloud) or user id (self-managed)',required=False)

    bearer_token = get_token_from_env()
    parser.add_argument('-P', '--password', type=Password, help='Specify password or secret, or get prompted for it',
                        default=Password.DEFAULT if not bearer_token else bearer_token)

    args = parser.parse_args()
    return args

#############################
# some debug notes
def debug_log(log_str):
    if args.debug:
        print("DEBUG: {}".format(log_str))

#############################
# get logged in for Cribl SaaS
def cloud_auth(client_id,client_secret):
    # get logged in and grab a token
    header = {'accept': 'application/json', 'Content-Type': 'application/json'}
    login = '{"grant_type": "client_credentials","client_id": "' + client_id + '", "client_secret": "' + client_secret + '","audience":"https://api.cribl.cloud"}'
    r = requests.post(cloud_token_url,headers=header,data=login,verify=False)
    if (r.status_code == 200):
        res = r.json()
        debug_log("Bearer token: " + res["access_token"])
        return res["access_token"]
    else:
        print("Login failed, terminating")
        print(str(r.json()))
        sys.exit()

#############################
# get logged in for self-managed instances
def on_prem_auth(leader_url,un,pw):
    # get logged in and grab a token
    header = {'accept': 'application/json', 'Content-Type': 'application/json'}
    login = '{"username": "' + un + '", "password": "' + pw + '"}'
    r = requests.post(leader_url+auth_uri,headers=header,data=login,verify=False)
    if (r.status_code == 200):
        res = r.json()
        return res["token"]
    else:
        print("Login failed, terminating")
        print(str(r.json()))
        sys.exit()


def get_job_list(leader, group, auth_token):
    header = {"Authorization": "Bearer {}".format(auth_token), "accept": "application/json", "Content-Type": "application/json"}
    if group:
        joburl = f"jobs?groupId={group}"
    else:
        joburl = "jobs"
    resp = requests.get(f"{leader}/{joburl}", headers=header, verify=False)
    return(json.loads(resp.text))

def trim_json(json_object):
    result = []
    for item in json_object['items']:
        # skip orphans
        if not item['status']['state'] == 'orphaned':
            item_dict = {}
            item_dict['id'] = item['id']
            item_dict['status'] = item['status']
            item_dict['stats'] = item['stats']
            item_dict['name'] = item['args']['id']
            item_dict['wg'] = item['args']['groupId']
            result.append(item_dict)
    return result

#############################
#############################
# main
if __name__ == "__main__":
    args = parse_args()
    # get logged in if needed
    if os.getenv('CRIBL_AUTH_TOKEN'):
        # use bearer token in the env if it's there
        bearer_token = os.getenv('CRIBL_AUTH_TOKEN')
    else:
        # use cloud login if it looks like a cloud url
        if args.leader.find('cribl.cloud') > 0:
            bearer_token = cloud_auth(args.username,str(args.password))
        # for self-managed use the library's built-in method
        else:
            bearer_token = on_prem_auth(args.leader, args.username, args.password).json()["token"]

    debug_log("GETting job list")
    if "group" in args:
        group = args.group
    else:
        group = False
    job_list = get_job_list(args.leader,group,bearer_token)
    # pretty print json with 4 indents
    print(json.dumps(trim_json(job_list),indent=4))
    # or compact print
    # print(json.dumps(trim_json(job_list)))
