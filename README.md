NaviCane
========

A portable cane to provide in-building navigation guidance for a visually-impaired person

*** User Story

Cylis is a woman in her 50s. She suffers from cataract since her
early 40s. The illness has rendered her practically blind now. With the help of her trusted
walking cane and Naal, her guide dog, Cylis has no problem travelling to many of her
favorite places in the city. However, navigating in a building poses a huge problem for her.
Firstly, many buildings disallow guide dog. Secondly, it is hard for her to traverse through
the maze‐like interior to get to her destination. Is there anything we can do to help Cylis and
many others like her?


*** Main Theme

A __portable__ device to provide **__in-building__** navigation guidance for a __visually-impaired__ person


*** Main Requirements

1. Wearable. Example: A cap, backpack, belt, walking stick etc. Weight, form factor and
comfort are all potential evaluation criteria.

2. Provide path navigation. Figure out the path from one point in the building to
another and guide the wearer to walk toward the specified endpoint.

3. Obstacle avoidance. Guide the wearer to avoid obstacle along the way. Obstacles
may be static and or moving. Elevation detection may be needed to handle staircase,
uneven ground, hole in the ground, etc.


*** Provided Information

1. There are several end points in a building to represent possible destinations.
--* Each end point will have a unique id for simplicity.
--* The wearer will specify the unique id of the starting and destination end points.
--* Building floor plan can be retrieved through internet.
2. Hardware platform:
--* A Raspberry Pi mini‐computer
--* An Arduino mega board
--* A set of standard sensors
--* $300 budget for additional hardware

