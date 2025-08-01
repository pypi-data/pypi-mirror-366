from matplotlib import pyplot as plt
import numpy as np
from collections import deque
from copy import deepcopy
from sklearn import tree
from sklearn.tree import DecisionTreeRegressor
import sklearn.model_selection


# generate 100 random numbers

X = np.random.rand(442, 1000)
y = np.random.rand(442) 

# random state is shared across all trees
rng = np.random.RandomState(12038)
model = DecisionTreeRegressor(max_leaf_nodes=6, max_depth=5, max_features=0.5)
estimators = deque()
for i in range(100):
    # this generates a random based in function
    # of the random state rng
    model.set_params(random_state=rng)
    model.fit(X, y)
    estimators.append(deepcopy(model)) #O(d)
    # indx = set(model.tree_.feature[model.tree_.feature != -2])
    # print(indx)

estimators = np.array(list(estimators))
k = 200
path = rng.randint(0, 2, size=(len(estimators), k))


m = estimators[0]
tree.plot_tree(m, proportion=True)
plt.show()

m.tree_.feature[m.tree_.feature != -2]


sklearn.model_selection.GridSearchCV

# path = get_new_path(estimators, path, p)
# picked_batches = select_path(path, CT_spps, test_errors, n_spps, args.factor, args.inbetween)
# write_batches(picked_file, picked_batches)
# ---------------------^^  In progress ^^ --------------------------------

# # disjoint batches creation
# batches = make_batches(path, CT_spps, n_spps)
# if args.window <= 1:
#     write_batches(batch_file, batches)
# else:
#     new_batches = agglomerate_batches(batches, window=args.window)
#     write_batches(batch_file, new_batches)
# if not args.nwerror and args.verbose:
#     # print(test_errors)
#     j_min = np.argmin(test_errors[:,1])
#     new_path_j = path[:,j_min]
#     min_err_sel = np.sum(new_path_j != 0)
#     print("Number of rows selected at min error: ", min_err_sel)

# --------------------------------------------------------------------------

# only in the case of ISLE
def get_new_path(estimators, path):
    """
    Takes the splitting variables from the trees
    """

    estimators = np.array(estimators) # O(M)
    new_path = deque()
    for j in range(path.shape[1]):
        if j == 0:
            continue

        coeffs = path[:,j]
        coeffs_logic = coeffs != 0

        # filter for active trees
        tmp_ensemble = estimators[coeffs_logic] # O(M)

        I_k = set()
        # O(M)
        for m in tmp_ensemble: 
            I_k_m = set(m.tree_.feature[m.tree_.feature != -2])
            I_k |= I_k_m
            
        new_path.append(I_k)

    return new_path



def choose_j(path, test_errors = None, factor = 1/2):
    """
    Choose the best j based on the path and test errors
    Parameters
    ----------
    path : numpy.ndarray
        The path of coefficients with shape (p,k)
        where p is the number of features and k is the number of lambda values
    test_errors : numpy.ndarray, optional
        The test errors with shape (k,2)
        where the first column is the lambda values and the second column is the RMSE values
    factor : float, optional
        The factor to choose the best j
        if factor is -1, then the function will return the index of the minimum test error
        if factor is between 0 and 1, then the function will return the index of the best j
        based on the number of non-zero coefficients
        The default is 1/2.

    Returns
    -------
    int
        The index of the best j
    
    """

    # path has (p,k) shape, where p is the number of features
    # and k is the number of lambda values
    if factor == -1 and test_errors is not None:
        # tests_errors contains two columns
        # the first one is the lambda values
        # the second one is the RMSE values
        # check 'calculate_test_errors' function
        
        # O(np) for obtain test_errors
        return np.argmin(test_errors[:,1]) # O(k) = O(1) for fixed k
    
    else:
        if factor < 0 or factor > 1:
            raise ValueError('Factor must be between 0 and 1 if nwerror is false and factor is not -1.')

        # recall p is the number of features
        p,k = path.shape
        user_selection = np.round(p*factor).astype(int)

        best_dist = np.inf
        best_j = 0
        for j in range(k):
            # beta_j is the j-th column of path
            # which is obtained from the j-th lambda value
            beta_j = path[:,j]
            # selection by elastic net
            model_selection = np.sum(beta_j != 0)
            # distance between of desired number of non-zero
            # coefficients and the current number of non-zero
            tmp_dist = np.abs(model_selection - user_selection)
            if tmp_dist < best_dist:
                best_dist = tmp_dist
                best_j = j

        return best_j


def select_path(path, CT_spps, test_errors, n_spps = 15, 
                factor = 1/2, inbetween = 0, 
                isle = False):
    
    """
    Select the path based on the test errors and the number of species
    Parameters
    ----------
    path : numpy.ndarray
        The path of coefficients with shape (p,k)
        where p is the number of features and k is the number of lambda values
        or (M,k) where M is the number of trees
    CT_spps : numpy.ndarray
        The concordance table with shape (n_spps, p)
        where n_spps is the number of species and p is the number of features
    test_errors : numpy.ndarray
        The test errors with shape (k,2)
        where the first column is the lambda values and the second column is the RMSE values
    n_spps : int, optional
        The number of species to be selected
        The default is 15.
    factor : float, optional
        The factor to choose the best j
        if factor is -1, then the function will return the index of the minimum test error
        if factor is between 0 and 1, then the function will return the index of the best j
        based on the number of non-zero coefficients
        The default is 1/2.
    inbetween : int, optional
        The number of inbetween j's to be selected
        The default is 0.
    isle : bool, optional
        If True, then the path is a M x k matrix
        where M is the number of trees and k is the number of lambda values
        The default is False.

    Returns
    -------
    deque
        The indices of the selected j's
        withn offset of 1
    """

    j_opt = choose_j(path, test_errors, factor = factor)
    chosen_j = np.linspace(0, j_opt, 2 + inbetween, 
                           endpoint=True, dtype = int)

    taken = set()
    new_batches = deque()
    for j in chosen_j:
        # it might be the case
        # that there are repeated j's
        if j in taken:
            continue

        if j == 0:
            taken.add(j)
            continue
        
        if not isle:
            # column vectors directly 
            # represent a feature or
            # row in the concordance table
            # i.e., path is a p x k matrix
            I = np.where(path[:,j] != 0)[0]
        else:
            # otherwise, the column represent the weights
            # for regression trees. Each tree used features.
            # TODO: add indeces from tree's splitting variables
            # in this case, path is M x k matrix

            # I has to be a list or an array of indices

            pass

        # check on the number of species
        # O(\rho T^4)
        if len(np.unique(CT_spps[I,:])) < n_spps:
            taken.add(j)
            continue

        # indices in python start from 0 but 
        # julia starts from 1. Julia is
        # used to read the data
        new_batches.append(I + 1) 
        taken.add(j)
    
    return new_batches


new_batches = select_path(path, path, None, n_spps = 15, 
                factor = 1/2, inbetween = 0, 
                isle = False)

min_err_sel = len(new_batches[-1])
print("Number of rows selected at min error: ", min_err_sel)





cv_results_report_file = "/Users/ulises/Desktop/ABL/software/experiments_qsin/empirical_hyper_leaf2.txt"

cv_results_report_l2 = {}
cv_results_report_l3 = {}

with open(cv_results_report_file, 'r') as f:
    for line in f.readlines():
        line = line.strip().split(",")
        
        alpha = float(line[1].replace("alpha: ", ""))
        nj = float(line[2].replace("eta: ", ""))
        vj = float(line[3].replace("nu: ", ""))
        lj = int(line[4].replace("leaves: ", ""))

        err = float(line[5].replace("err: ", ""))
        theta = (alpha, nj, vj)

        if lj == 2:
            if theta not in cv_results_report_l2:
                cv_results_report_l2[theta] = err/5
            else:
                cv_results_report_l2[theta] += err/5

        else:  
            if theta not in cv_results_report_l3:
                cv_results_report_l3[theta] = err/10
            else:
                cv_results_report_l3[theta] += err/10
        


sorted_l2 = sorted(cv_results_report_l2.items(), key=lambda x: x[1])
sorted_l3 = sorted(cv_results_report_l3.items(), key=lambda x: x[1])



a = [0/2,
4/2,
6/2,
8/2,
10/2,
12/2,
14/2,
16/2,
18/2,
20/2,
22/2,
24/2,
26/2,
28/2,
30/2,
32/2,
34/2,
36/2,
38/2,
40/2,
42/2,
44/2,
46/2,
48/2,
50/2,
56/2,
58/2,
60/2,
62/2,
64/2,
66/2,
68/2,
70/2,
72/2,
74/2,
76/2,
78/2,
80/2,
82/2,
84/2,
86/2,
88/2]

ran = set([ int(i) for i in a])
sub = set([ int(i) for i in range(0,51)])


for i in sub - ran:
    print(f"sbatch nl_submitter_{i}.sh")



