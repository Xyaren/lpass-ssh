import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Union, Generator, List

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.dsa import DSAPrivateKey
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed448 import Ed448PrivateKey
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey
from terminaltables import AsciiTable

from lpassssh import parse_args
from lpassssh.log import initialize_logging

REGEX_KEY = re.compile(r"(-----BEGIN RSA PRIVATE KEY-----.+-----END RSA PRIVATE KEY-----)", re.DOTALL)
REGEX_PASSPHRASE = re.compile(r"Passphrase:(.+)\nPrivate Key:", re.DOTALL)


@dataclass
class KeyEntry:
    name: str
    private_key: Union[Ed25519PrivateKey, Ed448PrivateKey, RSAPrivateKey, DSAPrivateKey, EllipticCurvePrivateKey]


def load(lastpass_entry: dict) -> Generator[KeyEntry, None, None]:
    fullname = lastpass_entry['fullname']
    secret_note = lastpass_entry['note']
    for ssh_key in REGEX_KEY.findall(secret_note):
        phrases = REGEX_PASSPHRASE.findall(secret_note) or []
        passphrase = phrases[0] if len(phrases) == 1 else None
        private_key = serialization.load_pem_private_key(ssh_key.encode(),
                                                         password=passphrase.encode() if passphrase else None)
        yield KeyEntry(name=fullname, private_key=private_key)


def startup():
    initialize_logging()
    config, parser = parse_args()

    if not check_installed("lpass"):
        eprint("lastpass-cli (lpass) needs to be installed on the system.")
        exit(1)
    elif not check_installed("ssh-add"):
        eprint("ssh-add needs to be installed on the system.")
        exit(1)

    ssh_keys = [entry for generator in load_lastpass_key_secret() for entry in load(generator)]

    if config.subparser_name == "list":
        if config.table:
            table_data = [
                ["Name", "Key Size", "Public Key"]
            ]
            for keyEntry in ssh_keys:
                public_key = keyEntry.private_key.public_key()
                public_key_openssh = public_key.public_bytes(
                    encoding=serialization.Encoding.OpenSSH,
                    format=serialization.PublicFormat.OpenSSH).decode()

                table_data.append([keyEntry.name, keyEntry.private_key.key_size, public_key_openssh])
            table = AsciiTable(table_data)
            print(table.table)
        else:
            print("\n".join(i.name for i in ssh_keys))
    elif config.subparser_name == "load":
        for entry in ssh_keys:
            load_key_to_agent(entry)


def load_key_to_agent(entry: KeyEntry):
    iprint(f"Loading \"{entry.name}\" ".ljust(79, ".")+" ")

    unencryped_private_key = entry.private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                                             format=serialization.PrivateFormat.TraditionalOpenSSL,
                                                             encryption_algorithm=serialization.NoEncryption()).decode()

    stdout, stderr = subprocess.Popen(['ssh-add', "-"], stdout=subprocess.PIPE, stdin=subprocess.PIPE,
                                      stderr=subprocess.PIPE, text=True).communicate(input=unencryped_private_key)
    if stderr == 'Could not add identity "(stdin)": agent refused operation\n':
        iprint("Already added\n")
    elif stderr == 'Identity added: (stdin) ((stdin))\n':
        iprint("Added.\n")
    else:
        iprint("Error: %s", stderr)


def load_lastpass_key_secret() -> List[dict]:
    result = subprocess.check_output(["lpass", "show", "-xjG", ".*"])
    all_entries = json.loads(result)
    ssh_keys = [a for a in all_entries if is_ssh_note(a)]
    return ssh_keys


def is_ssh_note(a):
    return "note" in a and "NoteType:SSH Key\n" in a["note"]


def check_installed(command: str) -> bool:
    rc = subprocess.call(['which', command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return rc == 0


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def iprint(*args, **kwargs):
    print(*args, file=sys.stdout, **kwargs, end="")


if __name__ == '__main__':
    startup()
