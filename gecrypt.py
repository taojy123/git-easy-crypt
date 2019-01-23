#!/usr/bin/env python

import sys
import os
import time
import hashlib
import base64


PWD = os.getcwd()
PYVERSION = sys.version_info[:2]


py2 = py3 = False
if PYVERSION[0] == 2:
    py2 = True
    input = raw_input
else:
    py3 = True


HELP = """
Usage:   
  gecrypt setkey mysecretkey             Set a secret key for encrypt/decrypt in current repo.
  gecrypt showkey                        Show secret key.
  gecrypt encrypt ./path_to_file         Encrypt a file.
  gecrypt decrypt ./path_to_file.sec     Decrypt a file.
  help                                   Show help for commands.
"""


class GecryptError(Exception):
    def __init__(self, info=''):
        self.info = info + '\n'

    def __str__(self):
        return self.info


class NeedHelp(Exception):
    def __init__(self, info=''):
        if info:
            self.info = info + '\n' + HELP
        else:
            self.info = HELP

    def __str__(self):
        return self.info


def rc4(string, op='encode', secret='12345'):

    def md5(string):
        if py3 and isinstance(string, str):
            string = string.encode()
        return hashlib.md5(string)

    def b64encode(string):
        if py3 and isinstance(string, str):
            string = string.encode()
        reslut = base64.b64encode(string)
        if py3:
            reslut = reslut.decode()
        return reslut

    def b64decode(string):
        if py3 and isinstance(string, str):
            string = string.encode()
        reslut = base64.b64decode(string)
        if py3:
            reslut = reslut.decode()
        return reslut

    assert op in ['encode', 'decode'], 'op must be encode or decode not %s' % op

    if py2 and isinstance(string, unicode):
        string = string.encode('utf8')

    ckey_lenth = 4
    secret = secret and secret or ''
    key = md5(secret).hexdigest()
    keya = md5(key[0:16]).hexdigest()
    keyb = md5(key[16:32]).hexdigest()

    keyc = ckey_lenth and (op == 'decode' and string[0:ckey_lenth] or md5(str(time.time())).hexdigest()[
                                                                      32 - ckey_lenth:32]) or ''

    cryptkey = keya + md5(keya + keyc).hexdigest()
    key_lenth = len(cryptkey)

    string = op == 'decode' and b64decode(string[4:]) or '0000000000' + md5(string + keyb).hexdigest()[
                                                                        0:16] + string
    string_lenth = len(string)

    result = ''
    box = list(range(256))
    randkey = []

    for i in range(255):
        randkey.append(ord(cryptkey[i % key_lenth]))

    for i in range(255):
        j = 0
        j = (j + box[i] + randkey[i]) % 256
        tmp = box[i]
        box[i] = box[j]
        box[j] = tmp

    for i in range(string_lenth):
        a = j = 0
        a = (a + 1) % 256
        j = (j + box[a]) % 256
        tmp = box[a]
        box[a] = box[j]
        box[j] = tmp

        result += chr(ord(string[i]) ^ (box[(box[a] + box[j]) % 256]))

    if op == 'encode':

        return keyc + b64encode(result)
    else:

        if (result[0:10] == '0000000000' or int(result[0:10]) - int(time.time()) > 0) and result[10:26] == md5(
                result[26:] + keyb).hexdigest()[0:16]:
            return result[26:]
        else:
            return None


def check_git():
    gitdir = os.path.join(PWD, '.git')
    if not os.path.isdir(gitdir):
        raise GecryptError('You should execute this command in the git repo directory!')
    add_gitignore('.git-easy-crypt-key')


def add_gitignore(name):
    gitignore_path = os.path.join(PWD, '.gitignore')
    open(gitignore_path, 'a')
    content = open(gitignore_path, 'r').read().replace('\r\n', '\n').replace('\r', '\n')

    if '\n' + name + '\n' in '\n' + content + '\n':
        return

    comment = '# managed by git-easy-crypt'
    if comment in content:
        content = content.replace(comment, comment + '\n' + name)
        open(gitignore_path, 'w').write(content)
    else:
        open(gitignore_path, 'a').write('\n# managed by git-easy-crypt\n%s\n' % name)


def get_key(verbose=False, raise_exception=True):
    open('.git-easy-crypt-key', 'a')
    key = open('.git-easy-crypt-key', 'r').read().strip() or None

    if verbose:
        print('Get key from .git-easy-crypt-key is: %s' % key)

    if key:
        return key

    key = os.environ.get('GECRYPT_KEY') or None

    if verbose:
        print('Get key from environment variable `GECRYPT_KEY` is: %s' % key)

    if key:
        return key

    if raise_exception:
        raise GecryptError(
            'You must set the secret key first.\n'
            'Just like: gecrypt setkey mysecretkey\n'
            'or you can set the key in environment variable `GECRYPT_KEY`.\n')
    return


def main(args=None):
    if not args:
        args = sys.argv[1:]

    # print(args)
    try:
        if not args or 'help' in args:
            raise NeedHelp()

        check_git()

        action = args[0]

        if action == 'setkey':
            if len(args) < 2:
                raise NeedHelp('Please type the secret key')
            key = args[1]
            if not key:
                raise NeedHelp('Secret key can not in null')

            k = get_key(raise_exception=False)
            if k:
                print('The secret key is `%s` now, are you sure to rewrite it? [type `Y` to confirm]' % k)
                t = input().lower()
                if t != 'y':
                    print('Nothing changed')
                    return

            open('.git-easy-crypt-key', 'w').write(key)
            print('`%s` has saved in .git-easy-crypt-key' % key)

        elif action == 'showkey':
            key = get_key(True)
            print('The secret key is: %s' % key)

        elif action == 'encrypt':
            key = get_key()
            if len(args) < 2:
                raise NeedHelp('Please type the file path')
            path = args[1]
            if not os.path.isfile(path):
                raise GecryptError('File path `%s` is not found' % path)

            content = open(path).read()
            try:
                content_sec = rc4(content, 'encode', key)
            except Exception as e:
                raise GecryptError('Encrypt failed: %s' % e)

            path_sec = path + '.sec'
            open(path_sec, 'w').write(content_sec)
            add_gitignore(path)
            print('Encrypt success!\n'
                  'The secret code has been saved in `%s`\n'
                  'and `%s` is ignored by git.' % (path_sec, path))

        elif action == 'decrypt':
            key = get_key()
            if len(args) < 2:
                raise NeedHelp('Please type the file path')
            path_sec = args[1]
            if not os.path.isfile(path_sec):
                raise GecryptError('File path `%s` is not found' % path_sec)

            content_sec = open(path_sec).read()
            try:
                content = rc4(content_sec, 'decode', key)
            except Exception as e:
                raise GecryptError('Decrypt failed: %s' % e)

            if path_sec.endswith('.sec'):
                path = path_sec[:-4]
            else:
                path = path_sec

            open(path, 'w').write(content)
            print('Decrypt success!\n'
                  'The source code has been saved in %s.' % path)

        else:
            raise NeedHelp()

    except GecryptError as e:
        if e.info:
            sys.stderr.write(e.info)
        else:
            print(HELP)

    except NeedHelp as e:
        print(e)


if __name__ == '__main__':
    main()
