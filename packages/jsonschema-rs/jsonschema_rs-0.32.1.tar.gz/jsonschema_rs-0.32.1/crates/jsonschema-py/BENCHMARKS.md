# Benchmark Suite

A benchmarking suite for comparing different Python JSON Schema implementations.

## Implementations

- `jsonschema-rs` (latest version in this repo)
- [jsonschema](https://pypi.org/project/jsonschema/) (v4.23.0)
- [fastjsonschema](https://pypi.org/project/fastjsonschema/) (v2.20.0)

## Usage

Install the dependencies:

```console
$ pip install -e ".[bench]"
```

Run the benchmarks:

```console
$ pytest benches/bench.py
```

## Overview

| Benchmark     | Description                                    | Schema Size | Instance Size |
|----------|------------------------------------------------|-------------|---------------|
| OpenAPI  | Zuora API validated against OpenAPI 3.0 schema | 18 KB       | 4.5 MB        |
| Swagger  | Kubernetes API (v1.10.0) with Swagger schema   | 25 KB       | 3.0 MB        |
| GeoJSON  | Canadian border in GeoJSON format              | 4.8 KB      | 2.1 MB        |
| CITM     | Concert data catalog with inferred schema      | 2.3 KB      | 501 KB        |
| Fast     | From fastjsonschema benchmarks (valid/invalid) | 595 B       | 55 B / 60 B   |

Sources:
- OpenAPI: [Zuora](https://github.com/APIs-guru/openapi-directory/blob/1afd351ddf50e050acdb52937a819ef1927f417a/APIs/zuora.com/2021-04-23/openapi.yaml), [Schema](https://spec.openapis.org/oas/3.0/schema/2021-09-28)
- Swagger: [Kubernetes](https://raw.githubusercontent.com/APIs-guru/openapi-directory/master/APIs/kubernetes.io/v1.10.0/swagger.yaml), [Schema](https://github.com/OAI/OpenAPI-Specification/blob/main/_archive_/schemas/v2.0/schema.json)
- GeoJSON: [Schema](https://geojson.org/schema/FeatureCollection.json)
- CITM: Schema inferred via [infers-jsonschema](https://github.com/Stranger6667/infers-jsonschema)
- Fast: [fastjsonschema benchmarks](https://github.com/horejsek/python-fastjsonschema/blob/master/performance.py#L15)

## Results

### Comparison with Other Libraries

| Benchmark     | fastjsonschema | jsonschema    | jsonschema-rs |
|---------------|----------------|---------------|----------------|
| OpenAPI       | - (1)          | 640.34 ms (**x94.35**) | 6.79 ms     |
| Swagger       | - (1)          | 1134.76 ms (**x232.81**)| 4.88 ms     |
| Canada (GeoJSON) | 10.43 ms (**x4.33**)  | 785.21 ms (**x325.59**) | 2.41 ms |
| CITM Catalog  | 4.97 ms (**x3.66**)   | 82.42 ms (**x60.67**) | 1.36 ms  |
| Fast (Valid)  | 1.95 µs (**x6.49**)   | 35.81 µs (**x119.15**) | 300.55 ns  |
| Fast (Invalid)| 2.17 µs (**x4.14**)   | 35.83 µs (**x68.31**) | 524.50 ns  |

### jsonschema-rs Performance: `validate` vs `is_valid`

| Benchmark     | validate   | is_valid   | Speedup |
|---------------|------------|------------|---------|
| OpenAPI       | 6.79 ms    | 6.84 ms    | **0.99x**   |
| Swagger       | 4.88 ms    | 4.73 ms    | **1.03x**   |
| Canada (GeoJSON) | 2.41 ms | 2.34 ms    | **1.03x**   |
| CITM Catalog  | 1.36 ms    | 1.28 ms    | **1.06x**   |
| Fast (Valid)  | 300.55 ns  | 249.95 ns  | **1.20x**   |
| Fast (Invalid)| 524.50 ns  | 561.00 ns  | **0.93x**   |

Notes:

1. `fastjsonschema` fails to compile the Open API spec due to the presence of the `uri-reference` format (that is not defined in Draft 4). However, unknown formats are explicitly supported by the spec.

You can find benchmark code in [benches/](benches/), Python version `3.13.0`, Rust version `1.82`.

## Contributing

Contributions to improve, expand, or optimize the benchmark suite are welcome. This includes adding new benchmarks, ensuring fair representation of real-world use cases, and optimizing the configuration and usage of benchmarked libraries. Such efforts are highly appreciated as they ensure accurate and meaningful performance comparisons.
