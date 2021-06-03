# lpass-ssh
Lastpass SSH Key Loader

# Install

## Requirements
This tool requires two commands to be available in order to work.

`ssh-add` needs to be available. This should be included in your distro already.

`lpass`, the LastPass CLI must be installed. Most package repositories have the package `lastpass-cli` available. If not, consult [the official repository](https://github.com/lastpass/lastpass-cli)

## Install the CLI
Install directly from git:
```
pip install git+git://github.com/Xyaren/lpass-ssh.git@0.1#egg=lpass-ssh
```

# Usage
## Preparations
Add SSH Keys in the "SSH Keys" section within your LastPass Vault.<br>
![SSH Keys Section](https://i.imgur.com/dQXSOxU.png)

The only fields required are **Private Key** and **Passphrase**, if the private key is encrypted.
![Fields](https://i.imgur.com/gmpjhQ9.png)

## List available keys
```
lpass-ssh list --table
```
If you omit the `--table` argument, a simplified list will be printed to the console.

## Add all keys to the SSH-Agent.
Ensure the agent is running already.
```
lpass-ssh load
```
This will iterate through all Keys and add them to the ssh-agent.
