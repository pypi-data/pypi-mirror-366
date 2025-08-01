from peaq.utils import ExtrinsicBatch


def _rpc_id(entity_id):
    return [int(entity_id[i:i + 2], 16) for i in range(0, len(entity_id), 2)]


def _from_rpc_id(entity_id):
    return ''.join(format(i, '02x') for i in entity_id)


def _comp_rbac_call(batch, cl_fcn, cl_par):
    batch.compose_call(
        'PeaqRbac',
        cl_fcn,
        cl_par
    )


def rbac_add_role_payload(batch, entity_id, name):
    _comp_rbac_call(
        batch,
        'add_role',
        {
            'role_id': entity_id,
            'name': name,
        })


def rbac_add_role(substrate, kp_src, entity_id, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_add_role_payload(batch, entity_id, name)
    return batch.execute()


def rbac_add_group_payload(batch, group_id, name):
    _comp_rbac_call(
        batch,
        'add_group',
        {
            'group_id': group_id,
            'name': name,
        })


def rbac_add_group(substrate, kp_src, group_id, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_add_group_payload(batch, group_id, name)
    return batch.execute()


def rbac_add_permission_payload(batch, permission_id, name):
    _comp_rbac_call(
        batch,
        'add_permission',
        {
            'permission_id': permission_id,
            'name': name,
        })


def rbac_add_permission(substrate, kp_src, permission_id, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_add_permission_payload(batch, permission_id, name)
    return batch.execute()


def rbac_permission2role_payload(batch, permission_id, role_id):
    _comp_rbac_call(
        batch,
        'assign_permission_to_role',
        {
            'permission_id': permission_id,
            'role_id': role_id,
        })


def rbac_permission2role(substrate, kp_src, permission_id, role_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_permission2role_payload(batch, permission_id, role_id)
    return batch.execute()


def rbac_role2group_payload(batch, role_id, group_id):
    _comp_rbac_call(
        batch,
        'assign_role_to_group',
        {
            'role_id': role_id,
            'group_id': group_id,
        })


def rbac_role2group(substrate, kp_src, role_id, group_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_role2group_payload(batch, role_id, group_id)
    return batch.execute()


def rbac_role2user_payload(batch, role_id, user_id):
    _comp_rbac_call(
        batch,
        'assign_role_to_user',
        {
            'role_id': role_id,
            'user_id': user_id,
        })


def rbac_role2user(substrate, kp_src, role_id, user_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_role2user_payload(batch, role_id, user_id)
    return batch.execute()


def rbac_user2group_payload(batch, user_id, group_id):
    _comp_rbac_call(
        batch,
        'assign_user_to_group',
        {
            'user_id': user_id,
            'group_id': group_id,
        })


def rbac_user2group(substrate, kp_src, user_id, group_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_user2group_payload(batch, user_id, group_id)
    return batch.execute()


def rbac_disable_group_payload(batch, group_id):
    _comp_rbac_call(
        batch,
        'disable_group',
        {
            'group_id': group_id,
        })


def rbac_disable_group(substrate, kp_src, group_id):
    batch = ExtrinsicBatch(substrate, kp_src)
    rbac_disable_group_payload(batch, group_id)
    return batch.execute()


def _convert_output(data):
    for convert_type in ['id', 'name', 'role', 'group', 'permission', 'user']:
        if convert_type in data:
            if not data[convert_type]:
                continue
            if isinstance(data[convert_type][0], list):
                data[convert_type] = [bytes(item).decode('utf-8')
                                      for item in data[convert_type]]
                continue
            try:
                data[convert_type] = bytes(data[convert_type]).decode('utf-8')
            except UnicodeDecodeError:
                data[convert_type] = _from_rpc_id(data[convert_type])


def _rbac_rpc_fetch_entity(substrate, addr, entity, params):
    bl_hsh = substrate.get_block_hash(None)
    data = substrate.rpc_request(
        f'peaqrbac_fetch{entity}',
        [addr] + params + [bl_hsh]
    )['result']

    if 'Err' in data:
        data['Err']['param'] = _from_rpc_id(data['Err']['param'])
    elif 'Ok' in data:
        ok = data['Ok']
        if isinstance(ok, list):
            for item in ok:
                _convert_output(item)
        else:
            _convert_output(ok)
    return data


def rbac_rpc_fetch_role(substrate, addr, entity_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Role', [_rpc_id(entity_id)])


def rbac_rpc_fetch_permission(substrate, addr, entity_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Permission', [_rpc_id(entity_id)])


def rbac_rpc_fetch_group(substrate, addr, entity_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Group', [_rpc_id(entity_id)])


def rbac_rpc_fetch_roles(substrate, addr):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Roles', [])


def rbac_rpc_fetch_permissions(substrate, addr):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Permissions', [])


def rbac_rpc_fetch_groups(substrate, addr):
    return _rbac_rpc_fetch_entity(substrate, addr, 'Groups', [])


def rbac_rpc_fetch_group_roles(substrate, addr, group_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'GroupRoles', [_rpc_id(group_id)])


def rbac_rpc_fetch_group_permissions(substrate, addr, group_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'GroupPermissions', [_rpc_id(group_id)])


def rbac_rpc_fetch_role_permissions(substrate, addr, role_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'RolePermissions', [_rpc_id(role_id)])


def rbac_rpc_fetch_user_roles(substrate, addr, user_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'UserRoles', [_rpc_id(user_id)])


def rbac_rpc_fetch_user_groups(substrate, addr, user_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'UserGroups', [_rpc_id(user_id)])


def rbac_rpc_fetch_user_permissions(substrate, addr, user_id):
    return _rbac_rpc_fetch_entity(substrate, addr, 'UserPermissions', [_rpc_id(user_id)])
