#!/usr/bin/env python
'Unit test for trepan.lib.complete'

import unittest
from import_relative import import_relative
Mcomplete = import_relative('lib.complete', '...trepan')

class TestLibComplete(unittest.TestCase):

    def test_complete(self):

        hash = {'ab': 1, 'aac': 2, 'aa': 3, 'a':  4}
        ary = sorted(hash.keys())
        for result, prefix in [
                [[], 'b'], [ary, 'a'],
                [['aa', 'aac'], 'aa'],
                [ary, ''], [['ab'], 'ab'], [[], 'abc']]:
            self.assertEqual(result, Mcomplete.complete_token(ary, prefix),
                             "Trouble matching %s on %s" %
                              (repr(ary), prefix))
            pass
        for result_keys, prefix in [
            [ary, 'a'],
            [['aa', 'aac'], 'aa'],
            [['ab'], 'ab'], [[], 'abc']]:
            result = [[key, hash[key]] for key in result_keys]
            self.assertEqual(result, Mcomplete.complete_token_with_next(hash, prefix),
                             "Trouble matching %s on %s" %
                             (repr(hash), prefix))
            pass
        return

    def test_next_token(self):
        x = '  now is  the  time'
        for pos, expect in [
                [0, [ 5, 'now']],
                [2, [ 5, 'now']],
                [5, [ 8, 'is']],
                [8, [13, 'the']],
                [9, [13, 'the']],
                [13, [19, 'time']],
                [19, [19, '']],
                ]:
            self.assertEqual(expect, Mcomplete.next_token(x, pos),
                             "Trouble with next_token(%s, %d)" % (x, pos))
            pass
        return
    pass

if __name__ == '__main__':
    unittest.main()
    pass
