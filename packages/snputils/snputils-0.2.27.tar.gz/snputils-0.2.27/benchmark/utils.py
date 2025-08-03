import numpy as np


def create_benchmark_test(benchmark, reader_func, file_path, name, ref_array, memory_profile):
    if memory_profile:
        from memory_profiler import memory_usage

        def run_with_memory_profile():
            def read_file():
                return reader_func(file_path)

            mem_usage, (result,) = memory_usage(
                (read_file, [], {}),
                retval=True,
                interval=0.1,
                include_children=True
            )
            return result, max(mem_usage)

        # Run benchmark with memory profiling
        result, max_mem = benchmark(run_with_memory_profile)
        benchmark.extra_info['max_memory_mb'] = max_mem

    else:
        # Run benchmark without memory profiling
        result = benchmark(reader_func, file_path)
        benchmark.extra_info['max_memory_mb'] = None

    # Verify output (not timed)
    assert np.array_equal(result, ref_array), f"Output does not match reference for {name}"
