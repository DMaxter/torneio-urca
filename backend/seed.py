"""
Script de seed para popular a base de dados do Torneio URCA com dados de teste.

Uso:
    uv run seed.py
    uv run seed.py --base-url http://localhost:8000

O backend deve estar a correr antes de executar este script.
"""

import httpx
import json
import sys
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/api"

# Ficheiro dummy para satisfazer o upload obrigatório no registo de equipas
DUMMY_FILE = ("dummy.txt", b"seed", "text/plain")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def ok(r: httpx.Response, context: str) -> dict:
    if r.status_code not in (200, 201):
        print(f"  ERRO [{context}] {r.status_code}: {r.text}")
        sys.exit(1)
    return r.json()


def login(client: httpx.Client) -> str:
    print("A fazer login como admin...")
    r = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    token = ok(r, "login")["access_token"]
    print("  OK\n")
    return token


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# Criação de entidades
# ---------------------------------------------------------------------------

def criar_torneio(client: httpx.Client, token: str, nome: str) -> str:
    print(f"A criar torneio '{nome}'...")
    r = client.post("/tournaments", json={"name": nome}, headers=auth(token))
    torneio_id = ok(r, "torneio")["id"]
    print(f"  ID: {torneio_id}\n")
    return torneio_id


def registar_equipa(
    client: httpx.Client,
    token: str,
    torneio_id: str,
    nome: str,
    responsavel: str,
    email: str,
    telefone: str,
    treinador: str,
    treinador_dn: str,
    fisiatra: str,
    fisiatra_dn: str,
    delegado: str,
    delegado_dn: str,
    jogadores: list[dict],
) -> str:
    print(f"  A registar equipa '{nome}'...")

    players_json = json.dumps(jogadores)

    data = {
        "tournament": torneio_id,
        "name": nome,
        "responsible_name": responsavel,
        "responsible_email": email,
        "responsible_phone": telefone,
        "main_coach_name": treinador,
        "main_coach_birth_date": treinador_dn,
        "physiotherapist_name": fisiatra,
        "physiotherapist_birth_date": fisiatra_dn,
        "first_deputy_name": delegado,
        "first_deputy_birth_date": delegado_dn,
        "players_json": players_json,
    }

    files = [("files", DUMMY_FILE)]

    r = client.post(
        "/teams/register",
        data=data,
        files=files,
        headers=auth(token),
    )
    equipa_id = ok(r, f"equipa {nome}")["id"]
    print(f"    ID: {equipa_id}")
    return equipa_id


def confirmar_jogadores(client: httpx.Client, token: str) -> None:
    print("\nA confirmar todos os jogadores...")
    r = client.get("/players", headers=auth(token))
    jogadores = ok(r, "listar jogadores")
    for j in jogadores:
        if not j["is_confirmed"]:
            rc = client.patch(f"/players/{j['id']}/confirm", headers=auth(token))
            if rc.status_code == 200:
                print(f"  Confirmado: {j['name']}")
            else:
                print(f"  AVISO ao confirmar {j['name']}: {rc.status_code}")
    print()


def criar_grupo(
    client: httpx.Client,
    token: str,
    torneio_id: str,
    nome: str,
    equipa_ids: list[str],
) -> str:
    print(f"A criar grupo '{nome}'...")
    r = client.post(
        "/groups",
        json={"tournament": torneio_id, "name": nome, "teams": equipa_ids},
        headers=auth(token),
    )
    grupo_id = ok(r, f"grupo {nome}")["id"]
    print(f"  ID: {grupo_id}")
    return grupo_id


def criar_jogo(
    client: httpx.Client,
    token: str,
    torneio_id: str,
    equipa_casa: str,
    equipa_fora: str,
    data_jogo: str,
) -> str:
    r = client.post(
        "/games",
        json={
            "tournament": torneio_id,
            "scheduled_date": data_jogo,
            "home_call": {"team": equipa_casa},
            "away_call": {"team": equipa_fora},
        },
        headers=auth(token),
    )
    jogo_id = ok(r, "jogo")["id"]
    return jogo_id


# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

EQUIPAS = [
    {
        "nome": "FC Porto de Mós",
        "responsavel": "Carlos Silva",
        "email": "carlos@fcportodemos.pt",
        "telefone": "912345678",
        "treinador": "António Ferreira",
        "treinador_dn": "1975-06-15T00:00:00",
        "fisiatra": "Rui Costa",
        "fisiatra_dn": "1980-03-20T00:00:00",
        "delegado": "João Matos",
        "delegado_dn": "1978-11-05T00:00:00",
        "jogadores": [
            {"name": "Miguel Rodrigues",   "birth_date": "1998-04-10T00:00:00", "fiscal_number": "123456001"},
            {"name": "Diogo Alves",        "birth_date": "2000-07-22T00:00:00", "fiscal_number": "123456002"},
            {"name": "Tiago Fernandes",    "birth_date": "1999-01-15T00:00:00", "fiscal_number": "123456003"},
            {"name": "Pedro Oliveira",     "birth_date": "2001-09-03T00:00:00", "fiscal_number": "123456004"},
            {"name": "Rúben Santos",       "birth_date": "1997-12-28T00:00:00", "fiscal_number": "123456005"},
            {"name": "André Martins",      "birth_date": "2003-05-17T00:00:00", "fiscal_number": "123456006"},
            {"name": "Gonçalo Pereira",    "birth_date": "1996-08-11T00:00:00", "fiscal_number": "123456007"},
            {"name": "Nuno Carvalho",      "birth_date": "2002-02-24T00:00:00", "fiscal_number": "123456008"},
        ],
    },
    {
        "nome": "GD Batalha",
        "responsavel": "Manuel Correia",
        "email": "manuel@gdbatalha.pt",
        "telefone": "913456789",
        "treinador": "Luís Marques",
        "treinador_dn": "1972-09-08T00:00:00",
        "fisiatra": "Paulo Lopes",
        "fisiatra_dn": "1983-07-14T00:00:00",
        "delegado": "Sérgio Nunes",
        "delegado_dn": "1979-04-30T00:00:00",
        "jogadores": [
            {"name": "Filipe Sousa",       "birth_date": "1999-03-05T00:00:00", "fiscal_number": "223456001"},
            {"name": "Bernardo Lima",      "birth_date": "2001-11-19T00:00:00", "fiscal_number": "223456002"},
            {"name": "Henrique Gomes",     "birth_date": "1998-06-27T00:00:00", "fiscal_number": "223456003"},
            {"name": "Fábio Ribeiro",      "birth_date": "2000-08-13T00:00:00", "fiscal_number": "223456004"},
            {"name": "Tomás Azevedo",      "birth_date": "2002-01-07T00:00:00", "fiscal_number": "223456005"},
            {"name": "Vasco Cunha",        "birth_date": "1997-10-22T00:00:00", "fiscal_number": "223456006"},
            {"name": "Marco Pinto",        "birth_date": "2003-04-16T00:00:00", "fiscal_number": "223456007"},
            {"name": "Sandro Moreira",     "birth_date": "1996-07-09T00:00:00", "fiscal_number": "223456008"},
        ],
    },
    {
        "nome": "AD Alcobaça",
        "responsavel": "Fernando Dias",
        "email": "fernando@adadm.pt",
        "telefone": "914567890",
        "treinador": "Ricardo Teixeira",
        "treinador_dn": "1974-02-18T00:00:00",
        "fisiatra": "Bruno Vieira",
        "fisiatra_dn": "1985-05-25T00:00:00",
        "delegado": "Álvaro Brito",
        "delegado_dn": "1977-08-12T00:00:00",
        "jogadores": [
            {"name": "Leandro Mendes",     "birth_date": "1998-09-14T00:00:00", "fiscal_number": "323456001"},
            {"name": "Renato Esteves",     "birth_date": "2000-03-31T00:00:00", "fiscal_number": "323456002"},
            {"name": "Cristiano Baptista", "birth_date": "1999-07-08T00:00:00", "fiscal_number": "323456003"},
            {"name": "Éder Monteiro",      "birth_date": "2001-12-02T00:00:00", "fiscal_number": "323456004"},
            {"name": "Nelson Pires",       "birth_date": "1997-05-20T00:00:00", "fiscal_number": "323456005"},
            {"name": "Hélder Cruz",        "birth_date": "2002-10-15T00:00:00", "fiscal_number": "323456006"},
            {"name": "Jorge Tavares",      "birth_date": "1996-01-28T00:00:00", "fiscal_number": "323456007"},
            {"name": "Luís Rocha",         "birth_date": "2003-06-04T00:00:00", "fiscal_number": "323456008"},
        ],
    },
    {
        "nome": "SC Leiria Futsal",
        "responsavel": "Joaquim Faria",
        "email": "joaquim@scleiria.pt",
        "telefone": "915678901",
        "treinador": "Sílvio Cardoso",
        "treinador_dn": "1973-11-03T00:00:00",
        "fisiatra": "Dário Freitas",
        "fisiatra_dn": "1982-04-17T00:00:00",
        "delegado": "Edmundo Ramos",
        "delegado_dn": "1976-09-28T00:00:00",
        "jogadores": [
            {"name": "Cláudio Machado",    "birth_date": "1999-02-19T00:00:00", "fiscal_number": "423456001"},
            {"name": "Nélson Borges",      "birth_date": "2000-06-07T00:00:00", "fiscal_number": "423456002"},
            {"name": "Rui Moura",          "birth_date": "1998-10-23T00:00:00", "fiscal_number": "423456003"},
            {"name": "Afonso Correia",     "birth_date": "2001-04-11T00:00:00", "fiscal_number": "423456004"},
            {"name": "Ivo Campos",         "birth_date": "1997-08-05T00:00:00", "fiscal_number": "423456005"},
            {"name": "Flávio Nogueira",    "birth_date": "2002-12-30T00:00:00", "fiscal_number": "423456006"},
            {"name": "Telmo Antunes",      "birth_date": "1996-03-16T00:00:00", "fiscal_number": "423456007"},
            {"name": "Simão Fonseca",      "birth_date": "2003-07-22T00:00:00", "fiscal_number": "423456008"},
        ],
    },
]

# Jogos: (índice equipa casa, índice equipa fora, data)
JOGOS_GRUPO_A = [
    (0, 1, "2026-04-12T10:00:00+00:00"),
    (1, 0, "2026-04-19T10:00:00+00:00"),
]
JOGOS_GRUPO_B = [
    (2, 3, "2026-04-12T12:00:00+00:00"),
    (3, 2, "2026-04-19T12:00:00+00:00"),
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    if len(sys.argv) > 1 and sys.argv[1].startswith("--base-url="):
        global BASE_URL
        BASE_URL = sys.argv[1].split("=", 1)[1]

    print("=" * 55)
    print("  Seed - Torneio URCA 2026")
    print("=" * 55)
    print(f"Backend: {BASE_URL}\n")

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        token = login(client)

        # Torneio
        torneio_id = criar_torneio(client, token, "Torneio URCA 2026")

        # Equipas
        print("A registar equipas...\n")
        equipa_ids = []
        for e in EQUIPAS:
            eid = registar_equipa(
                client, token, torneio_id,
                e["nome"], e["responsavel"], e["email"], e["telefone"],
                e["treinador"], e["treinador_dn"],
                e["fisiatra"], e["fisiatra_dn"],
                e["delegado"], e["delegado_dn"],
                e["jogadores"],
            )
            equipa_ids.append(eid)
        print()

        # Confirmar jogadores
        confirmar_jogadores(client, token)

        # Grupos
        print("A criar grupos...")
        criar_grupo(client, token, torneio_id, "Grupo A", equipa_ids[0:2])
        criar_grupo(client, token, torneio_id, "Grupo B", equipa_ids[2:4])
        print()

        # Jogos
        print("A criar jogos...")
        jogos_criados = 0
        for casa_i, fora_i, data in JOGOS_GRUPO_A:
            jid = criar_jogo(client, token, torneio_id, equipa_ids[casa_i], equipa_ids[fora_i], data)
            print(f"  {EQUIPAS[casa_i]['nome']} vs {EQUIPAS[fora_i]['nome']} → {jid}")
            jogos_criados += 1
        for casa_i, fora_i, data in JOGOS_GRUPO_B:
            jid = criar_jogo(client, token, torneio_id, equipa_ids[casa_i], equipa_ids[fora_i], data)
            print(f"  {EQUIPAS[casa_i]['nome']} vs {EQUIPAS[fora_i]['nome']} → {jid}")
            jogos_criados += 1

        print()
        print("=" * 55)
        print("  Seed concluído com sucesso!")
        print(f"  Torneio ID : {torneio_id}")
        print(f"  Equipas    : {len(equipa_ids)}")
        print(f"  Jogadores  : {len(equipa_ids) * 8} (confirmados)")
        print(f"  Grupos     : 2 (A e B)")
        print(f"  Jogos      : {jogos_criados}")
        print("=" * 55)


if __name__ == "__main__":
    main()
