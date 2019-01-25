# git-easy-crypt

The easy way to encrypt/decrypt private files in the git repo.


## Install

you can install git-easy-crypt by pip:

```
$ pip install git-easy-crypt
```

or download the script directly:

```
$ sudo curl -o /usr/local/bin/gecrypt https://raw.githubusercontent.com/taojy123/git-easy-crypt/master/gecrypt.py 
$ sudo chmod a+x /usr/local/bin/gecrypt
```


---------------


## Usage

``` 
gecrypt setkey mysecretkey             Set a secret key for encrypt/decrypt in current repo
gecrypt setkey mysecretkey -y          Set a secret key without input yes
gecrypt showkey                        Show secret key
gecrypt encrypt file                   Encrypt a file (decrypt file to file.sec)
gecrypt encryptall                     Encrypt all decrypted files in current repo
gecrypt decrypt file.sec               Decrypt a file (decrypt file.sec to file)
gecrypt decrypt file.sec anther_file   Decrypt file.sec to anther_file
gecrypt decryptall                     Decrypt all encrypted files in current repo
gecrypt version                        Show version
gecrypt help                           Show help for commands
```


---------------


## Best Practice


### Alice, encrypt the secret files and push:

```
$ git clone https://github.com/taojy123/test
Cloning into 'test'...
...
Unpacking objects: 100% (3/3), done.
$ cd test

$ gecrypt setkey abc123
`abc123` has saved in .git-easy-crypt-key

$ echo MYSECRET=AAA > keys.txt
$ ls
README.md    keys.txt

$ gecrypt encrypt keys.txt 
Encrypt success!
The secret code has been saved in `keys.txt.sec`, and `keys.txt` is ignored by git.
You must keep the secret key `abc123` in mind for decrypt the file in the future!!!
$ ls
README.md    keys.txt     keys.txt.sec

$ git add .
$ git commit -m "add encrypted secret file"
[master 3d8ef6f] add encrypted secret file
 2 files changed, 5 insertions(+)
 create mode 100644 .gitignore
 create mode 100644 keys.txt.sec

$ git push
...
To https://github.com/taojy123/test
   4d86b27..3d8ef6f  master -> master
$ 
```


### Bob, pull and decrypt the secret files:

```
$ git clone https://github.com/taojy123/test
Cloning into 'test'...
...
Unpacking objects: 100% (7/7), done.
$ cd test

$ ls
README.md    keys.txt.sec

$ gecrypt setkey abc123
`abc123` has saved in .git-easy-crypt-key

$ gecrypt decryptall
`./keys.txt.sec` has been decrypted to `./keys.txt`.

$ ls
README.md    keys.txt     keys.txt.sec

$ cat keys.txt
MYSECRET=AAA 
$ 
```

