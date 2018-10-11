from graphviz import Digraph


def plot_tree(est_pygbm, est_lightgbm=None, tree_index=0, view=True, **kwargs):
    """Plot the i'th tree from an estimator. Can also plot a LightGBM estimator
    (on the left) for comparison.

    Requires matplotlib and graphviz (both python package and binary program).

    kwargs are passed to graphviz.Digraph()

    Example:
    plotting.plot_tree(est_pygbm, est_lightgbm, view=False, filename='output')
    will silently save output to output.pdf
    """
    def make_pygbm_tree():
        def add(node_idx, parent=None, decision=None):
            predictor_tree = est_pygbm.predictors_[tree_index]
            node = predictor_tree.nodes[node_idx]
            name = 'split__{0}'.format(node_idx)
            label = '\nsplit_feature_index: {0}'.format(
                node['feature_idx'])
            label += r'\nthreshold: {0}'.format(node['threshold'])
            for info in ('gain', 'value', 'count'):
                label += r'\n{0}: {1}'.format(info, node[info])
            label += '\ntime: {0:.10f}'.format(node['time'])
            label += '\nfast: {0}'.format(node['fast'])
            label += '\nratio: {0}'.format(node['ratio'])
            label += '\nsum_g: {0}'.format(node['sum_g'])
            label += '\nsum_h: {0}'.format(node['sum_h'])
            if node['is_leaf']:
                label += '\nleaf_index: {0}'.format(node_idx)

            graph.node(name, label=label)
            if not node['is_leaf']:
                add(node['left'], name, decision='<=')
                add(node['right'], name, decision='>')

            if parent is not None:
                graph.edge(parent, name, decision)

        add(0)  # add root to graph and recursively add child nodes

    # make lightgbm tree
    if est_lightgbm is not None:
        import lightgbm as lb
        graph = lb.create_tree_digraph(
            est_lightgbm,
            tree_index=tree_index,
            show_info=['split_gain', 'internal_value', 'internal_count',
                       'leaf_count'],
            **kwargs)
    else:
        graph = Digraph(**kwargs)

    # make pygbm tree
    make_pygbm_tree()

    graph.render(view=view)