import argparse
import sys
from encryptor import encrypt
from runner import loader

def main():
    parser = argparse.ArgumentParser(
        description="ShadowSeal - Secure Python Encryption Tool",
        usage="shadowseal {encrypt,run,decrypt} ...\n"
              "  shadowseal encrypt <script>.py [-o <output>.shc] [-p <password>]\n"
              "  shadowseal run <script>.shc [-p <password>]\n"
              "  shadowseal decrypt <script>.shc -o <output>.py [-p <password>]"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Encrypt command
    encrypt_parser = subparsers.add_parser('encrypt', help='Encrypt a Python file')
    encrypt_parser.add_argument('input', help='Input Python (.py) file to encrypt')
    encrypt_parser.add_argument('-o', '--output', required=True, help='Output encrypted .shc file')
    encrypt_parser.add_argument('-p', '--password', help='Encryption password (optional - passwordless if not provided)')

    # Run command
    run_parser = subparsers.add_parser('run', help='Run an encrypted .shc file',
                                      usage="shadowseal run <script>.shc [-p PASSWORD] [-- script_args...]")
    run_parser.add_argument('file', help='Encrypted .shc file to run')
    run_parser.add_argument('-p', '--password', help='Decryption password (optional for passwordless files)')
    run_parser.add_argument('script_args', nargs=argparse.REMAINDER, help='Arguments to pass to the encrypted script')

    # Decrypt command
    decrypt_parser = subparsers.add_parser('decrypt', help='Decrypt a .shc file back to Python')
    decrypt_parser.add_argument('file', help='Encrypted .shc file to decrypt')
    decrypt_parser.add_argument('-o', '--output', required=True, help='Output Python (.py) file')
    decrypt_parser.add_argument('-p', '--password', help='Decryption password (optional for passwordless files)')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    if args.command == 'encrypt':
        print(f"🔐 Encrypting {args.input} to {args.output}...")
        password = encrypt.encrypt_file(args.input, args.output, args.password)
        if args.password is None:
            print("✅ Encryption complete (passwordless)")
        else:
            print("✅ Encryption complete")
            print(f"🔑 Password: {password}")
        print("\n📋 Usage:")
        print(f"  shadowseal run {args.output}")
        print(f"  shadowseal decrypt {args.output} -o original.py")

    elif args.command == 'run':
        print(f"💥 Running encrypted file: {args.file}")
        success = loader.run_shc(args.file, args.password)
        if success:
            print("✅ Execution completed successfully")
        else:
            print("❌ Execution failed")
            sys.exit(1)

    elif args.command == 'decrypt':
        print(f"🔓 Decrypting {args.file} to {args.output}...")
        try:
            encrypt.decrypt_file(args.file, args.output, args.password)
            print("✅ Decryption complete.")
        except Exception as e:
            print(f"❌ Decryption failed: {e}")
            sys.exit(1)

if __name__ == '__main__':
    main()
