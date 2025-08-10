#!/usr/bin/env python3
"""
Benchmark throughput of the image tile API.

- Discovers image shape and default tile_size via /specimens/{specimen_id}/tile-grid/{view}/{level}
- Generates tile requests starting from a random valid (z,y,x) voxel origin
- Traverses a YX area of size area_size x area_size in steps of tile_size
- Outer loop increases z by 1 for z_slices slices
- Supports serial mode and parallel mode (ThreadPoolExecutor)
- Reports MB/s, tiles/s, total time, success/error counts, and latency percentiles

Example:
  python scripts/benchmark_tiles.py \\
    --api-base http://localhost:8000/api \\
    --specimen macaque_brain_rm009 --view coronal --level 0 \\
    --channel 0 --area-size 4096 --z-slices 300 \\
    --mode parallel --concurrency 32
"""

import argparse
import json
import math
import random
import statistics
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional
from urllib.parse import urlencode
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed


@dataclass
class GridInfo:
    tile_size: int
    z_dim: int
    y_dim: int
    x_dim: int


@dataclass
class FetchResult:
    ok: bool
    bytes_read: int
    latency_s: float
    status: Optional[int]
    error: Optional[str]


def http_get_json(url: str, timeout: float = 10.0) -> dict:
    req = Request(url, headers={"Accept": "application/json"})
    with urlopen(req, timeout=timeout) as resp:
        data = resp.read()
    return json.loads(data.decode("utf-8"))


def http_get_bytes(url: str, timeout: float = 10.0) -> Tuple[int, Optional[int]]:
    """
    Returns (bytes_read, status_code). Reads full body to measure throughput.
    """
    req = Request(url, headers={"Accept": "image/*"})
    try:
        t0 = time.perf_counter()
        with urlopen(req, timeout=timeout) as resp:
            status = getattr(resp, "status", 200)  # Py3.9+: HTTPResponse.status
            body = resp.read()  # ensure full download
        # Some servers include Content-Length; length(body) is authoritative after read.
        return len(body), status
    except HTTPError as e:
        # Read and discard error body if any
        try:
            _ = e.read()
        except Exception:
            pass
        raise
    except URLError:
        raise


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    values_sorted = sorted(values)
    k = (len(values_sorted) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return values_sorted[int(k)]
    d0 = values_sorted[f] * (c - k)
    d1 = values_sorted[c] * (k - f)
    return d0 + d1


def fetch_grid_info(api_base: str, specimen: str, view: str, level: int, timeout: float) -> GridInfo:
    url = f"{api_base.rstrip('/')}/specimens/{specimen}/tile-grid/{view}/{level}"
    info = http_get_json(url, timeout=timeout)
    # Expect "image_shape": (Z,Y,X) and "tile_size"
    shape = info.get("image_shape") or info.get("dimensions") or [0, 0, 0]
    if not isinstance(shape, (list, tuple)) or len(shape) != 3:
        raise RuntimeError(f"Unexpected image_shape in tile-grid response: {shape}")
    tile_size = int(info.get("tile_size", 512))
    z_dim, y_dim, x_dim = int(shape[0]), int(shape[1]), int(shape[2])
    return GridInfo(tile_size=tile_size, z_dim=z_dim, y_dim=y_dim, x_dim=x_dim)


def build_request_urls(
    api_base: str,
    specimen: str,
    view: str,
    level: int,
    channel: int,
    tile_size: int,
    grid: GridInfo,
    area_size: int,
    z_slices: int,
    seed: Optional[int],
) -> List[str]:
    rng = random.Random(seed)

    # Clamp area to image bounds
    used_h = max(0, min(area_size, grid.y_dim))
    used_w = max(0, min(area_size, grid.x_dim))
    if used_h < tile_size or used_w < tile_size:
        raise RuntimeError(
            f"Area too small for tile_size: area ({used_h}x{used_w}), tile_size {tile_size}"
        )

    # Choose starting y,x so that tiles fit within bounds
    max_y0 = grid.y_dim - used_h
    max_x0 = grid.x_dim - used_w
    y0 = rng.randint(0, max(0, max_y0)) if max_y0 > 0 else 0
    x0 = rng.randint(0, max(0, max_x0)) if max_x0 > 0 else 0

    # Choose starting z so that we can take up to z_slices
    slices = min(z_slices, grid.z_dim) if grid.z_dim > 0 else 0
    if slices <= 0:
        raise RuntimeError("No available z slices in data")
    max_z0 = grid.z_dim - slices
    z0 = rng.randint(0, max(0, max_z0)) if max_z0 > 0 else 0

    # Offsets (ensure tiles fit: last origin + tile_size - 1 within bounds)
    y_offsets = list(range(0, used_h - tile_size + 1, tile_size))
    x_offsets = list(range(0, used_w - tile_size + 1, tile_size))

    urls: List[str] = []
    base = f"{api_base.rstrip('/')}/specimens/{specimen}/image/{view}/{level}"

    q = {"channel": channel, "tile_size": tile_size}

    for dz in range(slices):
        z = z0 + dz
        for oy in y_offsets:
            y = y0 + oy
            for ox in x_offsets:
                x = x0 + ox
                qs = urlencode(q)
                urls.append(f"{base}/{z}/{y}/{x}?{qs}")

    return urls


def fetch_one(url: str, timeout: float, retries: int) -> FetchResult:
    last_err = None
    for attempt in range(retries + 1):
        t0 = time.perf_counter()
        try:
            nbytes, status = http_get_bytes(url, timeout=timeout)
            t1 = time.perf_counter()
            if 200 <= (status or 0) < 300:
                return FetchResult(True, nbytes, t1 - t0, status, None)
            else:
                return FetchResult(False, 0, t1 - t0, status, f"HTTP {status}")
        except Exception as e:
            last_err = str(e)
            # simple backoff
            time.sleep(0.05 * (attempt + 1))
    return FetchResult(False, 0, 0.0, None, last_err)


def run_serial(warmup_urls: List[str], measured_urls: List[str], timeout: float, retries: int, progress_every: int) -> Tuple[List[FetchResult], float]:
    # Warmup
    for u in warmup_urls:
        _ = fetch_one(u, timeout, retries)

    t0 = time.perf_counter()
    results: List[FetchResult] = []
    for idx, u in enumerate(measured_urls, 1):
        r = fetch_one(u, timeout, retries)
        results.append(r)
        if progress_every > 0 and (idx % progress_every == 0):
            print(f"Progress: {idx}/{len(measured_urls)} measured tiles")
    total_time = time.perf_counter() - t0
    return results, total_time


def run_parallel(
    warmup_urls: List[str], measured_urls: List[str], timeout: float, retries: int, concurrency: int, progress_every: int
) -> Tuple[List[FetchResult], float]:
    # Warmup sequentially
    for u in warmup_urls:
        _ = fetch_one(u, timeout, retries)

    t0 = time.perf_counter()
    results: List[FetchResult] = []
    total = len(measured_urls)
    concurrency = max(1, concurrency)

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        in_flight = set()
        submit_idx = 0

        # Prime the pool
        initial = min(concurrency, total)
        for _ in range(initial):
            in_flight.add(ex.submit(fetch_one, measured_urls[submit_idx], timeout, retries))
            submit_idx += 1

        completed = 0
        while in_flight:
            for fut in as_completed(in_flight):
                in_flight.remove(fut)
                try:
                    results.append(fut.result())
                except Exception as e:
                    results.append(FetchResult(False, 0, 0.0, None, str(e)))
                completed += 1
                if progress_every > 0 and (completed % progress_every == 0):
                    print(f"Progress: {completed}/{total} measured tiles")
                if submit_idx < total:
                    in_flight.add(ex.submit(fetch_one, measured_urls[submit_idx], timeout, retries))
                    submit_idx += 1
                if not in_flight:
                    break

    total_time = time.perf_counter() - t0
    return results, total_time


def human_mb(nbytes: int) -> float:
    return nbytes / 1_000_000.0


def main():
    parser = argparse.ArgumentParser(description="Benchmark image tile API throughput.")
    parser.add_argument("--api-base", type=str, default="http://localhost:8000/api",
                        help="Base URL including /api (default: http://localhost:8000/api)")
    parser.add_argument("--specimen", type=str, required=True, help="Specimen ID")
    parser.add_argument("--view", type=str, choices=["coronal", "sagittal", "horizontal"], required=True,
                        help="View type")
    parser.add_argument("--level", type=int, required=True, help="Resolution level (e.g. 0)")
    parser.add_argument("--channel", type=int, default=0, help="Channel index (default 0)")
    parser.add_argument("--tile-size", type=int, default=0,
                        help="Tile size; if 0, use server default from tile-grid")
    parser.add_argument("--area-size", type=int, default=4096, help="Area side length to cover in YX (default 4096)")
    parser.add_argument("--z-slices", type=int, default=300, help="Number of z slices (outer loop) (default 300)")
    parser.add_argument("--mode", type=str, choices=["serial", "parallel"], default="parallel",
                        help="Fetch mode (default parallel)")
    parser.add_argument("--concurrency", type=int, default=32, help="Parallel workers (default 32)")
    parser.add_argument("--timeout", type=float, default=10.0, help="Request timeout seconds (default 10)")
    parser.add_argument("--warmup", type=int, default=0, help="Number of warmup tiles to ignore in stats")
    parser.add_argument("--retries", type=int, default=1, help="Retries per request on failure (default 1)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for choosing start coords")
    parser.add_argument("--dry-run", action="store_true", help="Only compute the request set and exit")
    parser.add_argument("--max-requests", type=int, default=0, help="Limit measured requests to this number (0=all)")
    parser.add_argument("--progress-every", type=int, default=100, help="Print progress every N completed tiles")
    args = parser.parse_args()

    # Discover grid info
    grid = fetch_grid_info(args.api_base, args.specimen, args.view, args.level, args.timeout)
    tile_size = args.tile_size if args.tile_size and args.tile_size > 0 else grid.tile_size

    # Build URLs
    urls = build_request_urls(
        api_base=args.api_base,
        specimen=args.specimen,
        view=args.view,
        level=args.level,
        channel=args.channel,
        tile_size=tile_size,
        grid=grid,
        area_size=args.area_size,
        z_slices=args.z_slices,
        seed=args.seed,
    )

    total_tiles = len(urls)
    if args.dry_run:
        print(f"Dry run: computed {total_tiles} tile requests")
        print(f"Example URL: {urls[0] if urls else 'N/A'}")
        return

    warmup = max(0, min(args.warmup, total_tiles))
    warmup_urls = urls[:warmup]
    measured_urls = urls[warmup:]
    if args.max_requests and args.max_requests > 0:
        measured_urls = measured_urls[:args.max_requests]
    measured_tiles = len(measured_urls)

    print(f"Planned: total={total_tiles}, warmup={warmup}, measuring={measured_tiles}")
    if measured_tiles > 0:
        print(f"First measured URL: {measured_urls[0]}")

    # Execute
    if args.mode == "serial":
        results, wall_time = run_serial(warmup_urls, measured_urls, args.timeout, args.retries, args.progress_every)
    else:
        results, wall_time = run_parallel(warmup_urls, measured_urls, args.timeout, args.retries, args.concurrency, args.progress_every)

    # Aggregate
    ok_results = [r for r in results if r.ok]
    err_results = [r for r in results if not r.ok]
    bytes_total = sum(r.bytes_read for r in ok_results)
    latencies = [r.latency_s for r in ok_results]

    tiles_s = (len(ok_results) / wall_time) if wall_time > 0 else 0.0
    mbs = (human_mb(bytes_total) / wall_time) if wall_time > 0 else 0.0

    p50 = percentile([l * 1000.0 for l in latencies], 50)
    p90 = percentile([l * 1000.0 for l in latencies], 90)
    p99 = percentile([l * 1000.0 for l in latencies], 99)

    # Summary
    print("Benchmark summary")
    print(f"- Mode: {args.mode}, Concurrency: {args.concurrency if args.mode=='parallel' else 1}")
    print(f"- Specimen: {args.specimen}, View: {args.view}, Level: {args.level}, Channel: {args.channel}")
    print(f"- Tile size: {tile_size}, Area: {args.area_size}x{args.area_size}, Z slices: {args.z_slices}")
    print(f"- Total tiles: {total_tiles} (warmup: {warmup}, measured: {measured_tiles})")
    print(f"- Success: {len(ok_results)}, Errors: {len(err_results)}")
    print(f"- Bytes: {bytes_total} ({human_mb(bytes_total):.2f} MB)")
    print(f"- Time: {wall_time:.3f} s, Tiles/s: {tiles_s:.2f}, MB/s: {mbs:.2f}")
    print(f"- Latency p50: {p50:.1f} ms, p90: {p90:.1f} ms, p99: {p99:.1f} ms")

    # CSV-friendly line
    print(
        "CSV,"
        f"{args.mode},{args.concurrency if args.mode=='parallel' else 1},"
        f"{args.specimen},{args.view},{args.level},{args.channel},"
        f"{tile_size},{args.area_size},{args.z_slices},"
        f"{total_tiles},{warmup},{measured_tiles},"
        f"{len(ok_results)},{len(err_results)},"
        f"{bytes_total},{human_mb(bytes_total):.3f},"
        f"{wall_time:.3f},{tiles_s:.3f},{mbs:.3f},"
        f"{p50:.1f},{p90:.1f},{p99:.1f}"
    )


if __name__ == "__main__":
    main()

"""
Benchmark results:
2025-08-11
(warming up by repeat 3 times)

$ python3 scripts/benchmark_tiles.py --api-base http://localhost:8000/api --specimen macaque_brain_rm009 --view coronal --level 0 --channel 0 --area-size 4096 --z-slices 50 --mode parallel --concurrency 8 --warmup 4 --max-requests 200 --progress-every 20 --timeout 5 --retries 0
Planned: total=3200, warmup=4, measuring=200
First measured URL: http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/0/5940/1666/3841?channel=0&tile_size=512
Progress: 20/200 measured tiles
Progress: 40/200 measured tiles
Progress: 60/200 measured tiles
Progress: 80/200 measured tiles
Progress: 100/200 measured tiles
Progress: 120/200 measured tiles
Progress: 140/200 measured tiles
Progress: 160/200 measured tiles
Progress: 180/200 measured tiles
Progress: 200/200 measured tiles
Benchmark summary
- Mode: parallel, Concurrency: 8
- Specimen: macaque_brain_rm009, View: coronal, Level: 0, Channel: 0
- Tile size: 512, Area: 4096x4096, Z slices: 50
- Total tiles: 3200 (warmup: 4, measured: 200)
- Success: 200, Errors: 0
- Bytes: 7803107 (7.80 MB)
- Time: 53.403 s, Tiles/s: 3.75, MB/s: 0.15
- Latency p50: 2264.3 ms, p90: 3661.4 ms, p99: 4654.9 ms
CSV,parallel,8,macaque_brain_rm009,coronal,0,0,512,4096,50,3200,4,200,200,0,7803107,7.803,53.403,3.745,0.146,2264.3,3661.4,4654.9
"""