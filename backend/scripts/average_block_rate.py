# backend\util\average_block_rate.py

import time
from backend.blockchain.blockchain import Blockchain
from backend.config import SECONDS

blockchain = Blockchain()

times = []

for i in range(1000):
    starttime = time.time_ns()
    blockchain.add_block(i)
    endtime = time.time_ns()

    new_block_mining_time = (endtime - starttime) / SECONDS
    times.append(new_block_mining_time)

    average_block_mining_time = sum(times) / len(times)

    print(f"New mined block difficulty: {blockchain.chain[-1].difficulty}")
    print(f"New block mining time: {new_block_mining_time}s")
    print(f"Average mining block time: {average_block_mining_time}s\n")
