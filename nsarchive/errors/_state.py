class AlreadyCandidateError(Exception): # 409
	def __init__(self, *args):
		super().__init__(*args)

class NotEnoughMembersError(Exception): # 422
	def __init__(self, *args):
		super().__init__(*args)

class NotAPartyError(Exception): # 422
	def __init__(self, *args):
		super().__init__(*args)