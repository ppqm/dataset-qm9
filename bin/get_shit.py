#!/usr/bin/env python

from subprocess import Popen, PIPE
import sys
import numpy as np
import re

ATOMIZATION = {}
ATOMIZATION['h'] = -0.499809832232
ATOMIZATION['c'] = -37.758578459
ATOMIZATION['n'] = -54.497609443022
ATOMIZATION['o'] = -74.957264928663
ATOMIZATION['s'] = -397.616129888347


def shell(cmd, shell=False):

    if shell:
        p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE)
    else:
        cmd = cmd.split()
        p = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE)

    output, err = p.communicate()
    return output


if __name__ == "__main__":

    args = sys.argv[1:]
    logfile = args[0]

    name = logfile.split(".")
    name = "".join(name[:-1])

    f = open(logfile, 'r')

    # TODO Get all orbitals / ionionzation energy
    # TODO Get energies
    # TODO Get dipole moment
    # TODO Vibrations? since gradient==0?

    orbital_energies = []
    atomization_energy = 0.0

    relaxed = False

    for line in f:

        if "CARTESIAN COORDINATES (ANGSTROEM)" in line:
            f.next()
            line = f.next()
            line = line.split()

            while len(line) > 1:
                atom = line[0]

                atomization_energy += ATOMIZATION[atom.lower()]

                line = f.next()
                line = line.split()


        if "FINAL SINGLE POINT ENERGY" in line:
            line = line.split()
            total_energy = float(line[-1])
            binding_energy = total_energy - atomization_energy

        if "ORBITAL ENERGIES" in line:

            f.next()
            f.next()
            header = f.next()

            line = f.next()
            line = line.split()
            N = len(line)

            ionization_energy = 0.0

            while N > 0:

                orbital_energy = line[2] # hartree
                electrons = line[1]

                if float(electrons) > 0.0:
                    ionization_energy = orbital_energy

                orbital_energies.append(orbital_energy)

                line = f.next()
                line = line.split()
                N = len(line)


        if "MP2 RELAXED DENSITY" in line:
            relaxed = True


        if "DIPOLE MOMENT" in line and relaxed:

            [f.next() for x in range(5)]

            dipole_moment = f.next()
            dipole_moment = dipole_moment.split()
            dipole_moment = np.array([float(x) for x in dipole_moment[4:]])

            dipole_magnitude = np.sqrt(np.sum(dipole_moment**2))

    f.close()

    print ", ".join(["name", "binding energy", "ionization energy", "dipole magnitude", "dipole x", "dipole y", "dipole z"])

    data = [name, binding_energy, ionization_energy, dipole_magnitude,\
        dipole_moment[0],\
        dipole_moment[1],\
        dipole_moment[2]]

    data = [str(x) for x in data]

    print ", ".join(data)

