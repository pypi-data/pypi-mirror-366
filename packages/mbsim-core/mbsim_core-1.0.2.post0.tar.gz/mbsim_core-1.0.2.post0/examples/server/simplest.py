"""
Simplest mbsim

This will setup a shared context with all Val set to 0
"""

import mbsim.core.server

mbsim.core.server.start("tcp", address=("", 5020))
