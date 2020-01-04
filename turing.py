import string
import random
from typing import Dict, List
import copy


class Rotor:
    def __init__(self):
        self._r_offsets = self._right_offsets()
        self._l_offsets = {v: k for k, v in self._r_offsets.items()}

    def __str__(self):
        rv = 'r->l: {}\n'.format(self._r_offsets)
        rv += 'l->r: {}\n'.format(self._l_offsets)
        return rv

    def _right_offsets(self):
        offsets = {}
        destinations = list(range(1, 27))
        for i in range(1, 27):
            candidate = random.choice(destinations)
            destinations.remove(candidate)
            offsets[i] = candidate

        return offsets

    def from_right(self, x, pos):
        x = self._r_offsets[wrap_add(pos, x)]
        return x

    def from_left(self, x, pos):
        x = wrap_add(self._l_offsets[x], -pos)
        return x


Plugs = Dict[int, int]
Reflector = int


class Enigma:
    def __init__(self, plugs: Plugs,
                 rotor_positions: List[int],
                 num_rotors=1,
                 reflector_offset: int = 1):
        assert num_rotors == len(rotor_positions)
        self.rotors = [Rotor() for _ in range(num_rotors)]
        self.rotor_positions = copy.deepcopy(rotor_positions)
        self.plugs = plugs
        self.out_plugs = {v: k for k, v in plugs.items()}
        self.reflector = reflector_offset

    def __str__(self):
        rv = 'Plugs: {}\n'.format(str(self.plugs))
        rv += 'Rotors: {}\n'.format([str(x) for x in self.rotors])
        rv += 'Rotor positions: {}\n'.format(str(self.rotor_positions))
        rv += 'Reflector: {}\n'.format(str(self.reflector))
        return rv

    def _advance_rotors(self, idx=0):
        next_pos = self.rotor_positions[idx] + 1
        if next_pos <= 26:
            # print('advancing {}'.format(idx))
            self.rotor_positions[idx] = next_pos
        else:
            self.rotor_positions[idx] = 1
            if idx + 1 < len(self.rotors):
                # print('about to advance {}'.format(idx+1))
                self._advance_rotors(idx + 1)

    def enc(self, message):
        rv = ''
        for c in message:
            ci = ord(c) % ord('a') + 1
            # print('start {}'.format(ci), end=' ')
            ci = self.plugs.get(ci, ci)
            for r, pos in zip(self.rotors, self.rotor_positions):
                ci = r.from_right(ci, pos)
            # print('forward {}'.format(ci), end=' ')

            ci = wrap_add(ci, self.reflector)
            # print('reflect {}'.format(ci), end=' ')
            for r, pos in zip(reversed(self.rotors), reversed(self.rotor_positions)):
                ci = r.from_left(ci, pos)
            print('backward {}'.format(ci))
            ci = self.out_plugs.get(ci, ci)
            print('out {}'.format(ci))
            self._advance_rotors()

            rv += chr(ci + ord('a') - 1)

        return rv

    def dec(self, message):
        rv = ''
        for c in message:
            ci = ord(c) % ord('a') + 1
            # print('start {}'.format(ci), end=' ')
            ci = self.plugs.get(ci, ci)
            for r, pos in zip(self.rotors, self.rotor_positions):
                ci = r.from_right(ci, pos)

            # print('forward {}'.format(ci), end=' ')
            ci = wrap_add(ci,  -self.reflector)
            # print('reflect {}'.format(ci), end=' ')
            for r, pos in zip(reversed(self.rotors), reversed(self.rotor_positions)):
                ci = r.from_left(ci, pos)

            print('backward {}'.format(ci))
            ci = self.out_plugs.get(ci, ci)
            print('out {}'.format(ci))
            self._advance_rotors()

            rv += chr(ci + ord('a') - 1)

        return rv


def wrap_add(x, y):
    return (x - 1 + y) % 26 + 1


def create_message(length: int):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))


random.seed(2)
test_rotor = Rotor()
start = 5
for start_position in range(20):
    forward = test_rotor.from_right(start, start_position)
    backward = test_rotor.from_left(forward, start_position)
    assert start == backward, '\n{} {}'.format(start, backward)


mess = 'e'
starting_rotor_positions = [1]
e = Enigma({1: 5}, starting_rotor_positions)

encrypted = e.enc(mess)
e.rotor_positions = starting_rotor_positions
decrypted = e.dec(encrypted)
ass_mess = '\n{} to \n{} back to\n{}'.format(mess, encrypted, decrypted)
assert mess == decrypted, ass_mess

for _ in range(20):
    mess = create_message(24)

    starting_rotor_positions = [1]
    e = Enigma({1: 5}, starting_rotor_positions)

    encrypted = e.enc(mess)
    e.rotor_positions = starting_rotor_positions
    decrypted = e.dec(encrypted)
    ass_mess = '\n{} to \n{} back to\n{}'.format(mess, encrypted, decrypted)
    assert mess == decrypted, ass_mess
    # print(ass_mess)

mess = 'thisreport'

starting_rotor_positions = [1]
e = Enigma({1: 5}, starting_rotor_positions)

encrypted = e.enc(mess)
e.rotor_positions = starting_rotor_positions
decrypted = e.dec(encrypted)
ass_mess = '{} to \n{} back to\n{}'.format(mess, encrypted, decrypted)
print(ass_mess)
assert mess == decrypted, ass_mess
