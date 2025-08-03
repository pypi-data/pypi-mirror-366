class LeafMixin:
    def get_path(self) -> str:
        """
        Get the path of the leaf in the diagnostics tree.

        Returns:
            str: The path of the leaf.
        """
        return f'{self._parent.name}/{self.name}'