

import json
from time import sleep

from steam.client import SteamClient
from steam.enums import EResult
import logging


# setup logging
from steam.guard import SteamAuthenticator

logging.basicConfig(filename='LOGS', filemode='a', format="%(asctime)s | %(message)s", level=logging.INFO)
LOG = logging.getLogger()

client = SteamClient()
client.set_credential_location(".")  # where to store sentry files and other stuff


@client.on("error")
def handle_error(result):
    LOG.info("Logon result: %s", repr(result))


@client.on("channel_secured")
def send_login():
    if client.relogin_available:
        client.relogin()


@client.on("connected")
def handle_connected():
    LOG.info("Connected to %s", client.current_server_addr)


@client.on("reconnect")
def handle_reconnect(delay):
    LOG.info("Reconnect in %ds...", delay)


@client.on("disconnected")
def handle_disconnect():
    LOG.info("Disconnected.")

    if client.relogin_available:
        LOG.info("Reconnecting...")
        client.reconnect(maxdelay=30)


@client.on("logged_on")
def handle_after_logon():

    LOG.info("-"*30)
    LOG.info("Logged on as: %s", client.user.name)
    LOG.info("Community profile: %s", client.steam_id.community_url)
    LOG.info("Last logon: %s", client.user.last_logon)
    LOG.info("Last logoff: %s", client.user.last_logoff)
    LOG.info("-"*30)
    LOG.info("Press ^C to exit")





def login(username, password, two_factor_code):
    result = client.login(username=username, password=password, two_factor_code=two_factor_code)

    # if result != EResult.OK:
    #     LOG.info("Failed to login: %s" % repr(result))
    #     raise SystemExit

    return client, result


def login_cli():
    result = client.cli_login()

    if result != EResult.OK:
        LOG.info("Failed to login: %s" % repr(result))
        raise SystemExit

    return client, result


def logout():
    client.logout()


def get_user_by_login_from_json(username):
    with open('users.json', 'r') as f:
        json_users = json.load(f)
        # print(json_users['users'])
        for user in json_users['users']:
            if user['login'] == username:
                return user
        return None


def main():
    # main bit
    LOG.info("Persistent logon recipe")
    LOG.info("-" * 30)
    user_1 = get_user_by_login_from_json('somovvesta')
    user_2 = get_user_by_login_from_json('cvetkovhloya')
    for user in [user_1, user_2]:
        print(user['login'])
        print(user['password'])
        try:
            # get 2fa code from shared_secret using steam.guard.generate_twofactor_code
            code = SteamAuthenticator(secrets={'shared_secret': user['shared_secret']}).get_code()
            client, result = login(user['login'], user['password'], code)
            if result != EResult.OK:
                LOG.info("Failed to login: %s" % repr(result))
                logout()
                raise Exception
            print(client.user.name)
            print(client.logged_on)
            print('sleep for 10 sec')
            sleep(10)
            print('end sleep')
            print(client.logged_on)
            logout()
            LOG.info('Logout')
            print('logout')
            print(client.logged_on)
        except Exception as e:
            print(e)
            print('error')
            # print('Invalid password')


if __name__ == '__main__':
    main()
