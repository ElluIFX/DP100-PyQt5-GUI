if (
    __import__("os").environ.get("MDP_SIM_MODE") is not None
    or "--sim" in __import__("sys").argv
):
    from mdp_controller.__sim_mdp_p906 import MDP_P906
else:
    from mdp_controller.mdp_p906 import MDP_P906

__all__ = ["MDP_P906"]
