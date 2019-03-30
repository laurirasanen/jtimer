# jtimer
jtimer is a [Source.Python](https://github.com/Source-Python-Dev-Team/Source.Python) speedrun timer plugin for TF2. Other Source games might work but have not been tested. jtimer is fully open source and welcomes contributors.

# Features
  - Sub engine tick timer accuracy
    - Floating point representation of players run time, rather than being limited by the closest intergral representation of Source engine ticks (e.g. 15 milliseconds in TF2). Achieved by checking the distance from players bounding box to the edge of a timer zone when moving into or out of the zone. Combining the distance with the players current velocity gives the exact time until the zone is triggered. 
  - Support for any tick rate
  - Timer HUD
  
**Planned features:**
  - Database support
  - In-game map/course/bonus editing (Tier, Zones, etc.)
  - In-game zone editing
    - Adding and removing zones
    - Scaling and moving zones
  - In-game time editing
    - Removing times
    - Adding times
  - In-game player editing
    - Wiping players times  

# Contributing
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)  
jtimer uses [Black](https://github.com/ambv/black) for code formatting. Contributors should follow the same style guidelines to maintain consistency and readability of the codebase. Small pull requests and those that do not implement new major features can be made directly into the `develop` branch. Large pull requests or ones that do implement new features should be made into a new branch, using the naming scheme `feature/<feature_name>`.

# Contributors
[Yoeri Poels (Author)](https://github.com/yoeripoels)  
[Lauri Räsänen (Author)](https://github.com/laurirasanen)
