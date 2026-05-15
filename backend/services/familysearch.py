"""
FamilySearch Integration Service
=================================
Usa Playwright para autenticar e capturar o Bearer Token da sessão.
Depois usa o token para chamar a API REST interna do FamilySearch
(descoberta via DevTools — não é API pública oficial).

Fluxo:
  1. login_familysearch()      → retorna token (fssessionid)
  2. ativar_ajudante()         → entra no modo Ajudante, retorna FS_ID do ajudado
  3. sync_ordenancas()         → busca dados de ordenanças via API REST
  4. sair_ajudante()           → sai do modo Ajudante
"""

import asyncio
import httpx
from playwright.async_api import async_playwright, Page, BrowserContext


BASE_URL = "https://www.familysearch.org"
LOGIN_URL = f"{BASE_URL}/pt/auth/familysearch/login"


# ---------------------------------------------------------------------------
# AUTENTICAÇÃO
# ---------------------------------------------------------------------------

async def login_familysearch(username: str, password: str) -> dict:
    """
    Faz login no FamilySearch via Playwright (headless).
    Retorna o token de sessão e o FS_ID do usuário logado.

    Args:
        username: nome de usuário ou e-mail do FamilySearch
        password: senha do FamilySearch

    Returns:
        {
            "token": "p0-xxxx...",       # Bearer token (fssessionid)
            "fs_person_id": "MMM9-B598"  # ID da pessoa no FamilySearch
        }
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            locale="pt-BR",
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/146.0.0.0 Safari/537.36"
            )
        )
        page = await context.new_page()

        # Navega para a página de login
        await page.goto(LOGIN_URL, wait_until="networkidle")

        # Preenche credenciais
        # TODO: confirmar seletores inspecionando a página de login
        await page.fill('input[name="username"]', username)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        # Captura o token (cookie fssessionid = Bearer Token)
        cookies = await context.cookies()
        token = next(
            (c["value"] for c in cookies if c["name"] == "fssessionid"),
            None
        )

        # Captura o FS_ID do usuário logado via cookie userId
        fs_person_id = next(
            (
                c["value"].split("%7C")[1]  # formato: g%3AMMM9-B598%7Ce%3A...
                for c in cookies
                if "userId" in c["name"]
            ),
            None
        )

        await browser.close()

        if not token:
            raise ValueError("Login falhou — token não encontrado. Verifique credenciais.")

        return {
            "token": token,
            "fs_person_id": fs_person_id
        }


# ---------------------------------------------------------------------------
# FUNÇÃO AJUDANTE
# ---------------------------------------------------------------------------

async def ativar_ajudante(
    token: str,
    primeiro_nome: str,
    nome_familiar: str,
    dia: int,
    mes: int,
    ano: int,
    codigo_ajudante: str
) -> str:
    """
    Ativa a Função Ajudante no FamilySearch.
    Usa a aba 'Nome completo' do formulário.

    Returns:
        fs_id do ajudado (ex: "GGM4-HDL")
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(locale="pt-BR")

        # Injeta o token como cookie para pular o login
        await context.add_cookies([{
            "name": "fssessionid",
            "value": token,
            "domain": ".familysearch.org",
            "path": "/"
        }])

        page = await context.new_page()
        await page.goto(f"{BASE_URL}/pt/tree/pedigree/portrait", wait_until="networkidle")

        # Clica no botão Função Ajudante
        # TODO: confirmar seletor — procurar pelo texto ou ícone
        await page.click('text=Função Ajudante')
        await page.wait_for_selector('text=Quem você gostaria de ajudar?')

        # Seleciona aba "Nome completo"
        await page.click('text=Nome completo')

        # Preenche o formulário
        await page.fill('input[placeholder*="Primeiro nome"]', primeiro_nome)
        await page.fill('input[placeholder*="Nome familiar"]', nome_familiar)

        # Data de nascimento (selects)
        await page.select_option('select >> nth=0', str(dia))    # dia
        await page.select_option('select >> nth=1', str(mes))    # mês
        await page.select_option('select >> nth=2', str(ano))    # ano

        # Código para Ajudante
        await page.fill('input[placeholder*="número de ajuda"]', codigo_ajudante)

        # Clica em Entrar no Sistema
        await page.click('button:has-text("ENTRAR NO SISTEMA")')
        await page.wait_for_load_state("networkidle")

        # URL após entrar: /pt/tree/pedigree/landscape/{FS_ID}
        url = page.url
        ajudado_fs_id = url.split("/")[-1]  # ex: GGM4-HDL

        # Recaptura o token (pode ter sido renovado)
        cookies = await context.cookies()
        novo_token = next(
            (c["value"] for c in cookies if c["name"] == "fssessionid"),
            token
        )

        await browser.close()

        return {
            "ajudado_fs_id": ajudado_fs_id,
            "token": novo_token  # usar este token para as chamadas de sync
        }


# ---------------------------------------------------------------------------
# SYNC DE DADOS VIA API REST
# ---------------------------------------------------------------------------

def _headers(token: str) -> dict:
    """Headers padrão para todas as requisições à API do FamilySearch."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "pt",
        "Referer": f"{BASE_URL}/pt/",
    }


async def sync_ordenancas(token: str, fs_person_id: str) -> dict:
    """
    Busca contagem de ordenanças de uma pessoa.
    Endpoint descoberto via DevTools em /pt/temple/reservations/

    Args:
        token: Bearer token da sessão
        fs_person_id: ID da pessoa no FamilySearch (ex: "93JB-DL7")

    Returns:
        {
            "completedOrdinances": 38,
            "completedOrdinancePersons": 20,
            "reservedNotShared": 2,
            "reservedNotSharedLimit": 300,
            "templeShared": 0
        }
    """
    url = f"{BASE_URL}/service/tree/tree-data/reservations/list/{fs_person_id}/counts"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_headers(token))
        response.raise_for_status()
        data = response.json()

    return {
        "completedOrdinances": data.get("completedOrdinances", 0),
        "completedOrdinancePersons": data.get("completedOrdinancePersons", 0),
        "reservedNotShared": data.get("individualsAndFamiliesNotTempleShared", 0),
        "reservedNotSharedLimit": data.get("individualsAndFamiliesNotTempleSharedLimit", 300),
        "templeShared": data.get("individualsAndFamiliesTempleShared", 0),
    }


async def sync_reservas(token: str) -> list:
    """
    Busca reservas ativas (nomes para o templo) do usuário autenticado.
    Endpoint descoberto via DevTools em /pt/temple/reservations/

    Returns:
        Lista de reservas (estrutura a confirmar com response real)
    """
    url = f"{BASE_URL}/service/cmn/assignments/assignments"

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=_headers(token))
        response.raise_for_status()
        data = response.json()

    # TODO: mapear estrutura real do response após testar
    return data


async def sync_completo(token: str, fs_person_id: str) -> dict:
    """
    Executa sync completo de um usuário ou ajudado.
    Roda em paralelo para ser mais rápido.

    Args:
        token: Bearer token (do consultor, já no modo Ajudante se aplicável)
        fs_person_id: ID da pessoa cujos dados serão sincronizados

    Returns:
        Dicionário com todos os dados coletados
    """
    # Roda as chamadas em paralelo
    ordenancas, reservas = await asyncio.gather(
        sync_ordenancas(token, fs_person_id),
        sync_reservas(token),
    )

    return {
        "fs_person_id": fs_person_id,
        "ordenancas": ordenancas,
        "reservas": reservas,
        # TODO: adicionar recordações e árvore quando mapear endpoints
    }


# ---------------------------------------------------------------------------
# TESTE LOCAL
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import json

    async def testar():
        print("=== Teste FamilySearch Service ===\n")

        # 1. Login
        print("1. Fazendo login...")
        resultado = await login_familysearch(
            username="SEU_USUARIO",
            password="SUA_SENHA"
        )
        token = resultado["token"]
        fs_id = resultado["fs_person_id"]
        print(f"   Token: {token[:20]}...")
        print(f"   FS ID: {fs_id}")

        # 2. Sync de ordenanças
        print("\n2. Sincronizando ordenanças...")
        dados = await sync_ordenancas(token, fs_id)
        print(json.dumps(dados, indent=2, ensure_ascii=False))

        print("\n✅ Teste concluído!")

    asyncio.run(testar())
