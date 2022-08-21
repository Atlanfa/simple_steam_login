from time import sleep

import steam.webauth as wa
from steam.client import SteamClient
from steam.enums import EResult
import logging


# setup logging
logging.basicConfig(filename='LOGS', filemode='a', format="%(asctime)s | %(message)s", level=logging.INFO)
LOG = logging.getLogger()

client = SteamClient()
client.proxy = "https://190.107.237.13:999"
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


def login():
    result = client.cli_login()

    if result != EResult.OK:
        LOG.info("Failed to login: %s" % repr(result))
        raise SystemExit

    return client, result


def logout(client):
    client.logout()
    return client


def main():
    # main bit
    LOG.info("Persistent logon recipe")
    LOG.info("-" * 30)
    client, result = login()
    print(client.user.name)
    print(client.logged_on)
    print('sleep for 10 sec')
    sleep(10)
    print('end sleep')
    print(client.logged_on)
    logout(client)
    LOG.info('Logout')
    print('logout')
    print(client.logged_on)


if __name__ == '__main__':
    main()
