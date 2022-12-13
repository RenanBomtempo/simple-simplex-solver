import numpy as np
import time
from utils import FloatToColoredString, CountAlphanumericWithoutColor, VectorToString, MatrixToString
import sys

class SimplexSolver():
    """
    Resolve um problema de programação linear escrito na Forma Padrão de Igualdades (i.e. problema de maximização )
    """
# Magic Methods
    def __init__(self, c, A, b, decimals=7, verbose=False):
        self.decimals = decimals
        self.verbose = verbose
        self.states = []
        self.A = A
        self.b = b
        self.c = c
        self.num_restricoes = self.A.shape[0]
        self.num_variaveis = self.A.shape[1]
        self.InitializeTableau()


# Private Methods
    def InitializeTableau(self):
        # Adicionar 0's no vetor de custo
        c_extended = -self.c.copy()
        c_extended.resize((1, self.num_restricoes+self.num_variaveis+1), refcheck=False)
        
        # Parte de baixo do tableau
        tableau_bottom = np.concatenate((self.A, np.identity(self.num_restricoes), self.b), axis=1)
        tableau = np.concatenate((c_extended, tableau_bottom), axis=0)

        # VERO
        vero = np.concatenate((np.zeros((1, self.num_restricoes)), np.identity(self.num_restricoes)), axis=0)
        self.tableau_VERO = np.concatenate([vero, tableau], axis=1)
        self.states.append(self.tableau_VERO.copy())

    def Log(self, msg, end="\n"):
        if self.verbose:
            print(msg, end=end)

    @property
    def tableau_b(self):
        return self.tableau[1:, -1]

    @property
    def tableau_restrictions(self):
        return self.tableau[1:, :-1]
    
    @property
    def tableau_c(self):
        return self.tableau[0, :-1]

    @property
    def tableau(self):
        """
        The real tableau actually contains a column of zeros in front of Matrix A, due to the 
        insertion of variable w = -cx:

        | 1 |   c   |   0   | o |
        -------------------------
        |   |       |       |   |
        | 0 |   A   |   I   | b |
        |   |       |       |   |
        
        But in this case, we omit the first column entirely because we will use the VERO tableau.
        """
        return self.tableau_VERO[:, self.num_restricoes:]

    def _PrintTableauVERO(self):
        # zeros in the first line up to the number of restrictions
        first_line = VectorToString(self.tableau_VERO[0, :self.num_restricoes], self.decimals) + "|"
        
        # cost vector
        first_line += VectorToString(self.tableau_c, self.decimals)

        # objective function value
        first_line += f"{FloatToColoredString(self.tableau_VERO[0, -1], self.decimals)} |"
        
        # deviding line
        self.Log(first_line)
        self.Log('-' * CountAlphanumericWithoutColor(first_line))

        # Rest of the tableau VERO
        for i in range(self.num_restricoes):
            self.Log(VectorToString(self.tableau_VERO[i+1, :self.num_restricoes], self.decimals), end="|")
            self.Log(VectorToString(self.tableau_VERO[i+1, self.num_restricoes:], self.decimals), end="\n")

    def _FindPivotElement(self):
        """
        Finds the pivot element in the tableau
        """
        # find the pivot column
        pivot_col = np.argmin(self.tableau_c)

        # find the pivot row
        quotients = []
        for i in range(self.num_restricoes):
            tmp = self.tableau_restrictions[i, pivot_col]
            if  tmp > 0:
                q = self.tableau_b[i] / tmp
                quotients.append(q)
            else:
                quotients.append(np.inf)
            
        pivot_row = np.argmin(quotients)

        return pivot_row+1, pivot_col+self.num_restricoes
    
    def _FindCurrentBasis(self):
        # find collumns of A that concatenate to the identity matrix
        AI = self.tableau_restrictions
        I = np.identity(self.num_restricoes)
        basis_indexes = []

        for k in range(self.num_restricoes):
            for i in range(len(AI[0])):
                if np.allclose(AI[:, i], I[:, k]):
                    basis_indexes.append(i)
                    break

        if len(basis_indexes) != self.num_restricoes:
            print
            return None
            
        return [AI[:, i] for i in basis_indexes], basis_indexes

    def _CalculateObjectiveFunctionValue(self):
        """
        Calculates the objective function value
        """
        vecs, _ = self._FindCurrentBasis()
        if vecs is None:
            return None
        x = [v @ self.b for v in vecs]
        if len(x) != len(self.c):
            return None
        return float(self.c @ x)

    def _PivotTableauVERO(self, pivot_row, pivot_col):
        """
        Pivots the tableau
        """
        # pivot element
        pivot = self.tableau_VERO[pivot_row, pivot_col]

        # pivot row
        self.tableau_VERO[pivot_row, :] /= pivot

        # other rows
        for i in range(self.num_restricoes+1):
            if i != pivot_row:
                self.tableau_VERO[i, :] -= self.tableau_VERO[i, pivot_col] * self.tableau_VERO[pivot_row, :]


# Public Methods
    def Print(self):
        self.Log("============================= Linear Programming  =============================")
        self.Log(f"Restrictions:\t{self.num_restricoes}")
        self.Log(f"Variables:\t{self.num_variaveis}")
        self.Log(f"Cost vector c:")
        self.Log(VectorToString(self.c, self.decimals))
        self.Log(f"Matrix A:")
        self.Log(MatrixToString(self.A, self.decimals))
        self.Log(f"Vector b:")
        self.Log(MatrixToString(self.b, self.decimals))

        # self.Log VERO Tableau as a matrix where each column has the same width
        self.Log("Tableau VERO™:")
        self._PrintTableauVERO()

    def IsViable(self):
        self.Log("Checking if the problem is viable...")
        aux = self.states[0].copy()

        for i in range(self.num_restricoes):
            if aux[1:, -1][i] < 0:
                aux[i+1, :self.num_restricoes+self.num_variaveis] *= -1
                aux[1:, -1][i] *= -1

        aux[0, self.num_restricoes:self.num_restricoes+self.num_variaveis] = np.zeros((self.num_variaveis,))
        aux[0, self.num_restricoes+self.num_variaveis:-1] = np.ones(self.num_restricoes)
        
        self.Log(MatrixToString(aux), end="\n\n")

        for i in range(self.num_restricoes):
            aux[0, :] -= aux[i+1, :]

        iterations = 0
        while True:
            # Check if the solution is optimal
            c = aux[0, self.num_restricoes:-1]
            b = aux[1:, -1]

            self.Log(MatrixToString(aux), end="\n\n")
            if np.all(c >= 0) and np.all(b >= 0):
                break
            
            # Find the pivot element
            # find the pivot column
            pivot_col = np.argmin(c) + self.num_restricoes

            # find the pivot row
            quotients = []
            for i in range(self.num_restricoes):
                tmp = aux[i+1, pivot_col]
                if  tmp > 0:
                    q = b[i] / tmp
                    quotients.append(q)
                else:
                    quotients.append(np.inf)
                
            pivot_row = np.argmin(quotients)+1
            
            # Pivot the tableau
            # pivot element
            pivot = aux[pivot_row, pivot_col]

            # pivot row
            aux[pivot_row, :] /= pivot

            # other rows
            for i in range(self.num_restricoes+1):
                if i != pivot_row:
                    aux[i, :] -= aux[i, pivot_col] * aux[pivot_row, :]

            iterations += 1

        
        if aux[0,-1] < 0:
            print("inviavel")
            print(" ".join([f"{val:.7f}" for val in aux[0, :self.num_restricoes]]))
            return False
        return True

    def GetTrivialSolution(self):
        x = []
        # for each column int the tableau corresponding to a variable, check if the c value is 0 and and if it contains only one 1 and the rest 0, if so, add its value to the solution
        for i in range(self.num_restricoes, self.num_restricoes+self.num_variaveis):
            if np.isclose(self.tableau_VERO[0, i], 0):
                zeros = 0
                one_index = -1
                for j in range(1, self.num_restricoes+1):
                    if np.isclose(self.tableau_VERO[j, i], 0):
                        zeros += 1
                    elif np.isclose(self.tableau_VERO[j, i], 1):
                        one_index = j
                if zeros == self.num_restricoes-1 and one_index != -1:
                    x.append(self.tableau_VERO[one_index, -1])
                else:
                    x.append(0)
            else:
                x.append(0)
        return x

    def IsOptimal(self):
        if np.all(self.tableau_c >= 0) and np.all(self.tableau_b >= 0):
            optimal_value = self.tableau_VERO[0, -1]
            self.Log(f"The solution is optimal and the objective function value is: {optimal_value}")
            print("otima")
            print(f"{optimal_value:.7f}")
            
            x = self.GetTrivialSolution()

            print(" ".join([f"{val:.7f}" for val in x]))
            print(" ".join([f"{val:.7f}" for val in self.tableau_VERO[0, :self.num_restricoes]]))
            return True
        return False
                

    def Solve(self):
        self.Log("\n--------------------Solving via Tableau VERO™--------------------\n")
        start_time = time.time()

        iterations = 0
        while True:
            if time.time() - start_time > 0.1:
                if not self.IsViable():
                    return

            # Check if the solution is optimal
            if self.IsOptimal():
                return
            
            # For each column of the tableau corresponding to a variable check if the column is entirely negative, if so, the problem is unbounded
            for i in range(self.num_restricoes, self.num_restricoes+self.num_variaveis):
                if np.all(self.tableau_VERO[1:, i] <= 0):
                    self.IsViable()
                    self.Log("The problem is unbounded")
                    print("ilimitada")
                    print(" ".join([f"{val:.7f}" for val in self.GetTrivialSolution()]))
                    print(" ".join([f"{val:.7f}" for val in self.tableau_VERO[0, :self.num_restricoes]]))
                    return
           
            
            self.Log(f"Iteration #{iterations}")
            self.states.append(self.tableau_VERO)
            
            # Find the pivot element
            self.Log("Finding the pivot element...", end=" ")
            pivot_row, pivot_col = self._FindPivotElement()
            self.Log(f"({pivot_row}, {pivot_col}): {self.tableau_VERO[pivot_row, pivot_col]}")
            
            # Pivot the tableau
            self.Log("Pivoting the tableau...")
            self._PivotTableauVERO(pivot_row, pivot_col)
            self._PrintTableauVERO()
            iterations += 1


if __name__ == "__main__":
    lines = [line.strip() for line in sys.stdin.readlines()]
    
    # 1ª linha: numero de restrições e variaveis
    num_restricoes, num_variaveis = np.array([int(val) for val in lines[0].split(' ')])
    
    # 2ª linha: vetor de custo
    c = np.array([int(val) for val in lines[1].split(' ')])
    
    # 3ª linha em diante: matriz A e vetor b
    A_b = np.array([ [int(val) for val in line.split(' ')] for line in lines[2:]])
    A = A_b[:, :-1]
    b = A_b[:, -1:]

    ss = SimplexSolver(c, A, b, decimals=1, verbose=True)
    ss.Print()
    ss.Solve()