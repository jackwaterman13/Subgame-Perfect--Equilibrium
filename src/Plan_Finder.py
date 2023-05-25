
def all_plans(state_t):
    deep_paths = dfs_path(state_t)

    plans = []

    for path in deep_paths:
        plan = []
        for state_t in path:
            plan.append(state_t)
            terminal_plan = plan.copy()
            terminal_plan.append(state_t.terminal_state)

            if terminal_plan not in plans:
                plans.append(terminal_plan)

    return plans


def dfs_path(state_t, halt_states=None, path=None):
    if halt_states is None:
        halt_states = [state_t]

    if path is None:
        path = [state_t]

    deep_paths = []

    for state_u in state_t.neighbours:

        if state_u in halt_states:
            # path.append(state_u)
            deep_paths.append(path)
            continue

        if state_u not in path:
            next_path = path.copy()
            next_path.append(state_u)
            new_paths = dfs_path(state_u, halt_states, next_path)

            for path_y in new_paths:
                if isinstance(path_y, list):
                    deep_paths.append(path_y)
                else:
                    deep_paths.append(new_paths)
                    break

    return deep_paths
