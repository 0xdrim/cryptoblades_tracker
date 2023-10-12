# cryptoblades_tracker
Python Cryptoblades Account Tracker (CBTracker)

I decided to create this when the original cbtracker became paid. Hope you can enjoy it.

## notes
```
Only supports BSC at the moment.
Only supports Gen1 Characters and Skill Token at the moment.
```


## requirement
```
- Python 3.10.6
- Bnb Smart Chain HTTP RPC Node (I recommend quicknode.com free plan)
```



## installation

#### 1 - Please Download all files (.py and .json) and put into one folder
#### 2 - Installation PIP's:

```
pip install web3==5.31.4
pip install web3-multicall
```



## how to use

#### 1   - Open `cbtracker_config.json` with your preferred text editor (I recommend VSCode or Notepad++)
#### 2.1 - Paste your BSC RPC Node at ``"user_settings" > "bsc_node"`` inside the ``""`` (please use HTTP node)
#### 2.2 - Paste all your cryptoblades account wallet address at ``"eoa_wallet"`` separated with ``","`` (do not place ``","`` at last address)

```
example:
  "eoa_wallet":[
      "0xd9fAbCb0BA8852AeCf59d0c0A577383Ec621066E",
      "0xDED7D851A245466B3e8EF738dC300A780bA50735",
      "0xB1f3Ba3cfc0247EDDa0797d379f40C975A260dd7"
  ]
```
#### 3   - Save and run ```python cbtracker.py```



## output structure
If account has more than 8 unclaimed skills it will considered as Claimable Skill (Ready).

```
| Number of account  | Account Wallet Address |
| Unclaimed Skill | Wallet Skill | Wallet BNB |

| Char1 ID | Level | Unclaimed XP | Trait | Stamina | + Stamina Color Indicator
| Char2 ID | Level | Unclaimed XP | Trait | Stamina | + Stamina Color Indicator
| Char3 ID | Level | Unclaimed XP | Trait | Stamina | + Stamina Color Indicator
| Char4 ID | Level | Unclaimed XP | Trait | Stamina | + Stamina Color Indicator

-------------------------------------------------

- Available/Total Monthly Pool
- Current Multiplier (If doesn't has multiplier it will show as 0.50x)
- Unclaimed Skill | Unclaimed with current Multiplier | Total Claimable Skill (Ready) | Amount of Claimable Wallets
- All Wallet Total Skill (sum)
- All Wallet Total BNB (sum)
```


## Buy me a coffee :)
BSC/ETH/Polygon BEP-20 Address: ```0xd9fAbCb0BA8852AeCf59d0c0A577383Ec621066E```
