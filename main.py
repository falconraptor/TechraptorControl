import time

import pexpect
import re
from discord.ext import commands
import os

bot = commands.Bot(command_prefix=commands.when_mentioned_or(''), description='Techraptor Control Bot')


@bot.event
async def on_ready():
    print('Logged in as: {0} (ID: {0.id})'.format(bot.user))


def run_command(screen, command, expected, sleep=.2, timeout=2, before=True):
    session = pexpect.spawn('/bin/bash')
    session.sendline('screen -r {} -p0 -X stuff "{}"'.format(screen, command))
    session.sendline('screen -r {} -p0 -X eval "stuff \\015"'.format(screen))
    time.sleep(sleep)
    session.sendline('screen -r {} -p0 -X hardcopy $(tty)'.format(screen))
    session.expect(expected, timeout=timeout)
    if before:
        output = session.before.decode().replace('\r', '').split('\n')
    else:
        output = session.after.decode().replace('\r', '').split('\n')
    session.close()
    return output


class Commands:
    mc_servers = {'custom-sky factory': 'sf-custom', 'sky factory': 'skyfactory', 'techraptor': 'mc', 'Invasion': 'invastion'}

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, no_pm=False)
    async def reply(self, ctx):
        await self.bot.say(ctx.message.content + '\n' + str(ctx.message.channel) + '\n' + str(ctx.message.author))

    @commands.group(name='list')
    async def list(self):
        pass

    @list.command(pass_context=True, no_pm=False)
    async def servers(self, ctx):
        await self.bot.say('\n'.join(self.mc_servers.keys()))

    @list.command(pass_context=True, no_pm=False)
    async def players(self, ctx, server=None):
        if not server:
            await self.bot.say('please use a server from the list servers command.')
            return
        output = run_command(self.mc_servers[server], 'list', 'list\r?\n[\[\]:_,\w /]+([\r\n\[\]:_,\w /]+)', before=False)
        amount = re.search(r'are (\d+/\d+) players', output[1])
        output = [u for o in output if re.search(': (.*)', o) for u in re.search(': (.*)', o)[1].split(',')]
        await self.bot.say(str(amount[1])+': '+','.join(output[1:]))


bot.add_cog(Commands(bot))

bot.run(os.environ['token'])
