"""
Client class for managing OpenXR clients in Monado.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .types import ClientState
from .errors import MonadoError

if TYPE_CHECKING:
    from .libmonado import LibMonado


class Client:
    """
    Represents an OpenXR client connected to Monado.
    
    A client is typically an OpenXR application that has connected to the
    Monado compositor. This class allows you to query information about
    the client and control its state.
    """
    
    def __init__(self, libmonado: "LibMonado", client_id: int):
        """
        Initialize a Client instance.
        
        Args:
            libmonado: The LibMonado instance
            client_id: The unique client ID assigned by Monado
        """
        self._lib = libmonado
        self._id = client_id
    
    @property
    def id(self) -> int:
        """The unique client ID."""
        return self._id
    
    def name(self) -> str:
        """
        Get the name of the client application.
        
        Returns:
            The client name as reported by the application
        """
        return self._lib.get_client_name(self._id)
    
    def state(self) -> ClientState:
        """
        Get the current state flags for this client.
        
        Returns:
            ClientState flags indicating if the client is primary,
            focused, has IO active, or is visible
        """
        return self._lib.get_client_state(self._id)
    
    def is_primary(self) -> bool:
        """Check if this client is the primary client."""
        return bool(self.state() & ClientState.ClientPrimaryApp)

    def is_focused(self) -> bool:
        """Check if this client has focus."""
        return bool(self.state() & ClientState.ClientSessionFocused)

    def is_io_active(self) -> bool:
        """Check if IO is active for this client."""
        return bool(self.state() & ClientState.ClientIoActive)

    def is_visible(self) -> bool:
        """Check if this client is visible."""
        return bool(self.state() & ClientState.ClientSessionVisible)

    def is_session_active(self) -> bool:
        """Check if this client's session is active."""
        return bool(self.state() & ClientState.ClientSessionActive)

    def is_overlay(self) -> bool:
        """Check if this client is an overlay."""
        return bool(self.state() & ClientState.ClientSessionOverlay)
    
    def set_primary(self) -> None:
        """
        Set this client as the primary client.
        
        The primary client receives special treatment from the compositor.
        """
        self._lib.set_client_primary(self._id)
    
    def set_focused(self) -> None:
        """
        Set this client as the focused client.
        
        The focused client receives input events.
        """
        self._lib.set_client_focused(self._id)
    
    def set_io_active(self, active: bool) -> None:
        """
        Set the IO active state for this client.
        
        Args:
            active: True to enable IO, False to disable
        """
        current_state = self.state()
        is_active = bool(current_state & ClientState.ClientIoActive)
        
        if is_active != active:
            self._lib.toggle_client_io_active(self._id)
    
    def __repr__(self) -> str:
        """String representation of the client."""
        try:
            name = self.name()
            state = self.state()
            return f"Client(id={self._id}, name='{name}', state={state})"
        except MonadoError:
            return f"Client(id={self._id}, <disconnected>)"
    
    def __eq__(self, other: object) -> bool:
        """Check if two clients are the same."""
        if not isinstance(other, Client):
            return NotImplemented
        return self._id == other._id
    
    def __hash__(self) -> int:
        """Hash based on client ID."""
        return hash(self._id)
