with open('app/core/token_blacklist.py', 'r') as f:
    content = f.read()

old = '''        raise


async def is_token_blacklisted'''
new = '''        # Gracefully handle Redis connection failures - log but don't raise
        # This ensures logout works even when Redis is unavailable


async def is_token_blacklisted'''

content = content.replace(old, new)

with open('app/core/token_blacklist.py', 'w') as f:
    f.write(content)
print('Done')