from peaq.utils import ExtrinsicBatch


# [TODO] Change API
def transfer_with_tip(substrate, kp_src, kp_dst_addr, token_num, tip, token_base=0):
    if not token_base:
        token_base = 10 ** 3

    batch = ExtrinsicBatch(substrate, kp_src)
    batch.compose_call(
        'Balances',
        'transfer_keep_alive', {
            'dest': kp_dst_addr,
            'value': token_num * token_base
        }
    )
    return batch.execute(False, None, tip * token_base)


# TODO Change API
def transfer(substrate, kp_src, kp_dst_addr, token_num, token_base=0):
    return transfer_with_tip(substrate, kp_src, kp_dst_addr, token_num, 0, token_base)
