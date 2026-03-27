# SMB Pentest Automation Tool (Python)

### 📌 Visão Geral:

Este projeto é uma ferramenta de automação para auditoria e testes de segurança em serviços SMB (Server Message Block), desenvolvida em Python utilizando a biblioteca Impacket.
O objetivo do script é facilitar atividades de reconhecimento, enumeração de usuários, teste automatizado de credenciais, verificação de compartilhamentos (shares) e interação com sistemas Windows via SMB em ambientes controlados.

⚠️ <b>Aviso Legal:</b> Esta ferramenta deve ser utilizada exclusivamente em ambientes autorizados, laboratórios ou testes de segurança com permissão explícita. O uso indevido em sistemas sem autorização é ilegal e pode violar legislações locais e internacionais.

### ⚙️ Funcionalidades Principais:

- Teste automatizado de credenciais SMB baseado em wordlist (formato usuário:senha)
- Detecção de autenticação com senha vazia em contas comuns
- Enumeração de usuários locais/domínio via protocolo MS-SAMR (RPC)
- Tentativa de dump remoto de SAM e SYSTEM (dependente de privilégios administrativos)
- Listagem de compartilhamentos SMB com verificação de permissões
- Interface interativa para navegação em compartilhamentos (pseudo-shell SMB)
- Upload e download de arquivos via SMB
- Execução paralela de tentativas de login utilizando múltiplas threads
- Autocomplete básico no terminal interativo

### 🧠 Arquitetura Geral:

O script é estruturado em módulos independentes que interagem com sessões SMB ativas quando necessário:

- Camada de autenticação SMB
- Camada de enumeração (usuários e shares)
- Camada de exploração (acesso a arquivos e tentativa de dump de credenciais locais)
- Interface interativa (shell SMB simplificada)
- Motor de execução concorrente (ThreadPoolExecutor)

### 📦 Dependências:
    Python 3.x
    Impacket
    readline
    pip install impacket
    OU
    python3 -m pip install impacket --break-system-packages

### 🚀 Como usar:
    python3 smbscript.py

### O sistema solicitará:

- IP do alvo
- Número de threads

### Em seguida, o fluxo automático inicia:

- Teste de autenticação com senha vazia
- Enumeração de usuários (quando possível)
- Listagem de shares SMB
- Execução de brute force baseado em wordlist

## ⚙️ Funcionalidades

### 📦 format_size(size)
Converte valores em bytes para um formato legível.

**Exemplo:**

    1024 → 1.0 KB
    1048576 → 1.0 MB


---

### 🔧 normalize_smb_path(path, file)
Normaliza caminhos SMB garantindo formatação correta com barras invertidas (`\`).

**Função:**
- Evita erros de concatenação de paths em operações SMB
- Garante compatibilidade com compartilhamentos Windows

---

### 👤 enum_users(target, username, password)
Realiza enumeração de usuários via protocolo **MS-SAMR (RPC)**.

**Processo técnico:**
- Conexão via SMBTransport
- Abertura de sessão DCE/RPC
- Enumeração de domínios disponíveis
- Listagem de usuários do domínio

**Observação:**
Pode falhar dependendo de permissões e políticas de segurança do host remoto.

---

### 🧬 dump_sam(conn, username, password)
Tenta realizar a extração remota das bases **SAM** e **SYSTEM**.

**Dependências críticas:**
- Privilégios administrativos no host remoto
- Acesso ao registro via RPC/SMB

**Processo:**
- Habilita acesso remoto ao registry
- Exporta hives SAM e SYSTEM
- Processa hashes localmente via Impacket

⚠️ **Importante:**
A funcionalidade depende fortemente de permissões elevadas e pode não funcionar em todos os ambientes.

---

### 📂 listar_shares(conn, user)
Lista compartilhamentos SMB disponíveis no host alvo e valida permissões.

**Processo:**
- Enumera shares via SMB
- Testa leitura (`listPath`)
- Testa escrita (`putFile` + `deleteFile`)

**Classificação de permissões:**
- READ/WRITE
- READ
- WRITE
- NO ACCESS

---

### 🧭 smb_shell(conn, user)
Interface interativa para exploração de compartilhamentos SMB.

**Tipo de interface:**
Pseudo-shell para navegação remota

**Comandos disponíveis:**
- `ls` → lista arquivos e diretórios
- `cd` → navegação entre diretórios
- `pwd` → exibe diretório atual
- `download` → baixa arquivos
- `upload` → envia arquivos
- `exit / quit` → encerra sessão

---

### 🔐 try_login(user, password)
Realiza tentativa de autenticação SMB.

**Fluxo:**
- Tentativa de login via SMBConnection
- Em caso de sucesso:
  - Exibe credencial válida
  - Executa enumeração de usuários (quando possível)
  - Tenta dump de SAM

---

### 🚪 detect_empty_password()
Testa autenticação com senha vazia em usuários comuns.

**Usuários testados:**
- admin
- administrator
- guest
- user

**Comportamento:**
Se autenticado com sucesso:
- Lista shares disponíveis
- Abre shell SMB automaticamente

---

### ⚙️ worker(user, password)
Wrapper para execução paralela de login.

**Função:**
- Executado em threads
- Encapsula `try_login`

---

### 🚀 main()
Função principal da ferramenta.

**Fluxo completo:**
1. Teste de senha vazia
2. Leitura da wordlist
3. Construção de credenciais (`user:password`)
4. Execução de brute force com múltiplas threads

---

## ⚡ Performance

A ferramenta utiliza:

- `ThreadPoolExecutor` para concorrência
- Timeout em conexões SMB
- Execução paralela de tentativas de login

👉 Isso garante alta performance em ambientes de teste controlados.

---

## 🛡️ Segurança e Boas Práticas

⚠️ Esta ferramenta deve ser usada **somente em ambientes autorizados**.

- Não utilize contra sistemas sem permissão explícita
- Voltada exclusivamente para aprendizado e auditoria de segurança
- Pode gerar tráfego detectável por IDS/IPS

---

## 📌 Autor

**Nanoxsec**  
Instagram: [@eulucas.97](https://instagram.com)

---

## 🧪 Possíveis Melhorias Futuras

- Exportação de resultados em JSON/YAML
- Integração com proxies SOCKS
- Detecção automática de vulnerabilidades SMB (CVEs)
- Interface TUI (Terminal User Interface)
- Logging estruturado (INFO, WARN, ERROR)
- Módulo de relatórios pós-execução

