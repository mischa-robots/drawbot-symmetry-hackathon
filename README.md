# Web3 Symmetry Hackathon Berlin 2024

We are Lana and Mischa - Team "Web3 Drawbot"

We are building a robot for an Interactive Robot Art Installation, where robots are drawing on a canvas while driving, controlled by AI and humans. A person can connect to a robot with their smart phone and take control via a web app. We are integrating blockchain into this web app to create a dApp, where a user can connect their wallet to buy a control token and use that control token to take control over the robot. The token becomes also a proof of participation in the installation and the finished drawing is then pushed automatically to every participants wallet as an NFT.

## Usage

The robot runs on a Jetson Nano with driver written in Rust lang running in a docker container based on [dustynv/onnxruntime:r32.7.1](https://github.com/dusty-nv/jetson-containers/tree/master/packages/onnxruntime) .

To use this repository for your robot project, give it first a star, then fork it to your Github account.

[Docker installation](https://docs.docker.com/engine/install/ubuntu/) is required, check also the [Jetson Nano docs](https://developer.nvidia.com/embedded/learn/tutorials/jetson-container), please.

Also make sure that you have the latest L4T version installed on your Jetson Nano (32.7.1)

## Setup project on your Jetson Nano

Clone your forked repository to your Jetson Nano like this:

```
git clone git@github.com:mischa-robots/drawbot-symmetry-hackathon.git
```

Download latest [mediamtx]() executable and extract it into the `mediamtx` directory.

Then start the docker containers:

```
cd jetbot-rust
docker compose up
```

This will start one docker container with a web server written in Rust, which provides a webservice to open the web app (dApp) on your phone and control the robot.

It will also start a second container with [mediamtx]() server and camera pipeline to stream the robots video in realtime to the web app.

## Access and develop your Jetbot from your local machine with VSCode

Read [VSCode Remote SSH](https://code.visualstudio.com/remote/advancedcontainers/develop-remote-host) to learn how you can access the Jetbot from your local Desktop VSCode instance and develop directly on the Jetbot.

## Web3 dApp implementation idea

The idea is to use the NMKR Api via the dApp and on the robot.

- The user connects to the robot over WiFi and opens the dApp in the mobile phone browser
- Then connect wallet to the dApp to mint an NFT (Control Token) via the NMKR Api
- Now the user can use the control token to take control over one robot, the robot will validate the token also via the NMKR Api
- If token is valid, the user will see joysticks and video stream in their dApp and can drive the robot for a certain amount of time (for example 5 minutes)
- When the time is run out, the dApp will close the connection to the robot
- The robot will mark the token via NMKR Api as used, so it will become a proof of participation in an installation
- When the installation is finished, a photo will be made of the result drawing and every participants token is updated via the NMKR Api to contain the Drawing as NFT
- Participants will become collectors of drawings in which they took part


## License

    Copyright (C) 2024 Mischa (Michael Schaefer)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the [GNU General Public License](LICENSE)
    along with this program.  If not, see <https://www.gnu.org/licenses/>.