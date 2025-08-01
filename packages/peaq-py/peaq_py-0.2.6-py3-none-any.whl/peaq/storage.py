from peaq.utils import ExtrinsicBatch


def storage_add_payload(batch, item_type, item):
    batch.compose_call(
        'PeaqStorage',
        'add_item',
        {
            'item_type': item_type,
            'item': item,
        })


def storage_add(substrate, kp_src, item_type, item):
    batch = ExtrinsicBatch(substrate, kp_src)
    storage_add_payload(batch, item_type, item)
    return batch.execute()


def storage_update_payload(batch, item_type, item):
    batch.compose_call(
        'PeaqStorage',
        'update_item',
        {
            'item_type': item_type,
            'item': item,
        })


def storage_update(substrate, kp_src, item_type, item):
    batch = ExtrinsicBatch(substrate, kp_src)
    storage_update_payload(batch, item_type, item)
    return batch.execute()


def storage_rpc_read(substrate, addr, item_type):
    bl_hsh = substrate.get_block_hash(None)
    data = substrate.rpc_request('peaqstorage_readAttribute', [
                                 addr, item_type, bl_hsh])
    return data['result']
