# THApp — Consultor Social de História da Família
> Documento de Visão e Especificação do Projeto
> Versão: 0.2 (Estruturado e Validado)
> Autor: Felipe A. Wolff
> GitHub: felipeawolff-hue
> Status: 🟢 Pronto para desenvolvimento

---

## 📌 Visão Geral

**THApp** (também escrito T.H.App — nome interno da comunidade) é uma plataforma social gamificada para consultores de História da Família (THF) da Igreja de Jesus Cristo dos Santos dos Últimos Dias.

O app combina:
- **Rede social** com feed de atividades e grupos por ala/estaca
- **Gamificação** com conquistas (badges), coins, streaks e ranking
- **Integração automática** com o FamilySearch via Selenium (scraping autenticado)
- **Digitalização de gincanas** — o modelo de pontuação da gincana THF serve de base para o sistema de recompensas

O objetivo é **engajar consultores, membros e líderes** no trabalho de história da família, tornando o processo atrativo e progressivo — especialmente para o público jovem (18–30 anos).

---

## 🎯 Objetivos do Projeto

- App Android + plataforma web standalone (separado do Jarvis)
- Banco de dados e conta Google dedicados (novo projeto Supabase)
- Hospedagem via GitHub `felipeawolff-hue` (Render/Vercel)
- Projeto de portfólio para Upwork (nicho: AI Automation + App Development)
- Testado inicialmente com consultores reais da Estaca Guarulhos Brasil Cumbica

---

## 📊 KPIs Reais do FamilySearch (Base para o App)

Estes são os indicadores que o FamilySearch já reporta por ala/estaca e que o THApp vai gamificar:

| KPI | O que mede | Fonte |
|-----|-----------|-------|
| Membros que enviaram nomes ao templo | Qtd. de membros com ≥1 nome enviado no ano | Relatório estaca |
| 4 gerações na árvore familiar | % de membros com 4 gerações preenchidas | Relatório estaca |
| Membros acessando o FamilySearch | Qtd. com login ativo no período | Relatório estaca |
| Antepassados acrescentados | Qtd. de registros novos na árvore | Relatório estaca |
| Recordações acrescentadas | Fotos/documentos adicionados | Relatório estaca |
| Indexadores ativos | Membros fazendo revisão de indexação | Relatório estaca |

> **Exemplo real da Estaca Cumbica (2026):** 93 de 2.724 membros participando — 45 nomes enviados em janeiro, 93 em fevereiro. O THApp visa mover esse número coletivamente.

---

## 👥 Hierarquia de Usuários

### 🔵 Membro (Pesquisador)
- Dashboard pessoal simplificado
- Acompanha próprio progresso no FamilySearch
- Pode se tornar **Multiplicador** ao ajudar outros membros
- Cadastro obrigatório via conta Google + dados complementares

### 🟡 Multiplicador
- Membro que passou a auxiliar outros (via função Ajudante)
- Herda pontos de quem ajuda (como na gincana: `d¹`)
- Interface semelhante ao consultor, sem todas as funções admin

### 🟢 Consultor de THF
- Acesso completo à função Ajudante do FamilySearch
- Dashboard completo: pessoas ajudadas, ordenanças, progresso por ajudado
- Pode criar desafios PvP entre consultores
- Acesso ao ranking da estaca
- **Verificação:** aprovação manual pelo administrador da ala/estaca

### 🔴 Líder (Ala / Estaca) — App Separado
- Painel administrativo com visão agregada (sem expor dados individuais)
- Cria metas coletivas e desafios para grupos
- Aprova novos consultores
- Acessa relatórios comparáveis ao do FamilySearch (gráficos por período)
- Vê dados consolidados: totais por ala, progresso coletivo, ranking

---

## 🏆 Sistema de Conquistas (Badges / Achievements)

Os badges aparecem em **preto e branco** no perfil até serem desbloqueados — quando ficam **coloridos com animação de unlock**. Termo usado no app: **"conquistas"** (linguagem de games).

| Badge | Nome da Conquista | Ícone | Como Desbloquear |
|-------|------------------|-------|-----------------|
| FamilySearch Ativo | Conta Conectada | 🌳 Árvore cinza→verde | Conectar conta FamilySearch ao THApp |
| Conta SUD | Membro Verificado | ⛪ Igreja azul | Vincular número de membro SUD |
| Consultor THF | Consultor | 🪪 Cartão azul | Aprovação pelo admin da ala |
| Ajudante | Ajudante | 🔴 Boia | Usar função Ajudante 1ª vez (consentimento registrado) |
| Nome Impresso | Papeleta | 📄 (a definir) | Imprimir X nomes (regra a definir) |
| Nome ao Templo | Templo | 🏛️ Templo verde | Enviar X nomes ao templo |
| 4 Gerações | Raízes | 🌳 (a definir) | Preencher 4 gerações na árvore |
| Recordação | Memória | 🌳 Árvore verde app | Adicionar X recordações no FamilySearch |
| Participe | Indexador | 🌳 Árvore azul | Completar X revisões de indexação |

> **TODO:** Definir thresholds numéricos de cada badge com líderes da ala
> **Nota:** O nome "badge" pode aparecer no app como "conquista", "selo" ou "troféu" — a definir com teste de usabilidade com jovens

---

## 💰 Sistema de Coins e Conquistas

### Coins vs. XP
- **Coins**: moeda do app — acumula, gasta na loja, aparece no ranking
- **XP**: pontuação de nível — só sobe, nunca desce, determina o rank
- São **separados**: XP reflete histórico total, Coins são o saldo atual

### Fontes de Coins — Via FamilySearch (Scraping Selenium)

| Ação | Coins | Observação |
|------|-------|-----------|
| Ordenança completada registrada | +50 | Detectado no sync |
| Nome enviado para o templo | +30 | Por nome |
| Registro adicionado à árvore | +10 | Por registro |
| 4ª geração preenchida | +80 | Marco único |
| Recordação adicionada | +15 | Por recordação |
| Sessão de Ajudante realizada | +20 | Por sessão |
| Meta de pessoas ajudadas atingida | +100 | Por meta |

### Fontes de Coins — Via App (Atividade Direta)

| Ação | Coins | Observação |
|------|-------|-----------|
| Login diário | +5 | Streak multiplica (ver abaixo) |
| Indexação (Participe) | +1 por nome | Atividade diária contínua |
| Completar tarefa criada pelo líder | +25 | Desafio coletivo |
| Aceitar desafio PvP | +15 | Ao aceitar |
| Completar desafio PvP | +60 | Ao vencer |
| Convidar membro que se cadastra | +40 | Multiplicador ativado |
| Membro convidado completa 1ª conquista | +25 | Bônus do multiplicador |

### Pontuação por Perfil (Base da Gincana — adaptado)

| Perfil | Multiplicador base |
|--------|--------------------|
| Jovem (18–30) | 1.0x |
| Adulto (31+) | 1.0x |
| Membro Novo (0–1 ano) | 1.3x |
| Pesquisador (não-membro) | 1.3x |
| Multiplicador | herda pts do ajudado |
| Consultor | herda pts do ajudado |

### Sistema de Streak
- Streak diário: bônus crescente a cada dia consecutivo
- Streak semanal: bônus especial ao completar 7 dias
- **Proteção de streak** (tipo Duolingo): o usuário pode "congelar" o streak uma vez por semana para não perder

### Penalidade por Inatividade
- Sem atividade por 7 dias: notificação de alerta
- Sem atividade por 14 dias: streak zerado
- **Nunca perde XP ou badges** — só perde streak e bônus futuros

---

## 🎖️ Níveis / Ranks

| Rank | XP necessário | Ícone |
|------|--------------|-------|
| Semente | 0–199 | 🌱 |
| Broto | 200–499 | 🌿 |
| Árvore Jovem | 500–999 | 🌳 |
| Árvore Plena | 1.000–2.499 | 🌲 |
| Raízes Fundas | 2.500–4.999 | 🏔️ |
| Ancestral | 5.000+ | 👑 |

> **TODO:** Revisar nomes dos ranks com consultores jovens — devem soar modernos sem perder o contexto THF

---

## 🛍️ Loja de Coins (Marketplace)

### Recompensas Digitais
- Molduras de perfil exclusivas (por rank ou conquista especial)
- Skins de badges animados
- Efeitos de perfil (partículas, brilhos)
- Troféus decorativos no perfil
- Emojis/reações exclusivas no feed

### Premiações Físicas (Coordenadas pelo Líder)
- Certificados digitais emitidos pelo líder
- Prêmios físicos gerenciados pelo admin da ala
- O app notifica o líder quando um membro acumula pontos suficientes para resgatar

> **Fluxo:** membro acumula coins → resgata na loja → se for prêmio físico, líder recebe notificação → confirma entrega no app

---

## 📱 Funcionalidades Sociais

### Feed de Atividades (Timeline)
- Conquistas recentes de consultores da mesma ala/estaca
- Ex: *"João Souza desbloqueou 'Nome ao Templo' 🏛️"*
- Ex: *"Maria completou desafio: 10 nomes esta semana! 🎉"*
- Interações: curtir, comentar, parabenizar
- Tom: sempre positivo e encorajador — sem toxicidade

### Ranking / Leaderboard
- Filtros: Semanal / Mensal / Geral
- Recortes: Minha Ala / Minha Estaca / Global
- Top 3 com visual especial (animação de pódio)
- Estratégia jovem: confete, troféus animados, notificação de "você subiu no ranking!"

### Desafios
- **PvP:** consultor desafia outro ("Quem envia mais nomes essa semana?")
- **Coletivo:** líder cria desafio para a ala inteira
- Campos: prazo, meta numérica, coins apostados/premiados
- Progresso em tempo real no feed

### Grupos por Ala/Estaca
- Grupo automático criado para cada ala cadastrada
- Canal de avisos do líder (somente líderes postam)
- Metas coletivas com barra de progresso visual compartilhada
- Ex: *"Ala Santos Dumont — Meta de março: 50 nomes ao templo — [███████░░░] 68%"*

---

## 🔗 Integração com FamilySearch (Selenium/Playwright)

### Estratégia de Autenticação (Híbrida)
1. Usuário faz login com credenciais FamilySearch **uma vez** no app
2. Backend armazena token/sessão com criptografia (nunca texto puro)
3. Servidor roda o Selenium usando essa sessão autenticada
4. Para dados do ajudado: consultor autentica e o Selenium acessa via **função Ajudante** nativa do FamilySearch

### Biblioteca Técnica
- **Playwright** (preferível ao Selenium puro — mais estável e moderno)
- Modo headless (sem abrir janela)
- Worker assíncrono rodando no backend

### Dados Coletados por Sync

**Conta pessoal do usuário:**
- Ordenanças completadas (tipo e data)
- Nomes enviados para o templo
- Registros na árvore genealógica
- Recordações adicionadas
- Status de 4 gerações preenchidas
- Atividade de indexação (Participe)

**Via função Ajudante (com consentimento):**
- Os mesmos dados acima, porém da conta do ajudado
- Dados nunca expostos publicamente — apenas visíveis para o consultor e agregados para o líder

### Frequência de Sync
- **Manual:** botão "Sincronizar agora"
- **Automático:** 1x por dia (em background, horário configurável)

### Ética e Privacidade
- Consentimento explícito registrado no app (com timestamp) antes de qualquer acesso
- Ajudado pode revogar consentimento a qualquer momento
- Dados individuais nunca aparecem no feed ou ranking
- Senhas/tokens com criptografia — nunca em texto puro

---

## 📋 Cadastro Obrigatório (Campos)

```
Cadastro via Google (OAuth) — dados básicos automáticos
Campos obrigatórios adicionais:
  - Nome completo
  - Número de membro (SUD)
  - Ala (seleção do banco de alas cadastradas)
  - Data de nascimento
  - WhatsApp (número)
  - E-mail (confirmado via Google)

Campo opcional:
  - Foto de perfil (ou usa foto do Google)
```

---

## 🔔 Notificações Push

São mensagens enviadas pelo app mesmo quando o usuário não está com o app aberto.

**Quando enviar:**
- Streak em risco (ex: "Você não fez atividade hoje — seu streak de 7 dias está em risco!")
- Nova conquista desbloqueada
- Subiu no ranking
- Desafio recebido de outro consultor
- Meta coletiva da ala atingida
- Líder postou aviso no grupo
- Prêmio disponível para resgate

**Tecnologia:** Firebase Cloud Messaging (FCM) — gratuito, funciona em Android e iOS

---

## 🏗️ Arquitetura Técnica

```
┌──────────────────────────────────────────────────────────┐
│                      THApp Frontend                      │
│           Android — React Native (Expo)                  │
│                + Web — Next.js (PWA)                     │
└────────────────────────┬─────────────────────────────────┘
                         │ HTTPS REST + WebSocket
┌────────────────────────▼─────────────────────────────────┐
│                      THApp Backend                       │
│                   FastAPI (Python)                       │
│              Render (free tier) via GitHub               │
└──────┬──────────────────────────────┬────────────────────┘
       │                              │
┌──────▼──────┐           ┌───────────▼──────────────────┐
│  Supabase   │           │   Playwright Worker           │
│ PostgreSQL  │           │   (Python assíncrono)         │
│ (nova conta)│           │   roda no backend             │
│ + Auth      │           │   sessão criptografada        │
│ + Storage   │           │   FamilySearch → banco        │
└─────────────┘           └──────────────────────────────┘
                                        │
                          ┌─────────────▼──────────────┐
                          │      FamilySearch.org       │
                          │  (login + função Ajudante)  │
                          └────────────────────────────┘
```

### Stack Definitivo

| Camada | Tecnologia | Motivo |
|--------|-----------|--------|
| Mobile | React Native (Expo) | JS familiar, build simplificado |
| Web | Next.js (PWA) | Plataforma web + portfólio |
| Backend | FastAPI (Python) | Domina, integra bem com Playwright |
| Banco | Supabase (nova conta) | PostgreSQL, Auth e Storage incluídos |
| Scraping | Python + Playwright | Mais estável que Selenium |
| Notificações | Firebase FCM | Gratuito, Android + iOS |
| Hospedagem | Render (backend) + Vercel (web) | Free tier, deploy via GitHub |

---

## 🗂️ Banco de Dados (Esquema)

```sql
-- Usuários
users (
  id, nome, email, google_id,
  tipo: pesquisador|membro|multiplicador|consultor|lider,
  ala_id, numero_membro, data_nascimento, whatsapp,
  foto_url, coins, xp, streak_dias, ultimo_acesso,
  fs_session_token_enc, -- token criptografado do FamilySearch
  criado_em, aprovado_em, aprovado_por
)

-- Conquistas (badges)
conquistas (id, nome, descricao, icone_pb_url, icone_color_url, threshold_tipo, threshold_valor)
usuarios_conquistas (user_id, conquista_id, desbloqueado_em)

-- Log de Atividades / Coins
atividades (id, user_id, tipo, coins_ganhos, xp_ganho, descricao, fonte: app|familysearch, criado_em)

-- Pessoas Ajudadas (com consentimento)
ajudados (
  id, consultor_id, nome_ajudado, fs_id_ajudado,
  consentimento_em, revogado_em, ativo
)

-- Sincronizações FamilySearch
fs_syncs (
  id, user_id, ajudado_id,
  ordenancas_json, nomes_templo_count, registros_arvore_count,
  recordacoes_count, geracoes_completas, indexacoes_count,
  criado_em
)

-- Desafios
desafios (id, criador_id, tipo: pvp|coletivo, meta_tipo, meta_valor, prazo, coins_premio, status)
desafios_participantes (desafio_id, user_id, progresso, finalizado_em, venceu)

-- Loja
loja_itens (id, nome, descricao, tipo: digital|fisico, custo_coins, icone_url, ativo)
resgates (id, user_id, item_id, status: pendente|confirmado, criado_em, confirmado_por)

-- Estrutura Igreja
estacas (id, nome, pais, estado)
alas (id, nome, estaca_id)

-- Notificações
notificacoes (id, user_id, tipo, titulo, corpo, lida, criado_em)
```

---

## 🎨 Identidade Visual

- **Nome:** THApp / T.H.App
- **Estilo:** Colorido, vibrante, gamificado — Habitica + Duolingo
- **Cor primária:** Verde (`#4CAF50` — derivado FamilySearch)
- **Cor secundária:** Teal/Azul (identidade da Igreja)
- **Cor destaque:** Âmbar/Dourado (para coins e conquistas especiais)
- **Badges:** P&B → coloridos com animação de unlock ao desbloquear
- **Tom:** Sempre positivo, encorajador — nunca punitivo
- **Público:** Jovens (18–30) como foco de engajamento, funcional para 40–60

### Telas Principais (a prototipar)
1. **Perfil** — foto, rank, badges, coins, XP, streak
2. **Feed** — timeline de atividades da ala
3. **Ranking** — leaderboard com filtros
4. **Conquistas** — grade de badges P&B/coloridos
5. **Minha Ala** — grupo, meta coletiva, avisos do líder
6. **FamilySearch Sync** — status da conexão, último sync, botão manual
7. **Loja** — itens digitais e premiações
8. **Admin (Líder)** — painel agregado, aprovações, criação de desafios

---

## 📋 Roadmap de Execução

### Fase 0 — Fundação
- [ ] Fechar e validar este documento
- [ ] Criar conta Google dedicada THApp
- [ ] Criar projeto Supabase novo (conta dedicada)
- [ ] Criar repositório GitHub `thapp` em `felipeawolff-hue`
- [ ] Definir thresholds numéricos dos badges com líderes da ala

### Fase 1 — Backend Core
- [ ] FastAPI com autenticação Supabase (Google OAuth)
- [ ] Tabelas do banco conforme esquema acima
- [ ] Endpoints: usuário, conquistas, atividades, coins/XP
- [ ] Sistema de aprovação de consultores pelo admin

### Fase 2 — Integração FamilySearch
- [ ] Script Playwright: login + extração de dados pessoais
- [ ] Script Playwright: função Ajudante + extração de dados do ajudado
- [ ] Worker assíncrono com sync diário agendado
- [ ] Testes com credenciais reais (inspecionar elementos do FamilySearch)

### Fase 3 — App Mobile
- [ ] React Native (Expo) — setup inicial
- [ ] Telas: perfil, feed, ranking, conquistas, sync
- [ ] Animação de unlock de badges
- [ ] Notificações push via FCM

### Fase 4 — Funcionalidades Sociais
- [ ] Feed de atividades em tempo real (WebSocket)
- [ ] Sistema de desafios (PvP e coletivo)
- [ ] Grupos por ala/estaca
- [ ] Loja de coins

### Fase 5 — App do Líder
- [ ] Painel admin separado
- [ ] Aprovação de consultores
- [ ] Criação de desafios coletivos
- [ ] Relatórios agregados (espelho do FamilySearch, gamificado)

### Fase 6 — Lançamento
- [ ] Testes com consultores da Estaca Cumbica
- [ ] Ajustes de UX com base no feedback
- [ ] Publicar app na Play Store
- [ ] Adicionar ao portfólio Upwork

---

## ❓ Pontos Ainda em Aberto

- [ ] Thresholds numéricos dos badges (definir com líderes)
- [ ] Nomes dos ranks — revisar com jovens consultores
- [ ] Inspeção dos elementos HTML do FamilySearch para mapear o scraping
- [ ] Regras exatas para badge "Nome Impresso" e "4 Gerações"
- [ ] Política de proteção de streak: quantas proteções por semana?
- [ ] Processo de verificação de pesquisadores (não-membros) na gincana

---

## 📎 Referências

- [FamilySearch Developers](https://www.familysearch.org/developers/)
- [Habitica](https://habitica.com) — gamificação de hábitos
- [Duolingo](https://duolingo.com) — streaks e engajamento jovem
- Relatório da Estaca Guarulhos Brasil Cumbica (2026) — KPIs reais
- Gincana THF Alvarenga — modelo de pontuação por perfil
- Conversa anterior: Selenium + FamilySearch (arquivo `.json`)

---

*Documento gerado com auxílio do Claude (Anthropic)*
*Propriedade e autoria: Felipe A. Wolff*
