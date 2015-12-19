# -*- coding: utf-8 -*-

"""
alfred.commands
~~~~~~~~

Command handlers

:copyright: (c) 2015 by Alejandro Ricoveri
:license: MIT, see LICENSE for more details.

"""

from telegram import Updater
from . import utils
from . import log
from . import config
from .procutils import proc_exec

def bot_command(command_func):
    """
    A decorator whose purpose is to stack middleware
    routines on top of its target function
    """

    # the actual middleware function
    def _middleware(bot, update):
        username = update.message.from_user.username
        userid = update.message.from_user.id
        command = update.message.text
        log.msg_debug("[{}:{}] Received command: '{}'".format(
                username, userid, command
            )
        )
        command_func(bot, update)

    # give the thing back!
    return _middleware

# /hello command
@bot_command
def _hello(bot, update):
    """a rather simple ping command"""

    chatter_name = update.message.from_user.first_name
    utils.echo_msg(
        bot, update,
        "Affirmative, {}. I read you. ".format(chatter_name)
    )

# /dryrun command
@bot_command
def _dryrun(bot, update):
    """toggle dry run mode"""
    config.set('dry_run', not config.get('dry_run'))
    if config.get('dry_run'):
        status = "ON"
    else:
        status = "OFF"
    utils.echo_msg(bot, update, "Dry run mode is {}".format(status))

# /lock command:
@bot_command
def _lock(bot, update):
    """
    it basically runs screenlock script resulting
    in the execution of i3lock
    """

    utils.echo_msg(bot, update, "Your screen(s) are now LOCKED")
    proc_exec('screenlock')

# /poweroff command:
@bot_command
def _poweroff(bot, update):
    """turn off your machine(s)"""

    if not config.get('queue_poweroff') and not config.get('queue_reboot'):
        utils.echo_msg(
            bot, update,
            "Your machines are to be shutdown in about {} minute(s)".format(
                config.get('time_poweroff')
            )
        )
        proc_exec("sudo shutdown -P +{}".format(
                config.get('time_poweroff')
            )
        )
        config.set('queue_poweroff', True)
    else:
        utils.echo_msg(
            bot, update,
            "Your machines are already going to be shutdown/rebooted"
        )


# /cancel command:
@bot_command
def _cancel(bot, update):
    """Cancel any pending reboot/poweroffs"""

    proc_exec("sudo shutdown -c")
    config.set('queue_reboot', False)
    config.set('queue_poweroff', False)
    utils.echo_msg(bot, update, "Operations cancelled")

# /reboot command:
@bot_command
def _reboot(bot, update):
    """reboot your machine(s)"""

    if not config.get('queue_poweroff') and not config.get('queue_reboot'):
        utils.echo_msg(
            bot, update,
            "I'm going to be rebooted in about {} minute(s)".format(
                config.get('time_reboot')
            )
        )
        proc_exec("sudo shutdown -r +{}".format(
                config.get('time_reboot')
            )
        )
        config.set('queue_reboot', True)
    else:
        utils.echo_msg(
            bot, update,
            "Your machines are already going to be shutdown/rebooted"
        )

@bot_command
def _unknown(bot, update):
    """default command handler"""

    chatter_name = update.message.from_user.first_name
    utils.echo_msg(
        bot, update,
        "I am sorry {}. I'm afraid I cannot do that ...".format(chatter_name)
    )

def _print_cmd_desc(commands):
    """Print command descriptions"""
    log.msg_warn("You will need to register my commands with my @BotFather")
    log.msg_warn("Ask him to /setcommands and after you")
    log.msg_warn("have mentioned me, you can paste the following:")
    log.msg("")
    for command, desc, handler in commands:
        print("{} - {}".format(command, desc))
    log.msg("")

def register_commands(updater, dispatcher):
    """register each and every command this bot is going to process"""

    commands = [
        ('hello', 'See if I "live"', _hello),
        ('lock', 'Lock the screen(s) on your host(s)', _lock),
        ('reboot', 'Reboot your host(s)', _reboot),
        ('poweroff', 'Shut down your host(s)', _poweroff),
        ('cancel', 'Cancel any pending operation(s)', _cancel),
        ('dryrun', 'Toggle "dry run" mode', _dryrun),
    ]

    # register every command there is
    for command, desc, handler in commands:
        dispatcher.addTelegramCommandHandler(command, handler)
        log.msg_debug("/{}: command registered".format(command))

    # and the default one as well ...
    log.msg_debug('Registering default handler')
    dispatcher.addUnknownTelegramCommandHandler(_unknown)

    # print command descriptions
    _print_cmd_desc(commands)

