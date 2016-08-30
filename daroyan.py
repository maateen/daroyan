import json
import requests
import time

from config import config
from database import All_IPs
from database import Banned_IPs
from database import Challenged_IPs
from database import UnBan_Schedule
from database import create_database
from database import db
from os import system
from sqlalchemy.orm import sessionmaker


class CloudFlare():

    """
    @description: We will define some methods here to play with CloudFlare
    @param: IP
        This will take an IP as arg.
    """

    def __init__(self):
        self.api = config['cloudflare_api_key']
        self.email = config['cloudflare_email_address']
        self.host = "https://api.cloudflare.com/client/v4/user/firewall/access_rules/rules"
        self.notes = "This rule is on because of an event that triggered by Daroyan!"

    def challenge_this_ip(self, target_ip):
        headers = {"X-Auth-Email": self.email,
                   "X-Auth-Key": self.api, "Content-Type": "application/json"}
        data = json.dumps({"mode": "challenge", "configuration": {
                          "target": "ip", "value": target_ip}, "notes": self.notes}).encode("UTF-8")

        # Requesting via API to challeneg an IP
        response = requests.post(self.host, data=data, headers=headers)

        if response.status_code == 200:
            data = requests.Response.json(response)
            return data

    def ban_this_ip(self, target_ip, identifier):
        headers = {"X-Auth-Email": self.email,
                   "X-Auth-Key": self.api, "Content-Type": "application/json"}
        data = json.dumps({"mode": "block", "configuration": {
                          "target": "ip", "value": target_ip}, "notes": self.notes}).encode("UTF-8")

        # Requesting via API to ban an IP
        host = self.host + '/' + identifier
        response = requests.post(self.host, data=data, headers=headers)

        if response.status_code == 200:
            data = requests.Response.json(response)
            return data

    def unban_this_ip(self, target_ip, identifier):
        headers = {"X-Auth-Email": self.email,
                   "X-Auth-Key": self.api, "Content-Type": "application/json"}

        # Requesting via API to unban an IP
        host = self.host + '/' + identifier
        response = requests.post(self.host, headers=headers)

        if response.status_code == 200:
            data = requests.Response.json(response)
            return data

# Let's define session
Session = sessionmaker()
# Let's create database.
create_database()
# Connect database to session
Session.configure(bind=db)
session = Session()
cloudflare = CloudFlare()
# Calculating waiting time
waiting_time = int(config['action_interval'])/2

while True:
    # This loop will run everytime and only terminate when the script will
    # stop to work!
    fail2ban_log = config['fail2ban_log']
    tmp_fail2ban_log = fail2ban_log + '.tmp'

    # Renaming fail2ban_log to tmp_fail2ban_log
    system("cp " + fail2ban_log + " " + tmp_fail2ban_log)
    # Creating fail2ban_log for as usual Fail2Ban tasks
    system("touch " + fail2ban_log)

    # Parsing IPs from tmp_fail2ban_log
    with open(tmp_fail2ban_log, 'r') as log:
        for target_ip in log:
            target_ip = target_ip.strip('\n')
            checker1 = session.query(All_IPs).filter_by(ip=target_ip).count()
            # If checker1 is zero, then IP isn't in 'ips' table, means the IP
            # was never banned by daroyan.
            if checker1 == 0:
                # Challenging the IP with CloudFlare
                print("Challenging "+target_ip+" with CloudFlare...")
                response = cloudflare.challenge_this_ip(target_ip)
                try:
                    if response['success'] is True:
                        ban_time = time.time() + float(config['ban_time'])
                        session.add_all([All_IPs(target_ip), Challenged_IPs(target_ip, 1, response[
                                        'result']['id']), UnBan_Schedule(target_ip, ban_time, response['result']['id'])])
                        session.commit()
                        print(
                            "New enemy, " + target_ip + " has been challenged.")
                    else:
                        print(
                            "Errors: " + response['errors'] + ", Messages: " + response['messages'])
                except TypeError as TE:
                    print(TE)
            else:
                checker2 = session.query(
                    Banned_IPs).filter_by(ip=target_ip).count()
                # If checker2 is zero, then IP isn't in 'banned_ips' table
                if checker2 == 0:
                    # Challenging the IP with CloudFlare
                    result = session.query(Challenged_IPs).filter_by(
                        ip=target_ip).first()
                    count = result.count
                    print(
                        target_ip + " has been challenged " + str(count) + " times already.")
                    if count >= 3:
                        # Getting the IP banned right now
                        response = cloudflare.ban_this_ip(
                            target_ip, result.identifier)
                        try:
                            if response['success'] is True:
                                session.add(
                                    Banned_IPs(target_ip, response['result']['id']))
                                ban_time = time.time() + \
                                    float(config['ban_time'])
                                session.query(UnBan_Schedule).filter_by(
                                    ip=target_ip).update({'time': ban_time})
                                session.commit()
                                print(
                                    "So, " + target_ip + " has been banned now.")
                            else:
                                print(
                                    response['errors'] + response['messages'])
                        except TypeError as TE:
                            print(TE)
                    else:
                        print("Let's do onnce more!")
                        session.query(Challenged_IPs).filter_by(
                            ip=target_ip).update({'count': count+1})
                        ban_time = time.time() + float(config['ban_time'])
                        session.query(UnBan_Schedule).filter_by(
                            ip=target_ip).update({'time': ban_time})
                        session.commit()
            time.sleep(1)
    # Let's wait some time
    time.sleep(waiting_time)

    # Let's unban IPs which has reached its freedom time
    print("\nUnblock process has started ...\n")
    results = session.query(UnBan_Schedule).order_by(UnBan_Schedule.id)
    for result in results:
        now = time.time()
        print(now-result.time)
        if now >= result.time:
            print("Here")
            response = cloudflare.unban_this_ip(target_ip, result.identifier)
            try:
                if response['success'] is True:
                    print(target_ip + "has been unbanned!")
                    session.delete(result)
                    session.delete(
                        session.query(All_IPs).filter_by(ip=target_ip).first())
                    session.delete(
                        session.query(Challenged_IPs).filter_by(ip=target_ip).first())
                    session.delete(
                        session.query(Banned_IPs).filter_by(ip=target_ip).first())
                else:
                    print(response['errors'] + response['messages'])
            except TypeError as TE:
                print(TE)

        time.sleep(1)
    print("\nUnblock process has finished.\n")
    # Let's wait some time
    time.sleep(waiting_time)
