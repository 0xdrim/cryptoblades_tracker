import json
import sys
import time
import math
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3_multicall import Multicall
from datetime import datetime, timedelta


class CBTracker():

    def __init__(self):
        
        self.cbtracker_config_path = r".\cbtracker_config.json"
        self.cbtracker_abi_path = r".\cbtracker_abi.json"
        self.cbtracker_weapon_abi_path = r".\cbtracker_weapon_abi.json"

        self.http_node, self.web3 = self.load_node()
        self.cbtracker_abi, self.cbtracker_weapon_abi = self.load_abis()
        self.user_wallet = self.load_wallet()

        #skill
        self.token_skill = self.web3.to_checksum_address("0x154a9f9cbd3449ad22fdae23044319d6ef2a1fab")
        self.contract_skill = self.web3.eth.contract(address=self.token_skill, abi=self.cbtracker_abi)

        #valor
        self.token_valor = self.web3.to_checksum_address("0x4Db374Da614c3653DdEaD0cB8f96BD90c87602C1")
        self.contract_valor = self.web3.eth.contract(address=self.token_valor, abi=self.cbtracker_abi)

        #treasury
        self.address_rewardpool = self.web3.to_checksum_address("0x812Fa2f7d89e5d837450702bd51120920dccaA99")
        self.contract_rewardpool = self.web3.eth.contract(address=self.address_rewardpool, abi=self.cbtracker_abi)

        #gameplay
        self.address_gameplay = self.web3.to_checksum_address("0x39bea96e13453ed52a734b6aceed4c41f57b2271")
        self.contract_gameplay = self.web3.eth.contract(address=self.address_gameplay, abi=self.cbtracker_abi)

        #characters
        self.address_characters = self.web3.to_checksum_address("0xc6f252c2cdd4087e30608a35c022ce490b58179b")
        self.contract_characters = self.web3.eth.contract(address=self.address_characters, abi=self.cbtracker_abi)

        #weapon
        self.address_weapon = self.web3.to_checksum_address("0x7e091b0a220356b157131c831258a9c98ac8031a")
        self.contract_weapon = self.web3.eth.contract(address=self.address_weapon, abi=self.cbtracker_weapon_abi)

        #bazaar
        self.address_bazaar = self.web3.to_checksum_address("0x90099dA42806b21128A094C713347C7885aF79e2")
        self.contract_bazaar = self.web3.eth.contract(address=self.address_bazaar, abi=self.cbtracker_abi)

        #equipment manager
        self.address_equipment = self.web3.to_checksum_address("0xa34c49de1d5212f753e6decc07c594c3aa3d3598")
        self.contract_equipment = self.web3.eth.contract(address=self.address_equipment, abi=self.cbtracker_abi)
        
        #fight
        self.address_fight = self.web3.to_checksum_address("0xce34a87173130ef691ff81fef1a6e8b8a9daca6f")
        self.contract_fight = self.web3.eth.contract(address=self.address_fight, abi=self.cbtracker_abi)

        #getEthBalance with web3-multicall
        self.multicall_address = self.web3.to_checksum_address("0x41263cba59eb80dc200f3e2544eda4ed6a90e76c")
        self.multicall_contract = self.web3.eth.contract(address=self.multicall_address, abi=self.cbtracker_abi)

        self.multicall = Multicall(self.web3.eth)


    def menu(self):
        
        while True:
            print("\n----------------------------------------------------")
            print(style().CYAN + "\nMain Menu:\n" + style().RESET)

            menu = {
                1: "Start CBTracker",
                2: "Exit"
            }

            for key in menu.keys():
                print(key, ": ", menu[key])

            try:
                option = int(input("\nSelect: "))
            except:
                self.sys_exit()

            if option == 1:
                print("\n----------------------------------------------------")
                self.cb_tracker_function()
            
            else:
                self.sys_exit()

            

    def cb_tracker_function(self):
        
        min_claimable_skill = 8 # after wallet claimable skills surpass this number, it will added to the "Ready"
        min_claimable_skill = min_claimable_skill * 10**18

        result_dict = {}

        # - Multicall Pool Structure - #
        #1 unclaimed skill
        #2 wallet skill
        #3 wallet bnb
        #3 getCharactersOwnedBy
        multicall_pool = [[],[],[],[]] 

        for wallet in self.user_wallet:
            multicall_pool[0].append(self.contract_gameplay.functions.getTokenRewardsFor(wallet))
            multicall_pool[1].append(self.contract_skill.functions.balanceOf(wallet))
            multicall_pool[2].append(self.multicall_contract.functions.getEthBalance(wallet))
            multicall_pool[3].append(self.contract_characters.functions.getCharactersOwnedBy(wallet))

            insert = {
                wallet:{
                    "unclaimed_reward":int,
                    "balance_skill":int,
                    "balance_bnb":int,
                    "character":{}
                }
            }

            result_dict.update(insert)
        

        result_pool = []
        for pool in multicall_pool:
            request = self.multicall.aggregate(pool)
            result_pool.append(json.loads(request.jsonstr()))


        i = 0
        total_skill = 0
        total_bnb = 0
        total_unclaimed = 0
        total_claimable = 0
        total_claimable_wallet = 0
        multicall_pool_character = [[],[],[],[]]
        multicall_pool_char_xp = [[]]
        for pool in result_pool:
            for result in pool["results"]:

                wallet = result["inputs"][0]["value"]
                value = result["results"][0]

                #value_r = f"{value / 10**18:.2f}"
                #result_dict[wallet]["skill"] = value_r
                
                if i == 0:
                    result_dict[wallet]["unclaimed_reward"] = f"{value / 10**18:.2f}"
                    total_unclaimed += value

                    if value >= min_claimable_skill:
                        total_claimable += value
                        total_claimable_wallet += 1

                elif i == 1:
                    result_dict[wallet]["balance_skill"] = f"{value / 10**18:.2f}"
                    total_skill += value
                elif i == 2:
                    result_dict[wallet]["balance_bnb"] = f"{value / 10**18:.5f}"
                    total_bnb += value

                elif i == 3:
                    
                    all_character = {}
                    for char in value["py/tuple"]:
                        char_dict = {
                            char:{
                                "trait": int,
                                "stamina": int,
                                "estimated_atk_time": datetime,
                                "level": int,
                                "xp": int,
                                "unclaimed_xp": int
                            }
                        }

                        all_character.update(char_dict)
                        multicall_pool_character[0].append(self.contract_weapon.functions.getTrait(char))
                        multicall_pool_character[1].append(self.contract_characters.functions.getStaminaPoints(char))
                        multicall_pool_character[2].append(self.contract_characters.functions.getLevel(char))
                        multicall_pool_character[3].append(self.contract_characters.functions.getXp(char))

                        multicall_pool_char_xp[0].append(self.contract_gameplay.functions.getXpRewards([char]))

                    result_dict[wallet]["character"] = all_character
            
            i += 1

        
        result_pool_character = []
        for pool in multicall_pool_character:
            request = self.multicall.aggregate(pool)
            result_pool_character.append(json.loads(request.jsonstr()))

        result_pool_char_xp = []
        for pool in multicall_pool_char_xp:
            request = self.multicall.aggregate(pool)
            result_pool_char_xp.append(json.loads(request.jsonstr()))


        i = 0
        for pool in result_pool_character:
            for result in pool["results"]:

                char = result["inputs"][0]["value"]
                value = result["results"][0]
                
                for wallet in result_dict:
                    if char in result_dict[wallet]["character"]:

                        # trait
                        if i == 0:
                            result_dict[wallet]["character"][char]["trait"] = value
                        
                        # stamina & estim. next attack time
                        elif i == 1:
                            current_time = datetime.now().replace(microsecond=0)
                            cooldown_time = timedelta(seconds=((200 - value) * 850))
                            next_atk = current_time + cooldown_time

                            result_dict[wallet]["character"][char]["stamina"] = value
                            result_dict[wallet]["character"][char]["estimated_atk_time"] = next_atk
                        
                        # level
                        elif i == 2:
                            result_dict[wallet]["character"][char]["level"] = int(value) + 1

                        # xp
                        elif i == 3:
                            result_dict[wallet]["character"][char]["xp"] = value

            i += 1


        # unclaimed xp
        for pool in result_pool_char_xp:
            for result in pool["results"]:

                char = result["inputs"][0]["value"][0]
                value = result["results"][0]["py/tuple"][0]
                
                for wallet in result_dict:
                    if char in result_dict[wallet]["character"]:
                        result_dict[wallet]["character"][char]["unclaimed_xp"] = value


        i = 1
        for wallet in result_dict:
            
            unclaimed_reward = result_dict[wallet]["unclaimed_reward"]
            balance_skill = result_dict[wallet]["balance_skill"]
            balance_bnb = result_dict[wallet]["balance_bnb"]


            print("\n-------------------------------------------------")
            if float(balance_skill) > 0:
                color = style().YELLOW
            else:
                color = style().RESET

            print(f"{i}: {wallet}\nUnclaimed: {unclaimed_reward} | Wallet: " + color + f"{balance_skill} Skill" + style().RESET + f" - {balance_bnb} BNB\n")

            print(f" {self.spacement(7, 'CharID')}   {self.spacement(7, 'Level')}     {self.spacement(18, 'Unclaimed XP')} {self.spacement(5, 'Trait')}   {self.spacement(7, 'Stamina')}")
            for char in result_dict[wallet]["character"]:
                trait_name = self.trait_name(result_dict[wallet]["character"][char]["trait"])
                stamina = result_dict[wallet]["character"][char]["stamina"]
                level = result_dict[wallet]["character"][char]["level"]
                xp = result_dict[wallet]["character"][char]["xp"]
                unclaimed_xp = result_dict[wallet]["character"][char]["unclaimed_xp"]

                next_level = self.getNextLevel(level, xp, unclaimed_xp)

                print(f"{self.spacement(7, char)} | {self.spacement(7, f'Lv. {level}')} | {self.spacement(8, f'{unclaimed_xp} XP')} {self.spacement(10, f'-> Lv. {next_level}')} | {self.spacement(5, trait_name)} | {self.spacement(7, f'{stamina}/200')} | ", end="")
                
                if 180 <= stamina <= 199:
                    print(style().YELLOW + "---" + style().RESET)

                elif stamina == 200:
                    print(style().RED + "---" + style().RESET)

                else:
                    print()

            i += 1

        print("\n-------------------------------------------------")

        status = False
        multiplier = int
        active_partners = self.contract_rewardpool.functions.getActivePartnerProjectsIds().call()
        try:
            for partner in active_partners:
                project = self.contract_rewardpool.functions.partneredProjects(partner).call()

                if "skill" in project[2].lower():
                    _partner_id = project[0]
                    multiplier = self.contract_rewardpool.functions.getProjectMultiplier(_partner_id).call()
                    multiplier = multiplier / 10**18
                    
                    monthly_pool = project[4]
                    remaining_pool = self.contract_rewardpool.functions.getRemainingPartnerTokenSupply(_partner_id).call() / 10**18

                    status = True

            if status == False:
                raise Exception
            
        except:
            monthly_pool = 0
            remaining_pool = 0
            multiplier = 0.50
            print(f"\nALERT: Error while fetching Skill data. Tracker will use {multiplier} as multiplier")
            
        print(f"\nMonthly Pool: {int(remaining_pool)}/{int(monthly_pool)}")
        print(f"Multiplier  : x{multiplier:.3f}")
        print(f"Unclaimed   : {total_unclaimed / 10**18:.2f} (Total: {(total_unclaimed * multiplier) / 10**18:.2f} | Ready: {total_claimable * multiplier / 10**18:.2f} - {total_claimable_wallet} Wallet)")
        print(f"Wallet Skill: {total_skill / 10**18:.2f}")
        print(f"Wallet BNB  : {total_bnb / 10**18:.5f}")
            


    # Analyze and print user in-game claimable skills and in-wallet BNB amounts.
    def cb_claim_tracker(self):
        result_dict = {}

        # - Multicall Pool Struct - #
        #0 unclaimed skill
        #1 wallet bnb
        multicall_pool = [[],[]]

        for wallet in self.user_wallet:
            multicall_pool[0].append(self.contract_gameplay.functions.getTokenRewardsFor(wallet))
            multicall_pool[1].append(self.multicall_contract.functions.getEthBalance(wallet))

            result_dict.update({wallet:{"skill":int, "bnb":int}})

        result_pool = []
        for pool in multicall_pool:
            request = self.multicall.aggregate(pool)
            result_pool.append(json.loads(request.jsonstr()))

        total_skill = 0
        total_bnb = 0
        for result in result_pool[0]["results"]:

            wallet = result["inputs"][0]["value"]
            value = result["results"][0]
            value_r = f"{value / 10**18:.2f}"

            result_dict[wallet]["skill"] = value_r
            total_skill += value

        for result in result_pool[1]["results"]:

            wallet = result["inputs"][0]["value"]
            value = result["results"][0]
            value_r = f"{value / 10**18:.5f}"

            result_dict[wallet]["bnb"] = value_r
            total_bnb += value

        i = 1
        for wallet in result_dict:
            print(f"{i}: {result_dict[wallet]['skill']} Skill - {result_dict[wallet]['bnb']} BNB")
            i += 1

        print(f"\nTotal Skill: {total_skill / 10**18:.2f} ({(total_skill * 0.23) / 10**18:.2f})")
        print(f"Total BNB  : {total_bnb / 10**18:.5f}")



    # Get character trait (element) name
    def trait_name(self, _trait):

        element_dict = {
            0: "Fire",
            1: "Earth",
            2: "Light",
            3: "Water",
            4: "Power"
        }

        return element_dict[_trait]


    # Get character XP
    def getXP(self, level):
        total = 0 
        xp = 16
        currentLevel = 1
        adder = 1
        prevrange = 1
        range = 1

        while(currentLevel <= level):
            #print(str(currentLevel)+ " " + str(xp) + f"({total})")
            total += xp
            xp = xp + adder
            prevrange = range 
            range = math.floor(xp/10)
            if range != prevrange:
                adder = adder + 1
            currentLevel = currentLevel + 1
        
        return total, xp


    # Calculate next reachable level spending the XP.
    def getNextLevel(self, actual_level, actual_xp, actual_unc_xp):
        actual_xp_info = self.getXP(actual_level)

        xp_after_claimed = actual_xp_info[0] + actual_unc_xp + actual_xp

        for i in range (1, 255):
            data = self.getXP(i)

            actual_level = data[0]
            range_level = data[0] + (data[1] - 1)
            next_level = data[0] + data[1]

            if actual_level <= xp_after_claimed <= range_level:
                return i
            

    # Load User RPC Node
    def load_node(self):
        with open (self.cbtracker_config_path) as file:
            config = json.load(file)
            node = config["user_settings"]["bsc_node"]
        
        print("\nRPC: ", end="")

        web3 = Web3(Web3.HTTPProvider(node, request_kwargs={'timeout': 60}))
        web3.middleware_onion.inject(geth_poa_middleware, layer=0)
        if web3.is_connected():
            print(style().GREEN + "Connected!\n" + style().RESET)
        else:
            print(style().RED + "Connection Failed!" + style().RESET)
            self.sys_exit()

        return node, web3

    # Load ABI
    def load_abis(self):
        with open (self.cbtracker_abi_path) as file:
            abi = json.load(file)

        with open (self.cbtracker_weapon_abi_path) as file:
            abi_wp = json.load(file)
        
        return abi, abi_wp

    # Load User Metamask Wallets
    def load_wallet(self):
        with open (self.cbtracker_config_path) as file:
            config = json.load(file)
            all_wallet = config["eoa_wallet"]
            checkum_wallets = []

            for eoa in all_wallet:
                if eoa == "":
                    continue

                try:
                    checksum = self.web3.to_checksum_address(eoa)
                    checkum_wallets.append(checksum)
                
                except:
                    print(f"Error: Can't load {checksum}. Is this wallet correct? Skipping.")
                    continue

            if len(checkum_wallets) == 0:
                print("Error: Can't find wallet address at cbtracker_config.json. Please verify and try again.")
                self.sys_exit()
        
        return checkum_wallets

    # Exit
    def sys_exit(self):
        print(style().RED + "\n\nExiting the app, see you again :p" + style().RESET)
        time.sleep(3)
        sys.exit()

    # Terminal Text Spacement
    def spacement(self, _desired_spacement, _string):
        string = str(_string)

        if len(string) < _desired_spacement:
            difference = _desired_spacement - len(string)

            for i in range (0, difference):
                string = string + " "

        return string

# Terminar Text Color Changing
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'
    

if __name__ == "__main__":
    process = CBTracker()
    process.menu()