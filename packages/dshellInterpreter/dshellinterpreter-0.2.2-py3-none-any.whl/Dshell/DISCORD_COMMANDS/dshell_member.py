from discord import MISSING, Message, Member


__all__ = [
    "dshell_ban_member",
    "dshell_unban_member",
    "dshell_kick_member",
    "dshell_rename_member",
    "dshell_add_roles",
    "dshell_remove_roles",
]

async def dshell_ban_member(ctx: Message, member: int, reason: str = MISSING):
    """
    Bans a member from the server.
    """
    banned_member = ctx.channel.guild.get_member(member)

    if not banned_member:
        return 1 # Member not found in the server

    await ctx.channel.guild.ban(banned_member, reason=reason)

    return banned_member.id

async def dshell_unban_member(ctx: Message, user: int, reason: str = MISSING):
    """
    Unbans a user from the server.
    """
    banned_users = ctx.channel.guild.bans()
    user_to_unban = None

    async for ban_entry in banned_users:
        if ban_entry.user.id == user:
            user_to_unban = ban_entry.user
            break

    if not user_to_unban:
        return 1  # User not found in the banned list

    await ctx.channel.guild.unban(user_to_unban, reason=reason)

    return user_to_unban.id

async def dshell_kick_member(ctx: Message, member: int, reason: str = MISSING):
    """
    Kicks a member from the server.
    """
    kicked_member = ctx.channel.guild.get_member(member)

    if not kicked_member:
        return 1  # Member not found in the server

    await ctx.channel.guild.kick(kicked_member, reason=reason)

    return kicked_member.id

async def dshell_rename_member(ctx: Message, new_name, member=None):
    """
    Renames a member in the server.
    """
    renamed_member = ctx.channel.guild.get_member(member)

    if not renamed_member:
        return 1  # Member not found in the server

    await renamed_member.edit(nick=new_name)

    return renamed_member.id

async def dshell_add_roles(ctx: Message, roles: list[int], member=None, reason: str = None):
    """
    Adds roles to a member in the server.
    """
    target_member: Member = ctx.author if member is None else ctx.channel.guild.get_member(member)

    if not target_member:
        return 1  # Member not found in the server

    roles_to_add = [ctx.channel.guild.get_role(role_id) for role_id in roles if ctx.channel.guild.get_role(role_id)]

    if not roles_to_add:
        return 2  # No valid roles found

    await target_member.add_roles(*roles_to_add, reason=reason)

    return target_member.id

async def dshell_remove_roles(ctx: Message, roles: list[int], member=None, reason: str = None):
    """
    Removes roles from a member in the server.
    """
    target_member: Member = ctx.author if member is None else ctx.channel.guild.get_member(member)

    if not target_member:
        return 1  # Member not found in the server

    roles_to_remove = [ctx.channel.guild.get_role(role_id) for role_id in roles if ctx.channel.guild.get_role(role_id)]

    if not roles_to_remove:
        return 2  # No valid roles found

    await target_member.remove_roles(*roles_to_remove, reason=reason)

    return target_member.id