"""
Implementação do simplex
"""
import numpy as np
import scipy as sp
from linearIndependence import makeMatrixFullRank


class SimplexSolver():
    """
    Resolve um problema de programação linear escrito na Forma Padrão de Igualdades (i.e. problema de maximização )
    """

    def __init__(self, filename=""):
        self.input_filename = filename
        if len(filename) > 0:
            self.LoadFromInputFile()

    def LoadFromInputFile(self):
        """
        Reads the input file and stores the data in the object.
        """
        lines = []
        with open(self.input_filename, 'r') as input:
            lines = [line.strip() for line in input.readlines()]

        # 1ª linha: numero de restrições e variaveis
        self.num_restricoes, self.num_variaveis = np.array([int(val) for val in lines[0].split(' ')])
        
        # 2ª linha: vetor de custo
        self.c = np.array([int(val) for val in lines[1].split(' ')])
        
        # 3ª linha em diante: matriz A e vetor b
        A_b = np.array([ [int(val) for val in line.split(' ')] for line in lines[2:]])
        self.A = A_b[:, :-1]
        self.b = A_b[:, -1:]
    
    def Print(self):
        print(f"Numero de restrições: {self.num_restricoes}")
        print(f"Numero de variaveis: {self.num_variaveis}")
        print(f"Vetor de custo c: {self.c}")
        print(f"Matriz A: {self.A}")
        print(f"Vetor b: {self.b}")

if __name__ == "__main__":
    ss = SimplexSolver(filename="Testes/02")
    ss.Print()