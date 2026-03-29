# CLAUDE.md — THApp
> Instruções técnicas para o Claude Code
> Projeto: THApp — Consultor Social de História da Família
> Autor: Felipe A. Wolff | GitHub: felipeawolff-hue
> Repositório: github.com/felipeawolff-hue/thapp

---

## 🧭 O que é este projeto

THApp é uma plataforma social gamificada para consultores de História da Família (THF) da Igreja de Jesus Cristo dos Santos dos Últimos Dias. Integra com o site FamilySearch via Playwright (scraping autenticado), possui sistema de coins/XP, conquistas (badges), feed social e ranking por ala/estaca.

**Documento de visão completo:** `docs/THAPP_PROJECT.md`

---

## 🗂️ Estrutura de Pastas

```
thapp/
├── CLAUDE.md                  # Este arquivo
├── docs/
│   └── THAPP_PROJECT.md       # Documento de visão e regras de negócio
├── backend/                   # FastAPI (Python)
│   ├── main.py                # Entrada da aplicação
│   ├── routers/               # Endpoints por domínio
│   │   ├── auth.py            # Login Google OAuth + Supabase
│   │   ├── users.py           # Perfil, coins, XP, rank
│   │   ├── conquistas.py      # Badges e conquistas
│   │   ├── atividades.py      # Log de atividades e coins
│   │   ├── desafios.py        # PvP e coletivos
│   │   ├── loja.py            # Marketplace de coins
│   │   ├── alas.py            # Grupos por ala/estaca
│   │   └── admin.py           # Funções do líder
│   ├── services/
│   │   ├── familysearch.py    # Playwright worker (scraping FS)
│   │   ├── coins.py           # Lógica de coins/XP/streak
│   │   ├── conquistas.py      # Engine de unlock de badges
│   │   └── notificacoes.py    # Firebase FCM push notifications
│   ├── models/                # Schemas Pydantic
│   ├── db/
│   │   └── supabase.py        # Cliente Supabase
│   ├── scheduler.py           # Sync diário agendado (APScheduler)
│   ├── requirements.txt
│   └── .env.example
├── mobile/                    # React Native (Expo)
│   ├── app/                   # Expo Router (file-based routing)
│   │   ├── (tabs)/
│   │   │   ├── feed.tsx       # Timeline de atividades
│   │   │   ├── ranking.tsx    # Leaderboard
│   │   │   ├── conquistas.tsx # Grade de badges
│   │   │   └── perfil.tsx     # Perfil do usuário
│   │   ├── ala/               # Grupo da ala
│   │   ├── loja/              # Marketplace
│   │   ├── sync/              # Status FamilySearch
│   │   └── admin/             # Telas do líder
│   ├── components/
│   ├── hooks/
│   ├── services/
│   │   └── api.ts             # Chamadas ao backend
│   ├── package.json
│   └── .env.example
└── web/                       # Next.js (PWA) — espelho web do mobile
    ├── app/
    ├── components/
    ├── package.json
    └── .env.example
```

---

## ⚙️ Stack Técnico

| Camada | Tecnologia | Versão mínima |
|--------|-----------|--------------|
| Backend | FastAPI (Python) | 3.11+ |
| Scraping | Playwright (Python) | latest |
| Banco | Supabase (PostgreSQL) | — |
| Mobile | React Native + Expo | SDK 51+ |
| Web | Next.js | 14+ |
| Notificações | Firebase FCM | — |
| Hospedagem backend | Render | — |
| Hospedagem web | Vercel | — |

---

## 🚀 Comandos Essenciais

### Backend
```bash
# Instalar dependências
cd backend
pip install -r requirements.txt

# Instalar Playwright e browsers
playwright install chromium

# Rodar localmente
uvicorn main:app --reload --port 8000

# Rodar scheduler (sync FamilySearch)
python scheduler.py
```

### Mobile
```bash
cd mobile
npm install

# Rodar no Android
npx expo run:android

# Rodar no Expo Go (teste rápido)
npx expo start
```

### Web
```bash
cd web
npm install
npm run dev      # desenvolvimento
npm run build    # produção
```

---

## 🔐 Variáveis de Ambiente

### Backend (`backend/.env`)
```env
# Supabase
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_KEY=xxxx

# Google OAuth
GOOGLE_CLIENT_ID=xxxx
GOOGLE_CLIENT_SECRET=xxxx

# Firebase FCM
FIREBASE_CREDENTIALS_JSON=xxxx

# Segurança
SECRET_KEY=xxxx                    # JWT signing
FS_ENCRYPTION_KEY=xxxx             # Criptografia dos tokens FamilySearch

# Ambiente
ENVIRONMENT=development            # development | production
```

### Mobile/Web (`mobile/.env` e `web/.env`)
```env
EXPO_PUBLIC_API_URL=http://localhost:8000
EXPO_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=xxxx
```

---

## 🗄️ Banco de Dados (Supabase)

**Projeto:** conta Google dedicada THApp (separada do Jarvis)

### Tabelas principais
```sql
users               -- perfil, coins, xp, streak, token FS criptografado
conquistas          -- catálogo de badges (pb_url + color_url)
usuarios_conquistas -- badges desbloqueados por usuário
atividades          -- log de coins/xp ganhos
ajudados            -- pessoas que o consultor ajuda (consentimento)
fs_syncs            -- dados coletados do FamilySearch por sync
desafios            -- PvP e coletivos
desafios_part.      -- progresso por participante
loja_itens          -- itens digitais e físicos
resgates            -- histórico de resgates
alas / estacas      -- estrutura da Igreja
notificacoes        -- log de push notifications
```

### Políticas RLS importantes
- Usuário só acessa próprios dados pessoais
- Dados de ajudados: só visíveis para o consultor responsável
- Dados agregados de ala: visíveis para todos os membros da ala
- Admin da ala acessa dados agregados (nunca individuais sensíveis)

---

## 🕷️ FamilySearch Scraping (Playwright)

**Arquivo:** `backend/services/familysearch.py`

### Fluxo de autenticação
1. Usuário fornece credenciais FS no app (uma vez)
2. Backend faz login via Playwright e extrai cookie/sessão
3. Sessão é criptografada com `FS_ENCRYPTION_KEY` e salva em `users.fs_session_token_enc`
4. Syncs futuros reutilizam a sessão — sem precisar das credenciais novamente
5. Se sessão expirar: app solicita reautenticação ao usuário

### Função Ajudante
```python
# Fluxo:
# 1. Carregar sessão do consultor
# 2. Navegar para familysearch.org/helper
# 3. Entrar no modo Ajudante com ID do ajudado
# 4. Extrair dados: ordenanças, nomes, árvore, recordações
# 5. Sair do modo Ajudante
# 6. Salvar em fs_syncs com ajudado_id
```

> **ATENÇÃO:** Antes de implementar o scraping de uma nova página do FamilySearch,
> inspecionar os elementos HTML e documentar os seletores em `docs/fs_selectors.md`

### Dados extraídos por sync
- `ordenancas`: lista com tipo e data
- `nomes_templo_count`: total de nomes enviados
- `registros_arvore_count`: registros adicionados
- `recordacoes_count`: memórias adicionadas
- `geracoes_completas`: boolean (4 gerações preenchidas)
- `indexacoes_count`: revisões de indexação (Participe)

---

## 💰 Sistema de Coins e XP

**Arquivo:** `backend/services/coins.py`

### Regras fundamentais
- **Coins**: saldo atual — pode ser gasto na loja
- **XP**: histórico total — nunca diminui — determina o rank
- Toda ação gera ambos (proporcionais)
- Streak diário: multiplica coins do dia (não o XP)

### Engine de unlock de badges
**Arquivo:** `backend/services/conquistas.py`

- Roda após cada sync do FamilySearch e após cada ação no app
- Compara dados do usuário com `threshold_valor` de cada conquista
- Se atingiu: insere em `usuarios_conquistas` e dispara notificação push
- Badge fica colorido no frontend após unlock

---

## 🔔 Notificações Push

**Arquivo:** `backend/services/notificacoes.py`
**Tecnologia:** Firebase FCM

### Gatilhos
| Evento | Mensagem |
|--------|---------|
| Streak em risco | "Seu streak de X dias está em risco! Faça uma atividade hoje." |
| Badge desbloqueado | "Você desbloqueou a conquista: [nome]! 🎉" |
| Subiu no ranking | "Você subiu para a posição #X no ranking da ala!" |
| Desafio recebido | "[Nome] te desafiou: [descrição]" |
| Meta coletiva atingida | "Sua ala atingiu a meta! [descrição]" |
| Prêmio disponível | "Você tem um prêmio para resgatar na loja!" |

---

## 👥 Hierarquia de Acesso (Roles)

```python
# Roles no Supabase (campo users.tipo)
"pesquisador"    # não-membro, acesso mínimo
"membro"         # membro da Igreja, dashboard básico
"multiplicador"  # membro que ajuda outros
"consultor"      # consultor THF aprovado
"lider"          # líder de ala ou estaca — acesso admin
```

### Verificação de consultor
- Usuário solicita upgrade para consultor no app
- Lider da ala recebe notificação
- Lider aprova via painel admin
- Backend atualiza `users.tipo` e `users.aprovado_por`

---

## 🎨 Design e Frontend

- **Cores:** Verde `#4CAF50` (primária), Teal `#00897B` (secundária), Âmbar `#FFC107` (coins)
- **Badges:** sempre carregar versão P&B (`icone_pb_url`) e trocar por colorido (`icone_color_url`) ao desbloquear — com animação
- **Tom:** sempre positivo — sem mensagens de fracasso ou punição
- **Animações prioritárias:** unlock de badge, subida de rank, meta coletiva atingida

---

## 🚫 O que NÃO fazer

- **Nunca** armazenar senha do FamilySearch em texto puro — sempre criptografado
- **Nunca** expor dados individuais de ajudados no feed ou ranking
- **Nunca** remover XP do usuário (só coins podem ser gastos)
- **Nunca** rodar scraping sem consentimento registrado em `ajudados.consentimento_em`
- **Nunca** misturar com o projeto Jarvis — bancos, contas e repositórios são separados
- **Nunca** commitar arquivos `.env` — usar `.env.example` como referência

---

## 📌 Contexto Importante

- Testado inicialmente com consultores da **Estaca Guarulhos Brasil Cumbica** (SP, Brasil)
- A Estaca tem 8 alas + 1 ramo — dados reais disponíveis em `docs/relatorio_estaca_2026.md`
- O modelo de pontuação é baseado na **Gincana THF Alvarenga** — ver `docs/gincana_thf.md`
- Relatório do FamilySearch mostra KPIs reais que o app vai gamificar

---

*Claude Code: leia este arquivo antes de qualquer tarefa neste projeto.*
*Em caso de dúvida sobre regras de negócio, consulte `docs/THAPP_PROJECT.md`.*
