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

### 🔍 Explicação das Funções:

