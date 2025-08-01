from peaq.utils import ExtrinsicBatch


def did_add_payload(batch, did_account, name, value, valid_for=None):
    batch.compose_call('PeaqDid', 'add_attribute', {
        'did_account': did_account,
        'name': name,
        'value': value,
        'valid_for': valid_for,
    })


def did_add(substrate, kp_src, did_account, name, value, valid_for=None):
    batch = ExtrinsicBatch(substrate, kp_src)
    did_add_payload(batch, did_account, name, value, valid_for)
    return batch.execute()


def did_update_payload(batch, did_account, name, value, valid_for=None):
    batch.compose_call(
        'PeaqDid',
        'update_attribute',
        {
            'did_account': did_account,
            'name': name,
            'value': value,
            'valid_for': valid_for,
        })


def did_update(substrate, kp_src, did_account, name, value, valid_for=None):
    batch = ExtrinsicBatch(substrate, kp_src)
    did_update_payload(batch, did_account, name, value, valid_for)
    return batch.execute()


def did_remove_payload(batch, did_account, name):
    batch.compose_call(
        'PeaqDid',
        'remove_attribute',
        {
            'did_account': did_account,
            'name': name,
        })


def did_remove(substrate, kp_src, did_account, name):
    batch = ExtrinsicBatch(substrate, kp_src)
    did_remove_payload(batch, did_account, name)
    return batch.execute()


def did_rpc_read(substrate, did_account, name):
    bl_hsh = substrate.get_block_hash(None)
    data = substrate.rpc_request('peaqdid_readAttribute', [did_account, name, bl_hsh])
    return data['result']
