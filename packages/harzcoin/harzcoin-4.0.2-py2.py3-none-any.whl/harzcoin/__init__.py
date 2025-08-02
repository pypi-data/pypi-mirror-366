import requests
import json
import hashlib
import random
import time
import uuid

globalUrl = "https://wnafumlmiulybbkqauew.supabase.co/functions/v1"
__version__ = "4.1.0"

## GLOBAL FUNCS ##
def version():
    print(f"Current version: v{__version__}")

## GLOBAL FUNCS ##

class wallet:
    def __init__(self, walletId, walletKey, supabase_url="https://wnafumlmiulybbkqauew.supabase.co"):
        self.walletId = walletId
        self.walletKey = walletKey
        self.supabase_url = supabase_url
        self.supabase_anon_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InduYWZ1bWxtaXVseWJia3FhdWV3Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTI5Mjc2NjMsImV4cCI6MjA2ODUwMzY2M30.yBllQMKN5Yuxwl9L_pVULPexzsmS4Q87kaXtVcbStno"
        self.last_mined_hash = None
        self.current_mine_difficulty = None
    
    def quick_send(self, receiverId, bal: float):
        sending_data = {
            "walletId": self.walletId,  
            "walletKey": self.walletKey,  
            "receiverId": receiverId, 
            "balanceSending": bal,  
            "feesWallet": "hz0000001"
        }

        response = requests.post(url=f"{globalUrl}/send", json=sending_data)
        return response.json()
    
    def advanced_transfer(self, walletId, walletKey, receiverId, bal: float, user_fee: str = "hz0000001"):
        sending_data = {
            "walletId": walletId,
            "walletKey": walletKey,
            "receiverId": receiverId,
            "balanceSending": bal,
            "feesWallet": user_fee
        }
        response = requests.post(url=f"{globalUrl}/send", json=sending_data)
        if response.status_code == 200:
            return response.json()
        else:
            return f"There was an error executing this request to Harzcoin node. Error: {response.status_code}."
    
    def fetch_mining_info(self):
        try:
            mining_info_response = requests.post(
                f'{self.supabase_url}/functions/v1/update-mining-block',
                headers={
                    'Authorization': f'Bearer {self.supabase_anon_key}' if self.supabase_anon_key else '',
                    'Content-Type': 'application/json'
                }
            )
        
            # Print full response for debugging
            print(f"Response Status: {mining_info_response.status_code}")
            print(f"Response Headers: {mining_info_response.headers}")
        
            try:
                response_json = mining_info_response.json()
                print(f"Response JSON: {response_json}")
            except ValueError as json_error:
                print(f"JSON Parsing Error: {json_error}")
                print(f"Response Text: {mining_info_response.text}")
        
            if mining_info_response.status_code != 200:
                print(f"Failed to fetch mining info. Status: {mining_info_response.status_code}")
                return None
        
            mining_info = mining_info_response.json()
            self.current_mine_difficulty = mining_info['mine_difficulty']
            return mining_info
    
        except requests.exceptions.RequestException as e:
            print(f"Network Error: {e}")
            return None
        except Exception as e:
            print(f"Unexpected Error: {e}")
            return None
    
    def mine_sha256(self, walletId: str = "hz8264812"):
        # Fetch current mining information
        mining_info = self.fetch_mining_info()
        
        if not mining_info:
            print("Could not retrieve mining information. Aborting mining.")
            return None
        
        # Extract current hash and difficulty
        current_hash = mining_info['current_hash']
        mine_difficulty = mining_info['mine_difficulty']
        
        # Check if this is a repeat attempt on the same hash
        if current_hash == self.last_mined_hash:
            print("This block has already been mined. Wait for the next block.")
            return None
        
        # Mining logic with dynamic difficulty
        nonce = 0
        mineprefix = "0" * mine_difficulty
        
        while True:
            # Combine current hash with nonce
            hashmsg = f"hrscoin{current_hash}{nonce}"
            sha256_hash = hashlib.sha256(hashmsg.encode('utf-8')).hexdigest()
            
            if sha256_hash.startswith(mineprefix):
                # Calculate reward based on current difficulty
                reward = 400 * mine_difficulty
                print(f"🔨 Block Mined: Hash {sha256_hash} | ⭐ Reward: {reward} | Difficulty: {mine_difficulty}")
                
                # Transfer reward using test wallet
                randomTestwallet = wallet(walletId="hz0000001", walletKey="ghx-ome-ga")
                transfer_result = randomTestwallet.advanced_transfer(
                    walletId="hz0000001", 
                    walletKey="ghx-ome-ga", 
                    receiverId=self.walletId, 
                    bal=reward, 
                    user_fee="hz000BURN"
                )
                
                # Update last mined hash to prevent duplicate mining
                self.last_mined_hash = current_hash
                
                return {
                    'hash': sha256_hash,
                    'nonce': nonce,
                    'reward': reward,
                    'difficulty': mine_difficulty
                }
            
            nonce += 1
    
class utilities:
    def __init__(self):
        pass

    def __str__(self):
        return "Utilities module. use *from harzcoin import wallet* to do transfers."
    
    def create(self):
        response = requests.get(url=f"{globalUrl}/create")
        return response.json()
    
    def view(self, walletId: str):
        sending_data = {
            "walletId": walletId
        }

        response = requests.post(url=f"{globalUrl}/wallet-view", json=sending_data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return f"There was an error trying to view the wallet. {response.status_code} error."
    
    def help(self, command: str = "else"):
        commandHelp = {
            "burn": "hz000BURN",
            "hcmc": "hz0000001",
            "else": "There is a documentation given, use that. Also type: 'burn' or 'hcmc' to get their respective wallets."
        }

        print(commandHelp[command.lower()])
    
if __name__ == "__main__":
    # Example usage with optional Supabase credentials
    mywallet = wallet(
        "hz8264812", 
        "bau-2hd-ako", 
        supabase_url="https://wnafumlmiulybbkqauew.supabase.co"
    )
    
    # Mine with the new competitive system
    mining_result = mywallet.mine_sha256()
    
    if mining_result:
        print("Mining successful:", mining_result)