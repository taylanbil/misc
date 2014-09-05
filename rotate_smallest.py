#!/usr/bin/env python
"""
    from:
    http://www.braingle.com/brainteasers/44119/half-again-as-big.html

    What is the smallest integer such that if you rotate the number to the left
    you get a number that is exactly one and a half times the original number?

    (To rotate the number left, take the first digit off the front and append
    it to the end of the number. 2591 rotated to the left is 5912.)

"""


from operator import itemgetter
from pprint import pprint


__author__ = 'taylanbil'


def double_int(n, carry):
    tmp = 2 * n + carry
    return (tmp % 10, tmp >= 10)


def step_one(half_num, num, carry):
    tmp = half_num[-1]
    n, carry = double_int(tmp, carry)
    half_num.append(n)
    num.append(n)
    return half_num, num, carry


def main(leading_digit):
    half_num = [leading_digit]
    num = []
    occured_pairs = set([])
    carry = 0
    while True:
        half_num, num, carry = step_one(half_num, num, carry)
        pair = (num[-1], half_num[-2])
        if pair in occured_pairs:
            if pair[1] == leading_digit:
                args = (''.join(map(str, num[-2::-1])),
                        ''.join(map(str, half_num[-3::-1])))
                assert int(args[0]) == 2 * int(args[1])
                # print ('Leading digit\t{0}\n'
                #        'Found\t%s\nhalf\t%s\n').format(leading_digit) % args
                return int(''.join(map(str, num[-2::-1])))
            else:
                print ('Not solvable with leading digit {0}...'
                       ' I\'m at %s').format(leading_digit)
                return False
        else:
            occured_pairs.add(pair)


if __name__ == '__main__':
    ans = []
    for i in xrange(1, 10):
        ans.append((i, main(i)))
    pprint(ans)
    print('\n')
    pprint(min(ans, key=itemgetter(1))[1])

    # The answer is below:
    # The smallest number is the first one.
    #
    # [(1, 105263157894736842),
    #  (2, 210526315789473684),
    #  (3, 315789473684210526),
    #  (4, 421052631578947368),
    #  (5, 526315789473684210),
    #  (6, 631578947368421052),
    #  (7, 736842105263157894),
    #  (8, 842105263157894736),
    #  (9, 947368421052631578)]
    #
    #  Interestingly, i'th number in the list above is i times the first number.
