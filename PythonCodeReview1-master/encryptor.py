import argparse
import sys
import pickle
import itertools as it
from string import punctuation, digits, ascii_letters


SUPPORTED_SYMBOLS = []
SUPPORTED_DICT = dict()


def read_data(filename):
    if filename is not None:
        with open(filename, 'r') as f:
            text = f.read()
        return text
    return sys.stdin.read().strip()  

def consists_from_supported_symbols(line):
    for letter in line:
        if letter not in SUPPORTED_DICT:
            return False
    return True


def add_range_of_symbols(first_symbol, last_symbol):
    index = first_symbol
    while index != last_symbol + 1:
        SUPPORTED_DICT[chr(index)] = len(SUPPORTED_DICT)
        SUPPORTED_SYMBOLS.append(chr(index))
        index += 1


def build_symbol_list():
    for letter in it.chain(punctuation, digits, ascii_letters):
        SUPPORTED_DICT[letter] = len(SUPPORTED_DICT)
        SUPPORTED_SYMBOLS.append(letter)
    add_range_of_symbols(ord('а'), ord('я'))
    add_range_of_symbols(ord('А'), ord('Я'))
    SUPPORTED_DICT['ё'] = len(SUPPORTED_DICT)
    SUPPORTED_SYMBOLS.append('ё')
    SUPPORTED_DICT['Ё'] = len(SUPPORTED_DICT)
    SUPPORTED_SYMBOLS.append('Ё')
    SUPPORTED_DICT[' '] = len(SUPPORTED_DICT)
    SUPPORTED_SYMBOLS.append(' ')
    SUPPORTED_DICT['\n'] = len(SUPPORTED_DICT)
    SUPPORTED_SYMBOLS.append('\n')


def print_data(data, output_file):
    if output_file is None:
        print(data, end='')
    else:
        with open(output_file, 'w') as f:
            f.write(data)


def caesar(text, encrypting_number):
    output_data = []
    for letter in text:
        if letter in SUPPORTED_DICT:
            code = SUPPORTED_DICT[letter]
            code = (code + encrypting_number + len(SUPPORTED_SYMBOLS)) % len(SUPPORTED_SYMBOLS)
            output_data.append(SUPPORTED_SYMBOLS[code])
        else:
            output_data.append(letter)
    return "".join(output_data)


def vigenere(text, encoding_word, encode):
    multiplier = 1
    if not encode:
        multiplier = -1
    current_index = 0
    output_data = []
    for letter in text:
        if letter in SUPPORTED_DICT:
            code = SUPPORTED_DICT[letter]
            code = (code + multiplier * SUPPORTED_DICT[encoding_word[current_index]]) % len(SUPPORTED_SYMBOLS)
            output_data.append(SUPPORTED_SYMBOLS[code])
            current_index = (current_index + 1) % len(encoding_word)
        else:
            output_data.append(letter)
    return "".join(output_data)


def train(text):
    counted_letters = 0
    counter = [0] * len(SUPPORTED_SYMBOLS)
    for letter in text:
        if letter in SUPPORTED_DICT:
            counter[SUPPORTED_DICT[letter]] += 1
            counted_letters += 1
    if counted_letters != 0:
        for i in range(len(SUPPORTED_SYMBOLS)):
            counter[i] = counter[i] / counted_letters
    return counter


def n_train(text, n):
    training_dict = dict()
    if len(text) < n:
        return dict()
    current_prefix = text[:n - 1]
    for i in range(n - 1, len(text)):
        if current_prefix in training_dict:
            if text[i] in training_dict[current_prefix]:
                training_dict[current_prefix][text[i]] += 1 / len(text)
            else:
                training_dict[current_prefix][text[i]] = 1 / len(text)
        else:
            training_dict[current_prefix] = dict()
            training_dict[current_prefix][text[i]] = 1 / len(text)
        current_prefix += text[i]
        current_prefix = current_prefix[1:]
    return training_dict


def hack(text, model):
    text_copy = text
    min_dif = float("inf")
    best_key = 0
    sum_arr = train(caesar(text_copy, 0))
    for key in range(len(SUPPORTED_SYMBOLS)):
        now_dif = count_difference(sum_arr, model, key)
        if now_dif < min_dif:
            min_dif, best_key = now_dif, key

    return caesar(text, best_key)


def count_difference(train1, train2, offset):
    total_difference = 0
    for i in range(len(SUPPORTED_SYMBOLS)):
        total_difference += (float(train1[(i - offset + len(SUPPORTED_SYMBOLS)) % len(SUPPORTED_SYMBOLS)]) - float(train2[i]))**2
    return total_difference


def n_hack(text, n, model):
    text_copy = text
    max_similarity = 0
    best_key = 0
    for key in range(len(SUPPORTED_SYMBOLS)):
        now_similarity = n_count_similarity(caesar(text_copy, key), n, model)
        if now_similarity > max_similarity:
            max_similarity, best_key = now_similarity, key
    return caesar(text, best_key)


def n_count_similarity(text, n, model):
    similarity = 0
    prefix = text[:n - 1]
    for i in range(n - 1, len(text)):
        if prefix in model:
            if text[i] in model[prefix]:
                similarity += model[prefix][text[i]]
        prefix += text[i]
        prefix = prefix[1:]
    return similarity


def encode_from_args(args):
    if args.cipher == "caesar":
        if args.key.isdigit():
            text = read_data(args.input_file)
            key = int(args.key) % len(SUPPORTED_SYMBOLS)
            output_data = caesar(text, key)
            print_data(output_data, args.output_file)
        else:
            print("Incorrect data entered: key is a word or a negative number.", file=sys.stderr)
    elif args.cipher == "vigenere":
        if consists_from_supported_symbols(args.key):
            text = read_data(args.input_file)
            output_data = vigenere(text, args.key, True)
            print_data(output_data, args.output_file)
        else:
            print("Incorrect data entered: key doesn't consist of supported symbols only.", file=sys.stderr)


def decode_from_args(args):
    if args.cipher == "caesar":
        if args.key.isdigit():
            text = read_data(args.input_file)
            key = int(args.key) % len(SUPPORTED_SYMBOLS)
            output_data = caesar(text, -key)
            print_data(output_data, args.output_file)
        else:
            print("Incorrect data entered: key is a word or a negative number.", file=sys.stderr)
    elif args.cipher == "vigenere":
        if consists_from_supported_symbols(args.key):
            text = read_data(args.input_file)
            output_data = vigenere(text, args.key, False)
            print_data(output_data, args.output_file)
        else:
            print("Incorrect data entered: key doesn't consist of supported symbols only.", file=sys.stderr)


def train_from_args(args):
    text = read_data(args.text_file)
    if args.n_gram is not None and args.n_gram > 1:
        output_dict = n_train(text, args.n_gram)
        output_data = {"n": args.n_gram, "dict": output_dict}
        with open(args.model_file, "wb") as f:
            pickle.dump(output_data, f)
    elif args.n_gram is not None and args.n_gram <= 1:
        print("Incorrect data entered: n must be more than one.", file=sys.stderr)
    else:
        output_arr = train(text)
        output_data = {"n": 0, "arr": output_arr}
        with open(args.model_file, "wb") as f:
            pickle.dump(output_data, f)


def hack_from_args(args):
    text = read_data(args.input_file)
    with open(args.model_file, "rb") as f:
        input_data = pickle.load(f)
    if input_data["n"] == 0:
        model = input_data["arr"]
        output_data = hack(text, model)
        print_data(output_data, args.output_file)
    else:
        n = input_data["n"]
        model = input_data["dict"]
        output_data = n_hack(text, n, model)
        print_data(output_data, args.output_file)


def get_arguments():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    encode_parser = subparsers.add_parser('encode')
    encode_parser.set_defaults(func=encode_from_args)
    encode_parser.add_argument("-c", "--cipher", help="Can be equal to caesar vigenere.", type=str, required=True,
                               choices=["caesar", "vigenere"])
    encode_parser.add_argument("-k", "--key", help="Can be a number if you chose caesar previously or a word otherwise.",
                               type=str, required=True)
    encode_parser.add_argument("-i", "--input-file", help="The name of the input file.", type=str)
    encode_parser.add_argument("-o", "--output-file", help="The name of the output file.", type=str)
    encode_parser.set_defaults(action='encode')

    decode_parser = subparsers.add_parser('decode')
    decode_parser.set_defaults(func=decode_from_args)
    decode_parser.add_argument("-c", "--cipher", help="Can be equal to caesar vigenere.", type=str, required=True,
                               choices=["caesar", "vigenere"])
    decode_parser.add_argument("-k", "--key", help="Can be a number if you chose caesar previously or a word otherwise.",
                               type=str, required=True)
    decode_parser.add_argument("-i", "--input-file", help="The name of the input file.", type=str)
    decode_parser.add_argument("-o", "--output-file", help="The name of the output file.", type=str)
    decode_parser.set_defaults(action='decode')

    train_parser = subparsers.add_parser('train')
    train_parser.set_defaults(func=train_from_args)
    train_parser.add_argument("-t", "--text-file", help="The name of the input file for model.", type=str)
    train_parser.add_argument("-m", "--model-file", help="The name of the output file for model.", type=str, required=True)
    train_parser.add_argument("-n", "--n-gram", help="The value of n to count n-grams.", type=int)
    train_parser.set_defaults(action='train')

    hack_parser = subparsers.add_parser('hack')
    hack_parser.set_defaults(func=hack_from_args)
    hack_parser.add_argument("-i", "--input-file", help="The name of the input file.", type=str)
    hack_parser.add_argument("-o", "--output-file", help="The name of the output file.", type=str)
    hack_parser.add_argument("-m", "--model-file", help="The name of the output file for model.", type=str, required=True)
    hack_parser.set_defaults(action='hack')

    return parser.parse_args()


def main():
    args = get_arguments()
    build_symbol_list()
    args.func(args)


if __name__ == "__main__":
    main()
