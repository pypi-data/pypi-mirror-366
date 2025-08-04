"""
CryptoPIX Command Line Interface

Provides command-line access to the revolutionary CryptoPIX cryptographic library.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import cryptopix

def create_kem_command(args):
    """Handle KEM operations"""
    kem = cryptopix.create_kem(args.security_level)
    
    if args.action == 'keygen':
        public_key, private_key = kem.keygen()
        
        # Save keys
        if args.public_key_file:
            with open(args.public_key_file, 'w') as f:
                json.dump(public_key.to_dict(), f, indent=2)
            print(f"Public key saved to {args.public_key_file}")
        
        if args.private_key_file:
            with open(args.private_key_file, 'w') as f:
                json.dump(private_key.to_dict(), f, indent=2)
            print(f"Private key saved to {args.private_key_file}")
        
        # Save visual representation
        if args.visual_file:
            with open(args.visual_file, 'wb') as f:
                f.write(public_key.visual_representation)
            print(f"Visual public key saved to {args.visual_file}")
    
    elif args.action == 'encapsulate':
        # Load public key
        with open(args.public_key_file, 'r') as f:
            pub_key_data = json.load(f)
        public_key = cryptopix.ChromaCryptPublicKey.from_dict(pub_key_data)
        
        # Encapsulate
        shared_secret, capsule = kem.encapsulate(public_key)
        
        # Save outputs
        with open(args.secret_file, 'wb') as f:
            f.write(shared_secret)
        
        with open(args.capsule_file, 'wb') as f:
            f.write(capsule)
        
        print(f"Shared secret saved to {args.secret_file}")
        print(f"Capsule saved to {args.capsule_file}")
    
    elif args.action == 'decapsulate':
        # Load private key and capsule
        with open(args.private_key_file, 'r') as f:
            priv_key_data = json.load(f)
        private_key = cryptopix.ChromaCryptPrivateKey.from_dict(priv_key_data)
        
        with open(args.capsule_file, 'rb') as f:
            capsule = f.read()
        
        # Decapsulate
        shared_secret = kem.decapsulate(private_key, capsule)
        
        # Save output
        with open(args.secret_file, 'wb') as f:
            f.write(shared_secret)
        
        print(f"Shared secret saved to {args.secret_file}")

def create_sign_command(args):
    """Handle signature operations"""
    sign = cryptopix.create_signature_scheme(args.security_level)
    
    if args.action == 'keygen':
        key_pair = sign.keygen()
        
        # Save key pair
        if args.key_file:
            with open(args.key_file, 'w') as f:
                f.write(sign.export_key_pair(key_pair))
            print(f"Key pair saved to {args.key_file}")
        
        # Save visual public key
        if args.visual_file:
            with open(args.visual_file, 'wb') as f:
                f.write(key_pair.visual_public_key)
            print(f"Visual public key saved to {args.visual_file}")
    
    elif args.action == 'sign':
        # Load key pair
        with open(args.key_file, 'r') as f:
            key_pair = sign.import_key_pair(f.read())
        
        # Read message
        if args.message_file:
            with open(args.message_file, 'rb') as f:
                message = f.read()
        else:
            message = args.message.encode('utf-8')
        
        # Sign
        signature = sign.sign(message, key_pair)
        
        # Save signature
        with open(args.signature_file, 'w') as f:
            f.write(sign.export_signature(signature))
        
        # Save visual signature
        if args.visual_file:
            with open(args.visual_file, 'wb') as f:
                f.write(signature.visual_signature)
        
        print(f"Signature saved to {args.signature_file}")
    
    elif args.action == 'verify':
        # Load key pair and signature
        with open(args.key_file, 'r') as f:
            key_pair = sign.import_key_pair(f.read())
        
        with open(args.signature_file, 'r') as f:
            signature = sign.import_signature(f.read())
        
        # Read message
        if args.message_file:
            with open(args.message_file, 'rb') as f:
                message = f.read()
        else:
            message = args.message.encode('utf-8')
        
        # Verify
        is_valid = sign.verify(message, signature, key_pair)
        
        if is_valid:
            print("Signature is VALID")
            sys.exit(0)
        else:
            print("Signature is INVALID")
            sys.exit(1)

def create_cipher_command(args):
    """Handle symmetric encryption operations"""
    cipher = cryptopix.create_cipher(args.security_level)
    
    if args.action == 'encrypt':
        # Read plaintext
        if args.input_file:
            with open(args.input_file, 'rb') as f:
                plaintext = f.read()
        else:
            plaintext = args.text.encode('utf-8')
        
        # Encrypt
        if args.fast_mode:
            cipher = cryptopix.create_cipher(args.security_level)
            cipher.fast_mode = True
            ciphertext, color_key = cipher.encrypt(plaintext, args.password)
            
            # Save as text file
            with open(args.output_file, 'w') as f:
                f.write(ciphertext)
        else:
            ciphertext, color_key = cipher.encrypt(plaintext, args.password)
            
            # Save as image
            with open(args.output_file, 'wb') as f:
                f.write(ciphertext)
        
        # Save color key
        with open(args.key_file, 'w') as f:
            f.write(cipher.export_color_key(color_key))
        
        print(f"Encrypted data saved to {args.output_file}")
        print(f"Color key saved to {args.key_file}")
    
    elif args.action == 'decrypt':
        # Load color key
        with open(args.key_file, 'r') as f:
            color_key = cipher.import_color_key(f.read())
        
        # Load ciphertext
        if color_key.metadata.get('encryption_mode') == 'fast':
            with open(args.input_file, 'r') as f:
                ciphertext = f.read()
        else:
            with open(args.input_file, 'rb') as f:
                ciphertext = f.read()
        
        # Decrypt
        plaintext = cipher.decrypt(ciphertext, color_key, args.password)
        
        # Save plaintext
        with open(args.output_file, 'wb') as f:
            f.write(plaintext)
        
        print(f"Decrypted data saved to {args.output_file}")

def create_hash_command(args):
    """Handle hash operations"""
    hasher = cryptopix.create_hash(args.security_level)
    
    # Read input data
    if args.input_file:
        with open(args.input_file, 'rb') as f:
            data = f.read()
    else:
        data = args.text.encode('utf-8')
    
    if args.format == 'colors':
        colors = hasher.hash_to_colors(data)
        print(f"Color hash: {colors}")
    
    elif args.format == 'hex':
        hex_hash = hasher.hash_to_hex_string(data)
        print(f"Hex hash: {hex_hash}")
        
        if args.output_file:
            with open(args.output_file, 'w') as f:
                f.write(hex_hash)
    
    elif args.format == 'image':
        image_data = hasher.hash_to_image(data)
        
        if args.output_file:
            with open(args.output_file, 'wb') as f:
                f.write(image_data)
            print(f"Hash image saved to {args.output_file}")
        else:
            print("Error: output file required for image format")

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CryptoPIX - Revolutionary Post-Quantum Cryptographic Library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate KEM key pair
  cryptopix kem keygen --security-level 128 --public-key pub.json --private-key priv.json
  
  # Sign a message
  cryptopix sign keygen --key keys.json
  cryptopix sign sign --key keys.json --message "Hello World" --signature sig.json
  
  # Encrypt data (fast mode)
  cryptopix cipher encrypt --text "Secret data" --password mypass --output data.txt --key key.json --fast
  
  # Hash to image
  cryptopix hash --text "Hello World" --format image --output hash.png
        """
    )
    
    parser.add_argument('--version', action='version', version=f'CryptoPIX {cryptopix.__version__}')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # KEM subcommand
    kem_parser = subparsers.add_parser('kem', help='Key Encapsulation Mechanism operations')
    kem_parser.add_argument('action', choices=['keygen', 'encapsulate', 'decapsulate'])
    kem_parser.add_argument('--security-level', type=int, choices=[128, 192, 256], default=128)
    kem_parser.add_argument('--public-key-file')
    kem_parser.add_argument('--private-key-file')
    kem_parser.add_argument('--visual-file')
    kem_parser.add_argument('--secret-file')
    kem_parser.add_argument('--capsule-file')
    
    # Sign subcommand
    sign_parser = subparsers.add_parser('sign', help='Digital signature operations')
    sign_parser.add_argument('action', choices=['keygen', 'sign', 'verify'])
    sign_parser.add_argument('--security-level', type=int, choices=[128, 192, 256], default=128)
    sign_parser.add_argument('--key-file')
    sign_parser.add_argument('--message')
    sign_parser.add_argument('--message-file')
    sign_parser.add_argument('--signature-file')
    sign_parser.add_argument('--visual-file')
    
    # Cipher subcommand
    cipher_parser = subparsers.add_parser('cipher', help='Symmetric encryption operations')
    cipher_parser.add_argument('action', choices=['encrypt', 'decrypt'])
    cipher_parser.add_argument('--security-level', type=int, choices=[128, 192, 256], default=128)
    cipher_parser.add_argument('--text')
    cipher_parser.add_argument('--input-file')
    cipher_parser.add_argument('--output-file')
    cipher_parser.add_argument('--key-file')
    cipher_parser.add_argument('--password', required=True)
    cipher_parser.add_argument('--fast', dest='fast_mode', action='store_true', help='Use fast mode')
    
    # Hash subcommand
    hash_parser = subparsers.add_parser('hash', help='Color hash operations')
    hash_parser.add_argument('--security-level', type=int, choices=[128, 192, 256], default=128)
    hash_parser.add_argument('--text')
    hash_parser.add_argument('--input-file')
    hash_parser.add_argument('--output-file')
    hash_parser.add_argument('--format', choices=['colors', 'hex', 'image'], default='hex')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'kem':
            create_kem_command(args)
        elif args.command == 'sign':
            create_sign_command(args)
        elif args.command == 'cipher':
            create_cipher_command(args)
        elif args.command == 'hash':
            create_hash_command(args)
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()