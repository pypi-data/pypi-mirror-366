synchronize_permissions('Masters')
rql('SET M owned_by U WHERE M foruser U, NOT M owned_by U')
checkpoint()
