MIN_ANIMATION_DURATION = 1
"""
The minimum number of seconds we accept as a
parameter to build a manim animation.
"""
MAX_ANIMATION_DURATION = 120
"""
The maximum number of seconds we accept as a
parameter to build a manim animation.
"""
INSTANTANEOUS_RUN_TIME = 1e-6
"""
The 'run_time' value to make the animation
to be instantaneous and not able to watch
it moving. This value allows us using 
methods like this one below, that would not
be possible with a value of 0:
- `ApplyMethod(mobject.move_to, position, run_time = INSTANTANEOUS_RUN_TIME)`
"""