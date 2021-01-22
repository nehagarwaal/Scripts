import boto3
import os

cidr_to_add = "91.209.223.0/24"
# existing_ips_to_match  = str(os.environ["existing_ips_to_match"])

def get_waf_client():
    client = boto3.client("waf-regional")
    return client

def get_change_token(waf_client):
    change_token = waf_client.get_change_token()
    return change_token.get("ChangeToken")

def get_ip_conditions_to_modify(waf_client):
    try:
        waf_ip_sets_to_modify = []
        response = waf_client.list_ip_sets()
        ip_set_list = response.get("IPSets")
        for ip_set in ip_set_list:
            response = waf_client.get_ip_set(
                IPSetId=ip_set["IPSetId"]
            )
            for ip in response.get("IPSet").get("IPSetDescriptors"):
                if ip.get("Value") in ["114.143.135.80/29"]:
                    waf_ip_sets_to_modify.append(ip_set)
                    break
        print('**WAF IP Conditions to modify are** \n')
        print(waf_ip_sets_to_modify)
        return waf_ip_sets_to_modify
    
    except:
        print ("Falied to fetch IP conditions to be modified")
        raise 

def add_cidr_ip_conditions(waf_client, waf_ip_sets_to_modify):
    try:
        for ip_set in waf_ip_sets_to_modify:
            change_token = get_change_token(waf_client)
            waf_client.update_ip_set(
                IPSetId=ip_set["IPSetId"],
                ChangeToken=change_token,
                Updates=[
                    {
                        'Action': 'INSERT',
                        'IPSetDescriptor': {
                            'Type': 'IPV4',
                            'Value': cidr_to_add
                        }
                    }
                ]
            )
            print("Added in " + ip_set["Name"])
    
    except:
        print ("Falied to update IP conditions")
        raise 

def main():
    waf_client = get_waf_client()
    waf_ip_sets_to_modify = get_ip_conditions_to_modify(waf_client)
    add_cidr_ip_conditions(waf_client,waf_ip_sets_to_modify)

if __name__ == "__main__":
    main()