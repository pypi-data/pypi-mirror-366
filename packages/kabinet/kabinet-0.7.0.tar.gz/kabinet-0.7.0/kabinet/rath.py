"""The graphql rath client for  kabinet"""

from types import TracebackType
from typing import Optional
from pydantic import Field
from rath import rath
import contextvars

from rath.links.auth import AuthTokenLink

from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.shrink import ShrinkingLink
from rath.links.split import SplitLink

current_kabinet_rath: contextvars.ContextVar[Optional["KabinetRath"]] = contextvars.ContextVar(
    "current_kabinet_rath", default=None
)


class KabinetLinkComposition(TypedComposedLink):
    """Kabinet Link Composition"""

    shrinking: ShrinkingLink = Field(default_factory=ShrinkingLink)
    dicting: DictingLink = Field(default_factory=DictingLink)
    auth: AuthTokenLink
    split: SplitLink


class KabinetRath(rath.Rath):
    """Kabinet Rath

    Args:
        rath (_type_): _description_
    """

    async def __aenter__(self) -> "KabinetRath":
        """Set the current Rekuest Next Rath client in the context variable."""
        await super().__aenter__()
        current_kabinet_rath.set(self)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Unset the current Rekuest Next Rath client in the context variable."""
        await super().__aexit__(exc_type, exc_val, exc_tb)
        current_kabinet_rath.set(None)
