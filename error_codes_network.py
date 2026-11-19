# ====================== Calculation functions ======================

def parity_bit(ncode):
    # Calculate the parity bit for the given code
    count = ncode.count('1')
    return '0' if count % 2 == 0 else '1'


def column_parity(rows):
    # Calculate the parity bit of each column and return them as a string
    result = ""
    for j in range(len(rows[0])):
        col = ""
        for row in rows:
            col += row[j]
        result += parity_bit(col)
    return result


def build_table(data_rows):
    # Add parity bit to each row, then add the column parity row
    table = []
    for row in data_rows:
        table.append(row + parity_bit(row))
    table.append(column_parity(table))
    return table


def print_table(table):
    # Print the table, with a line before the last row and a | before the last column
    for i in range(len(table)):
        row = table[i]
        print(" ".join(row[:-1]) + " | " + row[-1])
        if i == len(table) - 2:
            print("-" * (len(row) * 2 + 1))


def ones_sum(words, k):
    # Add the words with end-around carry (one's complement sum)
    mask = (1 << k) - 1
    total = 0
    for w in words:
        total += int(w, 2)
        while total > mask:
            total = (total & mask) + (total >> k)   # add the carry back to the beginning
    return total


def xor_bits(a, b):
    # XOR two bit strings with the same length
    result = ""
    for i in range(len(b)):
        if a[i] == b[i]:
            result += "0"
        else:
            result += "1"
    return result


def xor_divide(bits, gen):
    # XOR division of bits by gen, returns the remainder (len(gen) - 1 bits)
    for i in range(len(bits) - len(gen) + 1):
        if bits[i] == '1':
            bits = bits[:i] + xor_bits(bits[i:i + len(gen)], gen) + bits[i + len(gen):]
    return bits[-(len(gen) - 1):]


def is_power_of_two(n):
    return n & (n - 1) == 0


def hamming_check_count(m):
    # Number of check bits (r) for m data bits: 2^r >= m + r + 1
    r = 0
    while 2 ** r < m + r + 1:
        r += 1
    return r


def hamming_encode(data):
    # Check bits are placed at positions 1, 2, 4, 8, ... and data bits in other positions
    m = len(data)
    n = m + hamming_check_count(m)
    code = [0] * (n + 1)          # index 0 is not used, positions start from 1

    data_index = 0
    for pos in range(1, n + 1):
        if not is_power_of_two(pos):
            code[pos] = int(data[data_index])
            data_index += 1

    # each check bit covers the positions that have its bit set in their binary number
    pos = 1
    while pos <= n:
        count = 0
        for j in range(1, n + 1):
            if j & pos and j != pos:
                count += code[j]
        code[pos] = count % 2     # even parity
        pos *= 2

    result = ""
    for pos in range(1, n + 1):
        result += str(code[pos])
    return result


def hamming_syndrome(codeword):
    # Returns 0 if all checks are ok, otherwise the position of the wrong bit
    n = len(codeword)
    syndrome = 0
    pos = 1
    while pos <= n:
        count = 0
        for j in range(1, n + 1):
            if j & pos:
                count += int(codeword[j - 1])
        if count % 2 == 1:
            syndrome += pos
        pos *= 2
    return syndrome


def hamming_data(codeword):
    # Take the data bits out of the codeword (skip positions 1, 2, 4, 8, ...)
    data = ""
    for pos in range(1, len(codeword) + 1):
        if not is_power_of_two(pos):
            data += codeword[pos - 1]
    return data


def hamming_merge(data, sent_codeword):
    # Put the received data bits in the codeword, check bits come from the sender
    result = ""
    data_index = 0
    for pos in range(1, len(sent_codeword) + 1):
        if is_power_of_two(pos):
            result += sent_codeword[pos - 1]
        else:
            result += data[data_index]
            data_index += 1
    return result


def flip(bit):
    return '1' if bit == '0' else '0'


# ====================== Input functions ======================

def read_int(prompt):
    # Keep asking until the user enters a positive number
    while True:
        text = input(prompt).strip()
        if text.isdigit() and int(text) > 0:
            return int(text)
        print("Please enter a positive number.")


def read_bits(prompt, length, exact):
    # Keep asking until the input has only 0 and 1 and has a valid length
    while True:
        text = input(prompt).strip()
        if text == "" or not set(text) <= {"0", "1"}:
            print("Only 0 and 1 are allowed.")
        elif exact and len(text) != length:
            print(f"The length must be exactly {length} bits.")
        elif len(text) > length:
            print(f"Code {text} is longer than the specified length of {length}. Please enter a valid code.")
        else:
            return text


def read_codes(code_num, codes_len):
    # Read the codes of the sender, shorter codes are padded with zeros
    codes_ls = []
    while len(codes_ls) < code_num:
        ncode = read_bits(f"Enter code {len(codes_ls) + 1}: ", codes_len, False)
        codes_ls.append("0" * (codes_len - len(ncode)) + ncode)
    return codes_ls


def read_received(count, length, name):
    # Read the received data, the length must be exactly the same as the sender
    received_ls = []
    while len(received_ls) < count:
        received_ls.append(read_bits(f"Enter received {name} {len(received_ls) + 1}: ", length, True))
    return received_ls


# ====================== Method 1: simple parity ======================

def run_parity(codes_ls, codes_len):
    # ---------- Sender side ----------
    sent_ls = []
    for code in codes_ls:
        pb = parity_bit(code)
        full_code = code + pb
        sent_ls.append(full_code)
        print(f"Code: {code}, Parity Bit: {pb} ==> Full Code: {full_code}")

    # ---------- Receiver side ----------
    print("\nNow enter the received codes (with parity bit):")
    received_ls = read_received(len(sent_ls), codes_len + 1, "code")

    # ---------- Checking ----------
    print("\nResults:")
    for i in range(len(sent_ls)):
        sent = sent_ls[i]
        received = received_ls[i]

        data_part = received[:-1]
        received_pb = received[-1]
        parity_ok = (parity_bit(data_part) == received_pb)
        same_as_original = (received == sent)

        if same_as_original:
            print(f"Code {i + 1}: no error")
        elif not parity_ok:
            print(f"Code {i + 1}: error detected! (sent: {sent}, received: {received})")
        else:
            print(f"Code {i + 1}: there is an error but parity bit could not detect it! (sent: {sent}, received: {received})")


# ====================== Method 2: 2D parity ======================

def run_2d(codes_ls, codes_len):
    code_num = len(codes_ls)

    # ---------- Sender side ----------
    sent_table = build_table(codes_ls)

    print("\nSender table:")
    print_table(sent_table)

    # ---------- Receiver side ----------
    print(f"\nNow enter the received data ({code_num} rows, each {codes_len} bits, without parity):")
    received_data = read_received(code_num, codes_len, "row")

    # the receiver calculates the parity bits itself
    received_table = build_table(received_data)

    print("\nReceiver table (parity bits calculated by receiver):")
    print_table(received_table)

    # ---------- Checking ----------
    # compare the parity bits calculated by receiver with the ones from sender
    bad_rows = []
    for i in range(code_num):
        if received_table[i][-1] != sent_table[i][-1]:
            bad_rows.append(i)

    bad_cols = []
    for j in range(codes_len):
        if received_table[-1][j] != sent_table[-1][j]:
            bad_cols.append(j)

    print("\nResults:")
    for i in range(code_num):
        if i in bad_rows:
            print(f"Row {i + 1}: parity does not match -> wrong")
        else:
            print(f"Row {i + 1}: parity matches -> ok")
    for j in range(codes_len):
        if j in bad_cols:
            print(f"Column {j + 1}: parity does not match -> wrong")
        else:
            print(f"Column {j + 1}: parity matches -> ok")

    print()
    if len(bad_rows) == 0 and len(bad_cols) == 0:
        if received_data == codes_ls:
            print("No error.")
        else:
            print("There is an error but 2D parity could not detect it!")
    elif len(bad_rows) == 1 and len(bad_cols) == 1:
        r = bad_rows[0]
        c = bad_cols[0]
        print(f"Single-bit error detected at row {r + 1}, column {c + 1}.")

        # correct the wrong bit
        row = received_data[r]
        received_data[r] = row[:c] + flip(row[c]) + row[c + 1:]

        print("Corrected table:")
        print_table(build_table(received_data))
    else:
        print("Error detected! Bad rows:", [r + 1 for r in bad_rows], "Bad columns:", [c + 1 for c in bad_cols])
        print("More than one bit is wrong, so it can't be corrected.")


# ====================== Method 3: Checksum ======================

def run_checksum(codes_ls, codes_len):
    mask = (1 << codes_len) - 1

    # ---------- Sender side ----------
    sender_sum = ones_sum(codes_ls, codes_len)
    checksum = format(mask - sender_sum, 'b').zfill(codes_len)   # complement of the sum

    print("\nSender side:")
    for i in range(len(codes_ls)):
        print(f"Word {i + 1}: {codes_ls[i]}")
    print(f"Sum (with carry added back): {format(sender_sum, 'b').zfill(codes_len)}")
    print(f"Checksum (complement of sum): {checksum}")

    # ---------- Receiver side ----------
    print(f"\nNow enter the received words ({len(codes_ls)} words, each {codes_len} bits, without checksum):")
    received_data = read_received(len(codes_ls), codes_len, "word")

    # the checksum comes from the sender, the receiver adds everything
    receiver_sum = ones_sum(received_data + [checksum], codes_len)

    print("\nReceiver side:")
    print(f"Sum of received words + checksum: {format(receiver_sum, 'b').zfill(codes_len)}")

    # ---------- Checking ----------
    print("\nResults:")
    if received_data == codes_ls:
        print("No error.")
    elif receiver_sum != mask:
        print("Error detected! (the sum is not all 1s)")
    else:
        print("There is an error but checksum could not detect it!")


# ====================== Method 4: CRC ======================

def read_generator():
    # The generator must start with 1, has only 0 and 1 and at least 2 bits
    while True:
        gen = input("Enter the generator (like 10011): ").strip()
        if len(gen) >= 2 and gen[0] == '1' and set(gen) <= {"0", "1"}:
            return gen
        print("The generator must have at least 2 bits, only 0 and 1, and start with 1.")


def run_crc(codes_ls, codes_len):
    gen = read_generator()
    r = len(gen) - 1

    # ---------- Sender side ----------
    crc_ls = []
    print()
    for code in codes_ls:
        crc = xor_divide(code + "0" * r, gen)   # add r zeros, divide, remainder is the CRC
        crc_ls.append(crc)
        print(f"Data: {code}, CRC: {crc} ==> Frame: {code + crc}")

    # ---------- Receiver side ----------
    print(f"\nNow enter the received data ({len(codes_ls)} codes, each {codes_len} bits, without CRC):")
    received_data = read_received(len(codes_ls), codes_len, "code")

    # ---------- Checking ----------
    print("\nResults:")
    for i in range(len(received_data)):
        frame = received_data[i] + crc_ls[i]     # received data + CRC from the sender
        remainder = xor_divide(frame, gen)
        print(f"Code {i + 1}: frame = {frame}, remainder = {remainder}")

        if received_data[i] == codes_ls[i]:
            print(f"Code {i + 1}: no error")
        elif '1' in remainder:
            print(f"Code {i + 1}: error detected! (remainder is not zero)")
        else:
            print(f"Code {i + 1}: there is an error but CRC could not detect it!")


# ====================== Method 5: Hamming ======================

def run_hamming(codes_ls, codes_len):
    r = hamming_check_count(codes_len)
    print(f"\nHamming code ({codes_len + r},{codes_len}): {r} check bits at positions 1, 2, 4, ...")

    # ---------- Sender side ----------
    sent_ls = []
    for code in codes_ls:
        full_code = hamming_encode(code)
        sent_ls.append(full_code)
        print(f"Data: {code} ==> Hamming code: {full_code}")

    # ---------- Receiver side ----------
    print(f"\nNow enter the received data ({len(codes_ls)} codes, each {codes_len} bits, without check bits):")
    received_data = read_received(len(codes_ls), codes_len, "code")

    # ---------- Checking ----------
    print("\nResults:")
    for i in range(len(codes_ls)):
        # data comes from the channel, check bits come from the sender
        received_code = hamming_merge(received_data[i], sent_ls[i])
        syndrome = hamming_syndrome(received_code)
        print(f"Code {i + 1}: received codeword = {received_code}, error position = {syndrome}")

        if syndrome == 0:
            if received_data[i] == codes_ls[i]:
                print(f"Code {i + 1}: no error")
            else:
                print(f"Code {i + 1}: there is an error but Hamming code could not detect it!")
        elif syndrome > len(received_code):
            print(f"Code {i + 1}: error detected, but the position is out of range so it can't be corrected.")
        else:
            pos = syndrome
            fixed_code = received_code[:pos - 1] + flip(received_code[pos - 1]) + received_code[pos:]
            fixed_data = hamming_data(fixed_code)
            print(f"Code {i + 1}: error at position {pos}, corrected codeword = {fixed_code}")

            if fixed_data == codes_ls[i]:
                print(f"Code {i + 1}: corrected successfully, data = {fixed_data}")
            else:
                print(f"Code {i + 1}: more than one bit is wrong, so the correction is not right!")


# ====================== Main ======================

def main():
    method = ""
    while method not in ["parity", "2d", "checksum", "crc", "hamming"]:
        method = input("Which method? Enter 'parity', '2d', 'checksum', 'crc' or 'hamming': ").strip().lower()

    code_num = read_int("How many codes? ")
    codes_len = read_int("What is the length of codes? ")
    codes_ls = read_codes(code_num, codes_len)

    if method == "parity":
        run_parity(codes_ls, codes_len)
    elif method == "2d":
        run_2d(codes_ls, codes_len)
    elif method == "checksum":
        run_checksum(codes_ls, codes_len)
    elif method == "crc":
        run_crc(codes_ls, codes_len)
    else:
        run_hamming(codes_ls, codes_len)


if __name__ == "__main__":
    main()
