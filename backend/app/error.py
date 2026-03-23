"""
Custom error helpers for the tournament API.

Provides a collection of pre-configured HTTP exceptions with localized
error messages in Portuguese for consistent API error responses.
"""

from fastapi import HTTPException, status


class Error:
    @staticmethod
    def not_found(entity: str):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": f"{entity} não existente"},
        )

    @staticmethod
    def internal():
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Erro interno"},
        )

    @staticmethod
    def invalid_id(entity: str):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"ID inválido para {entity}"},
        )

    @staticmethod
    def player_not_in_team():
        return HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={"error": "Jogador não alocado à equipa"},
        )

    @staticmethod
    def player_not_in_game():
        return HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={"error": "Jogador não alocado ao jogo"},
        )

    @staticmethod
    def game_not_in_tournament():
        return HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={"error": "Jogo não alocado ao torneio"},
        )

    @staticmethod
    def game_not_in_progress():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "O jogo não está a decorrer"},
        )

    @staticmethod
    def user_not_player():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "Utilizador não é um jogador"},
        )

    @staticmethod
    def game_calls_not_delivered():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "As fichas de jogo ainda não foram entregues"},
        )

    @staticmethod
    def conflict(message: str):
        return HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": message},
        )

    @staticmethod
    def unauthorized(message: str):
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": message},
        )

    @staticmethod
    def bad_request(message: str):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": message},
        )
