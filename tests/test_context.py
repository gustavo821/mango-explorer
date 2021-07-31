from .context import mango

from solana.publickey import PublicKey


def context_has_default_values(ctx):
    assert ctx.cluster == "devnet"
    assert ctx.cluster_url == "https://api.devnet.solana.com"
    assert ctx.program_id == PublicKey("5fP7Z7a87ZEVsKr2tQPApdtq83GcTW4kz919R6ou5h5E")
    assert ctx.dex_program_id == PublicKey("DESVgJVGajEgKGXhb6XmqDHGz3VjdgP7rEVESBgxmroY")
    assert ctx.group_name == "devnet.0"
    assert ctx.group_id == PublicKey("ENALFdayYzkpkKoz3JBk33HchJ3wrEuEuEkPowRhnEu1")


def test_context_default_exists():
    assert mango.ContextBuilder.default() is not None


def test_context_default_values():
    context_has_default_values(mango.ContextBuilder.default())


# Need to have more than one working cluster for this test.
# def test_new_from_cluster():
#     context_has_default_values(mango.ContextBuilder.default())
#     derived = mango.ContextBuilder.default().new_from_cluster("mainnet-beta")
#     assert derived.cluster == "mainnet-beta"
#     assert derived.cluster_url == "https://solana-api.projectserum.com"
#     assert derived.program_id == PublicKey("5fP7Z7a87ZEVsKr2tQPApdtq83GcTW4kz919R6ou5h5E")
#     assert derived.dex_program_id == PublicKey("DESVgJVGajEgKGXhb6XmqDHGz3VjdgP7rEVESBgxmroY")
#     assert derived.group_name == "devnet.0"
#     assert derived.group_id == PublicKey("ENALFdayYzkpkKoz3JBk33HchJ3wrEuEuEkPowRhnEu1")
#     context_has_default_values(mango.ContextBuilder.default())


def test_new_from_cluster_url():
    context_has_default_values(mango.ContextBuilder.default())
    derived = mango.ContextBuilder.default().new_from_cluster_url("https://some-dev-host")
    assert derived.cluster == "devnet"
    assert derived.cluster_url == "https://some-dev-host"
    assert derived.program_id == PublicKey("5fP7Z7a87ZEVsKr2tQPApdtq83GcTW4kz919R6ou5h5E")
    assert derived.dex_program_id == PublicKey("DESVgJVGajEgKGXhb6XmqDHGz3VjdgP7rEVESBgxmroY")
    assert derived.group_name == "devnet.0"
    assert derived.group_id == PublicKey("ENALFdayYzkpkKoz3JBk33HchJ3wrEuEuEkPowRhnEu1")
    context_has_default_values(mango.ContextBuilder.default())


def test_new_from_group_name():
    context_has_default_values(mango.ContextBuilder.default())
    derived = mango.ContextBuilder.default().new_from_group_name("devnet.0")
    assert derived.cluster == "devnet"
    assert derived.cluster_url == "https://api.devnet.solana.com"
    assert derived.program_id == PublicKey("5fP7Z7a87ZEVsKr2tQPApdtq83GcTW4kz919R6ou5h5E")
    assert derived.dex_program_id == PublicKey("DESVgJVGajEgKGXhb6XmqDHGz3VjdgP7rEVESBgxmroY")

    # Should update both of these values on new group name.
    assert derived.group_name == "devnet.0"
    assert derived.group_id == PublicKey("ENALFdayYzkpkKoz3JBk33HchJ3wrEuEuEkPowRhnEu1")
    context_has_default_values(mango.ContextBuilder.default())


def test_new_from_group_id():
    context_has_default_values(mango.ContextBuilder.default())
    derived = mango.ContextBuilder.default().new_from_group_id(PublicKey("ENALFdayYzkpkKoz3JBk33HchJ3wrEuEuEkPowRhnEu1"))
    assert derived.cluster == "devnet"
    assert derived.cluster_url == "https://api.devnet.solana.com"
    assert derived.program_id == PublicKey("5fP7Z7a87ZEVsKr2tQPApdtq83GcTW4kz919R6ou5h5E")
    assert derived.dex_program_id == PublicKey("DESVgJVGajEgKGXhb6XmqDHGz3VjdgP7rEVESBgxmroY")

    # Should update both of these values on new group ID.
    assert derived.group_name == "devnet.0"
    assert derived.group_id == PublicKey("ENALFdayYzkpkKoz3JBk33HchJ3wrEuEuEkPowRhnEu1")
    context_has_default_values(mango.ContextBuilder.default())
