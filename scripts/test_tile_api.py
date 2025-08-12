#!/usr/bin/env python3
"""
Simple script to test tile API performance with random coordinates

Usage example:

  python scripts/test_tile_api.py --mode random --connections 50

"""

import asyncio
import aiohttp
import time
import random
import argparse
from statistics import mean, median

async def make_request(session, url, quiet=False):
    """Make a single request and return response time"""
    start_time = time.perf_counter()
    if not quiet:
        print(f"Making request to {url}")
    try:
        async with session.get(url) as response:
            await response.read()  # Read the response body
            end_time = time.perf_counter()
            if not quiet:
                print(f"Response status: {response.status}, time: {end_time - start_time:.3f} seconds")
            return {
                'status': response.status,
                'time': end_time - start_time,
                'success': response.status == 200
            }
    except Exception as e:
        end_time = time.perf_counter()
        return {
            'status': 'error',
            'time': end_time - start_time,
            'success': False,
            'error': str(e)
        }

async def main():
    parser = argparse.ArgumentParser(description='Test tile API performance with configurable parameters')
    parser.add_argument('--url', '-u', 
                       default="http://localhost:8000/api/specimens/macaque_brain_rm009/image/coronal/0",
                       help='Base URL for the tile API (default: %(default)s)')
    parser.add_argument('--requests', '-r', type=int, default=50,
                       help='Number of requests to make (default: %(default)s)')
    parser.add_argument('--connections', '-c', type=int, default=5,
                       help='Maximum simultaneous connections (default: %(default)s)')
    parser.add_argument('--mode', '-m', choices=['random', 'serial'], default='random',
                       help='Access mode: random coordinates or serial z increments (default: %(default)s)')
    parser.add_argument('--coord-range', type=int, default=5000,
                       help='Coordinate range for z,y,x values [0, RANGE] (default: %(default)s)')
    parser.add_argument('--seed', '-s', type=int, default=None,
                       help='Random seed for reproducible results (default: random)')
    parser.add_argument('--align', '-a', type=int, default=1,
                       help='Align coordinates to multiples of this value (default: %(default)s)')
    parser.add_argument('--quiet', '-q', action='store_true',
                       help='Suppress per-request output')
    
    args = parser.parse_args()
    
    base_url = args.url
    num_requests = args.requests
    max_connections = args.connections
    access_mode = args.mode
    coord_range = args.coord_range
    quiet = args.quiet
    align = args.align
    
    # Set random seed if provided
    if args.seed is not None:
        random.seed(args.seed)
        print(f"Random seed set to: {args.seed}")
    
    # Generate random coordinates
    urls = []

    if access_mode == 'serial':
        z = random.randint(0, coord_range) // align * align
        y = random.randint(0, coord_range) // align * align
        x = random.randint(0, coord_range) // align * align
        print(f"Starting serial mode from z={z}, y={y}, x={x}")
        for _ in range(num_requests):
            z = (z + 1) % coord_range
            url = f"{base_url}/{z}/{y}/{x}"
            urls.append(url)
    elif access_mode == 'random':
        for _ in range(num_requests):
            z = random.randint(0, coord_range) // align * align
            y = random.randint(0, coord_range) // align * align
            x = random.randint(0, coord_range) // align * align
            url = f"{base_url}/{z}/{y}/{x}"
            urls.append(url)
    else:
        raise ValueError(f"Unknown access mode: {access_mode}")

    print(f"Making {num_requests} requests to tile API...")
    print(f"Base URL: {base_url}")
    print(f"Max simultaneous connections: {max_connections}")
    print(f"Coordinate range: z,y,x in [0, {coord_range}]")
    print(f"Access mode: {access_mode}")
    if align > 1:
        print(f"Coordinate alignment: multiples of {align}")
    print("-" * 50)
    
    # Create connector with limited connections
    connector = aiohttp.TCPConnector(
        limit=max_connections,           # Total connection pool size
        limit_per_host=max_connections,  # Max connections per host
        ttl_dns_cache=300,              # DNS cache TTL
        use_dns_cache=True,
    )
    
    # Create session and make requests
    async with aiohttp.ClientSession(connector=connector) as session:
        start_wall_time = time.perf_counter()
        
        # Make all requests concurrently (but limited by connector)
        tasks = [make_request(session, url, quiet) for url in urls]
        results = await asyncio.gather(*tasks)
        
        end_wall_time = time.perf_counter()
    
    # Calculate statistics
    wall_time = end_wall_time - start_wall_time
    successful_requests = [r for r in results if r['success']]
    failed_requests = [r for r in results if not r['success']]
    
    response_times = [r['time'] for r in successful_requests]
    
    print(f"Results:")
    print(f"  Total requests: {num_requests}")
    print(f"  Successful: {len(successful_requests)}")
    print(f"  Failed: {len(failed_requests)}")
    print(f"  Wall time: {wall_time:.3f} seconds")
    print(f"  Requests per second: {num_requests / wall_time:.2f}")
    
    if response_times:
        print(f"\nResponse time statistics (successful requests):")
        print(f"  Mean: {mean(response_times):.3f} seconds")
        print(f"  Median: {median(response_times):.3f} seconds")
        print(f"  Min: {min(response_times):.3f} seconds")
        print(f"  Max: {max(response_times):.3f} seconds")
    
    if failed_requests:
        print(f"\nFailed requests:")
        for i, result in enumerate(failed_requests):
            status = result.get('status', 'unknown')
            error = result.get('error', 'unknown error')
            print(f"  Request {i+1}: Status {status} - {error}")

if __name__ == "__main__":
    asyncio.run(main())

"""
Benchmark result:
on xws, samba to HPC

python scripts/test_tile_api.py --mode serial --connections 1 --seed 123 --align 256

random mode
n_conn  reqs(6)     reqs(6,a32)  reqs(6,512,no)  reqs(6,a32,worker8)
1       1.58,4.14   4.67,4.76    3.10, 5.61      9.87~13.4~19.5
2       4.18        4.67
4       4.22        
32      4.17        4.62
new pos: 1.29 1.72

serial mode
n_conn  reqs(123)  reqs(6)  reqs(6,align256)  reqs(6,align16) align32
1       28.83      4.47     7.28             4.90           5.79
2       22.04      4.42     
4       21.49      4.27
8       20.82      4.27
16      21.70      4.30
32      20.79      4.25     6.62
new pos: 3.43, 3.63

Summary:
* generally, serial mode is faster than random mode.
* in random mode
  - warming up is significant (*2.6)
  - cocurrent do not help or make performance worse
  - grid alignment is significant

* in serial mode
  - cocurrent do not help or make performance worse
  - at some position, access time can be extremely fast (6 times faster)
  - warming up is not very significant effect (~ +7%)
  - grid alignment is significant (+60%)
  - the slowness is not due to network latency, because we tested even the data
    is in SSD, the performance is still suboptimal(4.47 -> 5.80).

* what we learn
  - API should not let server do CPU-bound tasks as possible, such as decompressing
    the data, since scaling up in client side is much easy, but hard in server side.
    Preferably read compressed data as is and send to client, let the client to decompress.
  - So the data tiling should design for 3-views seperately (coronal, sagittal and horizontal)
  - need to design api so that distinguish compressed data format, and notify
    client side to read block-by-block.

"""
