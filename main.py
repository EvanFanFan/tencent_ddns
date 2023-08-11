import re
import requests
import json
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.dnspod.v20210323 import dnspod_client, models

import configparser
config=configparser.ConfigParser()
config.read("config.ini")
SecretId=config["DEFAULT"]["SecretId"]
SecretKey=config["DEFAULT"]["SecretKey"]
domain=config["Domain"]["domain"]
sub_domain_list=config["Domain"]["sub_domain_list"].split(",")

def get_domain_recordlist(domain):
    try:
        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"

        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)

        req = models.DescribeRecordListRequest()
        params = {
            "Domain": domain
        }
        req.from_json_string(json.dumps(params))

        resp = client.DescribeRecordList(req)
        reslut_json=resp.to_json_string()
        reslut_data=json.loads(reslut_json)

        return reslut_data["RecordList"]
        
    except TencentCloudSDKException as err:
        print(err)

def chang_dns_record(domain,record_id,ip_addr,sub_domain):
    try:

        cred = credential.Credential(SecretId, SecretKey)
        httpProfile = HttpProfile()
        httpProfile.endpoint = "dnspod.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile
        client = dnspod_client.DnspodClient(cred, "", clientProfile)
        req = models.ModifyRecordRequest()
        params = {
            "Domain": domain,
            "SubDomain": sub_domain,
            "RecordType": "A",
            "RecordLine": "默认",
            "Value": ip_addr,
            "RecordId": record_id
        }
        req.from_json_string(json.dumps(params))

        resp = client.ModifyRecord(req)
        print(resp.to_json_string())
    except TencentCloudSDKException as err:
        print(err)

def get_ip_addr():
    try:
        aaa=requests.get("http://www.net.cn/static/customercare/yourip.asp")
        matchObj = re.findall( '您的本地上网IP是：<h2>(.*)</h2>', aaa.text)
        ip_addr=matchObj[0]
        return ip_addr
    except:
        print("get ip addr error")
        return ""


app_config=configparser.ConfigParser()
try:
    app_config.read('app.cfg')
    ip_addr_last=app_config["DEFAULT"].get("ip_addr_last")
except Exception as e:
    ip_addr_last=""

ip_addr_last=app_config["DEFAULT"].get("ip_addr_last")
cur_ip_addr=get_ip_addr()
if cur_ip_addr!=ip_addr_last and bool(cur_ip_addr):
    record_list=get_domain_recordlist(domain)
    for record in record_list:
        if record["Name"] in sub_domain_list:
            if cur_ip_addr!=record["Value"]:
                chang_dns_record(domain=domain,record_id=record["RecordId"],ip_addr=cur_ip_addr,sub_domain=record["Name"])
                print(record["Name"]+" changed")

app_config=configparser.ConfigParser()
app_config['DEFAULT']['ip_addr_last']=cur_ip_addr
with open('app.cfg', 'w') as configfile:
    app_config.write(configfile)
