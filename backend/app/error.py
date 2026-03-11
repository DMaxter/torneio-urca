from fastapi import HTTPException, status


class Error:
    @staticmethod
    def not_found(entity: str):
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": f"{entity} não existente",
                "message": f"{entity} not found",
            },
        )

    @staticmethod
    def internal():
        return HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": "Internal error", "message": "Erro interno"},
        )

    @staticmethod
    def invalid_id(entity: str):
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"Invalid ID for {entity}",
                "message": f"ID inválido para {entity}",
            },
        )

    @staticmethod
    def player_not_in_team():
        return HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "error": "Player not in team",
                "message": "Jogador não alocado à equipa",
            },
        )

    @staticmethod
    def player_not_in_game():
        return HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "error": "Player not in game",
                "message": "Jogador não alocado ao jogo",
            },
        )

    @staticmethod
    def game_not_in_tournament():
        return HTTPException(
            status_code=status.HTTP_412_PRECONDITION_FAILED,
            detail={
                "error": "Game not in tournament",
                "message": "Jogo não alocado ao torneo",
            },
        )

    @staticmethod
    def game_not_in_progress():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Game not in progress",
                "message": "O jogo não está a decorrer",
            },
        )

    @staticmethod
    def user_not_player():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "User not a player",
                "message": "Utilizador não é um jogador",
            },
        )

    @staticmethod
    def game_calls_not_delivered():
        return HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Game calls not delivered",
                "message": "As fichas de jogo ainda não foram entregues",
            },
        )
