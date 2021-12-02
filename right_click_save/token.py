import logging

from . import the_graph, utils
from .exceptions import TheGraphQueryError


__all__ = ("Token",)


log = logging.getLogger(__name__)


class Token:
    def __init__(self, address, id_, metadata, raw):
        self.address = address
        self.id_ = int(id_, 16)
        self.metadata = metadata
        self.raw = raw

    def __repr__(self):
        return f"<{self.__class__.__name__} [{self.address}, {self.id_}]>"

    @classmethod
    def from_address(cls, address):
        data = the_graph.query_erc721(address)
        for account in data["accounts"]:
            for erc721_token in account["tokens"]:
                token_address, token_id = erc721_token["id"].split("-")

                try:
                    # ERC-721 NFT with metadata that contains or points to an image / video.
                    if token_uri := erc721_token["uri"]:
                        metadata = utils.extract_erc721_metadata(token_uri)
                        yield cls(token_address, token_id, metadata, erc721_token)
                    # ENS
                    elif token_address == "0x57f1887a8bf19b14fc0df6fd9b2acc9af147ea85":
                        domain = the_graph.query_ens_by_labelhash(token_id)
                        metadata = {"name": domain}
                        yield cls(token_address, token_id, metadata, erc721_token)
                    else:
                        log.warning("Unhandled project at %s", token_address)
                except TheGraphQueryError as e:
                    log.exception(e)
