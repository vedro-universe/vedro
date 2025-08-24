# this module is for backward compatibility
from .di import ConflictError, Container, Factory, FactoryType, Singleton

__all__ = ("Container", "Factory", "Singleton", "FactoryType", "ConflictError")
