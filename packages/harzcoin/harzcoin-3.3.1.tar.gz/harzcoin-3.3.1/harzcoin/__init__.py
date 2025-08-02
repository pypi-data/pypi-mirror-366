__version__ = "3.3.1"

import hashlib
import time
import json
import os
import random
import socket
import threading
from uuid import uuid4
from typing import List, Dict
from threading import Thread, Lock

BASE_DIFFICULTY = 6
BLOCK_REWARD = 400
GAS_FEE = 0.5
MAX_SUPPLY = 1_200_000_000.0
HALVING_INTERVAL = 12_000_000
PRECISION = 5
PEER_PORT = 65432
PEERS = set()

mining_activity = {}

def generate_wallet_id():
    return "hz" + "-".join(''.join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=3)) for _ in range(3))

def generate_wallet_key():
    return "hzkey" + "-".join(''.join(random.choices("0123456789abcdefghijklmnopqrstuvwxyz", k=3)) for _ in range(4))

class Wallet:
    def __init__(self):
        self.wallet_id = generate_wallet_id()
        self.wallet_key = generate_wallet_key()

    def __str__(self):
        return f"[Wallet] ID: {self.wallet_id}, Key: {self.wallet_key}"

class Transaction:
    def __init__(self, sender, recipient, amount, key=None):
        self.sender = sender
        self.recipient = recipient
        self.amount = round(amount, PRECISION)
        self.fee = round(GAS_FEE, PRECISION)
        self.timestamp = time.time()
        self.key = key

    def to_dict(self):
        return self.__dict__

class Block:
    def __init__(self, index, transactions, previous_hash, reward, nonce=0, timestamp=None, hash=None):
        self.index = index
        self.timestamp = timestamp or time.time()
        self.transactions = [
            Transaction(**tx) if isinstance(tx, dict) else tx for tx in transactions
        ]
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.reward = round(reward, PRECISION)
        self.hash = hash or self.compute_hash()

    def compute_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "reward": self.reward
        }
        block_string = json.dumps(block_data, sort_keys=True, default=str)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine(self, difficulty):
        print(f"⛏️ Mining block {self.index} with difficulty {difficulty}...")
        while True:
            self.hash = self.compute_hash()
            if self.hash.startswith('0' * difficulty):
                break
            self.nonce += 1
        print(f"✅ Block mined: {self.hash}")

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "reward": self.reward,
            "hash": self.hash
        }

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.nodes: set = set()
        self.minted = 0.0
        self.lock = Lock()
        self.wallets: Dict[str, str] = {}
        self.claimed_blocks: Dict[int, str] = {}
        self.create_genesis_block()
        self.sync_chain_from_peers()
        self.start_peer_listener()

    def create_genesis_block(self):
        genesis = Block(0, [], "0", 0)
        self.chain.append(genesis)

    def get_last_block(self):
        return self.chain[-1]

    def get_current_reward(self):
        halvings = len(self.chain) // HALVING_INTERVAL
        reward = BLOCK_REWARD / (2 ** halvings)
        return max(0, round(reward, PRECISION))

    def get_dynamic_difficulty(self):
        recent_block_index = self.get_last_block().index
        active_miners = mining_activity.get(recent_block_index, 1)
        return BASE_DIFFICULTY + active_miners // 2

    def add_transaction(self, tx: Transaction):
        if tx.sender == "NETWORK":
            self.pending_transactions.append(tx)
        elif tx.sender in self.wallets and self.wallets[tx.sender] == tx.key:
            if tx.sender == tx.recipient:
                print("❌ Cannot send to self")
                return
            if self.get_balance(tx.sender) >= tx.amount + tx.fee:
                self.pending_transactions.append(tx)
            else:
                print("❌ Insufficient funds")
        else:
            print("❌ Invalid wallet key or wallet ID")

    def mine_pending(self, miner_address):
        with self.lock:
            index = len(self.chain)

            if index in self.claimed_blocks and self.claimed_blocks[index] != miner_address:
                print(f"⚠️ Block {index} already claimed.")
                return

            self.claimed_blocks[index] = miner_address
            mining_activity[index] = mining_activity.get(index, 0) + 1

            reward = self.get_current_reward()
            if self.minted + reward > MAX_SUPPLY:
                reward = max(0, MAX_SUPPLY - self.minted)

            if reward > 0:
                coinbase_tx = Transaction("NETWORK", miner_address, reward)
                all_transactions = [coinbase_tx] + self.pending_transactions
            else:
                all_transactions = self.pending_transactions

            block = Block(
                index=index,
                transactions=all_transactions,
                previous_hash=self.get_last_block().hash,
                reward=reward
            )

            difficulty = self.get_dynamic_difficulty()
            block.mine(difficulty)
            self.chain.append(block)
            self.pending_transactions = []
            self.minted += reward

            if index in self.claimed_blocks:
                del self.claimed_blocks[index]

            mining_activity[index] = max(0, mining_activity.get(index, 1) - 1)

            self.broadcast_block(block)

    def get_balance(self, address):
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx.recipient == address:
                    balance += tx.amount
                if tx.sender == address:
                    balance -= tx.amount + tx.fee
        return round(balance, PRECISION)

    def register_wallet(self, wallet: Wallet):
        self.wallets[wallet.wallet_id] = wallet.wallet_key

    def start_peer_listener(self):
        def handle_client(conn):
            with conn:
                data = conn.recv(65536)
                if data == b"CHAIN_REQUEST":
                    conn.sendall(json.dumps([b.to_dict() for b in self.chain], default=str).encode())
                else:
                    try:
                        block_data = json.loads(data.decode())
                        block = Block(**block_data)
                        if block.hash.startswith('0' * BASE_DIFFICULTY) and block.previous_hash == self.get_last_block().hash:
                            self.chain.append(block)
                            print("✅ Block received from peer")
                        elif block.index > self.get_last_block().index:
                            print("⚠️ Longer chain detected, syncing...")
                            self.sync_chain_from_peers()
                    except Exception as e:
                        print(f"❌ Invalid block from peer: {e}")

        def listener():
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.bind(("", PEER_PORT))
            server.listen()
            print(f"🌐 Listening on port {PEER_PORT}")
            while True:
                conn, _ = server.accept()
                Thread(target=handle_client, args=(conn,)).start()

        Thread(target=listener, daemon=True).start()

    def broadcast_block(self, block: Block):
        for peer in PEERS:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer, PEER_PORT))
                s.sendall(json.dumps(block.to_dict(), default=str).encode())
                s.close()
            except Exception as e:
                print(f"⚠️ Could not send block to {peer}: {e}")

    def sync_chain_from_peers(self):
        for peer in list(PEERS):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer, PEER_PORT))
                s.sendall(b"CHAIN_REQUEST")
                data = s.recv(65536)
                peer_chain = json.loads(data.decode())
                if len(peer_chain) > len(self.chain) and self.is_valid_chain(peer_chain):
                    self.chain = [Block(**b) for b in peer_chain]
                    print(f"🔗 Synced chain from {peer}")
                s.close()
            except Exception as e:
                print(f"❌ Sync failed with {peer}: {e}")

    def is_valid_chain(self, chain_data):
        try:
            for i in range(1, len(chain_data)):
                current = Block(**chain_data[i])
                prev = Block(**chain_data[i - 1])
                if current.previous_hash != prev.compute_hash():
                    return False
            return True
        except Exception as e:
            print(f"❌ Chain validation error: {e}")
            return False

    def add_peer(self, ip):
        PEERS.add(ip)

HARZ = Blockchain()

class HarzAPI:
    def create_wallet(self):
        wallet = Wallet()
        HARZ.register_wallet(wallet)
        return wallet

    def send(self, sender_id, sender_key, recipient, amount):
        tx = Transaction(sender_id, recipient, amount, sender_key)
        HARZ.add_transaction(tx)

    def mine(self, miner_address):
        HARZ.mine_pending(miner_address)
        return {"reward": HARZ.get_current_reward(), "message": "Block accepted!"}

    def balance(self, address):
        return HARZ.get_balance(address)

    def add_peer(self, ip):
        HARZ.add_peer(ip)

harz = HarzAPI()

if __name__ == '__main__':
    my_wallet = harz.create_wallet()
    print("Wallet ID:", my_wallet.wallet_id)
    print("Wallet Key:", my_wallet.wallet_key)

    harz.mine(my_wallet.wallet_id)
    print("Balance:", harz.balance(my_wallet.wallet_id))

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("🛑 Node stopped.")
