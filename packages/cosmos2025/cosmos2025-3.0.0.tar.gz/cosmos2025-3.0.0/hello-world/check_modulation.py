# use this snippet to check if the modulation and demodulation process works correctly
bits = np.random.randint(0, 2, 1000)
symbols = encode_bits(bits)
message = create_message(symbols)

decoded_symbols = decode_message(message)
assert np.allclose(symbols, decoded_symbols), (
    "Decoded symbols do not match encoded symbols"
)

decoded_bits = decode_symbols(decoded_symbols)
assert np.array_equal(bits, decoded_bits), "Decoded bits do not match original bits"
