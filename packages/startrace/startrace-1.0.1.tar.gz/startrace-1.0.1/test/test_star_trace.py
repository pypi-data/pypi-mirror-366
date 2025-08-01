# This file contains a few tests to run before pushing a new version

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import pytest
import numpy as np

from startrace.star_trace import *



def test_parameters():
    tok = Token('test')
    assert tok.phrases[0] == 'test'
    assert tok.num is None
    assert tok.iter is None

    tok = Token('token', 1.0, Iter(0.0, 1.0, 1.0))
    assert tok.phrases[0] == 'token'
    assert tok.num == 1.0
    assert tok.iter.start == 0.0
    assert tok.iter.end == 1.0
    assert tok.iter.step == 1.0

    tok = Token(['test', 'token'])
    assert tok.phrases[0] == 'test'
    assert tok.phrases[1] == 'token'
    assert tok.num == 0
    assert tok.iter.start == 0
    assert tok.iter.end == 1
    assert tok.iter.step == 1

    tok = Token('test', [0, 1, 2])
    assert tok.phrases[0] == 'test'
    assert tok.num == 0
    assert tok.iter.start == 0
    assert tok.iter.end == 2
    assert tok.iter.step == 1



    values = np.arange(0, 10, 1)
    tok = Token('test', values)
    assert tok.phrases[0] == 'test'
    assert tok.num == 0
    assert tok.iter.start == 0
    assert tok.iter.end == 9
    assert tok.iter.step == 1

    values = np.arange(1, 5, 1)
    tok = Token('', values)
    assert tok.phrases[0] == ''
    assert tok.num == 1
    assert tok.iter.start == 1
    assert tok.iter.end == 4
    assert tok.iter.step == 1


    pat = Pattern([
        Token('test'),
        Token('token', 0.0, Iter(0.0, 0.0, 1.0))
    ])
    assert pat.tokens[0].phrases[0] == 'test'
    assert pat.tokens[0].num is None
    assert pat.tokens[1].phrases[0] == 'token'
    assert pat.tokens[1].num == 0.0

def test_alternate_inputs():
    tok = Token('', 0, (0, 0, 1))
    assert tok.iter.start == 0.0
    assert tok.iter.end == 0.0
    assert tok.iter.step == 1.0

    pat = Pattern([
        Token('test'),
        tok
    ])
    assert pat.tokens[0].phrases[0] == 'test'
    assert pat.tokens[1].phrases[0] == ''
    assert pat.tokens[1].num == 0
    assert pat.tokens[1].iter.start == 0
    assert pat.tokens[1].iter.end == 0
    assert pat.tokens[1].iter.step == 1

def test_invalid_inputs():
    with pytest.raises(TypeError):
        Token('test', 0.0)

    with pytest.raises(TypeError):
        Token('token', 0, Iter(0.0, 1.0, 1.0))

    with pytest.raises(ValueError):
        Token('', 0, Iter(1, 0, 1))

    with pytest.raises(ValueError):
        Token(['test', 'token'], 0, Iter(0, 2, 1))

    with pytest.raises(ValueError):
        Token(['test', 'token'], 2, Iter(0, 1, 1))

    with pytest.raises(TypeError):
        Iter(0, 1, 1.0)

    with pytest.raises(ValueError):
        values = np.arange(1, 5, 1)
        phrases = ['test', 'token']
        tok = Token(phrases, values)

def test_pattern():
    pat = Pattern([
        Token('test_'),
        Token('token:', 0, Iter(0, 0, 1))
    ])
    assert pat.get_pattern() == 'test_token:0'

    pat = Pattern([
        Token(['testing_', 'test_']),
        Token('token:', 1, Iter(0, 1, 1)),
    ])
    assert pat.get_pattern() == 'testing_token:1'

def test_increment():
    pat = Pattern([
        Token('test_'),
        Token('token:', 0, Iter(0, 5, 1))
    ])
    for i in range(5):
        assert pat.get_pattern() == 'test_token:' + str(i)
        pat.increment()

    pat = Pattern([
        Token(['testing_', 'test_']),
        Token('token')
    ])
    assert pat.get_pattern() == 'testing_token'
    pat.increment()
    assert pat.get_pattern() == 'test_token'
    pat.increment()
    assert pat.get_pattern() == 'testing_token'

    pat = Pattern([
        Token('test_'),
        Token('', 0, Iter(0, 2, 1)),
        Token('', 0, Iter(0, 9, 1))
    ])
    for i in range(3):
        assert pat.get_pattern() == 'test_' + str(i) + '0'
        for j in range(10):
            assert pat.get_pattern() == 'test_' + str(i) + str(j)
            pat.increment()

if __name__ == '__main__':
    test_parameters()