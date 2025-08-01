from discord import MISSING, Message, Role, Permissions, PermissionOverwrite
from discord.utils import _MissingSentinel
from .._DshellInterpreteur.dshell_interpreter import build_colour, ListNode

__all__ = [
    'dshell_create_role',
    'dshell_delete_roles',
    'dshell_edit_role'

]

async def dshell_create_role(ctx: Message,
                             name: str = MISSING,
                             permissions: dict[None, PermissionOverwrite] = MISSING,
                             color: int = MISSING,
                             hoist: bool = MISSING,
                             mentionable: bool = MISSING,
                             reason: str = None):
    """
    Creates a role on the server.
    """
    if not isinstance(name, (str, _MissingSentinel)):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if not isinstance(permissions, (dict, _MissingSentinel)):
        raise Exception(f"Permissions must be a PermissionNode, not {type(permissions)} !")

    colour = build_colour(color)

    if not isinstance(hoist, (bool, _MissingSentinel)):
        raise Exception(f"Hoist must be a boolean, not {type(permissions)} !")

    if not isinstance(mentionable, (bool, _MissingSentinel)):
        raise Exception(f"Mentionable must be a boolean, not {type(permissions)} !")

    if isinstance(permissions, dict):
        if None in permissions:
            allow, deny = permissions[None].pair()
            permissions = allow

    created_role = await ctx.guild.create_role(name=name,
                                               permissions=permissions,
                                               colour=colour,
                                               hoist=hoist,
                                               mentionable=mentionable,
                                               reason=str(reason))

    return created_role.id


async def dshell_delete_roles(ctx: Message, roles, reason=None):
    """
    Delete the role on the server
    """
    roles: int | ListNode
    if not isinstance(roles, (int, ListNode)):
        raise Exception(f"Role must be a int, role mention or NodeList of both, not {type(roles)} !")

    if isinstance(roles, int):
        roles: tuple = (roles, )

    for i in roles:
        role_to_delete = ctx.guild.get_role(i)

        if role_to_delete is None:
            raise Exception(f'Role {i} not found in the server !')

        await role_to_delete.delete(reason=str(reason))


async def dshell_edit_role(ctx: Message,
                           role,
                           name=None,
                           permissions: dict[None, PermissionOverwrite]=None,
                           color=None,
                           hoist=None,
                           mentionable=None,
                           position=None,
                           reason=None,):
    """
    Edit the current role
    """
    if not isinstance(role, int):
        raise Exception(f"Role must be a int or role mention not {type(role)} !")

    role_to_edit = ctx.guild.get_role(role)

    if not isinstance(name, (str, None)):
        raise Exception(f"Name must be a string, not {type(name)} !")

    if not isinstance(permissions, (dict, None)):
        raise Exception(f"Permissions must be a PermissionNode, not {type(permissions)} !")

    if isinstance(permissions, dict):
        if None in permissions:
            allow, deny = permissions[None].pair()
            permissions = allow

    colour = build_colour(color)

    if not isinstance(hoist, (bool, None)):
        raise Exception(f"Hoist must be a boolean, not {type(permissions)} !")

    if not isinstance(mentionable, (bool, None)):
        raise Exception(f"Mentionable must be a boolean, not {type(permissions)} !")

    if not isinstance(position, (int, None)):
        raise Exception(f"Position must be an integer, not {type(permissions)} !")

    await role_to_edit.edit(name=name if name is not None else role_to_edit.name,
                            permissions=permissions if permissions is not None else role_to_edit.permissions,
                            colour=colour if color is not None else role_to_edit.colour,
                            hoist=hoist if hoist is not None else role_to_edit.hoist,
                            mentionable=mentionable if mentionable is not None else role_to_edit.mentionable,
                            position=position if position is not None else role_to_edit.position,
                            reason=str(reason))
