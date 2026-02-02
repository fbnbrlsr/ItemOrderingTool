from ortools.linear_solver import pywraplp

def get_decimal_places(x):
    from decimal import Decimal
    d = Decimal(str(x)).normalize()
    # If the number is an integer after normalization
    if d.as_tuple().exponent >= 0:
        return 0
    return -d.as_tuple().exponent

def generated_run_optimization(weights, capacity):
    from ortools.sat.python import cp_model
    from ortools.sat.cp_model_pb2 import CpSolverStatus
    import math
    
    decimals = max([get_decimal_places(w) for w in weights])
    weights = sorted(weights, reverse=True)
    scale = 10 ** decimals
    int_weights = [int(round(w * scale)) for w in weights]
    int_capacity = int(round(capacity * scale))

    def first_fit_decreasing(w):
        bins = []
        for x in w:
            for i in range(len(bins)):
                if bins[i] + x <= int_capacity:
                    bins[i] += x
                    break
            else:
                bins.append(x)
        return len(bins)

    max_bins = first_fit_decreasing(int_weights)
    n = len(int_weights)

    model = cp_model.CpModel()

    x = [[model.NewBoolVar(f"x_{i}_{j}") for j in range(max_bins)] for i in range(n)]
    y = [model.NewBoolVar(f"y_{j}") for j in range(max_bins)]

    for i in range(n):
        model.Add(sum(x[i][j] for j in range(max_bins)) == 1)

    for j in range(max_bins):
        model.Add(sum(int_weights[i] * x[i][j] for i in range(n)) <= int_capacity * y[j])

    # Symmetry breaking
    for j in range(max_bins - 1):
        model.Add(y[j] >= y[j + 1])

    # Lower bound
    lb = math.ceil(sum(int_weights) / int_capacity)
    model.Add(sum(y) >= lb)

    model.Minimize(sum(y))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 5
    solver.parameters.num_search_workers = 8

    status = solver.Solve(model)

    # Results
    if status == CpSolverStatus.OPTIMAL:
        print("Status: Optimal")
    elif status == CpSolverStatus.FEASIBLE:
        print("Status: Feasible")
    elif status == CpSolverStatus.INFEASIBLE:
        print("Status: Feasible")
    elif status == CpSolverStatus.UNBOUNDED:
        print("Status: Unbounded")
    elif status == CpSolverStatus.MODEL_INVALID:
        print("Status: Model invalid")
    elif status == CpSolverStatus.ABNORMAL:
        print("Status: Abnormal")
    elif status == CpSolverStatus.NOT_SOLVED:
        print("Status: Not solved")
    else:
        print("Status: ?")
    print(f"Total weight: {sum(weights)} -> min number of bins: {sum(weights) / capacity}")
    
    # Extract solution
    bins = []
    for j in range(max_bins):
        if solver.Value(y[j]):
            items = [i for i in range(len(weights)) if solver.Value(x[i][j])]
            weight = sum(weights[i] for i in items)
            bins.append((j, items, weight))

    # Print results
    print(f"Number of bins used: {len(bins)}")
    for j, items, w in bins:
        print(
            f"Bin {j}: items {[weights[i] for i in items]}, "
            f"total weight = {w:.3f}, "
            f"unused = {capacity - w:.3f}"
        )
        
    return {
        idx: [weights[i] for i in items]
        for idx, items, _ in bins
    }

def optimal_parts_groups(part_lengths, max_length):
    
    print("INPUT:")
    print(part_lengths)
    bins = int(sum(part_lengths) // max_length)
    
    # AI generated method
    groups = generated_run_optimization(part_lengths, max_length)
    
    
    
    # My method
    # solved = False
    # while not solved:
    #     print("Solving...")
    #     groups = run_optimization(part_lengths, max_length, bins)

    #     solved = True
    #     for k in groups:
    #         if sum(groups[k]) > max_length:
    #             bins += 1
    #             solved = False
    #             break
                
    print("Result:", groups)
    return groups
    
    
    
def run_optimization(part_lengths, max_length, bins):
    
    num_parts = len(part_lengths)
    
    # Use CP-SAT because we are using boolean variables
    solver = pywraplp.Solver.CreateSolver("SAT")
    if not solver:
        print("ERROR: No solver...")
    
    
    # VARIABLES: x_ij = 1 iff part i belongs to group j
    x = {}
    for i in range(num_parts):
        for j in range(bins):
            x[i, j] = solver.IntVar(0, 1, "")
            
            
    # CONSTRAINT 1: x_1j + ... + x_nj = 1, every part belongs to exactly one group
    for i in range(num_parts):
        solver.Add(solver.Sum([x[i, j] for j in range(bins)]) == 1)
    
    
    # CONSTRAINT 2: l_1 x_1j + ... + l_2 x_2j <= max_length, the sum of lengths in a group can at most be max_length (except trash)
    for j in range(bins-1):
        solver.Add(solver.Sum([part_lengths[i] * x[i, j] for i in range(num_parts)]) <= max_length)
    
    
    # OBJECTIVE: Minimize the difference between max_length and sum of part lengths for each group (except trash)
    objective_terms = []
    for i in range(num_parts):
        for j in range(bins-1):
            objective_terms.append(part_lengths[i] * x[i, j])
    solver.Maximize(solver.Sum(objective_terms))
    
    
    # Solve
    status = solver.Solve()
    
    
    # Results
    if status == pywraplp.Solver.OPTIMAL:
        print("Status: Optimal")
        print(f"Objective value = {solver.Objective().Value():.2f}")
    elif status == pywraplp.Solver.FEASIBLE:
        print("Status: Feasible")
        print(f"Objective value = {solver.Objective().Value():.2f}")
    elif status == pywraplp.Solver.INFEASIBLE:
        print("Status: Feasible")
    elif status == pywraplp.Solver.UNBOUNDED:
        print("Status: Unbounded")
    elif status == pywraplp.Solver.MODEL_INVALID:
        print("Status: Model invalid")
    elif status == pywraplp.Solver.ABNORMAL:
        print("Status: Abnormal")
    elif status == pywraplp.Solver.NOT_SOLVED:
        print("Status: Not solved")
    else:
        print("Status: ?")
        
    
    # Create groups according to computed group indices
    groups = {}
    for i in range(num_parts):
        part_length = part_lengths[i]
        arr = [x[i, j].solution_value() for j in range(bins)]
        group = arr.index(max(arr))
        
        if group in groups:
            groups[group].append(part_length)
        else:
            groups[group] = [part_length]
    
    return groups

if __name__ == '__main__':
    
    # Example
    parts = [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5, 3.5]
    l = 8.5
    
    res = optimal_parts_groups(parts, l)
    # print(res)
    
    # for k in res:
    #     l = res[k]
        
    #     print(l, "->", sum(l))
    