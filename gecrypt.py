#!/usr/bin/env python

import sys
import os
import time
import random
import base64


VERSION = '1.0.3'
PWD = os.getcwd()
PYVERSION = sys.version_info[:2]


if PYVERSION[0] == 2:
    input = raw_input


HELP = """
Usage:   
  gecrypt setkey mysecretkey             Set a secret key for encrypt/decrypt in current repo
  gecrypt setkey mysecretkey -y          Set a secret key without input yes
  gecrypt showkey                        Show secret key
  gecrypt encrypt file                   Encrypt a file (decrypt file to file.sec)
  gecrypt encryptall                     Encrypt all decrypted files in current repo
  gecrypt decrypt file.sec               Decrypt a file (decrypt file.sec to file)
  gecrypt decrypt file.sec anther_file   Decrypt file.sec to anther_file
  gecrypt decryptall                     Decrypt all encrypted files in current repo
  gecrypt registerhooks                  Register the git hooks
  gecrypt version                        Show version
  gecrypt help                           Show help for commands
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


def easy_b64_crypt(string, op='encode', key='1234'):
    """
    A simple encryption solution that is not strong
    """

    py2 = py3 = False
    if sys.version_info[0] == 2:
        py2 = True
    else:
        py3 = True

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

    if not string:
        return ''

    if py2 and isinstance(string, unicode):
        string = string.encode('utf8')

    key2 = b64encode(b64encode(key)).strip('=')
    key3 = b64encode(b64encode(b64encode(key))).strip('=')

    assert key2 and key3, key

    if op == 'encode':
        string = b64encode(string)

        if key2 in string:
            j = string.find(key2) + len(key2) - 1
        else:
            j = len(string)
        i = random.randint(0, j)
        string = string[:i] + key2 + string[i:]

        if key3 in string:
            j = string.find(key3) + len(key3) - 1
        else:
            j = len(string)
        i = random.randint(0, j)
        string = string[:i] + key3 + string[i:]

    else:

        string = string.replace(key3, '', 1)
        string = string.replace(key2, '', 1)
        string = b64decode(string)

    return string


def check_git():
    gitdir = os.path.join(PWD, '.git')
    if not os.path.isdir(gitdir):
        raise GecryptError('You should execute this command in the git repo directory!')
    add_gitignore('.git-easy-crypt-key')


def add_gitignore(name):
    gitignore_path = os.path.join(PWD, '.gitignore')
    open(gitignore_path, 'a')
    content = open(gitignore_path, 'r').read().replace('\r\n', '\n').replace('\r', '\n')

    if name.startswith('./'):
        name = name[2:]

    if '\n' + name + '\n' in '\n' + content + '\n':
        return

    comment = '# managed by git-easy-crypt'
    if comment in content:
        content = content.replace(comment, comment + '\n' + name)
        open(gitignore_path, 'w').write(content)
    else:
        open(gitignore_path, 'a').write('\n# managed by git-easy-crypt\n%s\n' % name)


def get_key(verbose=False, raise_exception=True):
    check_git()
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


def find_all_secret_files():
    rs = []
    for root, dirs, files in os.walk('.'):
        if '.git' in root:
            # skip the .git dir
            continue
        for file in files:
            if file.endswith('.sec'):
                path_sec = os.path.join(root, file)
                rs.append(path_sec)
    return rs


def main(args=None):
    if not args:
        args = sys.argv[1:]

    # print(args)
    try:
        if not args or 'help' in args or '--help' in args or '-h' in args:
            raise NeedHelp()

        action = args[0]

        # ========= setkey ===========
        if action == 'setkey':
            if len(args) < 2:
                raise NeedHelp('Please type the secret key')
            key = args[1]
            if not key:
                raise NeedHelp('Secret key can not in null')

            k = get_key(raise_exception=False)

            if len(args) > 2 and args[2] == '-y':
                force_yes = True
            else:
                force_yes = False

            if k and not force_yes:
                print('The secret key is `%s` now, are you sure to rewrite it? [type `Y` to confirm]' % k)
                t = input().lower()
                if t not in ['y', 'yes']:
                    print('Nothing changed')
                    return

            open('.git-easy-crypt-key', 'w').write(key)
            print('`%s` has saved in .git-easy-crypt-key' % key)

        # ========= showkey ===========
        elif action == 'showkey':
            key = get_key(verbose=True)
            print('The secret key is: %s' % key)

        # ========= encrypt ===========
        elif action == 'encrypt':
            key = get_key()
            if len(args) < 2:
                raise NeedHelp('Please type the file path')
            path = args[1]

            if path.endswith('.sec'):
                raise GecryptError('Can not encrypt a encrypted file')

            if not os.path.isfile(path):
                raise GecryptError('File path `%s` is not found' % path)

            try:
                content = open(path).read()
                content_sec = easy_b64_crypt(content, 'encode', key)
            except Exception as e:
                raise GecryptError('Encrypt failed: %s' % e)

            path_sec = path + '.sec'
            open(path_sec, 'w').write(content_sec)
            add_gitignore(path)
            print('Encrypt success!\n'
                  'The secret code has been saved in `%s`, and `%s` is ignored by git.\n'
                  'You must keep the secret key `%s` in mind '
                  'for decrypt the file in the future!!!' % (path_sec, path, key))

        # ========= encryptall ===========
        elif action == 'encryptall':
            key = get_key()
            for path_sec in find_all_secret_files():
                path = path_sec[:-4]
                try:
                    content = open(path).read()
                    content_sec = easy_b64_crypt(content, 'encode', key)
                except:
                    continue
                open(path_sec, 'w').write(content_sec)
                add_gitignore(path)
                print('`%s` has been encrypted to `%s`.' % (path, path_sec))

        # ========= decrypt ===========
        elif action == 'decrypt':
            key = get_key()
            if len(args) < 2:
                raise NeedHelp('Please type the file path')
            path_sec = args[1]
            if not os.path.isfile(path_sec):
                raise GecryptError('File path `%s` is not found' % path_sec)

            try:
                content_sec = open(path_sec).read()
                content = easy_b64_crypt(content_sec, 'decode', key)
            except Exception as e:
                raise GecryptError('Decrypt failed: %s' % e)

            if len(args) > 2:
                path = args[2]
            elif path_sec.endswith('.sec'):
                path = path_sec[:-4]
            else:
                path = path_sec

            open(path, 'w').write(content)
            add_gitignore(path)
            print('Decrypt success!\n'
                  'The source code has been saved in %s.' % path)

        # ========= decryptall ===========
        elif action == 'decryptall':
            key = get_key()
            for path_sec in find_all_secret_files():
                try:
                    content_sec = open(path_sec).read()
                    content = easy_b64_crypt(content_sec, 'decode', key)
                except:
                    continue
                path = path_sec[:-4]
                open(path, 'w').write(content)
                add_gitignore(path)
                print('`%s` has been decrypted to `%s`.' % (path_sec, path))

        # ========= registerall ===========
        elif action == 'registerall':
            check_git()

            hook = '.git/hooks/pre-commit'
            cmd = 'gecrypt encryptall'
            f = open(hook, 'a+')
            if cmd not in f.read():
                f.write('#!/bin/sh\n\n%s\n' % cmd)
            f.close()
            os.chmod(hook, 493)  # 755

            hook = '.git/hooks/post-update'
            cmd = 'gecrypt decryptall'
            f = open(hook, 'a+')
            if cmd not in f.read():
                f.write('#!/bin/sh\n\n%s\n' % cmd)
            f.close()
            os.chmod(hook, 493)  # 755

        # ========= version ===========
        elif action == 'version':
            print('Python version is: %s.%s' % PYVERSION)
            print('git-easy-crypt version is: %s' % VERSION)

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
