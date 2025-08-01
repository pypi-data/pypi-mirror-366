import dask.array as da
import ray

from tests.utils import ray_cluster, simple_worker, wait_for_head_node  # noqa: F401

NB_ITERATIONS = 10


@ray.remote(max_retries=0)
def head_script() -> None:
    """The head node checks that the values are correct"""
    from doreisa.head_node import init
    from doreisa.window_api import ArrayDefinition, run_simulation

    init()

    def simulation_callback(array: da.Array, timestep: int):
        # This is the standard dask task graph
        assert len(array.sum().dask) == 9

        x = array.sum().persist()

        # We still have a dask array
        assert isinstance(x, da.Array)

        # But only one task in the task graph, since the result is being computed
        assert len(x.dask) == 1

        x_final = x.compute()
        assert x_final == 10 * timestep

    run_simulation(
        simulation_callback,
        [ArrayDefinition("array")],
        max_iterations=NB_ITERATIONS,
    )


def test_dask_persist(ray_cluster) -> None:  # noqa: F811
    head_ref = head_script.remote()
    wait_for_head_node()

    worker_refs = []
    for rank in range(4):
        worker_refs.append(
            simple_worker.remote(
                rank=rank,
                position=(rank // 2, rank % 2),
                chunks_per_dim=(2, 2),
                nb_chunks_of_node=1,
                chunk_size=(1, 1),
                nb_iterations=NB_ITERATIONS,
                node_id=f"node_{rank}",
            )
        )

    ray.get([head_ref] + worker_refs)
