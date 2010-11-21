from waveapi import robot

USE_CHAIN_LENGTH = 4

def authorize():
	robot.setup_oauth(
		269341747276,
		'TLICc/8M9DzMOBRyzar+EfEZ',
		server_rpc_base="http://www-opensocial.googleusercontent.com/api/rpc"
		)
