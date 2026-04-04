"""
Script de seed para o Torneio Vila PMOS 2026 Feminino.
4 equipas com 6 jogadoras cada. Apenas cria torneio, equipas e jogadoras.

Uso:
    uv run seed_pmos2026_feminino.py
    uv run seed_pmos2026_feminino.py --base-url=http://localhost:8000
"""

import httpx
import json
import sys

BASE_URL = "http://localhost:8000/api"

DUMMY_FILE = ("dummy.txt", b"seed", "text/plain")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def ok(r: httpx.Response, context: str) -> dict:
    if r.status_code not in (200, 201):
        print(f"  ERRO [{context}] {r.status_code}: {r.text}")
        sys.exit(1)
    return r.json()


def login(client: httpx.Client) -> None:
    print("A fazer login como admin...")
    r = client.post("/auth/login", json={"username": "admin", "password": "admin"})
    ok(r, "login")
    print("  OK\n")


# ---------------------------------------------------------------------------
# Criação de entidades
# ---------------------------------------------------------------------------


def criar_torneio(client: httpx.Client, nome: str) -> str:
    print(f"A criar torneo '{nome}'...")
    r = client.post("/tournaments", json={"name": nome})
    torneio_id = ok(r, "torneio")["id"]
    print(f"  ID: {torneio_id}\n")
    return torneio_id


def registar_equipa(
    client: httpx.Client,
    torneio_id: str,
    nome: str,
    responsavel: str,
    email: str,
    telefone: str,
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
        "players_json": players_json,
    }

    files = [("files", DUMMY_FILE)]

    r = client.post(
        "/teams/register",
        data=data,
        files=files,
    )
    equipa_id = ok(r, f"equipa {nome}")["id"]
    print(f"    ID: {equipa_id}")
    return equipa_id


def confirmar_jogadores(client: httpx.Client) -> None:
    print("\nA confirmar todos os jogadores...")
    r = client.get("/players")
    jogadores = ok(r, "listar jogadores")
    for j in jogadores:
        if not j["is_confirmed"]:
            rc = client.patch(f"/players/{j['id']}/confirm")
            if rc.status_code == 200:
                print(f"  Confirmado: {j['name']}")
            else:
                print(f"  AVISO ao confirmar {j['name']}: {rc.status_code}")
    print()


# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

EQUIPAS = [
    {
        "nome": "(1) FC Porto de Mós Feminino",
        "responsavel": "Ana Silva",
        "email": "ana@fcportodemos.pt",
        "telefone": "913000001",
        "jogadores": [
            {
                "name": "Mariana Rodrigues",
                "birth_date": "1999-04-10T00:00:00",
                "fiscal_number": "910000001",
            },
            {
                "name": "Beatriz Alves",
                "birth_date": "2001-07-22T00:00:00",
                "fiscal_number": "910000002",
            },
            {
                "name": "Sofia Fernandes",
                "birth_date": "2000-01-15T00:00:00",
                "fiscal_number": "910000003",
            },
            {
                "name": "Inês Oliveira",
                "birth_date": "2002-09-03T00:00:00",
                "fiscal_number": "910000004",
            },
            {
                "name": "Catarina Santos",
                "birth_date": "1998-12-28T00:00:00",
                "fiscal_number": "910000005",
            },
            {
                "name": "Leonor Martins",
                "birth_date": "2003-05-17T00:00:00",
                "fiscal_number": "910000006",
            },
        ],
    },
    {
        "nome": "(2) CD Batalha Feminino",
        "responsavel": "Teresa Correia",
        "email": "teresa@cdbatalha.pt",
        "telefone": "913000002",
        "jogadores": [
            {
                "name": "Filipa Sousa",
                "birth_date": "2000-03-05T00:00:00",
                "fiscal_number": "920000001",
            },
            {
                "name": "Marta Lima",
                "birth_date": "2002-11-19T00:00:00",
                "fiscal_number": "920000002",
            },
            {
                "name": "Rita Gomes",
                "birth_date": "1999-06-27T00:00:00",
                "fiscal_number": "920000003",
            },
            {
                "name": "Joana Ribeiro",
                "birth_date": "2001-08-13T00:00:00",
                "fiscal_number": "920000004",
            },
            {
                "name": "Andreia Azevedo",
                "birth_date": "2003-01-07T00:00:00",
                "fiscal_number": "920000005",
            },
            {
                "name": "Patrícia Cunha",
                "birth_date": "1998-10-22T00:00:00",
                "fiscal_number": "920000006",
            },
        ],
    },
    {
        "nome": "(3) AD Alcobaça Feminino",
        "responsavel": "Sandra Dias",
        "email": "sandra@adalcobaca.pt",
        "telefone": "913000003",
        "jogadores": [
            {
                "name": "Daniela Mendes",
                "birth_date": "1999-09-14T00:00:00",
                "fiscal_number": "930000001",
            },
            {
                "name": "Cláudia Esteves",
                "birth_date": "2001-03-31T00:00:00",
                "fiscal_number": "930000002",
            },
            {
                "name": "Vanessa Baptista",
                "birth_date": "2000-07-08T00:00:00",
                "fiscal_number": "930000003",
            },
            {
                "name": "Érica Monteiro",
                "birth_date": "2002-12-02T00:00:00",
                "fiscal_number": "930000004",
            },
            {
                "name": "Nádia Pires",
                "birth_date": "1998-05-20T00:00:00",
                "fiscal_number": "930000005",
            },
            {
                "name": "Vera Cruz",
                "birth_date": "2003-10-15T00:00:00",
                "fiscal_number": "930000006",
            },
        ],
    },
    {
        "nome": "(4) SC Leiria Futsal Feminino",
        "responsavel": "Luísa Faria",
        "email": "luisa@scleiria.pt",
        "telefone": "913000004",
        "jogadores": [
            {
                "name": "Carla Machado",
                "birth_date": "2000-02-19T00:00:00",
                "fiscal_number": "940000001",
            },
            {
                "name": "Fátima Borges",
                "birth_date": "2001-06-07T00:00:00",
                "fiscal_number": "940000002",
            },
            {
                "name": "Helena Moura",
                "birth_date": "1999-10-23T00:00:00",
                "fiscal_number": "940000003",
            },
            {
                "name": "Susana Correia",
                "birth_date": "2002-04-11T00:00:00",
                "fiscal_number": "940000004",
            },
            {
                "name": "Lara Campos",
                "birth_date": "1998-08-05T00:00:00",
                "fiscal_number": "940000005",
            },
            {
                "name": "Tânia Nogueira",
                "birth_date": "2003-12-30T00:00:00",
                "fiscal_number": "940000006",
            },
        ],
    },
]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    if len(sys.argv) > 1 and sys.argv[1].startswith("--base-url="):
        global BASE_URL
        BASE_URL = sys.argv[1].split("=", 1)[1]

    print("=" * 55)
    print("  Seed - Torneio Vila PMOS 2026 Feminino")
    print("=" * 55)
    print(f"Backend: {BASE_URL}\n")

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        login(client)

        # Torneio
        torneio_id = criar_torneio(client, "Torneio Vila PMOS 2026 Feminino")

        # Equipas
        print("A registar equipas...\n")
        equipa_ids = []
        for e in EQUIPAS:
            eid = registar_equipa(
                client,
                torneio_id,
                e["nome"],
                e["responsavel"],
                e["email"],
                e["telefone"],
                e["jogadores"],
            )
            equipa_ids.append(eid)
        print()

        # Confirmar jogadoras
        confirmar_jogadores(client)

        print("=" * 55)
        print("  Seed concluído com sucesso!")
        print(f"  Torneio ID : {torneio_id}")
        print(f"  Equipas    : {len(equipa_ids)}")
        print(f"  Jogadoras  : {len(equipa_ids) * 6} (confirmadas)")
        print("=" * 55)


if __name__ == "__main__":
    main()
