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
# Magic Methods
    def __init__(self, filename=""):
        if len(filename) > 0:
            self._LoadFromInputFile(filename)
        
        self._BuildTableauVERO()

# Private Methods
    def _LoadFromInputFile(self, filename):
        """
        Reads the input file and stores the data in the object.
        """
        lines = []
        with open(filename, 'r') as input:
            lines = [line.strip() for line in input.readlines()]

        # 1ª linha: numero de restrições e variaveis
        self.num_restricoes, self.num_variaveis = np.array([int(val) for val in lines[0].split(' ')])
        
        # 2ª linha: vetor de custo
        self.c = np.array([int(val) for val in lines[1].split(' ')])
        
        # 3ª linha em diante: matriz A e vetor b
        A_b = np.array([ [int(val) for val in line.split(' ')] for line in lines[2:]])
        self.A = A_b[:, :-1]
        self.b = A_b[:, -1:]
        
   
    def _BuildTableauVERO(self):
        """
        Monta o Tableau VERO

           0   |||  -c^T |   0   | 0 
        ------------------------------  
               |||       |       |
           I   |||   A   |   I   | b    
               |||       |       |
        """
        # Adicionar 0's no vetor de custo
        c_extended = -self.c.copy()
        c_extended.resize((1, self.num_restricoes+self.num_variaveis+1))    
        
        # Parte de baixo do tableau
        tableau_bottom = np.concatenate((self.A, np.identity(self.num_restricoes), self.b), axis=1)
        tableau = np.concatenate((c_extended, tableau_bottom), axis=0)

        # VERO
        vero = np.concatenate((np.zeros((1, self.num_variaveis)), np.identity(self.num_variaveis)), axis=0)
        self.tableau_VERO = np.concatenate([vero, tableau], axis=1)

# Public Methods
    def Print(self):
        print(f"Numero de restrições: {self.num_restricoes}")
        print(f"Numero de variaveis: {self.num_variaveis}")
        print(f"Vetor de custo c: {self.c}")
        print(f"Matriz A:\n{self.A}")
        print(f"Vetor b:\n{self.b}")
        print(f"Tableau VERO™:\n{self.tableau_VERO}")

    def Solve(self):
        print("\n--------------------Solving the Tableau VERO™--------------------\n")
        pass

if __name__ == "__main__":
    ss = SimplexSolver(filename="Testes/01")
    ss.Print()
    ss.Solve()