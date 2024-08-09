
<!-- Improved compatibility of back to top link: See: https://github.com/othneildrew/Best-README-Template/pull/73 -->
<a name="readme-top"></a>
<!--
*** Thanks for checking out the Best-README-Template. If you have a suggestion
*** that would make this better, please fork the repo and create a pull request
*** or simply open an issue with the tag "enhancement".
*** Don't forget to give the project a star!
*** Thanks again! Now go create something AMAZING! :D
-->



<!-- PROJECT LOGO -->
<br />

  <h3 align="center">Swap Contract</h3>

  <p align="center">
    A Cardano smart contract written on Python
    <br />
    <a href="https://charli3-oracles.gitbook.io/charli3-documentation/charli3s-documentation/swap-contract"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/Charli3-Official/swap-pycardano/issues">Report Bug</a>
  </p>
</div>



<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contributing">Contributing</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
  </ol>
</details>



<!-- ABOUT THE PROJECT -->
## About The Project
This repository contains a Python-based Cardano smart contract that utilizes pre-production test data from Charli3 oracle feeds as a use case.

This project has been designed as an educational resource to teach the general public how to access Charli3's oracles information. Therefore, the contract addresses, wallets, tokens, NFTs, and related information are intended for use in test environments only and should not be used in a production environment. Nonetheless, the structure, logic, and methods used in this repository can be used as a foundation for developing contracts that interact with production Charli3's feeds.

The swap contract enables the exchange of native tokens through a wallet, based on exchange rates provided by an oracle. The contract utilizes a UTXO to store different tokens, such as tUSDT and tADA. Off-chain operations supported by the contract include:

* The "Run swap" transaction initiates the creation of a UTXO at the contract address, which contains a minted NFT. This serves as an identifier for the UTXO that will hold two assets.
* "Add liquidity" transaction enables the addition of specific amounts of tokens to the swap's UTXO. These quantities must be present in the wallet of the swap's creator.
* "Swap A" transaction allows the exchange of asset A from the user's wallet to the swap's UTXO in exchange for asset B.
* "Swap B" transaction enables the exchange of asset B from the user's wallet to the swap's UTXO in exchange for asset A.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



### Built With

* [Pycardano 0.7.2](https://pycardano.readthedocs.io/en/latest/index.html)
* [blockfrost-python 0.5.2](https://pypi.org/project/blockfrost-python/0.5.2/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- GETTING STARTED -->
## Getting Started

The initial configuration is sourced from the pycardano repository. To create the project environment variables, we recommend reading the documentation at [using Pycardano](https://pycardano.readthedocs.io/en/latest/tutorial.html#using-pycardano).

### Prerequisites


The required packages can be installed using pip with the following command:

  ```sh
  pip install -r requirements.txt

  ```

### Installation

1. Get an API Key at [Blockfrost](https://blockfrost.io/).
2. Clone the repo:
   ```sh
   git clone https://github.com/Charli3-Official/swap-pycardano.git
   ```
3. Enter your API and select your base Blockfrost's URL in `main.py`.
   ```py
   #Blockfrost's settings
   BLOCKFROST_PROJECT_ID = os.environ.get('BLOCKFROST_PROJECT_ID')
   BLOCKFROST_BASE_URL = os.environ.get('BLOCFROST_BASE_URL')
   ```
4. Create and configure the 24-words mnemonic wallet passphrase.

  ```py
  #Wallet 24 word passphase
  MNEMONIC_24 = os.environ.get('24_WALLET_PASSPHRASE')
   ```

  <p align="right">(<a href="#readme-top">back to top</a>)</p>
<!-- USAGE EXAMPLES -->



## Usage
The project has a command line interface to easily submit transactions. To access it, first navigate to the `src` directory. Then, run the command python `main.py -h` to display helpful information on how to use the command line options.

    usage: python main.py [-h] {trade,user,swap-contract,oracle-contract} ...

    The swap python script is a demonstrative smart contract (Plutus v2)
    featuring the interaction with a Charli3's oracle.
    This script uses the inline oracle feed as reference input simulating
    the exchange rate between tADA and tUSDT to sell or buy assets
    from a swap contract in the test environment of preproduction.

    positional arguments: {trade,user,swap-contract,oracle-contract}
    trade               Call the trade transaction to exchange a
                        user asset with another asset at the swap contract.
                        Supported assets tADA and tUSDT.
    user                Obtain information about the wallet of the user who
                        participate in the trade transaction.
    swap-contract       Obtain information about the SWAP smart contract.
    oracle-contract     Obtain information about the ORACLE smart contract.

    options:
                       -h, --help            show this help message and exit

    Copyrigth: (c) 2020 - 2024 Charli3

<p align="right">(<a href="#readme-top">back to top</a>)</p>


<!-- CONTRIBUTING -->
## Contributing

Contributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

If you have a suggestion that would make this better, please fork the repo and create a pull request. You can also simply open an issue with the tag "enhancement".
Don't forget to give the project a star! Thanks again!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>



<!-- CONTACT -->
## Contact

Charli3's developer team


<p align="right">(<a href="#readme-top">back to top</a>)</p>
