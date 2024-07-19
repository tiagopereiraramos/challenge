import logging
from colorlog import ColoredFormatter

class Logs:
    """
    Classe para gerenciamento de logs com formatação colorida.
    """

    def __init__(self) -> None:
        pass

    @staticmethod
    def Returnlog(nome: str, nome_funcao: str = ""):
        """
        Configura e retorna um logger com formatação colorida.

        Parâmetros:
        -----------
        nome : str
            Nome do logger.
        nome_funcao : str, opcional
            Nome da função associada ao logger. Padrão é uma string vazia.

        Retorna:
        --------
        logging.Logger
            Objeto logger configurado.
        """
        log = logging.getLogger(nome + " -> " + nome_funcao)
        log.setLevel(logging.DEBUG)

        LOG_COLORS = {
            "DEBUG": "white",
            "INFO": "green",
            "ERROR": "red",
            "WARNING": "blue"
        }

        formatter = ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(filename)s - %(log_color)s%(levelname)-8s: %(log_color)s%(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            log_colors=LOG_COLORS,
            reset=True,
            style="%",
        )

        file_handler = logging.FileHandler(".\\Log\\log_app.log")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)

        log.addHandler(file_handler)
        log.addHandler(stream_handler)

        return log
