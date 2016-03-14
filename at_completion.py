# based on http://scripts.irssi.org/scripts/hipchat_tab_completion.pl

import weechat
import re

SCRIPT_NAME = "at_completion"
SCRIPT_AUTHOR = "Jason Plum <max@warheads.net>"
SCRIPT_VERSION = "0.1"
SCRIPT_LICENSE = "GPL3"
SCRIPT_DESC = "Tab completion for protocols needing @"

STRIP_VAR = 'plugins.var.python.'+SCRIPT_NAME+'.'

config = {
    'enable'  : False,
    'servers' : [],
    'buffers' : [],
}
config_desc = {
    'enable'  : 'Enable/disable the completion function',
    'servers' : 'Comma seperated list of servers that should be completed for',
    'buffers' : 'Comma seperated list of buffers that should be completed for',
}

def check_buffers(name):
    if name in config['buffers']: return True
    for x in config['buffers']:
        i = x.index('*');
        if i != -1:
            x = '%s.*%s' % (re.escape(x[:i]),re.escape(x[i+1:]))
            r = re.compile(x)
            if r.match(name) : return True
    return False

def walk_nicklist(nicklist,word):
    weechat.infolist_reset_item_cursor(nicklist)
    ni = weechat.infolist_next(nicklist)
    while ni :
        type = weechat.infolist_string(nicklist,'type')
        if type == 'nick':
            nick = weechat.infolist_string(nicklist,'name')
            if nick.lower().startswith(word):
                return nick
        ni = weechat.infolist_next(nicklist)
    return ''

def at_completion(data, buffer, command):
    if not config['enable']:
        return weechat.WEECHAT_RC_OK
    
    input = weechat.buffer_get_string(buffer, 'input')
    if input[0] != '/':
        buffer_name = weechat.buffer_get_string(buffer,'name')
        plugin_name = weechat.buffer_get_string(buffer,'plugin')
        # don't nick complete in core
        if plugin_name == 'core': return weechat.WEECHAT_RC_OK
        server_name = buffer_name.split('.')[0]
        if (server_name not in config['servers'] 
           or not check_buffers(buffer_name) ):
           return weechat.WEECHAT_RC_OK
        pos = weechat.buffer_get_integer(buffer, 'input_pos')
        if pos > 0 and (pos == len(input) or input[pos] == ' '):
            n = input.rfind(' ', 0, pos)
            e = input.find(' ',n)
            at = 0
            word = input[n+1:pos]
            if e != n :
              word = word[:e]
            if word[0] == '@':
                word = word[1:]
                at = 1
            nicklist = weechat.infolist_get('nicklist', buffer, '')
            if nicklist:
                nick = walk_nicklist(nicklist,word)
                if nick != "":
                    complete = '%s@%s %s' %(input[:pos-len(word)-at],nick,input[pos:])
                    weechat.buffer_set(buffer, 'input', complete)
                    weechat.buffer_set(buffer, 'input_pos', str(pos - len(word) + len(nick)+2))
                    return weechat.WEECHAT_RC_OK_EAT
    return weechat.WEECHAT_RC_OK

def at_control(data,buffer,args):
    argv = args.split(' ')
    js = ', '
    if argv[0] in ['enable','disable','toggle']:
        if argv[0] == 'enable' : config['enable'] = True
        if argv[0] == 'disable': config['enable'] = False
        if argv[0] == 'toggle' : config['enable'] = not config['enable']
        weechat.config_set_plugin('enable','on' if config['enable'] else 'off')
    if argv[0] == 'status':
        weechat.prnt('','atcomplete: %s' % 'on' if config['enable'] else 'off')
        weechat.prnt('','   servers: %s' % js.join(config['servers']))
        weechat.prnt('','   buffers: %s' % js.join(config['buffers']))
    if argv[0] in ['server','buffer']:
        sets = argv[0]+'s'
        if argv[1] == 'list':
            weechat.prnt('','atcomplete %s: %s' % (sets,js.join(config[sets])))
        if (argv[1] == 'add' and len(argv) == 3):
            if argv[2] not in config[sets]: 
                config[sets].append(argv[2])
                at_config('',STRIP_VAR+sets,js.join(config[sets]))
        if (argv[1] == 'del' and len(argv) == 3):
            if argv[2] in config[sets]:
                config[sets].remove(argv[2])
                at_config('',STRIP_VAR+sets,js.join(config[sets]))
    return weechat.WEECHAT_RC_OK

def at_complete(data,item,buffer,completion):
    weechat.prnt('','at_complete: %s %s' % (item, weechat.buffer_get_string(buffer,'name')))
    args = weechat.hook_completion_get_string(completion,'args')
    weechat.prnt('','at_complete: a: %s' % args)
    return weechat.WEECHAT_RC_OK

def at_config(data = '', option = '', value = ''):
    return_code = weechat.WEECHAT_CONFIG_OPTION_SET_OK_SAME_VALUE
    option = option.replace(STRIP_VAR,'')
    if data == 'load' :
        for k in config.keys():
            if not weechat.config_is_set_plugin(k):
                v = config[k]
                if type(v) is list:
                    v = str.join(',',v)
                weechat.config_set_plugin(k, v)
                weechat.config_set_desc_plugin(k,config_desc[k])
            stored = weechat.config_string(weechat.config_get(STRIP_VAR+k))
            if k == 'enable':
                if stored in ['on','off']:
                    if stored == 'on':
                        config[k] = True
                    else:
                        config[k] = False
                weechat.config_set_plugin(k,'on' if config[k] else 'off')
            if k == 'servers' or k == 'buffers':
                stored = stored.replace(' ','')
                lst = stored.split(',')
                config[k] = lst
                weechat.config_set_plugin(k,stored)
        return weechat.WEECHAT_RC_OK
    else:
        if option == 'enable':
            if value in ['on', 'off']:
                return weechat.WEECHAT_CONFIG_OPTION_SET_ERROR
            value = True if value == 'on' else False
            if config[option] != value:
                return_code = weechat.WEECHAT_CONFIG_OPTION_SET_OK_CHANGED
            config[option] = value
        elif option == 'servers' or option == 'buffers':
            value = value.replace(' ','')
            if value != weechat.config_string(weechat.config_get(STRIP_VAR+option)):
                return_code = weechat.WEECHAT_CONFIG_OPTION_SET_OK_CHANGED
            lst = value.split(',')
            config[option] = lst
        else:
            return_code = weechat.WEECHAT_CONFIG_OPTION_SET_ERROR
    return return_code

def main():
    at_config('load')
    # hook our config
    weechat.hook_config(STRIP_VAR+'*','at_config','')
    # hook the nick complete
    weechat.hook_command_run('/input complete_next', 'at_completion', '')
    # hook the /atcomplete
    weechat.hook_command('atcomplete','manage @nick completion plugin',
        '[enable|disable|toggle] '
        ' | [servers [list | add name | del name]]'
        ' | [buffers [list | add name | del name]]',
        'args desc',
        'status %-'
        ' || enable %-'
        ' || disable %-'
        ' || toggle %-'
        ' || server list|add|del %(buffers_names)'
        ' || buffer list|add|del %(buffers_names)'
        ,
        'at_control','')
    # hook the completetion for /atcomplete
    weechat.hook_completion('plugin_at_completion','@nick completion','at_complete','')

if weechat.register(SCRIPT_NAME, SCRIPT_AUTHOR, SCRIPT_VERSION,
                    SCRIPT_LICENSE, SCRIPT_DESC, "", "") :
    main()
