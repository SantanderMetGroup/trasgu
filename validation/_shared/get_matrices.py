import bz2
import _pickle as cPickle
import os
import numpy as np


class matrix:
    def __init__(self, index, mat_type, matrix):
        self.index = index
        self.mat_type = mat_type
        self.matrix = np.flip(np.array(matrix), axis=0)


def decompress_pickle(file):
    # Load any compressed pickle file and return data
    data = bz2.BZ2File(file, "rb")
    data = cPickle.load(data)
    return data


def get_matrices(matrix_dir, nodes=4, subtrees=[]):
    # EXTRACT INFO FROM CHIMERA FILES DOWNLOADED FROM CHIMERA DELFT REPO
    # MARCELL CHIMERA VINES
    # Get all files in the directory
    files = os.listdir(matrix_dir)
    files.sort()
    to_get = []
    if len(subtrees) == 0:
        for x in files:
            if "_" + str(nodes) + "_" in x:
                to_get.append(x)
    else:
        for x in files:
            for st in subtrees:
                if st in x:
                    to_get.append(x)
    matrices = []
    for dat_file in to_get:
        data = decompress_pickle(matrix_dir + dat_file)
        mat = []
        index = 0
        mat_type = ""
        for line in data:
            if "Matrix" in line:
                if len(mat) != 0:
                    matrices.append(matrix(index, mat_type, mat))
                mat = []
                index = int(line.split()[-1])
            elif "Type" in line:
                mat_type = line.split()[-1]
            else:
                if len(line.split()) > 0:
                    row = [int(x) for x in line.split()]
                    mat.append(row)
        matrices.append(matrix(index, mat_type, mat))
    return matrices
