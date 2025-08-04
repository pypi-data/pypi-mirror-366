import logging
from typing import List
import socket
import aiohttp

from fakts_next.grants.remote.models import FaktsEndpoint

logger = logging.getLogger(__name__)


async def acheck_supported_layers(endpoint: FaktsEndpoint) -> List[str]:
    supported_layers: list[str] = []

    if endpoint.layers:
        logger.debug(f"Checking supported layers for {endpoint.name}")
        for layer in endpoint.layers:
            print(f"Checking layer {layer}")
            if layer.get_probe:
                # check if we access to the web layer
                async with aiohttp.ClientSession() as session:
                    try:
                        async with session.get(layer.get_probe) as response:
                            await response.text()

                    except Exception as e:
                        logger.debug(f"Could not access web layer: {e}")
                        continue

            if layer.dns_probe:
                # check if we access to the headscale layer
                try:
                    socket.gethostbyname(layer.dns_probe)
                except Exception as e:
                    print(f"Could not access headscale layer: {e}")
                    logger.debug(f"Could not access headscale layer: {e}")
                    continue

            supported_layers.append(layer.identifier)

    print("Supported layers", supported_layers)

    return supported_layers


def could_copy_to_clipboard(text: str) -> bool:
    """Copies text to clipboard if possible

    This function tries to copy the text to the clipboard.
    If it fails, it returns False, otherwise True.

    Parameters
    ----------
    text : str
        The text to copy to the clipboard

    Returns
    -------
    bool
        Could the text be copied to the clipboard?
    """

    try:
        import pyperclip  # type: ignore[import]

        pyperclip.copy(text)
        return True
    except ImportError:
        logger.debug("Could not import pyperclip, not copying to clipboard")
        return False


try:
    from rich import print as rprint
    from rich.panel import Panel

    def print_device_code_prompt(querystring: str, url: str, code: str) -> None:
        """Prints the device code prompt

        This function prints the device code prompt using rich.
        It also copies the code to the clipboard if possible.

        Parameters
        ----------
        querystring : str
            The querystring to visit
        url : str
            The url to visit (without querystring)
        code : str
            The code to enter on the website
        scopes : List[str]
            The scopes to grant
        """

        could_copy_to_clipboard(code)
        rprint(
            Panel.fit(
                f"""
    Please visit the following URL:
    [bold green][link={querystring}]{querystring}[/link][/bold green]
    or go to this URL:
    [bold green][link={url}]{url}[/link][/bold green]
    and enter the code:
    [bold blue]{code}[/bold blue]
        """,
                title="Device Code Grant",
                title_align="center",
            )
        )

    def print_succesfull_login() -> None:
        """Prints the successful login message

        This function prints the successful login message using rich.
        """
        rprint(
            Panel.fit(
                "You have successfully logged in!",
                title="Device Code Grant",
                title_align="center",
            )
        )

except ImportError:

    def print_device_code_prompt(querystring: str, url: str, code: str) -> None:
        """Prints the device code prompt

        This function prints the device code prompt using rich.
        It also copies the code to the clipboard if possible.

        Parameters
        ----------
        querystring : str
            The querystring to visit
        url : str
            The url to visit (without querystring)
        code : str
            The code to enter on the website
        scopes : List[str]
            The scopes to grant
        """
        could_copy = could_copy_to_clipboard(code)
        print("Please visit the following URL:")
        print("\t" + querystring)
        print("Or go to this URL:")
        print("\t" + url + "device")
        print("And enter the following code:")
        print("\t" + code)
        if could_copy:
            print("Code has been copied to clipboard")

    def print_succesfull_login() -> None:
        """Prints the successful login message

        This function prints the successful login message using rich.
        """
        print("You have successfully logged in!")
