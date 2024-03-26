## Performance Benchmarking

We use `pyperf` for performance benchmarking to ensure that changes do not adversely affect the performance of RTN. If you're making changes that might impact performance, please run the benchmarks with:

```bash
make benchmark