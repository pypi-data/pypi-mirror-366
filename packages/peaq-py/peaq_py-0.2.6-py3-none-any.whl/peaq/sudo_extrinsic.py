from peaq.utils import ExtrinsicBatch


def funds(substrate, kp_sudo, dsts, token_num, new_reserved=0):
    batch = ExtrinsicBatch(substrate, kp_sudo)
    for dst in dsts:
        batch.compose_sudo_call(
            'Balances',
            'force_set_balance',
            {
                'who': dst,
                'new_free': token_num,
                'new_reserved': new_reserved
            })
    return batch.execute()


# [TODO] Change the API, kp_dst to addr
def fund(substrate, kp_sudo, kp_dst, new_free, new_reserved=0):
    batch = ExtrinsicBatch(substrate, kp_sudo)
    batch.compose_sudo_call(
        'Balances',
        'force_set_balance',
        {
            'who': kp_dst.ss58_address,
            'new_free': new_free,
            'new_reserved': new_reserved
        }
    )
    return batch.execute()
