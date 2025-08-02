"""
Example: display the token of the current machine used for:
    - deactivating an active license
    - obtaining an offline activation code
"""

import pyRecFusionSDK as rf

print(f"Using RecFusionSDK v{rf.version()}")
print(f"This machine token: {rf.token()}")
