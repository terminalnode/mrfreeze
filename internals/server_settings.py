import os   # Required for interacting with the file system.

def read_server_setting(bot, server, setting):
    """Reads and returns a setting stored in self.servers_prefix/server.id/setting."""
    server_dir = create_server_settings(bot, server)
    if not server_dir:
        return False

    setting_path = os.path.join(server_dir, setting)
    try:
        with open(setting_path, 'r') as f:
            return f.read().strip()
    except:
        return False

def write_server_setting(bot, server, setting, content):
    """Writes content to self.servers_prefix/server.id/setting"""
    server_dir = create_server_settings(bot, server)
    if not server_dir:
        return False

    setting_path = os.path.join(server_dir, setting)
    try:
        with open(setting_path, 'w') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"{bot.current_time()} {bot.RED_B}Server settings:{bot.CYAN} failed to write {bot.YELLOW}{setting_path}{bot.CYAN}:\n" +
            f"{bot.RED}==> {e}{bot.RESET}")
        return False

def create_server_settings(bot, server):
    """Creates the directory in which server settings are stored."""
    server_dir = os.path.join(bot.servers_prefix, str(server.id))
    if not os.path.isdir(server_dir):
        if os.path.exists(server_dir):
            print(f"{bot.current_time()} {bot.RED_B}Server settings:{bot.CYAN} path for "+
                f"{bot.CYAN_B}{server.name} {bot.YELLOW}({server_dir}){bot.CYAN} exists but is a file.{bot.RESET}")
            return None
        else:
            try:
                os.makedirs(server_dir)
                print(f"{bot.current_time()} {bot.GREEN_B}Server settings:{bot.CYAN} created dir for " +
                    f"{bot.CYAN_B}{server.name} {bot.YELLOW}({server_dir}){bot.RESET}")
            except Exception as e:
                print(f"{bot.current_time()} {bot.RED_B}Server settings:{bot.CYAN} could not create dir for " +
                    f"{bot.CYAN_B}{server.name} {bot.YELLOW}({server_dir})\n" +
                    f"{bot.RED}==> {e}{bot.RESET}")
                return None
    return server_dir
