# OnBridge token indexing engine and API server

In-browser Web3 JS library is not capable to extract transactions history natively. It's also pretty slow, especially on large lists. And it can be connected to just one network at a time (and bridge needs info from two networks at least).

To make user experience smoother we offload heavy background tasks to backend that indexes contract states and events on both L1 and L2 networks and makes correlation between bridging requests and transactions on both sides.

## Build and Run

This service is designed to be built and run using docker compose. See the root repository for details.

To run in separately:

```sh
export ADMIN_USER=admin
export ADMIN_PASSWORD=<very secure admin password>
export DB_HOST=localhost
export DB_NAME=api
export DB_USER=api
export DB_PASSWORD=<very secure db password>
docker build -t api
docker run -it -e ADMIN_USER -e ADMIN_PASSWORD -e DB_HOST -e DB_NAME -e DB_USER -e DB_PASSWORD --network=host api
```

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
