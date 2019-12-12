"""
Module for functions relating to reading/retrieving server settings.

The bot saves server settings in a simple file structure rather than
a database. This makes it easier to delete, edit and overall manage
the settings than if they were in a database. Since the bot is fairly
specialised and not operating on a ton of servers the overhead for
this is very low.
"""
import os

from mrfreeze import colors


def read_server_setting(bot, server, setting):
    """Read and returns a setting stored in server_prefix/server_id/setting."""
    server_dir = create_server_settings(bot, server)
    if not server_dir:
        return False

    setting_path = os.path.join(server_dir, setting)
    try:
        with open(setting_path, "r") as f:
            return f.read().strip()
    except Exception:
        return False


def write_server_setting(bot, server, setting, content):
    """Write content to self.servers_prefix/server.id/setting."""
    server_dir = create_server_settings(bot, server)
    if not server_dir:
        return False

    setting_path = os.path.join(server_dir, setting)
    try:
        with open(setting_path, "w") as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"{bot.current_time()} {colors.RED_B}Server settings:" +
              f"{colors.CYAN} failed to write {colors.YELLOW}{setting_path}" +
              f"{colors.CYAN}:\n{colors.RED}==> {e}{colors.RESET}")
        return False


def create_server_settings(bot, server):
    """Create the directory in which server settings are stored."""
    server_dir = os.path.join(bot.servers_prefix, str(server.id))
    if not os.path.isdir(server_dir):
        if os.path.exists(server_dir):
            print(f"{bot.current_time()} {colors.RED_B}Server settings:" +
                  f"{colors.CYAN} path for {colors.CYAN_B}{server.name} " +
                  f"{colors.YELLOW}({server_dir}){colors.CYAN} exists " +
                  f"but is a file.{colors.RESET}")
            return None
        else:
            try:
                os.makedirs(server_dir)
                print(f"{bot.current_time()} {colors.GREEN_B}" +
                      f"Server settings:{colors.CYAN} created dir for " +
                      f"{colors.CYAN_B}{server.name} {colors.YELLOW}" +
                      f"({server_dir}){colors.RESET}")
            except Exception as e:
                print(f"{bot.current_time()} {colors.RED_B}Server settings:" +
                      f"{colors.CYAN} could not create dir for " +
                      f"{colors.CYAN_B}{server.name} {colors.YELLOW}" +
                      f"({server_dir})\n{colors.RED}==> {e}{colors.RESET}")
                return None
    return server_dir
