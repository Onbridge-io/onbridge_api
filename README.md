# OnBridge token indexing engine and API server

In-browser Web3 JS library is not capable to extract transactions history natively. It's also pretty slow, especially on large lists. And it can be connected to just one network at a time (and bridge needs info from two networks at least).

To make user experience smoother we offload heavy background tasks to backend that indexes contract states and events on both L1 and L2 networks and makes correlation between bridging requests and transactions on both sides.

# Build and Run API Server

This service is designed to be built and run using docker compose. Thus, you can also run it locally.

## Step 1. Postgres

Before run Django project one should create Postgresql connection at port 5432 (docker image or service)  
Create user `onbridge` with your password and also database `onbridge` and give to user permissions.

Example in postgres (This code is for cases when Postgres is not running in Docker)

```shell
psql
create database onbridge;
create user onbridge with encrypted password '<your db password>';
grant all privileges on database onbridge to onbridge;
```

Example of how to start Docker image of Postgres 

```shell
docker pull postgres
docker run --rm --name db -p 5432:5432 -e POSTGRES_PASSWORD=<your db password> -e POSTGRES_USER=onbridge -e POSTGRES_DB=onbridge postgres
```

## Step 2. Django project with API 

Envs to `runserver` locally

```dotenv
ADMIN_USER=admin
ADMIN_PASSWORD=<your admin password>
DB_HOST=localhost
DB_NAME=onbridge
DB_USER=onbridge
DB_PASSWORD=<your db password>
SECRET_KEY=<your secret key>
```

Command

```
python3 -m venv venv
source venv/bin/activate
python3 manage.py migrate
python3 manage.py runserver
```

Or via docker

```shell
set -a; source <your file with envs>; set +a;
docker build -t api
docker run -it -e ADMIN_USER -e ADMIN_PASSWORD -e DB_HOST -e DB_NAME -e DB_USER -e DB_PASSWORD --network=host api
```

## Step 3. Token indexers

Before starting indexers one should initialize token indexer's state: current block, chain id, etc.  
For this one should run `init_indexer_model.py` with following envs:

```dotenv
BSC_CHAIN_ID=97
ETH_CHAIN_ID=42
POLYGON_CHAIN_ID=80001
BSC_START_BLOCK=16780489
ETH_START_BLOCK=29852491
POLYGON_START_BLOCK=24965926
```

Run this code with activated venv

```shell
python3 manage.py migrate
python3 init_indexer_model.py
```

It is recommended to have a proper .env-file for each indexer.  
One indexer checks only one chain  
Contents of such chain env file:

```dotenv
UPSTREAM=<rpc provider url>
TOKEN_ABI_FILENAME=token_indexer/erc721-abi.json
TOKEN_ADDRESS=<address of token on this chain>
BRIDGE_ADDRESS=<address of bridge contract on this chain>
INDEXER_INTERVAL=<interval of indexer in seconds>
IPFS_HOST='https://ipfs.io'

ADMIN_USER=admin
ADMIN_PASSWORD=<your admin password>
DB_HOST=localhost
DB_NAME=onbridge
DB_USER=onbridge
DB_PASSWORD=<your db password>
SECRET_KEY=<your secret key>
```

Run this code with activated venv

```shell
set -a;
source <file with envs for specific chain>;
set +a;
python3 token_indexer/start.py
```

### Note: it is recommended to run L1 indexer firstly

Unless all tokens at L1 chain are written to database other indexers should be shut down.  
If we run L1 and L2 indexer in concurrent mode, there can be errors.

Envs from ADMIN_USER to SECRET_KEY are the same for all indexers (since they are Django project envs).
Others are describes bellow:

### BSC

```dotenv
UPSTREAM=https://data-seed-prebsc-1-s1.binance.org:8545/
TOKEN_ABI_FILENAME=token_indexer/erc721-abi.json
TOKEN_ADDRESS=0x0dB2EB9b77dc0fDF130d29D338763C0eDc7CA02D
BRIDGE_ADDRESS=0xc2d7c0C63FFB42924e1A2f4Ce487A10670248Ac6
INDEXER_INTERVAL=3
IPFS_HOST='https://ipfs.io'
```

### Kovan

```dotenv
UPSTREAM=https://kovan.infura.io/v3/<your infura key>
TOKEN_ABI_FILENAME=token_indexer/erc721-abi.json
TOKEN_ADDRESS=0x7EAD12149175470D91d1BEA465c1D6ee3C5E7E1A
BRIDGE_ADDRESS=0x98f8a9Ce7aA9dF2fe6C3931Dad6bf654e59d7C01
INDEXER_INTERVAL=3
IPFS_HOST='https://ipfs.io'
```

### Polygon

```dotenv
UPSTREAM=https://matic-mumbai.chainstacklabs.com/
TOKEN_ABI_FILENAME=token_indexer/erc721-abi.json
TOKEN_ADDRESS=0x81a6e27FE7659B210e9Fd7C30765Eb268294C9aA
BRIDGE_ADDRESS=0x7123d1e4fDC36300C083fE7276e8429EBC3F6d07
INDEXER_INTERVAL=3
IPFS_HOST='https://ipfs.io'
```


## Step 4. Oracle indexer

Oracle provides a REST API with which you can track the execution of transactions. Oracle indexer is a worker that tracks bridging closures.

```dotenv
ORACLE_API=<URL API>
URI_TX=<endpoint transaction Hash>
```

`python3 oracle_indexer/indexer.py`

## LICENSE

```
OnBridge - NFT bridge for advanced GameFi mechanics
Copyright (C) 2021 OnBridge.IO

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
```
