test scene for MPEG_Node_interactivity_:

INTERACTIVITY

- Balls are subject to gravity. Plane is not. Balls should fall and bounce when scene intializes.  

- When balls collide with the plane, the plane takes the same material as the ball, and a bouncing ball sound should play: `TRIGGER_COLLISION * TRIGGER_ACTIVATE_EACH_ENTER = ACTION_SET_MATERIAL, ACTION_MEDIA`

- When viewer gets close to the ball, its motion is frozen: `TRIGGER_PROXIMITY * TRIGGER_ACTIVATE_ON = ACTION_BLOCK`

- When viewer gets too far from the plane, the plane is removed from the scene, and the balls should fall: `TRIGGER_PROXIMITY * TRIGGER_ACTIVATE_EACH_ENTER = ACTION_ACTIVATE`


scene resets when: 
- on "/user/hand/left/input/select/click" => `TRIGGER_USER_INPUT * TRIGGER_ACTIVATE_EACH_ENTER = ACTION_TRASNFORM, ACTION_ACTIVATE`
- when the balls are too far from viewer
