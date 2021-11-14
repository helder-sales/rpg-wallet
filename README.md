# rpg-wallet

An wallet (originally meant to be used on tabletop RPG games) capable of arbitrary number of coin types and exchange values (defaults to 2 decimal places). Although it is working, there's not much error handling or some sort of defensive mechanism against bad user inputs. Works on Python 3.10+.

Please install the python dependencies below manually, or from the requirements.txt:

```bash
pytest==6.2.5
persist-queue==0.7.0
indexed==1.2.1
```

Usage: just run RPGWallet.py and follow the instructions from there.
