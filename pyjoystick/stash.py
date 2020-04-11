

__all__ = ['Stash']


class Stash(list):
    """List that is easy to search for matching contents instead of using an index."""

    @staticmethod
    def compare(list_item, key):
        """Compare each list item with the given key to find the right object in the list."""
        return list_item == key

    def __getitem__(self, key):
        if isinstance(key, int):
            try:
                return super(Stash, self).__getitem__(key)
            except (IndexError, Exception):
                pass

        for list_item in self:
            if self.compare(list_item, key):
                return list_item

        raise KeyError('Invalid item key given!')

    def __setitem__(self, key, value):
        if isinstance(key, int):
            return super(Stash, self).__setitem__(key, value)

        for i, list_item in enumerate(self):
            if self.compare(list_item, key):
                return super(Stash, self).__setitem__(i, value)

        raise KeyError('Invalid item key given!')

    def __contains__(self, key):
        if isinstance(key, int):
            return super(Stash, self).__getitem__(key)

        for list_item in self:
            if self.compare(list_item, key):
                return True

        return False

    def pop(self, key, default=None):
        """Find, remove, and return the given key or default value.

        Args:
            key (int/str/object): Key to use to find the value in the list
            default (object)[None]: Default value to return. If None and key is not found raise a KeyError

        Returns:
            value (object): Returns the value found

        Raises:
            error (KeyError): If default is None and the key was not found.
        """
        if isinstance(key, int):
            try:
                return super(Stash, self).pop(key)
            except (IndexError, Exception):
                pass

        for i, list_item in enumerate(self):
            if self.compare(list_item, key):
                return super(Stash, self).pop(i)

        if default is None:
            raise KeyError('Invalid item key given!')
        return default

    def remove(self, key):
        """Find, remove, and return the given key.

        Args:
            key (int/str/object): Key to use to find the value in the list

        Returns:
            value (object): Returns the value found

        Raises:
            error (ValueError): If default is None and the key was not found.
        """
        if isinstance(key, int):
            try:
                return super(Stash, self).pop(key)
            except (IndexError, Exception):
                pass

        for i, list_item in enumerate(self):
            if self.compare(list_item, key):
                return super(Stash, self).pop(i)

        raise ValueError('list.remove(x): x not in list')
