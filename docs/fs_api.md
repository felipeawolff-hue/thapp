# FamilySearch API — Endpoints Mapeados
> Arquivo: `docs/fs_api.md`
> Descoberto via DevTools (Network → Fetch/XHR)
> Base URL: `https://www.familysearch.org`

---

## 🔐 Autenticação

O FamilySearch usa **Bearer Token** em todas as requisições.

```
Authorization: Bearer {TOKEN}
```

### Como obter o token
1. Login via Playwright no FamilySearch
2. Após autenticação, capturar o cookie `fssessionid` — ele é o Bearer Token
3. Exemplo capturado: `fssessionid=p0-7OLNgpV~x6B.OibET~0HowN`
4. Usar como: `Authorization: Bearer p0-7OLNgpV~x6B.OibET~0HowN`

### Captura via Playwright
```python
# Após login bem-sucedido:
cookies = await page.context.cookies()
token = next(c['value'] for c in cookies if c['name'] == 'fssessionid')
# Usar token em todas as requisições seguintes
```

### Headers obrigatórios em todas as requisições
```python
headers = {
    "Authorization": f"Bearer {token}",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "pt",
    "Referer": "https://www.familysearch.org/pt/",
}
```

---

## 📋 Endpoints Descobertos

### 1. Contagem de Ordenanças (PRINCIPAL)

```
GET /service/tree/tree-data/reservations/list/{PERSON_ID}/counts
```

**Parâmetros:**
- `{PERSON_ID}` — ID do FamilySearch da pessoa (ex: `93JB-DL7`)

**Response (JSON):**
```json
{
  "individualsAndFamiliesNotTempleShared": 2,
  "individualsAndFamiliesNotTempleSharedLimit": 300,
  "individualsAndFamiliesTempleShared": 0,
  "completedOrdinances": 38,
  "completedOrdinancePersons": 20
}
```

**Campos úteis para o THApp:**
| Campo | Significado |
|-------|------------|
| `completedOrdinances` | Total de ordenanças completadas |
| `completedOrdinancePersons` | Total de pessoas com ordenanças completadas |
| `individualsAndFamiliesNotTempleShared` | Nomes reservados ainda não enviados |

---

### 2. Detalhes de Reservas por Pessoa

```
GET /service/tree/tree-data/reservations/person/{IDs}?locale=pt&owner={OWNER_ID}&pendingTransfer=true
```

**Parâmetros:**
- `{IDs}` — IDs separados por vírgula das pessoas na árvore (ex: `PQRN-73P,GGM4-7L3`)
- `owner={OWNER_ID}` — ID do dono da reserva (ex: `93JB-DL7`)
- `pendingTransfer=true` — inclui transferências pendentes

**Uso:** buscar detalhes das ordenanças de pessoas específicas da árvore

---

### 3. Reservas Ativas (Assignments)

```
GET /service/cmn/assignments/assignments
```

**Sem parâmetros** — retorna as reservas do usuário autenticado (ou do ajudado, no modo Ajudante)

**Uso:** listar nomes reservados para o templo

---

### 4. Recordações / Memórias (Galeria)

```
GET /service/cmn/assignments/assignments
Referer: https://www.familysearch.org/pt/memories/gallery/
fs-user-agent-chain: memories-react-prod (/pt/memories/gallery/)
```

> ⚠️ **Nota:** Endpoint igual ao de assignments, mas com headers diferentes.
> A página de Recordações (`/pt/memories/gallery/`) pode ter endpoints adicionais.
> **TODO:** Mapear endpoints específicos de fotos/documentos navegando na galeria de recordações.

---

## 🔄 Fluxo Completo de Sync

### Sync de conta pessoal do consultor
```python
async def sync_consultor(user_id: str, token: str, fs_person_id: str):
    base = "https://www.familysearch.org"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Accept-Language": "pt",
    }

    # 1. Ordenanças
    counts = await get(f"{base}/service/tree/tree-data/reservations/list/{fs_person_id}/counts", headers)

    # 2. Reservas ativas
    assignments = await get(f"{base}/service/cmn/assignments/assignments", headers)

    return {
        "completedOrdinances": counts["completedOrdinances"],
        "completedOrdinancePersons": counts["completedOrdinancePersons"],
        "activeReservations": len(assignments),  # ajustar conforme estrutura do response
    }
```

### Sync via Função Ajudante
```python
async def sync_ajudado(consultor_token: str, ajudado_fs_id: str):
    # O token do CONSULTOR já está no modo Ajudante após o login helper
    # Basta usar o ID do AJUDADO nos endpoints
    base = "https://www.familysearch.org"
    headers = {
        "Authorization": f"Bearer {consultor_token}",
        "Accept": "application/json",
        "Accept-Language": "pt",
    }

    counts = await get(
        f"{base}/service/tree/tree-data/reservations/list/{ajudado_fs_id}/counts",
        headers
    )
    return counts
```

---

## 🕷️ Login via Playwright

```python
from playwright.async_api import async_playwright

async def login_familysearch(username: str, password: str) -> str:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        await page.goto("https://www.familysearch.org/pt/auth/familysearch/login")
        await page.fill('input[name="username"]', username)  # confirmar seletor
        await page.fill('input[name="password"]', password)  # confirmar seletor
        await page.click('button[type="submit"]')            # confirmar seletor
        await page.wait_for_load_state("networkidle")

        # Capturar token
        cookies = await context.cookies()
        token = next(c['value'] for c in cookies if c['name'] == 'fssessionid')

        await browser.close()
        return token
```

> ⚠️ **TODO:** Confirmar seletores dos campos de login inspecionando a página de login do FamilySearch

---

## 🤝 Ativar Função Ajudante via Playwright

```python
async def ativar_ajudante(page, primeiro_nome: str, nome_familiar: str,
                           dia: str, mes: str, ano: str, codigo_ajudante: str):
    # Clicar no botão Função Ajudante
    await page.click('[data-testid="helper-function"]')  # confirmar seletor

    # Selecionar aba "Nome completo"
    await page.click('text=Nome completo')

    # Preencher campos
    await page.fill('input[placeholder*="Primeiro nome"]', primeiro_nome)
    await page.fill('input[placeholder*="Nome familiar"]', nome_familiar)

    # Data de nascimento
    await page.select_option('select[name="birthDay"]', dia)
    await page.select_option('select[name="birthMonth"]', mes)
    await page.select_option('select[name="birthYear"]', ano)

    # Código para Ajudante
    await page.fill('input[placeholder*="número de ajuda"]', codigo_ajudante)

    # Entrar
    await page.click('button:has-text("ENTRAR NO SISTEMA")')
    await page.wait_for_load_state("networkidle")

    # Após entrar, o token do consultor já acessa dados do ajudado
    # A URL muda para: /pt/tree/pedigree/landscape/{FS_ID_AJUDADO}
    current_url = page.url
    ajudado_fs_id = current_url.split("/")[-1]  # ex: GGM4-HDL
    return ajudado_fs_id
```

---

## ⚠️ Observações Importantes

1. **Token expira** — sessão dura algumas horas. Se expirar, Playwright faz novo login.
2. **Rate limiting** — adicionar delay entre requisições (sugestão: 1–2s entre calls).
3. **Modo Ajudante** — após ativar, o mesmo token do consultor acessa dados do ajudado. Não precisa de credenciais do ajudado — só nome completo, data de nascimento e código de ajudante.
4. **Seletores HTML** — os marcados com `# confirmar seletor` precisam ser validados inspecionando a página de login do FamilySearch.

---

## 📌 TODOs de Mapeamento

- [ ] Confirmar seletores da página de login (`input[name="username"]` etc.)
- [ ] Mapear endpoints de Recordações/Galeria (fotos e documentos)
- [ ] Mapear endpoint de Árvore Genealógica (gerações preenchidas)
- [ ] Mapear endpoint de Atividades recentes (indexação/Participe)
- [ ] Verificar estrutura completa do response de `assignments`
- [ ] Testar se o token do modo Ajudante é o mesmo ou gerado separado

---

*Mapeado por Felipe A. Wolff com auxílio do Claude (Anthropic)*
*Data: 29/03/2026*
