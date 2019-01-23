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


## Usage

``` 
gecrypt setkey mysecretkey             Set a secret key for encrypt/decrypt in current repo
gecrypt showkey                        Show secret key
gecrypt encrypt ./path_to_file         Encrypt a file
gecrypt decrypt ./path_to_file.sec     Decrypt a file
version                                Show version
help                                   Show help for commands
```

