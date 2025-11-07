"""
Squelette du système de commandes (Undo/Redo).
- À l'étape 0, on a juste une pile vide pour cable les menus.
- À l'étape 3, on y ajoutera des vraies commandes (AddShape, MoveShape, etc.).
"""

class Command:
    """Interface minimale : chaque commande sait s'exécuter et s'annuler."""
    def do(self):
        raise NotImplementedError

    def undo(self):
        raise NotImplementedError

class CommandStack:
    """Deux piles : undo_stack et redo_stack."""
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []

    def push(self, cmd: Command):
        """Exécute la commande et la pousse dans la pile undo."""
        cmd.do()
        self.undo_stack.append(cmd)
        self.redo_stack.clear()  # toute nouvelle action invalide la redo stack

    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0

    def undo(self):
        """Annule la dernière commande et la place dans la pile redo."""
        if not self.can_undo():
            return
        cmd = self.undo_stack.pop()
        cmd.undo()
        self.redo_stack.append(cmd)

    def redo(self):
        """Refait la dernière commande annulée."""
        if not self.can_redo():
            return
        cmd = self.redo_stack.pop()
        cmd.do()
        self.undo_stack.append(cmd)
