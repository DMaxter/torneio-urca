"""
Script de seed para o Torneio Vila PMOS 2026 Masculino.
10 equipas com 10 jogadores cada. Apenas cria torneio, equipas e jogadores.

Uso:
    uv run seed_pmos2026.py
    uv run seed_pmos2026.py --base-url=http://localhost:8000
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


# ---------------------------------------------------------------------------
# Dados de teste
# ---------------------------------------------------------------------------

EQUIPAS = [
    {
        "nome": "(1) FC Porto de Mós",
        "responsavel": "Carlos Silva",
        "email": "carlos@fcportodemos.pt",
        "telefone": "912000001",
        "jogadores": [
            {"name": "Miguel Rodrigues",    "birth_date": "1998-04-10T00:00:00", "fiscal_number": "100000001"},
            {"name": "Diogo Alves",         "birth_date": "2000-07-22T00:00:00", "fiscal_number": "100000002"},
            {"name": "Tiago Fernandes",     "birth_date": "1999-01-15T00:00:00", "fiscal_number": "100000003"},
            {"name": "Pedro Oliveira",      "birth_date": "2001-09-03T00:00:00", "fiscal_number": "100000004"},
            {"name": "Rúben Santos",        "birth_date": "1997-12-28T00:00:00", "fiscal_number": "100000005"},
            {"name": "André Martins",       "birth_date": "2003-05-17T00:00:00", "fiscal_number": "100000006"},
            {"name": "Gonçalo Pereira",     "birth_date": "1996-08-11T00:00:00", "fiscal_number": "100000007"},
            {"name": "Nuno Carvalho",       "birth_date": "2002-02-24T00:00:00", "fiscal_number": "100000008"},
            {"name": "Bruno Lopes",         "birth_date": "2000-11-06T00:00:00", "fiscal_number": "100000009"},
            {"name": "Sérgio Mendes",       "birth_date": "1995-03-19T00:00:00", "fiscal_number": "100000010"},
        ],
    },
    {
        "nome": "(2) CD Batalha",
        "responsavel": "Manuel Correia",
        "email": "manuel@cdbatalha.pt",
        "telefone": "912000002",
        "jogadores": [
            {"name": "Filipe Sousa",        "birth_date": "1999-03-05T00:00:00", "fiscal_number": "200000001"},
            {"name": "Bernardo Lima",       "birth_date": "2001-11-19T00:00:00", "fiscal_number": "200000002"},
            {"name": "Henrique Gomes",      "birth_date": "1998-06-27T00:00:00", "fiscal_number": "200000003"},
            {"name": "Fábio Ribeiro",       "birth_date": "2000-08-13T00:00:00", "fiscal_number": "200000004"},
            {"name": "Tomás Azevedo",       "birth_date": "2002-01-07T00:00:00", "fiscal_number": "200000005"},
            {"name": "Vasco Cunha",         "birth_date": "1997-10-22T00:00:00", "fiscal_number": "200000006"},
            {"name": "Marco Pinto",         "birth_date": "2003-04-16T00:00:00", "fiscal_number": "200000007"},
            {"name": "Sandro Moreira",      "birth_date": "1996-07-09T00:00:00", "fiscal_number": "200000008"},
            {"name": "Rodrigo Neves",       "birth_date": "2001-05-23T00:00:00", "fiscal_number": "200000009"},
            {"name": "Luís Ferreira",       "birth_date": "1994-09-14T00:00:00", "fiscal_number": "200000010"},
        ],
    },
    {
        "nome": "(3) AD Alcobaça",
        "responsavel": "Fernando Dias",
        "email": "fernando@adalcobaca.pt",
        "telefone": "912000003",
        "jogadores": [
            {"name": "Leandro Mendes",      "birth_date": "1998-09-14T00:00:00", "fiscal_number": "300000001"},
            {"name": "Renato Esteves",      "birth_date": "2000-03-31T00:00:00", "fiscal_number": "300000002"},
            {"name": "Cristiano Baptista",  "birth_date": "1999-07-08T00:00:00", "fiscal_number": "300000003"},
            {"name": "Éder Monteiro",       "birth_date": "2001-12-02T00:00:00", "fiscal_number": "300000004"},
            {"name": "Nelson Pires",        "birth_date": "1997-05-20T00:00:00", "fiscal_number": "300000005"},
            {"name": "Hélder Cruz",         "birth_date": "2002-10-15T00:00:00", "fiscal_number": "300000006"},
            {"name": "Jorge Tavares",       "birth_date": "1996-01-28T00:00:00", "fiscal_number": "300000007"},
            {"name": "Luís Rocha",          "birth_date": "2003-06-04T00:00:00", "fiscal_number": "300000008"},
            {"name": "Artur Simões",        "birth_date": "2000-08-17T00:00:00", "fiscal_number": "300000009"},
            {"name": "Cláudio Matos",       "birth_date": "1995-02-11T00:00:00", "fiscal_number": "300000010"},
        ],
    },
    {
        "nome": "(4) SC Leiria Futsal",
        "responsavel": "Joaquim Faria",
        "email": "joaquim@scleiria.pt",
        "telefone": "912000004",
        "jogadores": [
            {"name": "Cláudio Machado",     "birth_date": "1999-02-19T00:00:00", "fiscal_number": "400000001"},
            {"name": "Nélson Borges",       "birth_date": "2000-06-07T00:00:00", "fiscal_number": "400000002"},
            {"name": "Rui Moura",           "birth_date": "1998-10-23T00:00:00", "fiscal_number": "400000003"},
            {"name": "Afonso Correia",      "birth_date": "2001-04-11T00:00:00", "fiscal_number": "400000004"},
            {"name": "Ivo Campos",          "birth_date": "1997-08-05T00:00:00", "fiscal_number": "400000005"},
            {"name": "Flávio Nogueira",     "birth_date": "2002-12-30T00:00:00", "fiscal_number": "400000006"},
            {"name": "Telmo Antunes",       "birth_date": "1996-03-16T00:00:00", "fiscal_number": "400000007"},
            {"name": "Simão Fonseca",       "birth_date": "2003-07-22T00:00:00", "fiscal_number": "400000008"},
            {"name": "Dário Vieira",        "birth_date": "2001-01-30T00:00:00", "fiscal_number": "400000009"},
            {"name": "Márcio Teixeira",     "birth_date": "1994-11-08T00:00:00", "fiscal_number": "400000010"},
        ],
    },
    {
        "nome": "(5) GD Marinha Grande",
        "responsavel": "António Neves",
        "email": "antonio@gdmg.pt",
        "telefone": "912000005",
        "jogadores": [
            {"name": "Paulo Saraiva",       "birth_date": "1999-05-12T00:00:00", "fiscal_number": "500000001"},
            {"name": "João Brandão",        "birth_date": "2001-08-25T00:00:00", "fiscal_number": "500000002"},
            {"name": "Duarte Quintal",      "birth_date": "1998-02-14T00:00:00", "fiscal_number": "500000003"},
            {"name": "Mário Sequeira",      "birth_date": "2000-10-09T00:00:00", "fiscal_number": "500000004"},
            {"name": "Ricardo Valente",     "birth_date": "2003-03-27T00:00:00", "fiscal_number": "500000005"},
            {"name": "Sérgio Paiva",        "birth_date": "1996-07-03T00:00:00", "fiscal_number": "500000006"},
            {"name": "Álvaro Medeiros",     "birth_date": "2002-11-18T00:00:00", "fiscal_number": "500000007"},
            {"name": "Nuno Guerreiro",      "birth_date": "1997-04-22T00:00:00", "fiscal_number": "500000008"},
            {"name": "Tiago Barroso",       "birth_date": "2001-09-05T00:00:00", "fiscal_number": "500000009"},
            {"name": "Carlos Infante",      "birth_date": "1993-06-30T00:00:00", "fiscal_number": "500000010"},
        ],
    },
    {
        "nome": "(6) FC Nazaré",
        "responsavel": "Rui Calheiros",
        "email": "rui@fcnazare.pt",
        "telefone": "912000006",
        "jogadores": [
            {"name": "Alexandre Bento",     "birth_date": "1999-07-16T00:00:00", "fiscal_number": "600000001"},
            {"name": "Vítor Abreu",         "birth_date": "2000-12-03T00:00:00", "fiscal_number": "600000002"},
            {"name": "Sílvio Leal",         "birth_date": "1998-04-21T00:00:00", "fiscal_number": "600000003"},
            {"name": "Edmundo Cardoso",     "birth_date": "2002-09-07T00:00:00", "fiscal_number": "600000004"},
            {"name": "Gilberto Neto",       "birth_date": "1997-01-14T00:00:00", "fiscal_number": "600000005"},
            {"name": "Heitor Macedo",       "birth_date": "2003-06-28T00:00:00", "fiscal_number": "600000006"},
            {"name": "Ilídio Ramos",        "birth_date": "1996-10-02T00:00:00", "fiscal_number": "600000007"},
            {"name": "Jacinto Serra",       "birth_date": "2001-03-15T00:00:00", "fiscal_number": "600000008"},
            {"name": "Lúcio Figueiredo",    "birth_date": "1999-11-24T00:00:00", "fiscal_number": "600000009"},
            {"name": "Olavo Pinheiro",      "birth_date": "1994-08-10T00:00:00", "fiscal_number": "600000010"},
        ],
    },
    {
        "nome": "(7) UD Ansião",
        "responsavel": "Domingos Barata",
        "email": "domingos@udansiao.pt",
        "telefone": "912000007",
        "jogadores": [
            {"name": "Américo Vilas",       "birth_date": "1998-01-09T00:00:00", "fiscal_number": "700000001"},
            {"name": "Bento Marques",       "birth_date": "2000-05-18T00:00:00", "fiscal_number": "700000002"},
            {"name": "Caio Pedrosa",        "birth_date": "2002-08-04T00:00:00", "fiscal_number": "700000003"},
            {"name": "Danilo Freitas",      "birth_date": "1999-11-27T00:00:00", "fiscal_number": "700000004"},
            {"name": "Elias Barbosa",       "birth_date": "2001-04-13T00:00:00", "fiscal_number": "700000005"},
            {"name": "Fausto Ventura",      "birth_date": "1997-07-31T00:00:00", "fiscal_number": "700000006"},
            {"name": "Gaspar Couto",        "birth_date": "2003-02-06T00:00:00", "fiscal_number": "700000007"},
            {"name": "Horácio Leite",       "birth_date": "1996-09-22T00:00:00", "fiscal_number": "700000008"},
            {"name": "Ivanildo Melo",       "birth_date": "2000-12-15T00:00:00", "fiscal_number": "700000009"},
            {"name": "Januário Graça",      "birth_date": "1993-03-28T00:00:00", "fiscal_number": "700000010"},
        ],
    },
    {
        "nome": "(8) CF Pombal",
        "responsavel": "Serafim Costa",
        "email": "serafim@cfpombal.pt",
        "telefone": "912000008",
        "jogadores": [
            {"name": "Kelvin Andrade",      "birth_date": "1999-06-20T00:00:00", "fiscal_number": "800000001"},
            {"name": "Lázaro Moraes",       "birth_date": "2001-10-07T00:00:00", "fiscal_number": "800000002"},
            {"name": "Marcelo Reis",        "birth_date": "1998-03-14T00:00:00", "fiscal_number": "800000003"},
            {"name": "Narciso Veloso",      "birth_date": "2002-07-29T00:00:00", "fiscal_number": "800000004"},
            {"name": "Osvaldo Cunha",       "birth_date": "1997-01-05T00:00:00", "fiscal_number": "800000005"},
            {"name": "Plácido Brito",       "birth_date": "2003-09-12T00:00:00", "fiscal_number": "800000006"},
            {"name": "Quintino Faria",      "birth_date": "1996-04-25T00:00:00", "fiscal_number": "800000007"},
            {"name": "Ramiro Duarte",       "birth_date": "2000-08-08T00:00:00", "fiscal_number": "800000008"},
            {"name": "Salomão Nunes",       "birth_date": "2001-02-19T00:00:00", "fiscal_number": "800000009"},
            {"name": "Telmo Viegas",        "birth_date": "1994-05-03T00:00:00", "fiscal_number": "800000010"},
        ],
    },
    {
        "nome": "(9) SC Caldas da Rainha",
        "responsavel": "Valentim Rego",
        "email": "valentim@sccaldas.pt",
        "telefone": "912000009",
        "jogadores": [
            {"name": "Ulisses Amaro",       "birth_date": "1999-09-16T00:00:00", "fiscal_number": "900000001"},
            {"name": "Valter Braga",        "birth_date": "2001-01-03T00:00:00", "fiscal_number": "900000002"},
            {"name": "Xavier Campos",       "birth_date": "1998-05-20T00:00:00", "fiscal_number": "900000003"},
            {"name": "Yuri Delgado",        "birth_date": "2002-10-06T00:00:00", "fiscal_number": "900000004"},
            {"name": "Zacarias Estrada",    "birth_date": "1997-02-23T00:00:00", "fiscal_number": "900000005"},
            {"name": "Adélio Fonseca",      "birth_date": "2003-07-10T00:00:00", "fiscal_number": "900000006"},
            {"name": "Baltazar Gião",       "birth_date": "1996-12-17T00:00:00", "fiscal_number": "900000007"},
            {"name": "Celestino Horta",     "birth_date": "2000-04-01T00:00:00", "fiscal_number": "900000008"},
            {"name": "Delfim Iglésias",     "birth_date": "2001-08-14T00:00:00", "fiscal_number": "900000009"},
            {"name": "Eusébio Janela",      "birth_date": "1993-11-27T00:00:00", "fiscal_number": "900000010"},
        ],
    },
    {
        "nome": "(10) AD Ourém",
        "responsavel": "Firmino Lacerda",
        "email": "firmino@adourem.pt",
        "telefone": "912000010",
        "jogadores": [
            {"name": "Florindo Maia",       "birth_date": "1999-03-24T00:00:00", "fiscal_number": "101000001"},
            {"name": "Germano Norte",       "birth_date": "2001-07-11T00:00:00", "fiscal_number": "101000002"},
            {"name": "Hipólito Osório",     "birth_date": "1998-11-28T00:00:00", "fiscal_number": "101000003"},
            {"name": "Isidro Palma",        "birth_date": "2002-04-14T00:00:00", "fiscal_number": "101000004"},
            {"name": "Jerónimo Queirós",    "birth_date": "1997-09-01T00:00:00", "fiscal_number": "101000005"},
            {"name": "Ladislau Rato",       "birth_date": "2003-01-18T00:00:00", "fiscal_number": "101000006"},
            {"name": "Moisés Serrano",      "birth_date": "1996-06-05T00:00:00", "fiscal_number": "101000007"},
            {"name": "Nazário Teles",       "birth_date": "2000-10-22T00:00:00", "fiscal_number": "101000008"},
            {"name": "Onésimo Urbano",      "birth_date": "2001-03-07T00:00:00", "fiscal_number": "101000009"},
            {"name": "Pompeu Valério",      "birth_date": "1993-08-20T00:00:00", "fiscal_number": "101000010"},
        ],
    },
    {
        "nome": "(11) GD Fátima",
        "responsavel": "Augusto Pimentel",
        "email": "augusto@gdfatima.pt",
        "telefone": "912000011",
        "jogadores": [
            {"name": "Rafael Andrade",      "birth_date": "1999-04-05T00:00:00", "fiscal_number": "110000001"},
            {"name": "Hugo Batista",        "birth_date": "2001-08-19T00:00:00", "fiscal_number": "110000002"},
            {"name": "Igor Castelo",        "birth_date": "1998-12-03T00:00:00", "fiscal_number": "110000003"},
            {"name": "Jair Delgado",        "birth_date": "2002-05-17T00:00:00", "fiscal_number": "110000004"},
            {"name": "Kelton Esteves",      "birth_date": "1997-09-30T00:00:00", "fiscal_number": "110000005"},
            {"name": "Lino Flores",         "birth_date": "2003-02-14T00:00:00", "fiscal_number": "110000006"},
            {"name": "Murilo Gama",         "birth_date": "1996-06-28T00:00:00", "fiscal_number": "110000007"},
            {"name": "Nilton Henrique",     "birth_date": "2000-11-11T00:00:00", "fiscal_number": "110000008"},
            {"name": "Otávio Inácio",       "birth_date": "2001-04-24T00:00:00", "fiscal_number": "110000009"},
            {"name": "Palmiro Jardim",      "birth_date": "1994-07-08T00:00:00", "fiscal_number": "110000010"},
        ],
    },
    {
        "nome": "(12) FC Tomar",
        "responsavel": "Gracindo Lacerda",
        "email": "gracindo@fctomar.pt",
        "telefone": "912000012",
        "jogadores": [
            {"name": "Quirino Melo",        "birth_date": "1999-01-22T00:00:00", "fiscal_number": "120000001"},
            {"name": "Romualdo Neves",      "birth_date": "2001-05-09T00:00:00", "fiscal_number": "120000002"},
            {"name": "Silvano Osório",      "birth_date": "1998-08-26T00:00:00", "fiscal_number": "120000003"},
            {"name": "Tobias Pacheco",      "birth_date": "2002-12-12T00:00:00", "fiscal_number": "120000004"},
            {"name": "Urbano Quental",      "birth_date": "1997-04-29T00:00:00", "fiscal_number": "120000005"},
            {"name": "Valério Raposo",      "birth_date": "2003-08-15T00:00:00", "fiscal_number": "120000006"},
            {"name": "Wander Soares",       "birth_date": "1996-03-02T00:00:00", "fiscal_number": "120000007"},
            {"name": "Xisto Teles",         "birth_date": "2000-07-18T00:00:00", "fiscal_number": "120000008"},
            {"name": "Ygor Ulisses",        "birth_date": "2001-10-31T00:00:00", "fiscal_number": "120000009"},
            {"name": "Zózimo Vargas",       "birth_date": "1993-02-14T00:00:00", "fiscal_number": "120000010"},
        ],
    },
    {
        "nome": "(13) AD Ferreira do Zêzere",
        "responsavel": "Aníbal Wenceslau",
        "email": "anibal@adfz.pt",
        "telefone": "912000013",
        "jogadores": [
            {"name": "Abel Xavier",         "birth_date": "1999-06-10T00:00:00", "fiscal_number": "130000001"},
            {"name": "Bráulio Yanes",       "birth_date": "2001-10-27T00:00:00", "fiscal_number": "130000002"},
            {"name": "Calisto Zagalo",      "birth_date": "1998-02-13T00:00:00", "fiscal_number": "130000003"},
            {"name": "Demétrio Abílio",     "birth_date": "2002-07-01T00:00:00", "fiscal_number": "130000004"},
            {"name": "Euclides Bastos",     "birth_date": "1997-11-15T00:00:00", "fiscal_number": "130000005"},
            {"name": "Fabrício Caires",     "birth_date": "2003-04-02T00:00:00", "fiscal_number": "130000006"},
            {"name": "Gervasio Dinis",      "birth_date": "1996-08-19T00:00:00", "fiscal_number": "130000007"},
            {"name": "Hélio Espírito",      "birth_date": "2000-01-05T00:00:00", "fiscal_number": "130000008"},
            {"name": "Inácio Falcão",       "birth_date": "2001-05-22T00:00:00", "fiscal_number": "130000009"},
            {"name": "Juvêncio Galvão",     "birth_date": "1993-09-08T00:00:00", "fiscal_number": "130000010"},
        ],
    },
    {
        "nome": "(14) SC Torres Novas",
        "responsavel": "Kilson Henrique",
        "email": "kilson@sctorresnovas.pt",
        "telefone": "912000014",
        "jogadores": [
            {"name": "Lauro Inocêncio",     "birth_date": "1999-03-17T00:00:00", "fiscal_number": "140000001"},
            {"name": "Maurício Jales",      "birth_date": "2001-07-04T00:00:00", "fiscal_number": "140000002"},
            {"name": "Nataniel Kiko",       "birth_date": "1998-10-21T00:00:00", "fiscal_number": "140000003"},
            {"name": "Octávio Lança",       "birth_date": "2002-02-07T00:00:00", "fiscal_number": "140000004"},
            {"name": "Prudêncio Maia",      "birth_date": "1997-06-24T00:00:00", "fiscal_number": "140000005"},
            {"name": "Querubim Naves",      "birth_date": "2003-11-10T00:00:00", "fiscal_number": "140000006"},
            {"name": "Raimundo Ouro",       "birth_date": "1996-04-28T00:00:00", "fiscal_number": "140000007"},
            {"name": "Salústio Pena",       "birth_date": "2000-09-14T00:00:00", "fiscal_number": "140000008"},
            {"name": "Teodoro Quinta",      "birth_date": "2001-12-27T00:00:00", "fiscal_number": "140000009"},
            {"name": "Ugolino Ramos",       "birth_date": "1994-06-12T00:00:00", "fiscal_number": "140000010"},
        ],
    },
    {
        "nome": "(15) CF Entroncamento",
        "responsavel": "Vergílio Saraiva",
        "email": "vergilio@cfentro.pt",
        "telefone": "912000015",
        "jogadores": [
            {"name": "Waldo Tavares",       "birth_date": "1999-01-28T00:00:00", "fiscal_number": "150000001"},
            {"name": "Xico Uva",            "birth_date": "2001-05-15T00:00:00", "fiscal_number": "150000002"},
            {"name": "Yannick Vilas",       "birth_date": "1998-09-01T00:00:00", "fiscal_number": "150000003"},
            {"name": "Zeno Aguiar",         "birth_date": "2002-01-18T00:00:00", "fiscal_number": "150000004"},
            {"name": "Adão Bessa",          "birth_date": "1997-05-05T00:00:00", "fiscal_number": "150000005"},
            {"name": "Bonifácio Cid",       "birth_date": "2003-10-22T00:00:00", "fiscal_number": "150000006"},
            {"name": "Cândido Deus",        "birth_date": "1996-03-10T00:00:00", "fiscal_number": "150000007"},
            {"name": "Dário Escobar",       "birth_date": "2000-07-26T00:00:00", "fiscal_number": "150000008"},
            {"name": "Emídio Faro",         "birth_date": "2001-11-09T00:00:00", "fiscal_number": "150000009"},
            {"name": "Flávio Gil",          "birth_date": "1993-04-24T00:00:00", "fiscal_number": "150000010"},
        ],
    },
    {
        "nome": "(16) UD Rio Maior",
        "responsavel": "Gonçalo Hora",
        "email": "goncalo@udriomaior.pt",
        "telefone": "912000016",
        "jogadores": [
            {"name": "Heitor Ilha",         "birth_date": "1999-08-13T00:00:00", "fiscal_number": "160000001"},
            {"name": "Ilídio Julho",        "birth_date": "2001-12-30T00:00:00", "fiscal_number": "160000002"},
            {"name": "Jair Kuala",          "birth_date": "1998-04-16T00:00:00", "fiscal_number": "160000003"},
            {"name": "Kiko Lemos",          "birth_date": "2002-09-03T00:00:00", "fiscal_number": "160000004"},
            {"name": "Leopoldo Maga",       "birth_date": "1997-01-20T00:00:00", "fiscal_number": "160000005"},
            {"name": "Mendo Nobre",         "birth_date": "2003-06-07T00:00:00", "fiscal_number": "160000006"},
            {"name": "Névio Olival",        "birth_date": "1996-10-24T00:00:00", "fiscal_number": "160000007"},
            {"name": "Osmar Preto",         "birth_date": "2000-03-11T00:00:00", "fiscal_number": "160000008"},
            {"name": "Pascoal Quim",        "birth_date": "2001-07-28T00:00:00", "fiscal_number": "160000009"},
            {"name": "Quintiliano Rego",    "birth_date": "1993-12-15T00:00:00", "fiscal_number": "160000010"},
        ],
    },
    {
        "nome": "(17) FC Santarém",
        "responsavel": "Rosendo Sena",
        "email": "rosendo@fcsantarem.pt",
        "telefone": "912000017",
        "jogadores": [
            {"name": "Sancho Tejo",         "birth_date": "1999-05-31T00:00:00", "fiscal_number": "170000001"},
            {"name": "Timóteo Uba",         "birth_date": "2001-09-17T00:00:00", "fiscal_number": "170000002"},
            {"name": "Ulrico Vaz",          "birth_date": "1998-01-04T00:00:00", "fiscal_number": "170000003"},
            {"name": "Valentim Xara",       "birth_date": "2002-05-21T00:00:00", "fiscal_number": "170000004"},
            {"name": "Wenceslau Yves",      "birth_date": "1997-10-08T00:00:00", "fiscal_number": "170000005"},
            {"name": "Xerxes Zago",         "birth_date": "2003-03-25T00:00:00", "fiscal_number": "170000006"},
            {"name": "Ygor Anes",           "birth_date": "1996-08-12T00:00:00", "fiscal_number": "170000007"},
            {"name": "Zenão Belo",          "birth_date": "2000-12-29T00:00:00", "fiscal_number": "170000008"},
            {"name": "Acácio Cano",         "birth_date": "2001-06-13T00:00:00", "fiscal_number": "170000009"},
            {"name": "Balduíno Duro",       "birth_date": "1993-10-27T00:00:00", "fiscal_number": "170000010"},
        ],
    },
    {
        "nome": "(18) AD Abrantes",
        "responsavel": "Camilo Enes",
        "email": "camilo@adabrantes.pt",
        "telefone": "912000018",
        "jogadores": [
            {"name": "Dionísio Fiel",       "birth_date": "1999-02-14T00:00:00", "fiscal_number": "180000001"},
            {"name": "Egas Gato",           "birth_date": "2001-06-01T00:00:00", "fiscal_number": "180000002"},
            {"name": "Fonseca Hale",        "birth_date": "1998-09-18T00:00:00", "fiscal_number": "180000003"},
            {"name": "Gaudêncio Ivo",       "birth_date": "2002-01-05T00:00:00", "fiscal_number": "180000004"},
            {"name": "Henrique Jota",       "birth_date": "1997-05-22T00:00:00", "fiscal_number": "180000005"},
            {"name": "Ilário Kosta",        "birth_date": "2003-10-09T00:00:00", "fiscal_number": "180000006"},
            {"name": "Jacinto Lima",        "birth_date": "1996-03-27T00:00:00", "fiscal_number": "180000007"},
            {"name": "Karim Mano",          "birth_date": "2000-08-13T00:00:00", "fiscal_number": "180000008"},
            {"name": "Leovigildo Nata",     "birth_date": "2001-12-26T00:00:00", "fiscal_number": "180000009"},
            {"name": "Melquíades Ouro",     "birth_date": "1993-07-11T00:00:00", "fiscal_number": "180000010"},
        ],
    },
    {
        "nome": "(19) SC Peniche",
        "responsavel": "Narciso Pena",
        "email": "narciso@scpeniche.pt",
        "telefone": "912000019",
        "jogadores": [
            {"name": "Olegário Quinta",     "birth_date": "1999-04-28T00:00:00", "fiscal_number": "190000001"},
            {"name": "Plácido Raia",        "birth_date": "2001-08-15T00:00:00", "fiscal_number": "190000002"},
            {"name": "Quiliano Sal",        "birth_date": "1998-12-02T00:00:00", "fiscal_number": "190000003"},
            {"name": "Reginaldo Tejo",      "birth_date": "2002-04-19T00:00:00", "fiscal_number": "190000004"},
            {"name": "Sinésio Uva",         "birth_date": "1997-09-05T00:00:00", "fiscal_number": "190000005"},
            {"name": "Tarcísio Vela",       "birth_date": "2003-01-23T00:00:00", "fiscal_number": "190000006"},
            {"name": "Ulisses Xico",        "birth_date": "1996-06-10T00:00:00", "fiscal_number": "190000007"},
            {"name": "Venâncio Yule",       "birth_date": "2000-10-27T00:00:00", "fiscal_number": "190000008"},
            {"name": "Walmir Zeno",         "birth_date": "2001-03-12T00:00:00", "fiscal_number": "190000009"},
            {"name": "Xandinho Abreu",      "birth_date": "1993-08-26T00:00:00", "fiscal_number": "190000010"},
        ],
    },
    {
        "nome": "(20) AD Torres Vedras",
        "responsavel": "Yaroslav Bravo",
        "email": "yaroslav@adtv.pt",
        "telefone": "912000020",
        "jogadores": [
            {"name": "Zéfiro Carmo",        "birth_date": "1999-02-09T00:00:00", "fiscal_number": "200000001"},
            {"name": "Adelino Dama",        "birth_date": "2001-06-26T00:00:00", "fiscal_number": "200000002"},
            {"name": "Belmiro Ema",         "birth_date": "1998-10-13T00:00:00", "fiscal_number": "200000003"},
            {"name": "Celestino Fava",      "birth_date": "2002-03-01T00:00:00", "fiscal_number": "200000004"},
            {"name": "Dinis Gana",          "birth_date": "1997-07-18T00:00:00", "fiscal_number": "200000005"},
            {"name": "Eládio Hino",         "birth_date": "2003-12-04T00:00:00", "fiscal_number": "200000006"},
            {"name": "Fidelis Ibis",        "birth_date": "1996-05-22T00:00:00", "fiscal_number": "200000007"},
            {"name": "Gualter Jade",        "birth_date": "2000-09-08T00:00:00", "fiscal_number": "200000008"},
            {"name": "Hermínio Kino",       "birth_date": "2001-01-25T00:00:00", "fiscal_number": "200000009"},
            {"name": "Inocêncio Lago",      "birth_date": "1993-06-10T00:00:00", "fiscal_number": "200000010"},
        ],
    },
    {
        "nome": "(21) FC Mafra",
        "responsavel": "Januário Medo",
        "email": "januario@fcmafra.pt",
        "telefone": "912000021",
        "jogadores": [
            {"name": "Ladislau Naco",       "birth_date": "1999-03-27T00:00:00", "fiscal_number": "210000001"},
            {"name": "Macário Obra",        "birth_date": "2001-07-14T00:00:00", "fiscal_number": "210000002"},
            {"name": "Norberto Paco",       "birth_date": "1998-11-01T00:00:00", "fiscal_number": "210000003"},
            {"name": "Olímpio Quero",       "birth_date": "2002-04-18T00:00:00", "fiscal_number": "210000004"},
            {"name": "Pelino Raio",         "birth_date": "1997-08-04T00:00:00", "fiscal_number": "210000005"},
            {"name": "Quim Sardo",          "birth_date": "2003-01-21T00:00:00", "fiscal_number": "210000006"},
            {"name": "Rosário Taca",        "birth_date": "1996-06-08T00:00:00", "fiscal_number": "210000007"},
            {"name": "Sebastião Uço",       "birth_date": "2000-10-25T00:00:00", "fiscal_number": "210000008"},
            {"name": "Timóteo Vira",        "birth_date": "2001-03-10T00:00:00", "fiscal_number": "210000009"},
            {"name": "Urânio Xeno",         "birth_date": "1993-07-24T00:00:00", "fiscal_number": "210000010"},
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
    print("  Seed - Torneio Vila PMOS 2026 Masculino")
    print("=" * 55)
    print(f"Backend: {BASE_URL}\n")

    with httpx.Client(base_url=BASE_URL, timeout=30) as client:
        token = login(client)

        # Torneio
        torneio_id = criar_torneio(client, token, "Torneio Vila PMOS 2026 Masculino")

        # Equipas
        print("A registar equipas...\n")
        equipa_ids = []
        for e in EQUIPAS:
            eid = registar_equipa(
                client, token, torneio_id,
                e["nome"], e["responsavel"], e["email"], e["telefone"],
                e["jogadores"],
            )
            equipa_ids.append(eid)
        print()

        # Confirmar jogadores
        confirmar_jogadores(client, token)

        print("=" * 55)
        print("  Seed concluído com sucesso!")
        print(f"  Torneio ID : {torneio_id}")
        print(f"  Equipas    : {len(equipa_ids)}")
        print(f"  Jogadores  : {len(equipa_ids) * 10} (confirmados)")
        print("=" * 55)


if __name__ == "__main__":
    main()
