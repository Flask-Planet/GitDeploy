import os

from app import wsgi

# this is an attempt to try and stop conflicts between the main app and the satellite app
VERSION_SIG = '8cc331ae4b'

# These should reflect the values in app/default.config.toml
os.environ[f"INSTANCE_TAG_{VERSION_SIG}"] = f"gitdeploy_{os.urandom(24).hex()}"
os.environ[f"SECRET_KEY_{VERSION_SIG}"] = os.urandom(24).hex()
os.environ[f"SESSION_{VERSION_SIG}"] = f"session_{os.urandom(24).hex()}"

wsgi.run(host="0.0.0.0", port=9898, debug=True)
