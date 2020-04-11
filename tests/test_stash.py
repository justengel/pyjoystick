def test_stash():
    from pyjoystick.stash import Stash

    class CustomObject(object):
        def __init__(self, identifier, index, value):
            self.identifier = identifier
            self.index = index
            self.value = value

        def __eq__(self, other):
            if isinstance(other, CustomObject):
                return super().__eq__(other)
            return self.identifier == other

    li = Stash((CustomObject('{}.{}'.format(i, j), j, k) for i in range(3) for j in range(3) for k in range(3)))

    assert '0.0' in li
    assert li[0] == li['0.0'], 'Get from index does not match get from __eq__!'

    # Test pop
    item = li.pop('0.0')
    assert item.identifier == '0.0'
    assert item.index == 0
    assert item.value == 0

    try:
        li.pop(50000000)
        raise AssertionError('remove function did not raise a KeyError when not exists!')
    except KeyError:
        pass

    assert li.pop(50000000, 'Default Value') == 'Default Value', 'pop function did not return a default value!'

    # Test remove
    item = li.remove('1.0')
    assert item.identifier == '1.0'
    assert item.index == 0
    assert item.value == 0

    try:
        li.remove(50000000)
        raise AssertionError('remove function did not raise a ValueError when not exists!')
    except ValueError:
        pass


if __name__ == '__main__':
    test_stash()

    print('All tests finished successfully!')
